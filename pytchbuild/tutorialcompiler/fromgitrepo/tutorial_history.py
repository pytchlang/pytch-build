from cached_property import cached_property


################################################################################

class ProjectCommit:
    def __init__(self, repo, oid):
        self.repo = repo
        self.commit = repo[oid]
        self.oid = self.commit.id
