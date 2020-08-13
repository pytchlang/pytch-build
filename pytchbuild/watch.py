from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import json
import janus
import asyncio
import websockets


class PytchFilesHandler(FileSystemEventHandler):
    """Handler for changes to the directory of interest

    Usage

        file_monitor = PytchFilesHandler(write_q)
        file_monitor.launch(dirname)

    where ``write_q`` is something which has a ``put()`` method.

    We sit here waiting to be called by the ``Observer`` we launch.  When we get
    called, we work out what the file having the new content is, and, if that
    file is an 'interesting' one (code or tutorial), we pass it on to our
    write-queue.
    """

    # We keep an eye on the Python code, and on the compiled HTML fragment.
    #
    # TODO: Don't keep rebuilding the entire ProjectHistory if all that's
    # changed is the tutorial text markdown file.
    #
    filenames_of_interest = [
        "code.py",
        "tutorial.html",
    ]

    def __init__(self, sync_q):
        self.sync_q = sync_q

    def on_created(self, event):
        if not event.is_directory:
            self.on_new_file_contents(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.on_new_file_contents(event.dest_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.on_new_file_contents(event.src_path)

    def on_new_file_contents(self, pathname):
        path = Path(pathname)
        print(f'on_new_file_contents(): considering "{path}"')
        if path.name in self.filenames_of_interest:
            print(f'on_new_file_contents(): sending "{path}"')
            self.sync_q.put(path)

    def launch(self, dirname):
        print(f'launch(): watching "{dirname}"')
        observer = Observer()
        observer.schedule(self, dirname)
        observer.start()


@dataclass
class IdeMessage:
    """A message to be sent to the web IDE

    Contains information in a form helpful to the IDE: Which tutorial this file
    belongs to, what kind of file it is (code or tutorial), and the actual
    file contents as text.

    Typically constructed from a path via

        msg = IdeMessage.from_path(path)

    and then used in its JSON representation via

        do_something_with(msg.as_json())

    Also provides a classmethod task which can transform paths read on one queue
    to ``IdeMessage`` instances written on another:

        asyncio.create_task(IdeMessage.transform_paths(read_q, write_q))
    """

    dir: str
    kind: str
    text: str

    def __str__(self):
        return f"<IdeMessage: {self.kind} / {len(self.text)} chars>"

    @classmethod
    def from_path(cls, path):
        kind = path.stem
        with path.open("rt") as f_in:
            text = f_in.read()
        return cls(path.parent.name, kind, text)

    def as_json(self):
        return json.dumps({
            "tutorial_name": self.dir,
            "kind": self.kind,
            "text": self.text,
        })

    @classmethod
    async def transform_paths(cls, read_q, write_q):
        while True:
            path = await read_q.get()
            await write_q.put(cls.from_path(path))


async def aggregate_modifies(read_q, write_q):
    """Aggregate multiply temporally-close updates into one

    When writing a big file, a handful of modify events are sometimes generated
    in quick succession.  We want to hold off processing the new file until it's
    been fully written.  (On Linux this could be done with the IN_CLOSE_WRITE
    inotify event but we're trying to be cross-platform.)  Delay passing on a
    message until we know it was the last one in its 'group', defined by a
    hard-coded delay of 125ms here.
    """

    seqnum_from_path = defaultdict(int)

    async def delayed_handle(path, seqnum):
        print('delayed_handle():', path, seqnum, 'entering')
        await asyncio.sleep(0.125)
        print('delayed_handle():', path, seqnum, 'waking', seqnum_from_path[path])
        if seqnum == seqnum_from_path[path]:
            print('delayed_handle(): sending', path)
            await write_q.put(path)

    while True:
        print("aggregate_modifies(): waiting for path msg")
        path = await read_q.get()
        print(f'aggregate_modifies(): processing path "{path}"')
        seqnum_from_path[path] += 1
        asyncio.create_task(delayed_handle(path, seqnum_from_path[path]))


class MessageBroker:
    """Broker relaying messages from a producer to all registered consumers

    Constructed from the queue it is to read messages from:

        broker = MessageBroker(read_q)

    and then set in motion via a task:

        asyncio.create_task(broker.relay_messages())

    Then other tasks can register consumption queues with the broker, being
    given a queue-id in return, and unregister themselves when finished.  A
    client task which is only interested in reading one message could do:

        qid = broker.register(my_read_q)
        msg = await my_read_q.get()
        broker.unregister(qid)
    """

    def __init__(self, read_q):
        self.read_q = read_q
        self.write_q_from_id = {}
        self.next_qid = 1000

    def register(self, write_q):
        assigned_qid = self.next_qid
        self.next_qid += 1
        self.write_q_from_id[assigned_qid] = write_q
        return assigned_qid

    def unregister(self, qid):
        del self.write_q_from_id[qid]

    async def relay_messages(self):
        while True:
            print("relay_messages(): awaiting message")
            msg = await self.read_q.get()
            n_clients = len(self.write_q_from_id)
            print(f'relay_messages(): sending "{msg}" to {n_clients} client/s')
            for write_q in self.write_q_from_id.values():
                await write_q.put(msg)


class ReloadServer:
    """WebSockets server which tells clients when code/tutorial has changed

    Constructed from the MessageBroker it is to register itself with:

        reload_server = ReloadServer(message_broker)

    and then turned into a WebSockets server via, say:

        websocket_server = await websockets.serve(reload_server.serve_client,
                                                  "127.0.0.1", 4111)

    which can then be run essentially forever by:

        await websocket_server.wait_closed()
    """

    def __init__(self, message_broker):
        self.message_broker = message_broker

    async def serve_client(self, websocket, path):
        print("serve_client(): entering")
        queue = asyncio.Queue()
        qid = self.message_broker.register(queue)
        print("serve_client(): registered and got qid", qid)
        try:
            while True:
                print(f"serve_client() [{qid}]: waiting for msg")
                msg = await queue.get()
                print(f"serve_client() [{qid}]: passing on \"{msg}\"")
                await websocket.send(msg.as_json())
        except websockets.ConnectionClosed as closure:
            print(f"serve_client() [{qid}]: connection closed:"
                  f" {closure.code} / \"{closure.reason}\"")
        finally:
            self.message_broker.unregister(qid)
            print(f"serve_client() [{qid}]: unregistered; leaving")


async def async_main(dirname):
    """Connect all the above together

    We launch a ``PytchFilesHandler``, which feeds into a ``MessageBroker``.
    This needs us to bridge the threaded and asyncio worlds, which we do via a
    ``Janus`` queue.  A ``ReloadServer`` accepts connections from browsers, each
    of which becomes a consumer of the ``MessageBroker``.

        [PytchFilesHandler]
            |
            | [sync side]
        (paths via Janus queue)
            | [async side]
            v
        [IdeMessage.transform_paths()]
            |
            |
        (IdeMessage instances via asyncio queue)
            |
            v
        [MessageBroker.relay_messages()]
            |
            +---------------------------------+
            |                                 |
        (IdeMessages via asyncio queue)    (IdeMessages via asyncio queue)
            |                                 |
            v                                 v
        [ReloadServer.serve_client()]      [ReloadServer.serve_client()]
            |                                 |
            v                                 v
        [browser]                          [browser]
    """

    paths_q = janus.Queue()
    file_monitor = PytchFilesHandler(paths_q.sync_q)
    file_monitor.launch(dirname)

    aggregated_paths_q = asyncio.Queue()
    asyncio.create_task(aggregate_modifies(paths_q.async_q, aggregated_paths_q))

    ide_msgs_q = asyncio.Queue()
    asyncio.create_task(IdeMessage.transform_paths(aggregated_paths_q, ide_msgs_q))

    message_broker = MessageBroker(ide_msgs_q)
    asyncio.create_task(message_broker.relay_messages())

    reload_server = ReloadServer(message_broker)
    server = await websockets.serve(reload_server.serve_client, "127.0.0.1", 4111)

    await server.wait_closed()
