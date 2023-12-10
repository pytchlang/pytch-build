import pytch


class Bowl(pytch.Sprite):
    Costumes = ["bowl.png", "basket.png"]

    @pytch.when_green_flag_clicked
    def move_with_keys(
        self
    ):
        pass


class Apple(pytch.Sprite):
    Costumes = ["apple.png"]

    @pytch.when_I_receive("drop-apple")
    def move_down_stage(self):
        print(1)
        print(2)
        print(3)


# Pretend this is a Stage with Backdrops for purposes of test.
class ScoreKeeper(pytch.Stage):
    Backdrops = ["Dani.png"]

    @pytch.when_green_flag_clicked
    def initialise(self):
        print(100)

    @pytch.when_I_receive("award-point")
    def award_point(self):
        pass

    @pytch.when_green_flag_clicked
    def drop_apples(self):
        pass
