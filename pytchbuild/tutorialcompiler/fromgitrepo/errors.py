class InternalError(ValueError):
    """Situations which really shouldn't happen."""
    pass


class TutorialStructureError(ValueError):
    """Situations where the input repo is not suitable."""
    pass
