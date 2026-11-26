from framework import assets, animations
from framework.stage import *

class Witness:

    def __init__(self, stage):
        self.stage = stage
        self.font_18 = assets.load_font('powdrft_.ttf', 18)
        self.font_19 = assets.load_font('powdrft_.ttf', 19)
        self.font_20 = assets.load_font('powdrft_.ttf', 20)
        self.font_24 = assets.load_font('powdrft_.ttf', 24)
        self.rollover_sound = stage.rollover_sound
        self.click_sound = stage.click_sound
        self.layer = Layer()
        self.set_up_witness_background()
        self.set_up_witness_texts()
        self.set_up_witness_buttons()
        return

    def show_witness(self, witness, close_callback=None):
        self.close_callback = close_callback
        witness_image = assets.load_image(witness.image)
        self.image.set_image(witness_image)
        self.name.set_text(witness.name)
        self.city.set_text(witness.city.name)
        self.department.set_text(witness.department.name)
        s = '"' + witness.witness_statement.intro_statement.text + '"\n\n"' + witness.witness_statement.janitor_statement.text + '"\n\n"' + witness.witness_statement.identikit_statement.text + '"'
        if witness.witness_statement.location_statement:
            s += '\n\n"' + witness.witness_statement.location_statement.text.replace('\n', ' ') + '"'
        self.statement.set_text(s)
        self.stage.show_dialog(self.layer, self.witness_handle_event)
        return

    def close_witness(self):
        self.stage.close_dialog(self.layer)
        if self.close_callback != None:
            self.close_callback()
        return

    def witness_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.close_witness()
        return

    def set_up_witness_background(self):
        self.background_image = assets.load_image('p0_witness_popup.png')
        self.background = ItemImage(112, 53, self.background_image, None)
        self.image = ItemImage(154, 82, None, None)
        self.layer.add(self.background)
        self.layer.add(self.image)
        return

    def set_up_witness_texts(self):
        self.name = ItemText(219, 78, self.font_24, 0, '', (157, 21, 21), None, 180, 232)
        self.department = ItemText(220, 117, self.font_18, 0, '', (102, 102, 102), None, 250, 232)
        self.city = ItemText(221, 101, self.font_20, 0, '', (51, 51, 51), None, 250, 232)
        additional_fonts = {'bold': (self.font_19, 14, 0)}
        self.statement = ItemText(157, 158, self.font_19, 14, '', (51, 51, 51), None, 285, 205, 1, 1, additional_fonts)
        self.layer.add(self.name)
        self.layer.add(self.city)
        self.layer.add(self.department)
        self.layer.add(self.statement)
        return

    def set_up_witness_buttons(self):
        self.close_button_image = assets.load_image('btn_testigo_x_normal.png')
        self.close_button_image_rollover = assets.load_image('btn_testigo_x_rollover.png')
        self.close_button = ItemImage(432, 75, self.close_button_image, None, True)
        self.close_button.set_rollover(self.close_button_image_rollover, self.rollover_sound)
        self.close_button.add_event_handler(ItemEvent.CLICK, self.close_click)
        self.layer.add(self.close_button)
        return

    def close_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.close_witness()
        return


