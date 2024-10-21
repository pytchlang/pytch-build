import pytch
import random


class Bowl(pytch.Sprite):
    Costumes = ["bowl.png"]

    @pytch.when_green_flag_clicked
    def move_with_keys(self):
        self.go_to_xy(0, -145)

        while True:
            if pytch.key_pressed("a"):
                if self.x_position >= -145:
                    self.change_x(-2)
            if pytch.key_pressed("d"):
                if self.x_position <= 190:
                    self.change_x(2)


class Apple(pytch.Sprite):
    Costumes = ["apple.png", "pear.png", "banana.png"]

    @pytch.when_I_receive("drop-apple")
    def move_down_stage(self):
        drop_x = random.randint(-145, 190)
        self.go_to_xy(drop_x, 200)
        self.show()
        while self.y_position > -140:
            self.change_y(-3)
            if self.touching(Bowl):
                self.hide()
                pytch.broadcast("award-point")


class ScoreKeeper(pytch.Sprite):
    Costumes = ["Dani.png"]

    @pytch.when_green_flag_clicked
    def initialise(self):
        self.go_to_xy(-215, -115)
        self.score = 0
        self.say(self.score)

    @pytch.when_I_receive("award-point")
    def award_point(self):
        self.score += 1
        self.say(self.score)

    @pytch.when_green_flag_clicked
    def drop_apples(self):
        while True:
            pytch.broadcast_and_wait("drop-apple")
