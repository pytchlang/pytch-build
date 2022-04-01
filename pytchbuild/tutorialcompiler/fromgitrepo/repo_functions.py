import pygit2
import time


def create_signature(repo):
    return pygit2.Signature(
        repo.config["user.name"],
        repo.config["user.email"],
        time=int(time.time()),
    )
