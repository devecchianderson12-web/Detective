from . import startscreen
from framework import animations
from framework.stage import *

class LogoTCStage(Stage):

    def __init__(self, game):
        Stage.__init__(self, game)
        return

    def initialize(self):
        self.layer = Layer()
        back_rect = ItemRect(0, 0, 600, 450, None, 0, '', (0, 0, 0), (173, 168, 153))
        self.layer.add(back_rect)
        logo_image = assets.load_image_alpha('p0_placalogo.gif', None)
        self.logo = ItemImage(220, 121, logo_image)
        self.add_layer(self.layer)
        animations.wait(self, 2000, self.show_logo)
        return

    def show_logo(self):
        self.layer.add(self.logo)
        animations.fade_in_item(self.logo, 500, self.wait_show_logo)
        return

    def wait_show_logo(self, item):
        animations.wait(self, 3300, self.hide_logo)
        return

    def hide_logo(self):
        animations.fade_out_item(self.logo, False, 500, self.wait_hide_logo)
        return

    def wait_hide_logo(self, item):
        animations.wait(self, 500, self.go_to_main)
        return

    def go_to_main(self):
        self.game.set_stage(startscreen.StartScreenStage(self.game))
        return


