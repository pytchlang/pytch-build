import pytch


class Bowl(pytch.Sprite):
    Costumes = ["bowl.png"]

    @pytch.when_green_flag_clicked
    def move_with_keys(self):
        pass
