import pytch

# Keep flake8 happy:
from not_really import when_things_happen, when_colour_appears


@when_things_happen
def h1(): pass


@pytch.when_unicorns_arrive
def h2(): pass


@when_colour_appears("red")
def h3(): pass


@pytch.when_things_dance("people")
def h4(): pass
