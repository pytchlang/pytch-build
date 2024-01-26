import pytch


class Bowl(pytch.Sprite):
    Costumes = ["hello.png"]

    @pytch.when_green_flag_clicked
    @pytch.when_this_sprite_clicked
    def bad(self):
        pass
