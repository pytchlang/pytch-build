import pytch


@pytch.when_green_flag_clicked
def h1(): pass


@pytch.when_I_start_as_a_clone
def h2(): pass


@pytch.when_I_receive("hello-world")
def h3(): pass


@pytch.when_key_pressed("b")
def h4(): pass


@pytch.when_this_sprite_clicked
def h5(): pass


@pytch.when_stage_clicked
def h6(): pass
