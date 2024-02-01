def make_of_kind(kind):
    def make(cls, *args):
        return cls(kind, *args)
    return classmethod(make)
