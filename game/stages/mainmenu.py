from framework.animations import BlindDirection
import pygame
from framework import assets, text, animations
from framework.stage import *
from game.data import serialization
from game.stages import help, merits, phase0, case
import string
from . import characterid
from framework import web
from framework.external import open_browser
STATE_ROLLOVER_TIMER_KEY = 'show_create_char_state_rollover'

class MainMenu:

    def __init__(self, stage):
        self.stage = stage
        self.main_layer = Layer()
        self.create_layer = None
        self.click_sound = stage.click_sound
        self.rollover_sound = stage.rollover_sound
        self.character_id = characterid.CharacterId(self.rollover_sound)
        self.accents_translate_table = str.maketrans('áéíóúÁÉÍÓÚ', 'aeiouAEIOU')
        return

    def show_mainmenu(self, overlay, close_callback=None, apply_blind=True):
        self.overlay = overlay
        self.close_callback = close_callback
        self.update_added = False
        self.deleted_characters = []
        self.set_up_mainmenu()
        self.stage.show_dialog(self.main_layer, self.handle_event, None)
        if self.current_character == None:
            self.show_create(None, False, None, True)
        if apply_blind:
            self.stage.blind_dialog(self.main_layer, animations.BlindDirection.SHOW_DOWN, False, [], self.show_mainmenu_callback)
        else:
            self.show_mainmenu_callback()
        return

    def show_mainmenu_callback(self, layer=None):
        if self.create_layer != None:
            self.set_create_name_focus()
        if self.stage.game.update_manager.exists_update():
            self.notify_update_available(self.stage.game.update_manager.description)
        return

    def close_mainmenu(self):
        self.stage.blind_dialog(self.main_layer, BlindDirection.HIDE_UP, True, [], self.close_mainmenu_callback)
        return

    def close_mainmenu_callback(self, layer):
        self.stage.close_dialog(self.main_layer)
        if self.close_callback != None:
            self.close_callback()
        return

    def set_up_mainmenu(self):
        background_image = assets.load_image('p0_mainmenu_mainback.jpg')
        background_item = ItemImage(0, 0, background_image)
        self.main_layer.add(background_item)
        self.current_character = self.get_active_character()
        self.character_id.set_up_id(self.main_layer, self.current_character, 120, 126, click_callback=self.charid_click)
        if not self.overlay:
            welcome_image = assets.load_image('p0_mainmenu_title_welcome.png')
            welcome_item = ItemImage(192, 113, welcome_image)
            self.main_layer.add(welcome_item)
        play_normal_image = assets.load_image('p0_mainmenu_btn_play_normal.png')
        play_rollover_image = assets.load_image('p0_mainmenu_btn_play_rollover.png')
        self.play_button = ItemImage(237, 299, play_normal_image)
        self.play_button.set_rollover_image(play_rollover_image, self.rollover_sound)
        self.play_button.add_event_handler(ItemEvent.CLICK, self.play_click)
        self.main_layer.add(self.play_button)
        if self.overlay:
            backtogame_normal_image = assets.load_image('p0_mainmenu_btn_backtogame_normal.png')
            backtogame_rollover_image = assets.load_image('p0_mainmenu_btn_backtogame_rollover.png')
            self.backtogame_button = ItemImage(183, 302, backtogame_normal_image)
            self.backtogame_button.set_rollover_image(backtogame_rollover_image, self.rollover_sound)
            self.backtogame_button.add_event_handler(ItemEvent.CLICK, self.play_click)
            self.main_layer.add(self.backtogame_button)
            self.play_button.set_visible(False)
        highscores_normal_image = assets.load_image('p0_mainmenu_btn_highscores_normal.png')
        highscores_rollover_image = assets.load_image('p0_mainmenu_btn_highscores_rollover.png')
        highscores_item = ItemImage(11, 295, highscores_normal_image)
        highscores_item.set_rollover_image(highscores_rollover_image, self.rollover_sound)
        highscores_item.add_event_handler(ItemEvent.CLICK, self.highscores_click)
        self.main_layer.add(highscores_item)
        swapdetective_normal_image = assets.load_image('p0_mainmenu_btn_swapdetective_normal.png')
        swapdetective_rollover_image = assets.load_image('p0_mainmenu_btn_swapdetective_rollover.png')
        swapdetective_item = ItemImage(465, 298, swapdetective_normal_image)
        swapdetective_item.set_rollover_image(swapdetective_rollover_image, self.rollover_sound)
        swapdetective_item.add_event_handler(ItemEvent.CLICK, self.swapdetective_click)
        self.main_layer.add(swapdetective_item)
        help_normal_image = assets.load_image('p0_mainmenu_btn_help_normal.png')
        help_rollover_image = assets.load_image('p0_mainmenu_btn_help_rollover.png')
        help_item = ItemImage(135, 386, help_normal_image)
        help_item.set_rollover_image(help_rollover_image, self.rollover_sound)
        help_item.add_event_handler(ItemEvent.CLICK, self.help_click)
        self.main_layer.add(help_item)
        credits_normal_image = assets.load_image('p0_mainmenu_btn_credits_normal.png')
        credits_rollover_image = assets.load_image('p0_mainmenu_btn_credits_rollover.png')
        credits_item = ItemImage(254, 385, credits_normal_image)
        credits_item.set_rollover_image(credits_rollover_image, self.rollover_sound)
        credits_item.add_event_handler(ItemEvent.CLICK, self.credits_click)
        self.main_layer.add(credits_item)
        exit_normal_image = assets.load_image('p0_mainmenu_btn_exit_normal.png')
        exit_rollover_image = assets.load_image('p0_mainmenu_btn_exit_rollover.png')
        exit_item = ItemImage(375, 386, exit_normal_image)
        exit_item.set_rollover_image(exit_rollover_image, self.rollover_sound)
        exit_item.add_event_handler(ItemEvent.CLICK, self.exit_click)
        self.main_layer.add(exit_item)
        return

    def notify_update_available(self, description):
        if not self.update_added:
            update_normal_image = assets.load_image('p0_mainmenu_updater_btn_normal.png')
            update_rollover_image = assets.load_image('p0_mainmenu_updater_btn_rollover.png')
            self.updategame_item = ItemImage(475, 15, update_normal_image)
            self.updategame_item.set_rollover_image(update_rollover_image, self.rollover_sound)
            self.updategame_item.add_event_handler(ItemEvent.CLICK, self.update_game_click)
            self.update_description = description
            self.update_added = True
            dismissed = False
            if hasattr(self.stage.game, 'updategame_dismissed'):
                dismissed = self.stage.game.updategame_dismissed
            if not self.overlay and not dismissed:
                self.show_updategame()
            else:
                self.main_layer.add(self.updategame_item)
        return

    def set_up_swapdetective(self):
        self.swapdetective_layer = Layer()
        background_image = assets.load_image('p0_mainmenu_swap_backdrop.png')
        background_item = ItemImage(116, 26, background_image)
        self.swapdetective_layer.add(background_item)
        self.swapdetective_font_14 = assets.load_font('evilgeniusbb_reg.ttf', 14)
        font_13 = assets.load_font('evilgeniusbb_bld.ttf', 13)
        selector_rollover_image = assets.load_image('p0_mainmenu_swap_selector_rollover.png')
        self.swapdetective_rollover_back_item = ItemImage(0, 0, selector_rollover_image)
        self.swapdetective_rollover_back_item.set_visible(False)
        self.swapdetective_layer.add(self.swapdetective_rollover_back_item)
        selector_selected_image = assets.load_image('p0_mainmenu_swap_selector_selected.png')
        self.swapdetective_selected_back_item = ItemImage(0, 0, selector_selected_image)
        self.swapdetective_selected_back_item.set_visible(False)
        self.swapdetective_layer.add(self.swapdetective_selected_back_item)
        self.swapdetective_selected_text_item = ItemText(0, 0, font_13, 0, '', (117,
                                                                                51,
                                                                                12), None, 250, 20, 2, 1)
        self.swapdetective_selected_text_item.set_visible(False)
        self.swapdetective_layer.add(self.swapdetective_selected_text_item)
        create_normal_image = assets.load_image('p0_mainmenu_btn_create_normal.png')
        create_rollover_image = assets.load_image('p0_mainmenu_btn_create_rollover.png')
        create_disabled_image = assets.load_image('p0_mainmenu_btn_create_inactive.png')
        self.create_button = ItemImage(137, 355, create_normal_image)
        self.create_button.set_rollover_image(create_rollover_image, self.rollover_sound)
        self.create_button.add_event_handler(ItemEvent.CLICK, self.swapdetective_create_click)
        self.swapdetective_layer.add(self.create_button)
        self.create_button_disabled = ItemImage(137, 355, create_disabled_image)
        self.create_button_disabled.set_visible(False)
        self.swapdetective_layer.add(self.create_button_disabled)
        select_normal_image = assets.load_image('p0_mainmenu_btn_select_normal.png')
        select_rollover_image = assets.load_image('p0_mainmenu_btn_select_rollover.png')
        select_disabled_image = assets.load_image('p0_mainmenu_btn_select_inactive.png')
        self.select_button = ItemImage(252, 355, select_normal_image)
        self.select_button.set_rollover_image(select_rollover_image, self.rollover_sound)
        self.select_button.add_event_handler(ItemEvent.CLICK, self.swapdetective_select_click)
        self.swapdetective_layer.add(self.select_button)
        self.select_button_disabled = ItemImage(252, 355, select_disabled_image)
        self.select_button_disabled.set_visible(False)
        self.swapdetective_layer.add(self.select_button_disabled)
        delete_normal_image = assets.load_image('p0_mainmenu_btn_delete_normal.png')
        delete_rollover_image = assets.load_image('p0_mainmenu_btn_delete_rollover.png')
        delete_disabled_image = assets.load_image('p0_mainmenu_btn_delete_inactive.png')
        self.delete_button = ItemImage(374, 355, delete_normal_image)
        self.delete_button.set_rollover_image(delete_rollover_image, self.rollover_sound)
        self.delete_button.add_event_handler(ItemEvent.CLICK, self.swapdetective_delete_click)
        self.swapdetective_layer.add(self.delete_button)
        self.delete_button_disabled = ItemImage(374, 355, delete_disabled_image)
        self.delete_button_disabled.set_visible(False)
        self.swapdetective_layer.add(self.delete_button_disabled)
        back_normal_image = assets.load_image('p0_mainmenu_btn_back_normal.png')
        back_rollover_image = assets.load_image('p0_mainmenu_btn_back_rollover.png')
        back_item = ItemImage(263, 401, back_normal_image)
        back_item.set_rollover_image(back_rollover_image, self.rollover_sound)
        back_item.add_event_handler(ItemEvent.CLICK, self.swapdetective_back_click)
        self.swapdetective_layer.add(back_item)
        self.swapdetective_selected = None
        self.swapdetective_over_item = None
        self.swapdetective_character_items = []
        self.load_characters()
        return

    def load_characters(self):
        for item in self.swapdetective_character_items:
            self.swapdetective_layer.remove(item)

        self.swapdetective_character_items = []
        characters = self.stage.game.datastore.characters[:]
        characters.sort(key=self.get_character_name)
        y = 113
        default_selection = None
        k = 0
        for c in characters:
            text_item = ItemText(175, y, self.swapdetective_font_14, 0, c.name, (73,
                                                                                 72,
                                                                                 54), None, 250, 20, 2, 1)
            self.swapdetective_layer.add(text_item)
            self.swapdetective_character_items.append(text_item)
            text_mask = ItemMask(175, y - 4, (250, 25))
            text_mask.charinfo = c
            text_mask.text_item = text_item
            text_mask.add_event_handler(ItemEvent.MOUSE_ENTER, self.swapdetective_item_enter)
            text_mask.add_event_handler(ItemEvent.MOUSE_LEAVE, self.swapdetective_item_leave)
            text_mask.add_event_handler(ItemEvent.CLICK, self.swapdetective_item_click)
            self.swapdetective_layer.add(text_mask)
            self.swapdetective_character_items.append(text_mask)
            if self.current_character != None and c.id == self.current_character.id:
                default_selection = text_mask
            y += 28
            k += 1

        self.set_swapdetective_selected(default_selection)
        self.update_swapdetective_buttons()
        return

    def update_swapdetective_buttons(self):
        characters = self.stage.game.datastore.characters[:]
        k = len(characters)
        if k >= 8:
            self.create_button.set_visible(False)
            self.create_button_disabled.set_visible(True)
        else:
            self.create_button.set_visible(True)
            self.create_button_disabled.set_visible(False)
        if k == 0 or self.swapdetective_selected == None:
            self.select_button.set_visible(False)
            self.select_button_disabled.set_visible(True)
            self.delete_button.set_visible(False)
            self.delete_button_disabled.set_visible(True)
        else:
            self.select_button.set_visible(True)
            self.select_button_disabled.set_visible(False)
            self.delete_button.set_visible(True)
            self.delete_button_disabled.set_visible(False)
        return

    def set_up_create(self):
        self.create_layer = Layer()
        background_image = assets.load_image('p0_mainmenu_swap_new_backdrop.png')
        background_item = ItemImage(116, 26, background_image)
        self.create_layer.add(background_item)
        font_14 = assets.load_font('evilgeniusbb_reg.ttf', 14)
        self.create_flip_sound = assets.load_sound('GUI_Flip.ogg')
        self.create_name_item = ItemText(232, 105, font_14, 0, '', (0, 0, 0), None, 200, 18, 2, 1)
        self.create_name_item.set_watermark_text('INGRESE AQUÍ SU NOMBRE')
        self.create_name_item.set_editable(True, self.create_name_keypressed)
        self.create_name_item.set_max_chars(30)
        self.create_layer.add(self.create_name_item)
        character_name_mask = ItemMask(224, 103, (216, 19))
        self.create_layer.add(character_name_mask)
        self.create_name_item.set_edit_on_click(character_name_mask)
        character_state_mask = ItemMask(263, 128, (178, 19))
        state_rollover_image = assets.load_image('p0_mainmenu_btn_state_rollover.png')
        character_state_mask.set_rollover(state_rollover_image, self.rollover_sound, 0, -1)
        character_state_mask.add_event_handler(ItemEvent.CLICK, self.create_state_click)
        self.create_layer.add(character_state_mask)
        self.character_state_item = ItemText(265, 130, font_14, 0, '', (0, 0, 0), None, 170, 18, 2, 1)
        self.create_layer.add(self.character_state_item)
        male_mask = ItemMask(311, 162, (17, 15))
        male_mask.add_event_handler(ItemEvent.CLICK, self.create_male_click)
        self.create_layer.add(male_mask)
        female_mask = ItemMask(397, 162, (17, 15))
        female_mask.add_event_handler(ItemEvent.CLICK, self.create_female_click)
        self.create_layer.add(female_mask)
        sex_check_image = assets.load_image('p0_mainmenu_swap_new_check.png')
        self.create_sex_check_item = ItemImage(313, 156, sex_check_image)
        self.create_layer.add(self.create_sex_check_item)
        self.create_avatar_item = ItemImage(242, 208, None)
        self.create_layer.add(self.create_avatar_item)
        box_image = assets.load_image('p0_merits_main_id_box.png')
        box_item = ItemImage(237, 203, box_image)
        self.create_layer.add(box_item)
        self.right_arrow_normal_image = assets.load_image('p0_mainmenu_swap_new_arrow_normal.png')
        self.right_arrow_rollover_image = assets.load_image('p0_mainmenu_swap_new_arrow_rollover.png')
        self.right_arrow_clicked_image = assets.load_image('p0_mainmenu_swap_new_arrow_clicked.png')
        self.create_right_arrow_item = ItemImage(360, 255, self.right_arrow_normal_image)
        self.create_right_arrow_state = 0
        self.create_right_arrow_item.add_event_handler(ItemEvent.MOUSE_ENTER, self.create_next_avatar_enter)
        self.create_right_arrow_item.add_event_handler(ItemEvent.MOUSE_LEAVE, self.create_next_avatar_leave)
        self.create_right_arrow_item.add_event_handler(ItemEvent.CLICK, self.create_next_avatar_click)
        self.create_layer.add(self.create_right_arrow_item)
        self.left_arrow_normal_image = self.right_arrow_normal_image.flip_h_copy()
        self.left_arrow_rollover_image = self.right_arrow_rollover_image.flip_h_copy()
        self.left_arrow_clicked_image = self.right_arrow_clicked_image.flip_h_copy()
        self.create_left_arrow_item = ItemImage(207, 255, self.left_arrow_normal_image)
        self.create_left_arrow_state = 0
        self.create_left_arrow_item.add_event_handler(ItemEvent.MOUSE_ENTER, self.create_previous_avatar_enter)
        self.create_left_arrow_item.add_event_handler(ItemEvent.MOUSE_LEAVE, self.create_previous_avatar_leave)
        self.create_left_arrow_item.add_event_handler(ItemEvent.CLICK, self.create_previous_avatar_click)
        self.create_layer.add(self.create_left_arrow_item)
        accept_normal_image = assets.load_image('p0_mainmenu_btn_accept_normal.png')
        accept_rollover_image = assets.load_image('p0_mainmenu_btn_accept_rollover.png')
        accept_disabled_image = assets.load_image('p0_mainmenu_btn_accept_inactive.png')
        self.accept_button = ItemImage(202, 369, accept_normal_image)
        self.accept_button.set_rollover_image(accept_rollover_image, self.rollover_sound)
        self.accept_button.add_event_handler(ItemEvent.CLICK, self.create_accept_click)
        self.create_layer.add(self.accept_button)
        self.accept_button_disabled = ItemImage(202, 369, accept_disabled_image)
        self.accept_button_disabled.set_visible(False)
        self.create_layer.add(self.accept_button_disabled)
        cancel_normal_image = assets.load_image('p0_mainmenu_btn_cancel_normal.png')
        cancel_rollover_image = assets.load_image('p0_mainmenu_btn_cancel_rollover.png')
        cancel_item = ItemImage(306, 369, cancel_normal_image)
        cancel_item.set_rollover_image(cancel_rollover_image, self.rollover_sound)
        cancel_item.add_event_handler(ItemEvent.CLICK, self.create_cancel_click)
        self.create_layer.add(cancel_item)
        self.create_sex_male = True
        self.create_character_location = ''
        self.create_avatar_count = 4
        self.create_avatar = 1
        self.update_create_sex_mark()
        self.update_create_avatar_image()
        self.update_create_accept()
        return

    def set_up_state_list(self):
        self.state_list_layer = Layer()
        background_image = assets.load_image('p0_mainmenu_swap_new_stateselector_backdrop.png')
        background_item = ItemImage(166, 17, background_image)
        self.state_list_layer.add(background_item)
        departments = self.stage.game.datastore.list_departments[:]
        departments.sort(key=self.get_department_name)
        state_rollover_image = assets.load_image('p0_mainmenu_swap_new_stateselector_rollover.png')
        self.create_state_rollover_item = ItemImage(179, 0, state_rollover_image)
        self.create_state_rollover_item.set_visible(False)
        self.state_list_layer.add(self.create_state_rollover_item)
        y = 59
        dep_y = [58, 76, 94, 112, 130, 148, 166, 184, 202, 220, 238, 256, 273, 292, 310, 328, 346, 364, 382]
        for i in range(len(departments)):
            dep = departments[i]
            mask = ItemMask(179, dep_y[i], state_rollover_image.get_size())
            mask.add_event_handler(ItemEvent.MOUSE_ENTER, self.create_department_enter)
            mask.add_event_handler(ItemEvent.MOUSE_LEAVE, self.create_department_leave)
            mask.add_event_handler(ItemEvent.CLICK, self.create_department_click)
            mask.department = dep
            self.state_list_layer.add(mask)
            y += 17

        return

    def update_create_sex_mark(self):
        if self.create_sex_male:
            self.create_sex_check_item.set_left(313)
        else:
            self.create_sex_check_item.set_left(399)
        return

    def update_create_avatar_image(self):
        if self.create_sex_male:
            image = assets.load_image('p0_detective_male_' + '%03d' % self.create_avatar + '_id.jpg')
        else:
            image = assets.load_image('p0_detective_female_' + '%03d' % self.create_avatar + '_id.jpg')
        self.create_avatar_item.set_image(image)
        self.create_left_arrow_item.set_visible(self.create_avatar > 1)
        self.create_right_arrow_item.set_visible(self.create_avatar < self.create_avatar_count)
        return

    def set_up_delete(self, charinfo):
        self.delete_layer = Layer()
        background_image = assets.load_image('p0_mainmenu_swap_del_backdrop.png')
        background_item = ItemImage(150, 24, background_image)
        self.delete_layer.add(background_item)
        font_14 = assets.load_font('evilgeniusbb_reg.ttf', 14)
        message = '¿ESTÁ SEGURO QUE DESEA ELIMINAR ESTE DETECTIVE? TODO EL PROGRESO GUARDADO SE PERDERÁ'
        question_item = ItemText(168, 91, font_14, 13, message, (153, 0, 0), None, 268, 52, 2, 1)
        self.delete_layer.add(question_item)
        charid = characterid.CharacterId()
        charid.set_up_id(self.delete_layer, charinfo, 123, 147)
        yes_normal_image = assets.load_image('p0_mainmenu_btn_yes_normal.png')
        yes_rollover_image = assets.load_image('p0_mainmenu_btn_yes_rollover.png')
        yes_item = ItemImage(222, 372, yes_normal_image)
        yes_item.set_rollover_image(yes_rollover_image, self.rollover_sound)
        yes_item.add_event_handler(ItemEvent.CLICK, self.delete_yes_click)
        self.delete_layer.add(yes_item)
        no_normal_image = assets.load_image('p0_mainmenu_btn_no_normal.png')
        no_rollover_image = assets.load_image('p0_mainmenu_btn_no_rollover.png')
        no_item = ItemImage(304, 372, no_normal_image)
        no_item.set_rollover_image(no_rollover_image, self.rollover_sound)
        no_item.add_event_handler(ItemEvent.CLICK, self.delete_no_click)
        self.delete_layer.add(no_item)
        return

    def charid_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.load_character_progress()
        merits_dialog = merits.Merits(self.stage)
        merits_dialog.show_merits(False)
        return

    def load_character_progress(self):
        datastore = self.stage.game.datastore
        if datastore.user_character == None or datastore.user_character.charinfo.id != self.current_character.id:
            datastore.load_character(self.current_character)
        return

    def get_character_name(self, char_info):
        return self.remove_accents_and_upper(char_info.name)

    def get_department_name(self, dep):
        return self.remove_accents_and_upper(dep.name)

    def remove_accents_and_upper(self, text):
        return text.translate(self.accents_translate_table).upper()

    def swapdetective_item_enter(self, item, args):
        self.set_swapdetective_rollover_over(item)
        return

    def swapdetective_item_leave(self, item, args):
        self.set_swapdetective_rollover_over(None)
        return

    def swapdetective_item_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.set_swapdetective_selected(item)
        return

    def set_swapdetective_rollover_over(self, item):
        if self.swapdetective_over_item != item:
            if item == None:
                self.swapdetective_rollover_back_item.set_visible(False)
            else:
                self.swapdetective_rollover_back_item.set_left(item.get_left())
                self.swapdetective_rollover_back_item.set_top(item.get_top())
                self.swapdetective_rollover_back_item.set_visible(True)
            self.swapdetective_over_item = item
        return

    def set_swapdetective_selected(self, item):
        if self.swapdetective_selected != item:
            if item == None:
                self.swapdetective_selected_back_item.set_visible(False)
                self.swapdetective_selected_text_item.set_visible(False)
            else:
                self.swapdetective_selected_back_item.set_left(item.get_left() - 16)
                self.swapdetective_selected_back_item.set_top(item.get_top() - 5)
                self.swapdetective_selected_back_item.set_visible(True)
                self.swapdetective_selected_text_item.set_left(item.get_left())
                self.swapdetective_selected_text_item.set_top(item.get_top() + 3)
                self.swapdetective_selected_text_item.set_text(item.charinfo.name)
                self.swapdetective_selected_text_item.set_visible(True)
                item.text_item.set_visible(False)
            if self.swapdetective_selected != None:
                self.swapdetective_selected.text_item.set_visible(True)
            self.swapdetective_selected = item
        self.update_swapdetective_buttons()
        return

    def set_up_credits(self):
        self.credits_layer = Layer()
        background_image = assets.load_image('p0_credits_background.jpg')
        background_item = ItemImage(0, 0, background_image)
        self.credits_layer.add(background_item)
        close_normal_image = assets.load_image('p0_tutorial_remake_btn_close_normal.png')
        close_rollover_image = assets.load_image('p0_tutorial_remake_btn_close_rollover.png')
        close_item = ItemImage(267, 393, close_normal_image)
        close_item.set_rollover_image(close_rollover_image, self.rollover_sound)
        close_item.add_event_handler(ItemEvent.CLICK, self.credits_close_click)
        self.credits_layer.add(close_item)
        prev_normal_image = assets.load_image('p0_tutorial_remake_btn_prev_normal.png')
        prev_rollover_image = assets.load_image('p0_tutorial_remake_btn_prev_rollover.png')
        self.credits_prev_item = ItemImage(235, 398, prev_normal_image)
        self.credits_prev_item.set_rollover_image(prev_rollover_image, self.rollover_sound)
        self.credits_prev_item.add_event_handler(ItemEvent.CLICK, self.credits_prev_click)
        self.credits_layer.add(self.credits_prev_item)
        next_normal_image = assets.load_image('p0_tutorial_remake_btn_next_normal.png')
        next_rollover_image = assets.load_image('p0_tutorial_remake_btn_next_rollover.png')
        self.credits_next_item = ItemImage(354, 399, next_normal_image)
        self.credits_next_item.set_rollover_image(next_rollover_image, self.rollover_sound)
        self.credits_next_item.add_event_handler(ItemEvent.CLICK, self.credits_next_click)
        self.credits_layer.add(self.credits_next_item)
        self.credits_font_30 = assets.load_font('turkey.ttf', 30)
        self.credits_font_24 = assets.load_font('turkey.ttf', 24)
        self.credits_font_20 = assets.load_font('turkey.ttf', 20)
        self.credits_font_18 = assets.load_font('turkey.ttf', 18)
        self.credits_font_16 = assets.load_font('turkey.ttf', 16)
        self.credits_font_12 = assets.load_font('turkey.ttf', 12)
        self.credits_people_layer = Layer()
        self.credits_people_layer_old = None
        self.credits_page = 1
        self.credits_pagecount = 7
        return

    def load_current_credits(self, apply_effect=True):
        header = None
        footer = None
        line_separation = 30
        small_line_font = None
        small_line_height = 0
        if self.credits_page == 1:
            top_margin = 10
            title_font = self.credits_font_30
            text_font = self.credits_font_24
            small_line_font = self.credits_font_16
            small_line_height = 24
            text = [
             '&#c223,0,0!&#f:t!DISEÑO DE JUEGO:&#c!&#f!\n' + 'MARTÍN DA SILVEIRA\n' + '&#f:s! \n&#f!' + '&#c223,0,0!&#f:t!ARTE:&#c!&#f!\n' + 'FERNANDO PICÚN\n' + '&#f:s! \n&#f!' + '&#c223,0,0!&#f:t!MÚSICA Y SONIDO:&#c!&#f!\n' + 'MARTÍN DA SILVEIRA\n',
             '&#c223,0,0!&#f:t!PROGRAMACIÓN:&#c!&#f!\n' + 'NICOLÁS CASTAGNET\n' + 'JUAN PABLO AYALA\n' + 'FELIPE OTAMENDI\n\n' + '&#c223,0,0!&#f:t!PRODUCCIÓN:&#c!&#f!\n' + 'MARIANO DE LARROBLA\n' + 'CARMEN FERNANDEZ\n']
        elif self.credits_page == 2:
            top_margin = 70
            title_font = self.credits_font_24
            text_font = self.credits_font_20
            small_line_font = self.credits_font_16
            small_line_height = 7
            text = [
             '&#c223,0,0!&#f:t!ASESORAMIENTO PEDAGÓGICO:&#c!&#f!\n' + '&#f:s! \n&#f!' + 'ANDRÉS COPES\n' + 'WANDA SPINELLI\n',
             '&#c223,0,0!&#f:t!CORRECCIÓN DE TEXTOS:&#c!&#f!\n' + '&#f:s! \n&#f!' + 'LETICIA CHIFFLET\n',
             '&#c223,0,0!&#f:t!EQUIPO DE TESTING:&#c!&#f!\n' + '&#f:s! \n&#f!' + 'EUGENIA DE LARROBLA\n' + 'GABRIELA CONZE\n']
        elif self.credits_page == 3:
            top_margin = 38
            title_font = self.credits_font_24
            text_font = self.credits_font_16
            line_separation = 23
            header_separation = 44
            header = '&#c223,0,0!&#f:t!BETA TESTERS:&#c!&#f!\n'
            text = [
             'ADRIÁN KIRCHNITZ\n' + 'AGUSTÍN RAMASCO\n' + 'AGUSTINA ALVAREZ\n' + 'AGUSTINA CHALKLING\n' + 'ALEJANDRO GONZÁLEZ\n' + 'ALEJO PIREZ\n' + 'ALEXANDER ACEVEDO\n' + 'ALVARO GARCÍA BARBIERI\n' + 'ANDREA FERRERO PEREIRA\n' + 'ANGEL MATÍAS FERRARI SUÁREZ\n' + 'ANTONELLA ECHEVESTE PALOMEQUE\n',
             'BIANCA MARCHESONI\n' + 'BIANCA LEGUIZAMÓN\n' + 'BRAHIAN RAMIRO GHISOLFO RAMOS\n' + 'BRUNO LEEMAN\n' + 'CRISTIAN ALMADA\n' + 'DANIEL FIGUEREDO\n' + 'DIEGO FERNANDO NELCIS PIRIZ\n' + 'DIEGO HERNÁNDEZ\n' + 'DIEGO PIEGAS\n' + 'EMILIANO PICÚN\n' + 'ENZO FAGUNDEZ\n']
        elif self.credits_page == 4:
            top_margin = 38
            title_font = self.credits_font_24
            text_font = self.credits_font_16
            line_separation = 23
            header_separation = 44
            header = '&#c223,0,0!&#f:t!BETA TESTERS:&#c!&#f!\n'
            text = [
             'ERIC MORDEZKI\n' + 'ESTEFANI CAÑETE\n' + 'EZEQUIEL CABRERA\n' + 'FABRIZZIO OVIEDO\n' + 'FEDERICO MÉNDEZ\n' + 'FELIPE DA SILVEIRA\n' + 'FIORELLA TORRES\n' + 'GABRIEL CURTI\n' + 'GABRIELA DENISE GÓMEZ MEDINA\n' + 'GONZALO DE SOSA\n' + 'GUIDAÍ BLENGINI\n',
             'GUILLERMO GARCÍA BARBIERI\n' + 'GUILLERMO MORDEZKI\n' + 'JAVIER SINTES\n' + 'JOAQUÍN DÍAZ\n' + 'JOSÉ IGNACIO GALATTI\n' + 'JUAN I. CROSA\n' + 'JUAN IGNACIO MEDINA CRUZ\n' + 'JUAN IGNACIO VALLE\n' + 'JUAN MANUEL VALLE\n' + 'JUAN SEBASTIÁN MARTÍNEZ APLANALP\n' + 'JULIA DE LEÓN\n']
        elif self.credits_page == 5:
            top_margin = 38
            title_font = self.credits_font_24
            text_font = self.credits_font_16
            line_separation = 23
            header_separation = 44
            header = '&#c223,0,0!&#f:t!BETA TESTERS:&#c!&#f!\n'
            text = [
             'JULIA PISSANO\n' + 'LARA CONSANI\n' + 'LAURA BELÉN VEGA AYALA\n' + 'LINET JOANA ALTAMIRANDA DA SILVA\n' + 'LUANA PIREZ\n' + 'LUCAS GENOLET\n' + 'LUCAS MATTOS\n' + 'LUCÍA CABRERA\n' + 'MAIKEL PEREYRA\n' + 'MARÍA EUGENIA DE SOUZA\n' + 'MATÍAS IBARRA\n',
             'MAURICIO SILVA\n' + 'MAURO CAUTERUCCIO\n' + 'MICAELA ALMADA ZÁRATE\n' + 'MILENA ZÁRATE MELGAREJO\n' + 'MILTON AYALA SANTOS\n' + 'NAHUEL ROMERO\n' + 'ORIANA MONTAÑA\n' + 'PABLO SOSA\n' + 'PAULA GARCÍA\n' + 'PILAR MÉNDEZ\n' + 'RENZO CAUTERUCCIO\n']
        elif self.credits_page == 6:
            top_margin = 38
            title_font = self.credits_font_24
            text_font = self.credits_font_16
            line_separation = 23
            header_separation = 44
            footer_y = 301
            header = '&#c223,0,0!&#f:t!BETA TESTERS:&#c!&#f!\n'
            footer = '&#c223,0,0!&#f:t!¡MUCHAS GRACIAS A TODOS!&#c!&#f!\n'
            text = [
             'ROCÍO CAMILA CURTI MAWAD\n' + 'SANTIAGO NICOLÁS PRÓSPER VEINZ\n' + 'SANTIAGO QUIJANO\n' + 'SERGIO DANIEL GARCÍA SIERRA\n' + 'SOFÍA GASPERI\n',
             'SOFÍA PIEDRA CUEVA\n' + 'TATIANA PIREZ\n' + 'TOLENTINO GÓMEZ\n' + 'VALENTINA GONZÁLEZ\n' + 'WINSTON SANTOS\n']
        elif self.credits_page == 7:
            top_margin = 36
            title_font = self.credits_font_24
            text_font = self.credits_font_18
            line_separation = 24
            header_separation = 42
            header = '&#c223,0,0!&#f:t!AGRADECIMIENTOS:&#c!&#f!\n'
            text = [
             'DCA\nINGENIO\n' + 'PROYECTO RAYUELA\n' + 'FUNDACIÓN "LOS PINOS"\n' + 'ANAINÉS ZIGNAGO\n' + 'JOHN MARTZ\n' + 'MARTÍN PÉREZ\n' + 'RAFAEL GARCÍA\n' + 'SHIRLEY SIRI\n' + 'CARLOS DA SILVEIRA\n' + "DIEGO LÓPEZ D'ALESSANDRO\n",
             'JUAN PABLO PISÓN\n' + 'LILIANA BARDALLO\n' + 'MARIANA GIL SALABERRY\n' + 'MARTÍN CHAPARRO\n' + 'MARTÍN LOSKÍN\n' + 'ZZ\n' + 'CHAIM GINGOLD\n' + 'ELI BARNETT\n' + 'FERNANDO SANSBERRO\n' + 'ROBIN HUNICKE']
        if self.credits_people_layer_old != None:
            self.stage.remove_layer(self.credits_people_layer_old)
        self.credits_people_layer_old = self.credits_people_layer
        self.credits_people_layer = Layer()
        x = 7
        y = 81 + top_margin
        column_width = _div(585 , len(text))
        height = 295
        additional_fonts = {'t': (title_font, 0)}
        if small_line_font != None:
            additional_fonts['s'] = (
             small_line_font, small_line_height)
        if header != None:
            header_x = 7
            header_y = 81 + top_margin - header_separation
            header_width = 585
            header_height = 30
            shadow_text = header.replace('&#c223,', '&#c0,')
            shadow = ItemText(header_x + 2, header_y + 3, text_font, 30, shadow_text, (0,
                                                                                       0,
                                                                                       0), None, header_width, header_height, 2, 1, additional_fonts)
            self.credits_people_layer.add(shadow)
            item = ItemText(header_x, header_y, text_font, 30, header, (255, 255, 255), None, header_width, header_height, 2, 1, additional_fonts)
            self.credits_people_layer.add(item)
        if footer != None:
            footer_x = 7
            footer_width = 585
            footer_height = 30
            shadow_text = footer.replace('&#c223,', '&#c0,')
            shadow = ItemText(footer_x + 2, footer_y + 3, text_font, 30, shadow_text, (0,
                                                                                       0,
                                                                                       0), None, footer_width, footer_height, 2, 1, additional_fonts)
            self.credits_people_layer.add(shadow)
            item = ItemText(footer_x, footer_y, text_font, 30, footer, (255, 255, 255), None, footer_width, footer_height, 2, 1, additional_fonts)
            self.credits_people_layer.add(item)
        for column in text:
            shadow_text = column.replace('&#c223,', '&#c0,')
            shadow = ItemText(x + 2, y + 3, text_font, line_separation, shadow_text, (0,
                                                                                      0,
                                                                                      0), None, column_width - 5, height, 2, 1, additional_fonts)
            self.credits_people_layer.add(shadow)
            item = ItemText(x, y, text_font, line_separation, column, (255, 255, 255), None, column_width - 5, height, 2, 1, additional_fonts)
            self.credits_people_layer.add(item)
            x += column_width

        self.stage.add_layer(self.credits_people_layer)
        if apply_effect:
            area = pygame.Rect(0, 40, 0, 362)
            animations.stop_blind_layer(self.credits_people_layer_old)
            animations.stop_blind_layer(self.credits_people_layer)
            self.credits_people_layer_old.set_clip(None)
            self.credits_people_layer.set_clip(None)
            animations.blind_layer(self.credits_people_layer_old, animations.BlindDirection.HIDE_DOWN, area, 400, None, False)
            animations.blind_layer(self.credits_people_layer, animations.BlindDirection.SHOW_DOWN, area, 400, None, False)
        else:
            self.stage.remove_layer(self.credits_people_layer_old)
        self.credits_prev_item.set_visible(self.credits_page > 1)
        self.credits_next_item.set_visible(self.credits_page < self.credits_pagecount)
        return

    def set_up_exit(self):
        self.exit_layer = Layer()
        background_image = assets.load_image('p0_mainmenu_exit_backdrop.png')
        background_item = ItemImage(132, 77, background_image)
        self.exit_layer.add(background_item)
        yes_normal_image = assets.load_image('p0_mainmenu_btn_yes_normal.png')
        yes_rollover_image = assets.load_image('p0_mainmenu_btn_yes_rollover.png')
        yes_item = ItemImage(221, 228, yes_normal_image)
        yes_item.set_rollover_image(yes_rollover_image, self.rollover_sound)
        yes_item.add_event_handler(ItemEvent.CLICK, self.exit_yes_click)
        self.exit_layer.add(yes_item)
        no_normal_image = assets.load_image('p0_mainmenu_btn_no_normal.png')
        no_rollover_image = assets.load_image('p0_mainmenu_btn_no_rollover.png')
        no_item = ItemImage(303, 228, no_normal_image)
        no_item.set_rollover_image(no_rollover_image, self.rollover_sound)
        no_item.add_event_handler(ItemEvent.CLICK, self.exit_no_click)
        self.exit_layer.add(no_item)
        font_14 = assets.load_font('evilgeniusbb_reg.ttf', 14)
        font_13 = assets.load_font('evilgeniusbb_bld.ttf', 13)
        text1 = ItemText(167, 150, font_14, 13, '¿ESTÁ SEGURO QUE DESEA\nSALIR DEL JUEGO?', (153,
                                                                                                    0,
                                                                                                    0), None, 268, 30, 2, 1)
        self.exit_layer.add(text1)
        text2 = ItemText(161, 193, font_13, 13, '- SU PROGRESO QUEDARÁ GUARDADO -', (0,
                                                                                         0,
                                                                                         0), None, 278, 23, 2, 1)
        self.exit_layer.add(text2)
        return

    def get_active_character(self):
        datastore = self.stage.game.datastore
        for c in datastore.characters:
            if c.active:
                return c

        if len(datastore.characters) > 0:
            return datastore.characters[0]
        return

    def update_game_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.show_updategame()
        return

    def set_up_updategame(self):
        self.updategame_layer = Layer()
        background_image = assets.load_image('p0_mainmenu_updater_backdrop.png')
        background_item = ItemImage(120, 47, background_image)
        self.updategame_layer.add(background_item)
        font_14 = assets.load_font('evilgeniusbb_reg.ttf', 14)
        update_available_text = ItemText(167, 117, font_14, 13, 'Hay actualizaciones disponibles.', (153,
                                                                                                     0,
                                                                                                     0), None, 265, 30, 2, 1)
        self.updategame_layer.add(update_available_text)
        update_description_text = ItemText(155, 137, font_14, 13, self.update_description, (0,
                                                                                            0,
                                                                                            0), None, 289, 129, 2, 2)
        self.updategame_layer.add(update_description_text)
        install_text_text = ItemText(167, 279, font_14, 13, 'Para instalarlas,\ndebe salir del juego.\n\nSu progreso quedará guardado.', (153,
                                                                                                                                              0,
                                                                                                                                              0), None, 265, 55, 2, 1)
        self.updategame_layer.add(install_text_text)
        selector_rollover_image = assets.load_image('p0_mainmenu_swap_selector_rollover.png')
        self.swapdetective_rollover_back_item = ItemImage(0, 0, selector_rollover_image)
        self.swapdetective_rollover_back_item.set_visible(False)
        self.updategame_layer.add(self.swapdetective_rollover_back_item)
        yes_normal_image = assets.load_image('p0_mainmenu_btn_yes_normal.png')
        yes_rollover_image = assets.load_image('p0_mainmenu_btn_yes_rollover.png')
        yes_item = ItemImage(221, 361, yes_normal_image)
        yes_item.set_rollover_image(yes_rollover_image, self.rollover_sound)
        yes_item.add_event_handler(ItemEvent.CLICK, self.updategame_yes_click)
        self.updategame_layer.add(yes_item)
        no_normal_image = assets.load_image('p0_mainmenu_btn_no_normal.png')
        no_rollover_image = assets.load_image('p0_mainmenu_btn_no_rollover.png')
        no_item = ItemImage(303, 361, no_normal_image)
        no_item.set_rollover_image(no_rollover_image, self.rollover_sound)
        no_item.add_event_handler(ItemEvent.CLICK, self.updategame_no_click)
        self.updategame_layer.add(no_item)
        return

    def updategame_yes_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.stage.game.update_manager.execute_update()
        self.stage.game.quit()
        return

    def updategame_no_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.stage.game.updategame_dismissed = True
        self.close_updategame()
        return

    def show_updategame(self):
        self.set_up_updategame()
        self.stage.show_dialog(self.updategame_layer, self.updategame_handle_event)
        self.stage.blind_dialog(self.updategame_layer, animations.BlindDirection.SHOW_DOWN, True, [])
        return

    def close_updategame(self):
        self.stage.blind_dialog(self.updategame_layer, animations.BlindDirection.HIDE_UP, True, [], self.blind_close_updategame_callback)
        return

    def blind_close_updategame_callback(self, layer):
        self.stage.close_dialog(layer)
        if self.updategame_item not in self.main_layer.items:
            self.main_layer.add(self.updategame_item)
            animations.fade_in_item(self.updategame_item, 200)
        return

    def updategame_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.close_updategame()
        return

    def swapdetective_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.set_up_swapdetective()
        self.stage.show_dialog(self.swapdetective_layer, self.swapdetective_handle_event)
        self.stage.blind_dialog(self.swapdetective_layer, animations.BlindDirection.SHOW_DOWN, True, [])
        return

    def swapdetective_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.close_swapdetective()
        return

    def swapdetective_create_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.show_create(self.swapdetective_layer, True)
        return

    def blind_show_create_callback(self, layer):
        self.set_create_name_focus()
        return

    def set_create_name_focus(self):
        self.create_name_item.begin_edit()
        return

    def swapdetective_select_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        if self.swapdetective_selected != None:
            selected_charinfo = self.swapdetective_selected.charinfo
            self.select_character(selected_charinfo)
            self.stage.blind_dialog(self.swapdetective_layer, animations.BlindDirection.HIDE_UP, True, [], self.blind_close_swapdetective_callback)
        return

    def select_character(self, charinfo):
        self.current_character = charinfo
        self.character_id.load_character(charinfo)
        self.update_play_button()
        return

    def update_play_button(self):
        if self.overlay:
            if self.should_back_to_game():
                self.backtogame_button.set_visible(True)
                self.play_button.set_visible(False)
            else:
                self.backtogame_button.set_visible(False)
                self.play_button.set_visible(True)
        return

    def swapdetective_delete_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        if self.swapdetective_selected != None:
            self.set_up_delete(self.swapdetective_selected.charinfo)
            self.stage.show_dialog(self.delete_layer, self.delete_handle_event, None)
            self.stage.blind_dialog(self.swapdetective_layer, animations.BlindDirection.HIDE_DOWN, False, [])
            self.stage.blind_dialog(self.delete_layer, animations.BlindDirection.SHOW_DOWN, False, [])
        return

    def swapdetective_back_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.close_swapdetective()
        return

    def close_swapdetective(self):
        self.stage.blind_dialog(self.swapdetective_layer, animations.BlindDirection.HIDE_UP, True, [], self.blind_close_swapdetective_callback)
        return

    def blind_close_swapdetective_callback(self, layer):
        self.stage.close_dialog(layer)
        return

    def create_name_keypressed(self, key):
        self.update_create_accept()
        if key == K_RETURN:
            self.stage.render()
            self.click_sound.play()
            self.accept_create()
        return

    def update_create_accept(self):
        name = self.create_name_item.get_text().strip()
        if name == '':
            self.accept_button.set_visible(False)
            self.accept_button_disabled.set_visible(True)
        else:
            self.accept_button.set_visible(True)
            self.accept_button_disabled.set_visible(False)
        return

    def create_previous_avatar_enter(self, item, args):
        self.stage.render()
        self.rollover_sound.play()
        if self.create_left_arrow_state == 0:
            self.create_left_arrow_item.set_image(self.left_arrow_rollover_image)
        else:
            self.create_left_arrow_item.set_image(self.left_arrow_clicked_image)
        return

    def create_previous_avatar_leave(self, item, args):
        self.create_left_arrow_item.set_image(self.left_arrow_normal_image)
        return

    def create_previous_avatar_click(self, item, args):
        self.create_left_arrow_item.set_image(self.left_arrow_clicked_image)
        self.create_left_arrow_state = 1
        self.stage.capture_leftmousedown(item, self.create_previous_avatar_mousecapture)
        return

    def create_previous_avatar_mousecapture(self, args, released):
        if released:
            self.create_left_arrow_state = 0
            if self.stage.get_over_item() == self.create_left_arrow_item:
                self.stage.render()
                self.create_flip_sound.play()
                if self.create_avatar > 1:
                    self.create_avatar -= 1
                    self.update_create_avatar_image()
                self.create_left_arrow_item.set_image(self.left_arrow_rollover_image)
        return

    def create_next_avatar_enter(self, item, args):
        self.stage.render()
        self.rollover_sound.play()
        if self.create_right_arrow_state == 0:
            self.create_right_arrow_item.set_image(self.right_arrow_rollover_image)
        else:
            self.create_right_arrow_item.set_image(self.right_arrow_clicked_image)
        return

    def create_next_avatar_leave(self, item, args):
        self.create_right_arrow_item.set_image(self.right_arrow_normal_image)
        return

    def create_next_avatar_click(self, item, args):
        self.create_right_arrow_item.set_image(self.right_arrow_clicked_image)
        self.create_right_arrow_state = 1
        self.stage.capture_leftmousedown(item, self.create_next_avatar_mousecapture)
        return

    def create_next_avatar_mousecapture(self, args, released):
        if released:
            self.create_right_arrow_state = 0
            if self.stage.get_over_item() == self.create_right_arrow_item:
                self.stage.render()
                self.create_flip_sound.play()
                if self.create_avatar < self.create_avatar_count:
                    self.create_avatar += 1
                    self.update_create_avatar_image()
                self.create_right_arrow_item.set_image(self.right_arrow_rollover_image)
        return

    def create_accept_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.accept_create()
        return

    def accept_create(self):
        name = self.create_name_item.get_text().strip()
        if name == '':
            self.create_name_item.set_text('')
            self.create_name_item.begin_edit()
        elif self.create_character_location == '':
            self.show_state_list()
        else:
            name = characterid.apply_name_text_casing(name)
            newchar = self.stage.game.datastore.create_character(name, self.create_sex_male, self.create_avatar, self.create_character_location, False)
            self.select_character(newchar)
            if self.create_callback != None:
                self.create_callback()
            elif self.create_background_layer != None:
                self.stage.blind_dialog(self.create_background_layer, animations.BlindDirection.HIDE_UP, True, [], self.blind_accept_create_callback)
            else:
                self.stage.blind_dialog(self.create_layer, animations.BlindDirection.HIDE_UP, True, [], self.blind_accept_create_callback)
        return

    def blind_accept_create_callback(self, layer):
        self.stage.close_dialog(self.create_layer)
        if self.create_background_layer != None:
            self.stage.close_dialog(self.create_background_layer)
        self.create_layer = None
        self.create_callback = None
        self.stage.update_mouse()
        return

    def create_state_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.show_state_list()
        return

    def show_state_list(self):
        self.set_up_state_list()
        self.stage.show_dialog(self.state_list_layer, self.state_list_handle_event, None)
        self.stage.blind_dialog(self.state_list_layer, animations.BlindDirection.SHOW_DOWN, False, [], None)
        return

    def state_list_handle_event(self, e):
        return

    def create_department_enter(self, item, args):
        self.stage.stop_timer(STATE_ROLLOVER_TIMER_KEY)
        self.create_over_department = item
        self.stage.start_timer(STATE_ROLLOVER_TIMER_KEY, 50, self.show_department_rollover)
        return

    def create_department_leave(self, item, args):
        self.stage.stop_timer(STATE_ROLLOVER_TIMER_KEY)
        self.create_state_rollover_item.set_visible(False)
        return

    def show_department_rollover(self, key, data):
        self.stage.stop_timer(key)
        self.stage.render()
        self.rollover_sound.play()
        self.create_state_rollover_item.set_top(self.create_over_department.get_top())
        self.create_state_rollover_item.set_visible(True)
        return

    def create_department_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.create_character_location = item.department.name
        self.character_state_item.set_text(item.department.name)
        animations.blind_layer(self.state_list_layer, animations.BlindDirection.HIDE_DOWN, None, 450, self.blind_close_state_list_callback)
        return

    def blind_close_state_list_callback(self, layer):
        self.stage.close_dialog(self.state_list_layer)
        self.state_list_layer = None
        self.stage.update_mouse()
        return

    def create_male_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.create_sex_male = True
        self.create_avatar = 1
        self.update_create_sex_mark()
        self.update_create_avatar_image()
        return

    def create_female_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.create_sex_male = False
        self.create_avatar = 1
        self.update_create_sex_mark()
        self.update_create_avatar_image()
        return

    def create_cancel_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.close_create()
        return

    def create_handle_event(self, e):
        if e.type == KEYDOWN:
            if e.key == K_RETURN:
                self.stage.render()
                self.click_sound.play()
                self.accept_create()
            elif e.key == K_ESCAPE:
                self.stage.render()
                self.click_sound.play()
                self.close_create()
        return

    def show_create(self, background_layer, apply_blind, callback=None, dark_background=False):
        self.create_background_layer = background_layer
        self.create_callback = callback
        self.create_dark_background = dark_background
        self.set_up_create()
        if dark_background:
            self.stage.show_dialog(self.create_layer, self.create_handle_event)
        else:
            self.stage.show_dialog(self.create_layer, self.create_handle_event, None)
        if apply_blind:
            if background_layer != None:
                self.stage.blind_dialog(background_layer, animations.BlindDirection.HIDE_DOWN, False, [])
            self.stage.blind_dialog(self.create_layer, animations.BlindDirection.SHOW_DOWN, dark_background, [], self.blind_show_create_callback)
        return

    def close_create(self):
        if self.create_background_layer != None:
            self.create_background_layer.set_clip(None)
            animations.blind_layer(self.create_background_layer, animations.BlindDirection.SHOW_DOWN, None, 450)
        if self.create_dark_background:
            self.stage.blind_dialog(self.create_layer, animations.BlindDirection.HIDE_UP, True, [], self.blind_close_create_callback)
        else:
            animations.blind_layer(self.create_layer, animations.BlindDirection.HIDE_DOWN, None, 450, self.blind_close_create_callback)
        return

    def blind_close_create_callback(self, layer):
        self.stage.close_dialog(self.create_layer)
        self.create_layer = None
        self.create_callback = None
        self.stage.update_mouse()
        return

    def delete_yes_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        characters = self.stage.game.datastore.characters[:]
        characters.sort(key=self.get_character_name)
        selection_index = characters.index(self.swapdetective_selected.charinfo)
        if selection_index == 0:
            new_selection_index = selection_index + 1
        else:
            new_selection_index = selection_index - 1
        if new_selection_index >= 0 and new_selection_index < len(characters):
            new_selected_char = characters[new_selection_index]
        else:
            new_selected_char = None
        selected_character = self.swapdetective_selected.charinfo
        self.stage.game.datastore.delete_character(selected_character)
        if new_selected_char != None:
            self.select_character(new_selected_char)
        else:
            self.select_character(None)
        self.load_characters()
        self.stage.render()
        self.deleted_characters.append(selected_character.id)
        if self.current_character == selected_character:
            if new_selected_char != None:
                self.select_character(new_selected_char)
                self.current_character.active = True
                datastore = self.stage.game.datastore
                datastore.save_characters()
            else:
                self.select_character(None)
        self.swapdetective_layer.set_clip(None)
        animations.blind_layer(self.swapdetective_layer, animations.BlindDirection.SHOW_DOWN, None, 450)
        animations.blind_layer(self.delete_layer, animations.BlindDirection.HIDE_DOWN, None, 450, self.blind_close_delete_callback)
        return

    def delete_no_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.close_delete()
        return

    def delete_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.close_delete()
        return

    def close_delete(self):
        self.swapdetective_layer.set_clip(None)
        animations.blind_layer(self.swapdetective_layer, animations.BlindDirection.SHOW_DOWN, None, 450)
        animations.blind_layer(self.delete_layer, animations.BlindDirection.HIDE_DOWN, None, 450, self.blind_close_delete_callback)
        return

    def blind_close_delete_callback(self, layer):
        self.stage.close_dialog(self.delete_layer)
        self.delete_layer = None
        self.stage.update_mouse()
        return

    def credits_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.set_up_credits()
        self.stage.show_dialog(self.credits_layer, self.credits_handle_event)
        self.load_current_credits(False)
        self.stage.blind_dialog(self.credits_layer, animations.BlindDirection.SHOW_DOWN, True, [])
        return

    def credits_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.close_credits()
        return

    def credits_close_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.close_credits()
        return

    def close_credits(self):
        self.stage.blind_dialog(self.credits_layer, animations.BlindDirection.HIDE_UP, True, [], self.blind_close_credits_callback)
        return

    def blind_close_credits_callback(self, layer):
        self.stage.close_dialog(self.credits_layer)
        return

    def credits_next_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        if self.credits_page < self.credits_pagecount:
            self.credits_page += 1
            self.load_current_credits()
        return

    def credits_prev_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        if self.credits_page > 1:
            self.credits_page -= 1
            self.load_current_credits()
        return

    def play_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        if self.should_back_to_game():
            self.close_mainmenu()
        elif self.current_character == None:
            self.show_create(None, True, self.start_game, True)
        else:
            self.start_game()
        self.deleted_characters = []
        return

    def should_back_to_game(self):
        datastore = self.stage.game.datastore
        return self.overlay and datastore.user_character != None and self.current_character != None and datastore.user_character.charinfo.id == self.current_character.id and self.current_character.id not in self.deleted_characters

    def start_game(self):
        if self.current_character != None:
            if not self.overlay:
                self.stage.set_music_volume(0, 300)
            black_layer = Layer()
            black_background = ItemRect(0, 0, 600, 450)
            black_layer.add(black_background)
            self.stage.add_layer(black_layer)
            animations.blind_layer(black_layer, animations.BlindDirection.SHOW_DOWN, None, 450, self.blind_hide_main_callback)
        return

    def blind_hide_main_callback(self, layer):
        datastore = self.stage.game.datastore
        if not self.current_character.active:
            for c in self.stage.game.datastore.characters:
                c.active = False

            self.current_character.active = True
            datastore.save_characters()
        self.load_character_progress()
        if datastore.user_character_stage == None or datastore.user_character_stage == 'nc':
            case_generator = serialization.CaseGenerator(datastore)
            datastore.user_character_progress.set_case(case_generator.new_case())
            stage = case.CaseStage(self.stage.game)
            self.stage.game.set_stage(stage)
        else:
            user_character_stage = self.stage.game.datastore.user_character_stage
            if user_character_stage == 'p1':
                loading_image = 'p0_loading_slides_001.jpg'
            elif user_character_stage == 'p2':
                loading_image = 'p0_loading_slides_002.jpg'
            elif user_character_stage == 'p3':
                loading_image = 'p0_loading_slides_003.jpg'
            else:
                loading_image = 'p0_loading_slides_001.jpg'
            self.stage.game.show_loading(self.show_loading_callback, loading_image)
        return

    def show_loading_callback(self, layer):
        user_character_stage = self.stage.game.datastore.user_character_stage
        if user_character_stage == 'p1':
            stage = phase0.Phase0Stage(self.stage.game, 1)
            stage.save_state_on_next_load_phase = False
        elif user_character_stage == 'p2':
            stage = phase0.Phase0Stage(self.stage.game, 2)
            stage.save_state_on_next_load_phase = False
        elif user_character_stage == 'p3':
            stage = phase0.Phase0Stage(self.stage.game, 3)
            stage.save_state_on_next_load_phase = False
        else:
            raise Exception('Unknown character current stage (' + user_character_stage + ')')
        self.stage.game.set_stage(stage)
        self.stage.game.hide_loading()
        return

    def highscores_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        merits_dialog = merits.Merits(self.stage)
        merits_dialog.show_highscores()
        return

    def help_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        help_dialog = help.Help(self.stage, True, True)
        help_dialog.show_help(1, True, False)
        return

    def exit_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.set_up_exit()
        self.stage.show_dialog(self.exit_layer, self.exit_handle_event)
        self.stage.blind_dialog(self.exit_layer, animations.BlindDirection.SHOW_DOWN, True, [])
        return

    def exit_yes_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.stage.game.quit()
        return

    def exit_no_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.close_exit()
        return

    def exit_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.close_exit()
        return

    def close_exit(self):
        self.stage.blind_dialog(self.exit_layer, animations.BlindDirection.HIDE_UP, True, [], self.blind_close_exit_callback)
        return

    def blind_close_exit_callback(self, layer):
        self.stage.close_dialog(self.exit_layer)
        return

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE and self.overlay:
                self.stage.render()
                self.click_sound.play()
                self.close_mainmenu()
                return True
        return


