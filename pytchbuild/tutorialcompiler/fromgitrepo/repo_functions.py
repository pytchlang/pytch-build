import pygit2
import time


def create_signature(repo):
    return pygit2.Signature(
        repo.config["user.name"],
        repo.config["user.email"],
        time=int(time.time()),
    )


def ensure_status_clean(repo):
    acceptable_flags_values = [
        pygit2.GIT_STATUS_CURRENT,
        pygit2.GIT_STATUS_IGNORED,
    ]

    unclean_paths = []
    for path, flags in repo.status().items():
        if flags not in acceptable_flags_values:
            unclean_paths.append(path)

    if unclean_paths:
        raise RuntimeError(f'repo not clean: {", ".join(unclean_paths)}')
