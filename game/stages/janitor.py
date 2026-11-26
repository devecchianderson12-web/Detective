from framework import assets, text, animations
from framework.stage import *
import random
HIDEOUT_DIALOG = 1
QUESTION_DIALOG = 2
WRONGDOOR_DIALOG = 3

class Janitor:

    def __init__(self, stage):
        self.stage = stage
        self.layer = Layer()
        self.character_layer = Layer()
        self.folder_layer = None
        self.rollover_sound = assets.load_sound('GUI_roll_over.ogg')
        self.continue_sound = assets.load_sound('GUI_Click.ogg')
        self.janitor_sound = assets.load_sound('p0_janitor.ogg')
        self.wrong_door_open_sound = assets.load_sound('p0_wrong_door_open.ogg')
        self.wrong_door_man_sound = assets.load_sound('p0_wrong_door_no.ogg')
        self.wrong_door_female_sound = assets.load_sound('p0_wrong_door_no_female.ogg')
        return

    def show_janitor(self, city, option_texts, right_option):
        self.option_texts = option_texts
        self.right_choice = right_option
        self.city = city
        self.active_dialog = HIDEOUT_DIALOG
        self.ignore_layers = []
        self.stage.prepare_dialog(self.character_layer, False, True)
        self.stage.show_dialog(self.layer, self.handle_event)
        self.stage.add_layer(self.character_layer)
        self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, True, [self.character_layer] + self.ignore_layers, self.blind_show_janitor_callback)
        return

    def blind_show_janitor_callback(self, layer):
        self.load_option_results()
        self.set_up_hideout_dialogue(self.city)
        self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, False, [self.character_layer, self.folder_layer] + self.ignore_layers)
        return

    def set_up_hideout_dialogue(self, city):
        hideout_box_image = assets.load_image('p1_hideout_box.png')
        hideout_box = ItemImage(108, 86, hideout_box_image, None)
        self.layer.add(hideout_box)
        font_24 = assets.load_font('powdrft_.ttf', 24)
        city_text = ItemText(163, 93, font_24, 0, text.to_upper(city.name), (157, 21,
                                                                             21), None, 272, 30, 2, 2)
        self.layer.add(city_text)
        font_14 = assets.load_font('evilgeniusbb_reg.ttf', 14)
        message = 'Luego de indagar en la localidad,\nconcluyes que el ladrón se hospeda en un\ncondominio de la zona. Una vez allí\n.'
        info_text = ItemText(119, 112, font_14, 18, message, (0, 0, 0), None, 360, 151, 2, 2)
        self.layer.add(info_text)
        font_14_bld = assets.load_font('evilgeniusbb_bld.ttf', 14)
        message_bld = 'interrogas al conserje.'
        info_text_bld = ItemText(150, 205, font_14_bld, 18, message_bld, (0, 0, 0), None, 300, 25, 2)
        self.layer.add(info_text_bld)
        next_image = assets.load_image('p0_button_next_active.png')
        next_rollover_image = assets.load_image('p0_button_next_rollover.png')
        next = ItemImage(278, 238, next_image)
        next.set_rollover_image(next_rollover_image, self.rollover_sound)
        next.add_event_handler(ItemEvent.CLICK, self.hideout_next_click)
        self.layer.add(next)
        return

    def set_up_question_dialog(self):
        self.active_dialog = QUESTION_DIALOG
        self.layer.empty()
        self.set_up_janitor()
        self.set_up_avatar()
        self.set_up_options()
        self.set_up_folder()
        self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, False, [self.character_layer, self.folder_layer] + self.ignore_layers, self.blind_show_question_callback)
        return

    def blind_show_question_callback(self, layer):
        self.stage.render()
        self.janitor_sound.play()
        return

    def set_up_wrongdoor_dialog(self, kid_number):
        self.active_dialog = WRONGDOOR_DIALOG
        self.layer.empty()
        self.set_up_wrongdoor(kid_number)
        self.kid_number = kid_number
        self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, False, [self.character_layer, self.folder_layer] + self.ignore_layers, self.blind_show_wrongdoor_callback)
        animations.wait(self.stage, 50, self.play_wrong_door)
        return

    def play_wrong_door(self):
        self.wrong_door_open_sound.play()
        return

    def blind_show_wrongdoor_callback(self, layer):
        self.stage.render()
        if self.kid_number == 1:
            self.wrong_door_man_sound.play()
        elif self.kid_number == 2:
            self.wrong_door_female_sound.play()
        animations.wait_locked(self.stage, 400, self.update_wrong_door_time_left)
        return

    def update_wrong_door_time_left(self):
        self.stage.set_time_left(1)
        return

    def set_up_janitor(self):
        janitor_image = assets.load_image('p1_janitor.png')
        janitor = ItemImage(453, 87, janitor_image, None)
        self.layer.add(janitor)
        janitor_box_image = assets.load_image('p1_janitor_box.png')
        janitor_box = ItemImage(119, 74, janitor_box_image, None)
        self.layer.add(janitor_box)
        case = self.stage.game.datastore.user_character_progress.case
        question = case.list_witness_statements[0].janitor_statement.type
        if question == 1:
            question_image = assets.load_image('p1_janitor_question_sport.gif')
        elif question == 2:
            question_image = assets.load_image('p1_janitor_question_pet.gif')
        question = ItemImage(152, 140, question_image)
        self.layer.add(question)
        return

    def load_option_results(self):
        kid_number = random.randint(1, 2)
        self.option_results = []
        for option_text in self.option_texts:
            if option_text == self.right_choice:
                self.option_results.append(0)
            else:
                self.option_results.append(kid_number)
                if kid_number == 1:
                    kid_number = 2
                else:
                    kid_number = 1

        return

    def set_up_options(self):
        font = assets.load_font('evilgeniusbb_bld.ttf', 11)
        option_hover_image = assets.load_image('p1_avatar_option_hover.png')
        x = 141
        y = 259
        for i in range(len(self.option_texts)):
            option_text = self.option_texts[i]
            if self.option_results[i] == -1:
                text = ItemText(x, y, font, 0, option_text, (153, 153, 153), None, option_hover_image.get_width(), option_hover_image.get_height(), 2, 2)
                self.layer.add(text)
            else:
                text = ItemText(x, y, font, 0, option_text, (79, 79, 79), None, option_hover_image.get_width(), option_hover_image.get_height(), 2, 2)
                text.set_rollover(option_hover_image, self.rollover_sound, 0, 1)
                text.set_rollover_color((132, 15, 15), None)
                text.add_event_handler(ItemEvent.CLICK, self.option_click)
                text.index = i
                self.layer.add(text)
            y += 24

        return

    def set_up_folder(self):
        if self.folder_layer == None:
            folder = self.stage.folder_icon
            folder_layer = folder.get_layer()
            folder_layer.remove(folder)
            self.folder_layer = folder_layer
            folder.select_witnesses = True
            self.character_layer.add(folder)
            folder_text_image = assets.load_image('p0_bottomgui_case_tag.png')
            folder_text_item = ItemImage(441, 376, folder_text_image)
            self.character_layer.add(folder_text_item)
        return

    def restore_folder(self):
        if self.folder_layer != None:
            folder = self.stage.folder_icon
            folder.select_witnesses = False
            self.layer.remove(folder)
            self.folder_layer.add(folder)
        return

    def set_up_avatar(self):
        avatar_box_image = assets.load_image('p1_avatar_box.png')
        left = 119
        top = 244
        avatar_box = ItemImage(left, top, avatar_box_image)
        self.layer.add(avatar_box)
        return

    def set_up_wrongdoor(self, kid_number):
        box_image = assets.load_image('p1_wrongdoor_box.png')
        box = ItemImage(81, 116, box_image)
        self.layer.add(box)
        if kid_number == 1:
            kid_image = assets.load_image('p1_wrongdoor_kid_001.png')
            kid = ItemImage(415, 104, kid_image)
        elif kid_number == 2:
            kid_image = assets.load_image('p1_wrongdoor_kid_002.png')
            kid = ItemImage(434, 84, kid_image)
        self.layer.add(kid)
        next_image = assets.load_image('p0_button_previous_active.png')
        next_rollover_image = assets.load_image('p0_button_previous_rollover.png')
        next = ItemImage(262, 249, next_image)
        next.set_rollover_image(next_rollover_image, self.rollover_sound)
        next.add_event_handler(ItemEvent.CLICK, self.wrongdoor_next_click)
        self.layer.add(next)
        return

    def hideout_next_click(self, item, args):
        self.stage.render()
        self.continue_sound.play()
        self.show_next()
        return

    def show_next(self):
        if self.active_dialog == HIDEOUT_DIALOG:
            self.set_up_question_dialog()
        elif self.active_dialog == WRONGDOOR_DIALOG:
            self.set_up_question_dialog()
        return

    def wrongdoor_next_click(self, item, args):
        self.stage.render()
        self.continue_sound.play()
        self.show_next()
        return

    def option_click(self, item, args):
        self.stage.render()
        self.continue_sound.play()
        result = self.option_results[item.index]
        if result == 0:
            self.go_to_Phase2()
        else:
            self.set_up_wrongdoor_dialog(result)
            self.option_results[item.index] = -1
        return

    def go_to_Phase2(self):
        self.restore_folder()
        self.stage.game.datastore.user_character_progress.case.time_spend += 1
        self.stage.set_phase(2)
        return

    def handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.continue_sound.play()
            if self.active_dialog == QUESTION_DIALOG:
                self.stage.show_mainmenu()
            else:
                self.show_next()
            return True
        return


