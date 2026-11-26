from . import map
from framework import animations
from framework.stage import *

class CaseStage(Stage):

    def __init__(self, game):
        Stage.__init__(self, game)
        return

    def initialize(self):
        self.font = assets.load_font('powdrft_.ttf', 17)
        self.newcase_sound = assets.load_sound('GUI_Turn_Page.ogg')
        self.rollover_sound = assets.load_sound('GUI_roll_over.ogg')
        self.continue_sound = assets.load_sound('GUI_Click.ogg')
        return

    def prepare(self):
        self.set_up_case()
        return

    def set_up_case(self):
        self.case_layer = Layer()
        background = assets.load_image('p0_case_presentation_clean.jpg')
        background_image = ItemImage(0, 0, background)
        self.case_layer.add(background_image)
        text1 = ItemText(45, 120, self.font, 13, '', (0, 0, 0), None, 230, 270)
        self.case_layer.add(text1)
        text2 = ItemText(330, 68, self.font, 13, '', (0, 0, 0), None, 131, 102)
        self.case_layer.add(text2)
        text3 = ItemText(330, 159, self.font, 13, '', (0, 0, 0), None, 220, 227)
        self.case_layer.add(text3)
        text1.break_text_into(text2)
        text2.break_text_into(text3)
        text = self.game.datastore.user_character_progress.case.get_full_text(self.game.datastore.user_character, self.game.datastore.user_character_progress)
        text1.set_text(text)
        next_image = assets.load_image('p0_endings_btn_continue_normal.png')
        next_rollover_image = assets.load_image('p0_endings_btn_continue_rollover.png')
        self.next_button = ItemImage(220, 401, next_image)
        self.next_button.set_rollover_image(next_rollover_image, self.rollover_sound)
        self.next_button.add_event_handler(ItemEvent.CLICK, self.next_click)
        self.case_layer.add(self.next_button)
        self.add_layer(self.case_layer)
        animations.blind_layer(self.case_layer, animations.BlindDirection.SHOW_DOWN, None)
        self.render()
        self.newcase_sound.play()
        return

    def next_click(self, item, args):
        self.render()
        self.continue_sound.play()
        self.go_next()
        return

    def go_next(self):
        crime_department = self.game.datastore.user_character_progress.case.crime_location.department
        m = map.Map(self, False, True)
        self.show_dialog(m.map_layer, None)
        m.add_other_layer()
        m.go_to(crime_department, False)
        return

    def handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.render()
            self.continue_sound.play()
            self.go_next()
        return


