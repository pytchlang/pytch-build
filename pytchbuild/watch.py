from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


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
