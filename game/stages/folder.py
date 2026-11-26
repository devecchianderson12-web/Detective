from framework.stage import *
from framework import assets, animations
import random
from game.data import datastore
from . import witness
CASE = 1
CASE_EXTENDED = 2
IDENTIKIT = 3
WITNESS = 4

class Folder(Item):

    def __init__(self, stage):
        self.stage = stage
        self.base_layer = Layer()
        self.folder_back_layer = Layer()
        self.case_layer = Layer()
        self.case_data_layer = Layer()
        self.case_extended_layer = Layer()
        self.identikit_layer = Layer()
        self.identikit_thief_layer = Layer()
        self.witness_layer = Layer()
        self.witness_data_layer = Layer()
        self.arrest_order_layer = Layer()
        self.active_layer = ''
        self.arrest_order_is_working = False
        self.arrest_order_sent = False
        self.pending_changes_to_save = False
        self.font_15 = assets.load_font('powdrft_.ttf', 15)
        self.font_16 = assets.load_font('powdrft_.ttf', 16)
        self.font_17 = assets.load_font('powdrft_.ttf', 17)
        self.font_18 = assets.load_font('powdrft_.ttf', 18)
        self.font_20 = assets.load_font('powdrft_.ttf', 20)
        self.font_21 = assets.load_font('powdrft_.ttf', 21)
        self.font_23 = assets.load_font('powdrft_.ttf', 23)
        self.font_22 = assets.load_font('powdrft_.ttf', 22)
        self.font_24 = assets.load_font('powdrft_.ttf', 24)
        self.font_25 = assets.load_font('powdrft_.ttf', 24)
        self.click_sound = stage.click_sound
        self.rollover_sound = stage.rollover_sound
        self.popup_sound = stage.witness_popup_sound
        self.turn_page_sound = assets.load_sound('GUI_Turn_Page.ogg')
        self.flip_option_sound = assets.load_sound('GUI_Flip.ogg')
        self.witness_fade_in_sound = assets.load_sound('fade.ogg')
        self.set_up_identikit()
        self.set_up_witness()
        self.set_up()
        return

    def set_up(self):
        self.set_up_background()
        self.set_up_buttons()
        self.set_up_case_texts()
        self.set_up_case_extended_texts()
        return

    def set_up_background(self):
        folder_center_image = assets.load_image('p0_folder_center.jpg')
        folder_center = ItemImage(34, 39, folder_center_image, None)
        self.folder_back_layer.add(folder_center)
        folder_top_image = assets.load_image('p0_folder_top.png')
        folder_top = ItemImage(23, 16, folder_top_image, None)
        self.folder_back_layer.add(folder_top)
        folder_bottom_image = assets.load_image('p0_folder_bottom.png')
        folder_bottom = ItemImage(18, 387, folder_bottom_image, None)
        self.folder_back_layer.add(folder_bottom)
        folder_left_image = assets.load_image('p0_folder_left.png')
        folder_left = ItemImage(21, 39, folder_left_image, None)
        self.folder_back_layer.add(folder_left)
        folder_right_image = assets.load_image('p0_folder_right.png')
        folder_right = ItemImage(550, 39, folder_right_image, None)
        self.folder_back_layer.add(folder_right)
        self.case_image = assets.load_image('p0_folder_case1_back.png')
        self.case_data_image = assets.load_image('p0_folder_case2_back.png')
        self.case_background = ItemImage(44, 72, self.case_image, None)
        self.case_data_background = ItemImage(44, 116, self.case_data_image, None)
        self.case_layer.add(self.case_background)
        self.case_data_layer.add(self.case_data_background)
        return

    def set_up_buttons(self):
        self.set_up_menu_buttons()
        self.set_up_case_page_button()
        self.set_up_identikit_page_button()
        self.set_up_witness_page_button()
        return

    def set_up_menu_buttons(self):
        close_button_image = assets.load_image('p0_button_close.png')
        self.close_button_rollover_image = assets.load_image('p0_button_close_rollover.png')
        self.next_button_image = assets.load_image('p0_button_next_active.png')
        next_button_rollover_image = assets.load_image('p0_button_next_rollover.png')
        self.previous_button_image = assets.load_image('p0_button_previous_active.png')
        self.previous_button_rollover_image = assets.load_image('p0_button_previous_rollover.png')
        self.close_button = ItemImage(275, 392, close_button_image, None)
        self.close_button.set_rollover_image(self.close_button_rollover_image, self.rollover_sound)
        self.next_button = ItemImage(305, 392, self.next_button_image, None)
        self.previous_button = ItemImage(245, 392, self.previous_button_image, None)
        self.next_button.set_rollover_image(next_button_rollover_image, self.rollover_sound)
        self.previous_button.set_rollover_image(self.previous_button_rollover_image, self.rollover_sound)
        self.close_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.next_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.previous_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.base_layer.add(self.close_button)
        self.base_layer.add(self.next_button)
        self.base_layer.add(self.previous_button)
        return

    def set_up_case_page_button(self):
        self.case_button_active_image = assets.load_image('p0_folder_btn_case_active.png')
        self.case_button_inactive_image = assets.load_image('p0_folder_btn_case_inactive.png')
        self.case_button_rollover_image = assets.load_image('p0_folder_btn_case_hovered.png')
        self.case_button = ItemImage(538, 67, self.case_button_inactive_image, None)
        self.case_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.base_layer.add(self.case_button)
        return

    def set_up_witness_page_button(self):
        self.witness_button_active_image = assets.load_image('p0_folder_btn_witnesses_active.png')
        self.witness_button_inactive_image = assets.load_image('p0_folder_btn_witnesses_inactive.png')
        self.witness_button_rollover_image = assets.load_image('p0_folder_btn_witnesses_hovered.png')
        self.witness_button = ItemImage(538, 249, self.witness_button_inactive_image, None)
        self.witness_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.base_layer.add(self.witness_button)
        return

    def set_up_witness_texts(self):
        self.witness_case_text = ItemText(90, 154, self.font_16, 0, '', (157, 21, 21), None, 100, 20)
        self.witness_case_text.set_text(self.stage.game.datastore.user_character_progress.case.number)
        self.witness_layer.add(self.witness_case_text)
        return

    def set_up_witness_buttons(self):
        self.witness_set_rollover_image = assets.load_image('p0_folder_witness_whiteback.png')
        self.witness_underline = assets.load_image('p0_folder_witness_underline.png')
        size = self.witness_set_rollover_image.get_size()
        self.witness_sets = []
        witness1_mask = ItemMask(46, 204, size)
        self.witness_sets.append(witness1_mask)
        witness2_mask = ItemMask(318, 107, size)
        self.witness_sets.append(witness2_mask)
        witness3_mask = ItemMask(318, 234, size)
        self.witness_sets.append(witness3_mask)
        for witness_mask in self.witness_sets:
            witness_mask.add_event_handler(ItemEvent.CLICK, self.witness_button_click)

        for witness_mask in self.witness_sets:
            self.witness_data_layer.add(witness_mask)

        return

    def set_up_identikit_page_button(self):
        self.identikit_button_active_image = assets.load_image('p0_folder_btn_identikit_active.png')
        self.identikit_button_inactive_image = assets.load_image('p0_folder_btn_identikit_inactive.png')
        self.identikit_button_rollover_image = assets.load_image('p0_folder_btn_identikit_hovered.png')
        self.identikit_button = ItemImage(538, 152, self.identikit_button_inactive_image, None)
        self.identikit_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.base_layer.add(self.identikit_button)
        return

    def set_up_identikit_buttons(self):
        thief_dialog_close_button_image = assets.load_image('btn_testigo_x_normal.png')
        thief_dialog_close_button_rollover_image = assets.load_image('btn_testigo_x_rollover.png')
        self.thief_dialog_close_button = ItemImage(425, 39, thief_dialog_close_button_image, None, True)
        self.thief_dialog_close_button.set_rollover_image(thief_dialog_close_button_rollover_image, self.rollover_sound)
        arrow_left_image = assets.load_image('p0_identikit_arrow_prev_standby.png')
        self.arrow_left_image_rollover = arrow_left_image_rollover = assets.load_image('p0_identikit_arrow_prev_hover.png')
        self.arrow_left_image_pressed = arrow_left_image_pressed = assets.load_image('p0_identikit_arrow_prev_pressed.png')
        arrow_right_image = assets.load_image('p0_identikit_arrow_next_standby.png')
        self.arrow_right_image_rollover = arrow_right_image_rollover = assets.load_image('p0_identikit_arrow_next_hover.png')
        self.arrow_right_image_pressed = arrow_right_image_pressed = assets.load_image('p0_identikit_arrow_next_pressed.png')
        self.arrest_order_not_working_image = assets.load_image('p0_folder_identikit_orderbutton_inactive.png')
        self.arrest_order_issued_image = assets.load_image('p0_identikit_done_orderbutton.png')
        self.arrest_order_working_image = assets.load_image('p0_folder_identikit_orderbutton_active.png')
        self.arrest_order_working_rollover_image = assets.load_image('p0_folder_identikit_orderbutton_rollover.png')
        arrest_order_dialog_close_button_image = assets.load_image('p0_button_close.png')
        arrest_order_dialog_close_button_rollover_image = assets.load_image('p0_button_close_rollover.png')
        self.sex_left_button = ItemImage(42, 194, arrow_left_image)
        self.sex_left_button.set_rollover_image(arrow_left_image_rollover, self.rollover_sound)
        self.sex_left_button.set_pressed_image(arrow_left_image_pressed)
        self.sex_right_button = ItemImage(246, 194, arrow_right_image)
        self.sex_right_button.set_rollover_image(arrow_right_image_rollover, self.rollover_sound)
        self.sex_right_button.set_pressed_image(arrow_right_image_pressed)
        self.height_left_button = ItemImage(42, 239, arrow_left_image)
        self.height_left_button.set_rollover_image(arrow_left_image_rollover, self.rollover_sound)
        self.height_left_button.set_pressed_image(arrow_left_image_pressed)
        self.height_right_button = ItemImage(246, 239, arrow_right_image)
        self.height_right_button.set_rollover_image(arrow_right_image_rollover, self.rollover_sound)
        self.height_right_button.set_pressed_image(arrow_right_image_pressed)
        self.hair_left_button = ItemImage(42, 286, arrow_left_image)
        self.hair_left_button.set_rollover_image(arrow_left_image_rollover, self.rollover_sound)
        self.hair_left_button.set_pressed_image(arrow_left_image_pressed)
        self.hair_right_button = ItemImage(246, 286, arrow_right_image)
        self.hair_right_button.set_rollover_image(arrow_right_image_rollover, self.rollover_sound)
        self.hair_right_button.set_pressed_image(arrow_right_image_pressed)
        self.distinctive_left_button = ItemImage(42, 332, arrow_left_image)
        self.distinctive_left_button.set_rollover_image(arrow_left_image_rollover, self.rollover_sound)
        self.distinctive_left_button.set_pressed_image(arrow_left_image_pressed)
        self.distinctive_right_button = ItemImage(246, 332, arrow_right_image)
        self.distinctive_right_button.set_rollover_image(arrow_right_image_rollover, self.rollover_sound)
        self.distinctive_right_button.set_pressed_image(arrow_right_image_pressed)
        self.arrest_order_box = ItemImage(317, 296, self.arrest_order_not_working_image, None, True)
        self.arrest_order_button = ItemMask(318, 316, (219, 39))
        self.arrest_order_dialog_close_button = ItemImage(272, 305, arrest_order_dialog_close_button_image, None, True)
        self.arrest_order_dialog_close_button.set_rollover_image(arrest_order_dialog_close_button_rollover_image, self.rollover_sound)
        self.thief_dialog_close_button.add_event_handler(ItemEvent.CLICK, self.identikit_new_dialog_click)
        self.sex_left_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.sex_right_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.height_left_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.height_right_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.hair_left_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.hair_right_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.distinctive_left_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.distinctive_right_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.arrest_order_button.add_event_handler(ItemEvent.CLICK, self.identikit_new_dialog_click)
        self.arrest_order_dialog_close_button.add_event_handler(ItemEvent.CLICK, self.identikit_new_dialog_click)
        self.identikit_thief_layer.add(self.thief_dialog_close_button)
        self.identikit_layer.add(self.sex_left_button)
        self.identikit_layer.add(self.sex_right_button)
        self.identikit_layer.add(self.height_left_button)
        self.identikit_layer.add(self.height_right_button)
        self.identikit_layer.add(self.hair_left_button)
        self.identikit_layer.add(self.hair_right_button)
        self.identikit_layer.add(self.distinctive_left_button)
        self.identikit_layer.add(self.distinctive_right_button)
        self.identikit_layer.add(self.arrest_order_button)
        self.identikit_layer.add(self.arrest_order_box)
        self.arrest_order_layer.add(self.arrest_order_dialog_close_button)
        return

    def set_up_identikit_texts(self):
        self.identikit_case_text = ItemText(90, 154, self.font_16, 0, '', (157, 21,
                                                                           21), None, 100, 20)
        self.identikit_sex_text = ItemText(99, 192, self.font_24, 0, '', (0, 0, 0), None, 110, 30, 2)
        self.identikit_height_text = ItemText(99, 237, self.font_24, 0, '', (0, 0,
                                                                             0), None, 110, 30, 2)
        self.identikit_hair_text = ItemText(99, 284, self.font_24, 0, '', (0, 0, 0), None, 110, 30, 2)
        self.identikit_distinctive_text = ItemText(99, 329, self.font_24, 0, '', (0,
                                                                                  0,
                                                                                  0), None, 110, 30, 2)
        self.identikit_thief_name = ItemText(161, 210, self.font_24, 0, '', (157, 21,
                                                                             21), None, 290, 30)
        self.identikit_thief_nickname = ItemText(161, 229, self.font_23, 0, '', (51,
                                                                                 51,
                                                                                 51), None, 250, 30)
        self.identikit_thief_age = ItemText(166, 248, self.font_18, 0, '', (102, 102,
                                                                            102), None, 158, 25)
        self.identikit_thief_description = ItemText(161, 270, self.font_18, 14, '', (0,
                                                                                     0,
                                                                                     0), None, 275, 132)
        self.arrest_order_name_text = ItemText(163, 263, self.font_22, 0, '', (51,
                                                                               51,
                                                                               51), None, 267, 32, 2)
        self.arrest_order_nick_text = ItemText(163, 280, self.font_20, 0, '', (102,
                                                                               51,
                                                                               51), None, 267, 30, 2)
        self.identikit_case_text.set_text(self.stage.game.datastore.user_character_progress.case.number)
        self.identikit_layer.add(self.identikit_case_text)
        self.identikit_layer.add(self.identikit_sex_text)
        self.identikit_layer.add(self.identikit_height_text)
        self.identikit_layer.add(self.identikit_hair_text)
        self.identikit_layer.add(self.identikit_distinctive_text)
        self.identikit_thief_layer.add(self.identikit_thief_name)
        self.identikit_thief_layer.add(self.identikit_thief_age)
        self.identikit_thief_layer.add(self.identikit_thief_nickname)
        self.identikit_thief_layer.add(self.identikit_thief_description)
        self.arrest_order_layer.add(self.arrest_order_name_text)
        self.arrest_order_layer.add(self.arrest_order_nick_text)
        return

    def set_up_case_texts(self):
        self.case_number_text = ItemText(90, 154, self.font_16, 0, '', (157, 21, 21), None, 100, 20)
        self.case_agent_text = ItemText(68, 192, self.font_18, 13, '', (0, 0, 0), None, 170, 50, 1, 2)
        self.case_department_text = ItemText(138, 228, self.font_18, 0, '', (0, 0,
                                                                             0), None, 115, 25)
        self.case_place_text = ItemText(92, 251, self.font_17, 13, '', (0, 0, 0), None, 175, 95)
        self.case_number2_text = ItemText(467, 111, self.font_16, 0, '', (157, 21,
                                                                          21), None, 100, 25)
        self.case_stolen_obj_text = ItemText(323, 149, self.font_17, 13, '', (0, 0,
                                                                              0), None, 210, 95)
        self.case_time_text = ItemText(376, 274, self.font_18, 0, '', (0, 0, 0), None, 225, 232)
        self.case_number_text.set_text(self.stage.game.datastore.user_character_progress.case.number)
        self.case_number2_text.set_text(self.stage.game.datastore.user_character_progress.case.number)
        self.case_department_text.set_text(self.stage.game.datastore.user_character_progress.case.crime_location.department.name)
        self.case_place_text.set_text(self.stage.game.datastore.user_character_progress.case.crime_location.name)
        so = self.stage.game.datastore.user_character_progress.case.stolen_object.description1
        self.case_stolen_obj_text.set_text(so[0].capitalize() + so[1:len(so)])
        self.case_time_text.set_text('Día %s a las %s hs.' % self.stage.game.datastore.user_character_progress.case.get_time_limit())
        self.case_data_layer.add(self.case_number_text)
        self.case_data_layer.add(self.case_agent_text)
        self.case_data_layer.add(self.case_department_text)
        self.case_data_layer.add(self.case_place_text)
        self.case_data_layer.add(self.case_number2_text)
        self.case_data_layer.add(self.case_stolen_obj_text)
        self.case_data_layer.add(self.case_time_text)
        return

    def set_up_case_extended_texts(self):
        self.case_ext_number_text = ItemText(90, 154, self.font_16, 0, '', (157, 21,
                                                                            21), None, 100, 25)
        self.case_ext_text_left = ItemText(45, 174, self.font_16, 12, '', (0, 0, 0), None, 228, 184)
        self.case_ext_text_right = ItemText(320, 105, self.font_16, 12, '', (0, 0,
                                                                             0), None, 228, 257)
        self.case_ext_number_text.set_text(self.stage.game.datastore.user_character_progress.case.number)
        self.case_ext_text_left.break_text_into(self.case_ext_text_right)
        self.case_extended_layer.add(self.case_ext_number_text)
        self.case_extended_layer.add(self.case_ext_text_left)
        self.case_extended_layer.add(self.case_ext_text_right)
        return

    def load_agent_name(self):
        name = self.stage.game.datastore.user_character.charinfo.name
        self.case_agent_text.set_text(name)
        return

    def load_case_text(self):
        text = self.stage.game.datastore.user_character_progress.case.get_full_text(self.stage.game.datastore.user_character, self.stage.game.datastore.user_character_progress)
        self.case_ext_text_left.set_text(text)
        return

    def close_folder(self):
        self.stage.close_dialog(self.base_layer)
        self.stage.folder_default_tab = self.active_layer
        return

    def show_arrest_order_done_dialog(self):
        self.arrest_order_layer.empty()
        self.arrest_order_sent_sound = assets.load_sound('GUI_arrest_order_sent.ogg')
        arrest_order_background_image = assets.load_image('p0_identikit_arrest_order_done_background.png')
        self.arrest_order_background.set_image(arrest_order_background_image)
        self.arrest_order_background.set_lefttop(109, 75)
        self.arrest_order_layer.add(self.arrest_order_background)
        self.arrest_order_thief_image.set_lefttop(261, 202)
        self.arrest_order_layer.add(self.arrest_order_thief_image)
        self.arrest_order_name_text.set_lefttop(163, 263)
        self.arrest_order_nick_text.set_lefttop(163, 280)
        self.arrest_order_layer.add(self.arrest_order_name_text)
        self.arrest_order_layer.add(self.arrest_order_nick_text)
        self.arrest_order_layer.add(self.arrest_order_dialog_close_button)
        self.obsure_folder_close()
        self.stage.show_dialog(self.arrest_order_layer, self.arrest_order_handle_event, callback=self.clarify_folder_close)
        self.stage.render()
        self.arrest_order_sent_sound.play()
        return

    def set_up_arrest_order_dialog(self):
        self.arrest_order_layer.empty()
        self.arrest_order_sound = assets.load_sound('GUI_arrest_order.ogg')
        arrest_order_dialog_background_image = assets.load_image('p0_identikit_arrest_order_warning_background.png')
        self.arrest_order_background.set_image(arrest_order_dialog_background_image)
        self.arrest_order_background.set_lefttop(119, 36)
        self.arrest_order_layer.add(self.arrest_order_background)
        self.arrest_order_thief_image.set_lefttop(272, 177)
        self.arrest_order_layer.add(self.arrest_order_thief_image)
        self.arrest_order_name_text.set_lefttop(168, 237)
        self.arrest_order_nick_text.set_lefttop(168, 254)
        self.arrest_order_layer.add(self.arrest_order_name_text)
        self.arrest_order_layer.add(self.arrest_order_nick_text)
        arrest_order_dialog_accept_button_image = assets.load_image('p0_identikit_arrest_order_btn_acept_normal.png')
        arrest_order_dialog_accept_button_rollover_image = assets.load_image('p0_identikit_arrest_order_btn_acept_rollover.png')
        arrest_order_dialog_cancel_button_image = assets.load_image('p0_identikit_arrest_order_btn_cancel_normal.png')
        arrest_order_dialog_cancel_button_rollover_image = assets.load_image('p0_identikit_arrest_order_btn_cancel_rollover.png')
        self.arrest_order_dialog_accept_button = ItemImage(204, 296, arrest_order_dialog_accept_button_image, None, True)
        self.arrest_order_dialog_accept_button.set_rollover_image(arrest_order_dialog_accept_button_rollover_image, self.rollover_sound)
        self.arrest_order_dialog_cancel_button = ItemImage(313, 296, arrest_order_dialog_cancel_button_image, None, True)
        self.arrest_order_dialog_cancel_button.set_rollover_image(arrest_order_dialog_cancel_button_rollover_image, self.rollover_sound)
        self.arrest_order_dialog_accept_button.add_event_handler(ItemEvent.CLICK, self.identikit_new_dialog_click)
        self.arrest_order_layer.add(self.arrest_order_dialog_accept_button)
        self.arrest_order_dialog_cancel_button.add_event_handler(ItemEvent.CLICK, self.identikit_new_dialog_click)
        self.arrest_order_layer.add(self.arrest_order_dialog_cancel_button)
        return

    def load_identikit_data(self):
        self.get_list_identikit()
        self.identikit_image_matrix = ["" for x in range(9)]
        circle_outline_back = assets.load_image('p0_folder_identikit_suspect_selected.png')
        self.circle_outlined_image = ItemImage(325, 110, circle_outline_back, None)
        self.arrest_order_thief_image = ItemImage(261, 202, None, None)
        self.arrest_order_layer.add(self.arrest_order_thief_image)
        self.selected_sex_feature = 0
        self.selected_height_feature = 0
        self.selected_hair_feature = 0
        self.selected_distinctive_feature = 0
        self.list_sex_features = []
        self.list_height_features_male = []
        self.list_height_features_female = []
        self.list_hair_features = []
        self.list_distinctive_features = []
        self.list_sex_features.append('-')
        self.list_sex_features.append('Hombre')
        self.list_sex_features.append('Mujer')
        self.list_height_features_male.append('-')
        self.list_height_features_male.append('Alto')
        self.list_height_features_male.append('Bajo')
        self.list_height_features_female.append('-')
        self.list_height_features_female.append('Alta')
        self.list_height_features_female.append('Baja')
        self.list_hair_features.append('-')
        self.list_hair_features.append('Morocho')
        self.list_hair_features.append('Rubio')
        self.list_hair_features.append('Pelirrojo')
        self.list_hair_features.append('Canoso')
        self.list_distinctive_features.append('-')
        self.list_distinctive_features.append('Cicatriz')
        self.list_distinctive_features.append('Tatuaje')
        self.list_distinctive_features.append('Lentes')
        self.list_distinctive_features.append('Lunar')
        self.identikit_sex_text.set_text(self.list_sex_features[0])
        self.identikit_height_text.set_text(self.list_sex_features[0])
        self.identikit_hair_text.set_text(self.list_hair_features[0])
        self.identikit_distinctive_text.set_text(self.list_distinctive_features[0])
        return

    def set_up_identikit_background(self):
        self.identikit_image = assets.load_image('p0_folder_identikit_back.png')
        self.identikit_thief_background_image = assets.load_image('p0_folder_identikit_suspect_popup_back.png')
        self.identikit_background = ItemImage(44, 72, self.identikit_image, None)
        self.identikit_thief_background = ItemImage(128, 8, self.identikit_thief_background_image, None)
        self.identikit_thief_image = ItemImage(160, 37, None, None)
        self.identikit_thief_image_side = ItemImage(292, 37, None, None)
        self.arrest_order_background = ItemImage(109, 75, None, None)
        self.identikit_layer.add(self.identikit_background)
        self.identikit_thief_layer.add(self.identikit_thief_background)
        self.identikit_thief_layer.add(self.identikit_thief_image)
        self.identikit_thief_layer.add(self.identikit_thief_image_side)
        self.arrest_order_layer.add(self.arrest_order_background)
        return

    def set_up_witness_background(self):
        self.witness_image = assets.load_image('p0_folder_witness_back.png')
        self.witness_background = ItemImage(44, 72, self.witness_image, None)
        self.witness_layer.add(self.witness_background)
        return

    def identikit_arrest_order_sent(self):
        if not self.arrest_order_sent:
            self.arrest_order_sent = True
            done_back_center_image = assets.load_image('p0_identikit_done_back_center.jpg')
            done_back_center_item = ItemImage(48, 49, done_back_center_image)
            self.identikit_layer.add(done_back_center_item)
            done_back_top_image = assets.load_image('p0_identikit_done_back_top.png')
            done_back_top_item = ItemImage(30, 27, done_back_top_image)
            self.identikit_layer.add(done_back_top_item)
            done_back_bottom_image = assets.load_image('p0_identikit_done_back_bottom.png')
            done_back_bottom_item = ItemImage(33, 373, done_back_bottom_image)
            self.identikit_layer.add(done_back_bottom_item)
            done_back_left_image = assets.load_image('p0_identikit_done_back_left.png')
            done_back_left_item = ItemImage(28, 49, done_back_left_image)
            self.identikit_layer.add(done_back_left_item)
            done_back_right_image = assets.load_image('p0_identikit_done_back_right.png')
            done_back_right_item = ItemImage(276, 49, done_back_right_image)
            self.identikit_layer.add(done_back_right_item)
            self.arrest_order_thief_image = ItemImage(93, 127, None, None)
            stamp = ItemImage(182, 128, assets.load_image('p0_identikit_done_overstamp.png'))
            arrest_order_name_text = ItemText(58, 313, self.font_24, 16, '', (31, 31,
                                                                              31), None, 207, 33, 2, 2)
            arrest_order_nick_text = ItemText(28, 344, self.font_20, 0, '', (102, 51,
                                                                             51), None, 267, -1, 2, 2)
            if self.stage.game.datastore.user_character_progress.case.arrest_order_thief == None:
                arrest_order_thief = self.list_identikit_thieves[self.identikit_image_matrix.index('')].thief
                self.stage.game.datastore.user_character_progress.case.arrest_order_thief = arrest_order_thief
                self.arrest_order_thief_image.set_image(assets.load_image(self.list_identikit_thieves[self.identikit_image_matrix.index('')].thief.identikit_large_image_front))
                arrest_order_name_text.set_text(self.list_identikit_thieves[self.identikit_image_matrix.index('')].thief.name)
                arrest_order_nick_text.set_text(self.list_identikit_thieves[self.identikit_image_matrix.index('')].thief.nickname)
            else:
                arrest_order_thief = self.stage.game.datastore.user_character_progress.case.arrest_order_thief
                arrest_order_thief_img = assets.load_image(arrest_order_thief.identikit_large_image_front)
                self.arrest_order_thief_image.set_image(arrest_order_thief_img)
                arrest_order_name_text.set_text(arrest_order_thief.name)
                arrest_order_nick_text.set_text(arrest_order_thief.nickname)
            self.arrest_order_thief_image.add_event_handler(ItemEvent.CLICK, self.identikit_button_click)
            self.disable_thieves()
            self.identikit_layer.add(self.arrest_order_thief_image)
            self.identikit_layer.add(arrest_order_name_text)
            self.identikit_layer.add(arrest_order_nick_text)
            self.identikit_layer.add(stamp)
            self.identikit_layer.remove(self.sex_left_button)
            self.identikit_layer.remove(self.sex_right_button)
            self.identikit_layer.remove(self.height_left_button)
            self.identikit_layer.remove(self.height_right_button)
            self.identikit_layer.remove(self.hair_left_button)
            self.identikit_layer.remove(self.hair_right_button)
            self.identikit_layer.remove(self.distinctive_left_button)
            self.identikit_layer.remove(self.distinctive_right_button)
            self.identikit_layer.remove(self.arrest_order_button)
            self.arrest_order_box.set_image(self.arrest_order_issued_image)
        return

    def identikit_new_dialog_click(self, item, args):
        if item == self.arrest_order_button and self.arrest_order_is_working:
            self.arrest_order_name_text.set_text(self.list_identikit_thieves[self.identikit_image_matrix.index('')].thief.name)
            self.arrest_order_nick_text.set_text(self.list_identikit_thieves[self.identikit_image_matrix.index('')].thief.nickname)
            self.arrest_order_thief_image.set_image(self.list_identikit_thieves[self.identikit_image_matrix.index('')].identikit_item_image)
            self.set_up_arrest_order_dialog()
            self.obsure_folder_close()
            self.stage.show_dialog(self.arrest_order_layer, self.arrest_order_confirm_handle_event, callback=self.clarify_folder_close)
            self.stage.render()
            self.arrest_order_sound.play()
        elif item == self.arrest_order_dialog_close_button:
            self.stage.render()
            self.click_sound.play()
            self.close_arrest_order()
        elif item == self.thief_dialog_close_button:
            self.stage.render()
            self.click_sound.play()
            self.close_identikit_thief()
        elif item == self.arrest_order_dialog_cancel_button:
            self.stage.render()
            self.click_sound.play()
            self.cancel_arrest_order()
        elif item == self.arrest_order_dialog_accept_button:
            self.stage.render()
            self.click_sound.play()
            self.stage.close_dialog(self.arrest_order_layer)
            self.show_arrest_order_done_dialog()
            self.identikit_arrest_order_sent()
            self.stage.render()
            self.stage.save_progress(False)
        return

    def identikit_thief_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.close_identikit_thief()
        return

    def close_identikit_thief(self):
        self.identikit_thief_image.set_image(None)
        self.identikit_thief_image_side.set_image(None)
        self.stage.close_dialog(self.identikit_thief_layer)
        return

    def arrest_order_confirm_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.cancel_arrest_order()
        return

    def cancel_arrest_order(self):
        self.stage.close_dialog(self.arrest_order_layer)
        return

    def arrest_order_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.close_arrest_order()
        return

    def close_arrest_order(self):
        self.stage.close_dialog(self.arrest_order_layer)
        cp = self.stage.game.datastore.user_character_progress
        if not cp.identikit_help:
            self.obsure_folder_close()
            self.stage.show_help_dialog(101, 1000, call_after_close=self.clarify_folder_close)
            cp.identikit_help = True
        return

    def button_click(self, item, args):
        if item == self.close_button:
            if self.pending_changes_to_save:
                self.stage.save_progress(False)
                self.pending_changes_to_save = False
            self.stage.render()
            self.click_sound.play()
            self.close_folder()
        elif item == self.next_button:
            if self.active_layer == 1:
                self.update_active_layer(2)
        elif item == self.previous_button:
            if self.active_layer == 2:
                self.update_active_layer(1)
        elif item == self.case_button and self.active_layer != CASE and self.active_layer != CASE_EXTENDED:
            self.update_active_layer(CASE)
        elif item == self.identikit_button and self.active_layer != IDENTIKIT:
            self.update_active_layer(IDENTIKIT)
        elif item == self.witness_button and self.active_layer != WITNESS:
            self.update_active_layer(WITNESS)
        return

    def select_witnesses(self):
        if self.active_layer != WITNESS:
            self.update_active_layer(WITNESS)
        return

    def identikit_button_click(self, item, args):
        if self.stage.game.datastore.user_character_progress.case.arrest_order_thief == None:
            if self.identikit_layer.contains(item):
                for folder_thief in self.list_identikit_thieves:
                    if item == folder_thief.identikit_item_image:
                        large_image = assets.load_image(folder_thief.thief.identikit_large_image_front)
                        large_image_side = assets.load_image(folder_thief.thief.identikit_large_image_side)
                        self.identikit_thief_image.set_image(large_image)
                        self.identikit_thief_image_side.set_image(large_image_side)
                        self.identikit_thief_name.set_text(folder_thief.thief.name)
                        self.identikit_thief_nickname.set_text(folder_thief.thief.nickname)
                        self.identikit_thief_age.set_text(folder_thief.thief.age)
                        self.identikit_thief_description.set_text(folder_thief.thief.description)
                        self.obsure_folder_close()
                        self.stage.show_dialog(self.identikit_thief_layer, self.identikit_thief_handle_event, callback=self.clarify_folder_close)
                        self.stage.render()
                        self.popup_sound.play()

        elif item == self.arrest_order_thief_image:
            arrest_order_thief = self.stage.game.datastore.user_character_progress.case.arrest_order_thief
            large_image = assets.load_image(arrest_order_thief.identikit_large_image_front)
            large_image_side = assets.load_image(arrest_order_thief.identikit_large_image_side)
            self.identikit_thief_image.set_image(large_image)
            self.identikit_thief_image_side.set_image(large_image_side)
            self.identikit_thief_name.set_text(arrest_order_thief.name)
            self.identikit_thief_nickname.set_text(arrest_order_thief.nickname)
            self.identikit_thief_age.set_text(arrest_order_thief.age)
            self.identikit_thief_description.set_text(arrest_order_thief.description)
            self.obsure_folder_close()
            self.stage.show_dialog(self.identikit_thief_layer, self.identikit_thief_handle_event, callback=self.clarify_folder_close)
            self.stage.render()
            self.popup_sound.play()
        return

    def witness_button_click(self, item, args):
        if item in self.witness_sets:
            i = self.witness_sets.index(item)
            witnesses = self.stage.game.datastore.user_character_progress.case.list_visited_witnesses
            if i < len(witnesses):
                self.obsure_folder_close()
                self.witness_dialog.show_witness(witnesses[i], self.clarify_folder_close)
                self.stage.render()
                self.popup_sound.play()
        return

    def obsure_folder_close(self):
        self.close_button.set_alpha(80)
        return

    def clarify_folder_close(self):
        self.close_button.set_alpha(255)
        return

    def identikit_arrow_click(self, item, args):
        last_sex_choice = self.selected_sex_feature
        if item == self.sex_left_button or item == self.sex_right_button:
            max = self.list_sex_features.__len__() - 1
            if self.selected_sex_feature > 0 and item == self.sex_left_button:
                self.selected_sex_feature = self.selected_sex_feature - 1
            elif self.selected_sex_feature < max and item == self.sex_right_button:
                self.selected_sex_feature = self.selected_sex_feature + 1
            elif self.selected_sex_feature == 0 and item == self.sex_left_button:
                self.selected_sex_feature = max
            elif self.selected_sex_feature == max and item == self.sex_right_button:
                self.selected_sex_feature = 0
        if item == self.height_left_button or item == self.height_right_button:
            max = self.list_height_features_male.__len__() - 1
            if self.selected_height_feature > 0 and item == self.height_left_button:
                self.selected_height_feature = self.selected_height_feature - 1
            elif self.selected_height_feature < max and item == self.height_right_button:
                self.selected_height_feature = self.selected_height_feature + 1
            elif self.selected_height_feature == 0 and item == self.height_left_button:
                self.selected_height_feature = max
            elif self.selected_height_feature == max and item == self.height_right_button:
                self.selected_height_feature = 0
        if item == self.hair_left_button or item == self.hair_right_button:
            max = self.list_hair_features.__len__() - 1
            if self.selected_hair_feature > 0 and item == self.hair_left_button:
                self.selected_hair_feature = self.selected_hair_feature - 1
            elif self.selected_hair_feature < max and item == self.hair_right_button:
                self.selected_hair_feature = self.selected_hair_feature + 1
            elif self.selected_hair_feature == 0 and item == self.hair_left_button:
                self.selected_hair_feature = max
            elif self.selected_hair_feature == max and item == self.hair_right_button:
                self.selected_hair_feature = 0
        if item == self.distinctive_left_button or item == self.distinctive_right_button:
            max = self.list_distinctive_features.__len__() - 1
            if self.selected_distinctive_feature > 0 and item == self.distinctive_left_button:
                self.selected_distinctive_feature = self.selected_distinctive_feature - 1
            elif self.selected_distinctive_feature < max and item == self.distinctive_right_button:
                self.selected_distinctive_feature = self.selected_distinctive_feature + 1
            elif self.selected_distinctive_feature == 0 and item == self.distinctive_left_button:
                self.selected_distinctive_feature = max
            elif self.selected_distinctive_feature == max and item == self.distinctive_right_button:
                self.selected_distinctive_feature = 0
        self.update_identikit(last_sex_choice)
        self.stage.render()
        self.flip_option_sound.play()
        case = self.stage.game.datastore.user_character_progress.case
        case.list_selected_features = []
        case.list_selected_features.append(self.selected_sex_feature)
        case.list_selected_features.append(self.selected_height_feature)
        case.list_selected_features.append(self.selected_hair_feature)
        case.list_selected_features.append(self.selected_distinctive_feature)
        self.mark_pending_changes_to_save(True)
        return

    def update_identikit(self, last_sex_choice):
        self.identikit_sex_text.set_text(self.list_sex_features[self.selected_sex_feature])
        self.identikit_hair_text.set_text(self.list_hair_features[self.selected_hair_feature])
        self.identikit_distinctive_text.set_text(self.list_distinctive_features[self.selected_distinctive_feature])
        if self.selected_sex_feature == 1 or last_sex_choice == 1 and self.selected_sex_feature == 0 or last_sex_choice == 0 and self.selected_sex_feature == 0:
            self.identikit_height_text.set_text(self.list_height_features_male[self.selected_height_feature])
        elif self.selected_sex_feature == 2 or last_sex_choice == 2 and self.selected_sex_feature == 0:
            self.identikit_height_text.set_text(self.list_height_features_female[self.selected_height_feature])
        case_thief = self.stage.game.datastore.user_character_progress.case.thief
        if self.selected_sex_feature == case_thief.sex and self.selected_height_feature == case_thief.height and self.selected_distinctive_feature == case_thief.distinctive_feature and self.selected_hair_feature == case_thief.hair:
            self._right_identikit_selection = True
        else:
            self._right_identikit_selection = False
        self.update_images()
        return

    def load_witnesses_data(self):
        case = self.stage.game.datastore.user_character_progress.case
        l = case.list_visited_witnesses
        folder_witnesses = case.list_folder_witnesses
        play_sound = True
        i = 0
        for witness in l:
            if not witness.identikit_added:
                witness.identikit_added = True
                folder_witness = self.FolderWitness(witness)
                image = assets.load_image(folder_witness.witness.image)
                folder_witness.image = ItemImage(self.witness_sets[i].get_left() + 8, self.witness_sets[i].get_top() + 9, image, None)
                folder_witness.underline = ItemImage(self.witness_sets[i].get_left() + 8, self.witness_sets[i].get_top() + 78, self.witness_underline, None)
                folder_witness.name = ItemText(self.witness_sets[i].get_left() + 9, self.witness_sets[i].get_top() + 61, self.font_22, 0, folder_witness.witness.name, (157,
                                                                                                                                                                        21,
                                                                                                                                                                        21), None, 200, 30)
                folder_witness.city = ItemText(self.witness_sets[i].get_left() + 9, self.witness_sets[i].get_top() + 84, self.font_18, 10, folder_witness.witness.city.name, (51,
                                                                                                                                                                              51,
                                                                                                                                                                              51), None, 200, 30)
                folder_witness.department = ItemText(self.witness_sets[i].get_left() + 9, self.witness_sets[i].get_top() + 98, self.font_20, 0, folder_witness.witness.department.name, (102,
                                                                                                                                                                                         102,
                                                                                                                                                                                         102), None, 200, 30)
                self.witness_data_layer.add(folder_witness.image)
                self.witness_data_layer.add(folder_witness.underline)
                self.witness_data_layer.add(folder_witness.name)
                self.witness_data_layer.add(folder_witness.department)
                self.witness_data_layer.add(folder_witness.city)
                self.witness_sets[i].set_rollover(self.witness_set_rollover_image, self.rollover_sound)
                if witness not in folder_witnesses:
                    animations.fade_in_item(folder_witness.image)
                    if play_sound:
                        play_sound = False
                        self.stage.render()
                        self.witness_fade_in_sound.play()
                    folder_witnesses.append(witness)
                    self.mark_pending_changes_to_save(False)
            i += 1
            if i >= 3:
                break

        return

    def get_list_identikit(self):
        self.list_identikit_thieves = []
        self.list_identikit_crosses = []
        cross_back = assets.load_image('p0_folder_identikit_suspect_crossed.png')
        thief_rollover = assets.load_image('p0_thieves_small_rollovershadow.png')
        x = 325
        y = 110
        for i in range(3):
            for z in range(3):
                pos = z + i + (i + i)
                folder_thief = self.FolderThief(self.stage.game.datastore.user_character_progress.case.list_thieves[pos])
                image = assets.load_image(folder_thief.thief.identikit_image)
                folder_thief.identikit_item_image = ItemImage(x, y, image, None)
                self.list_identikit_thieves.append(folder_thief)
                self.identikit_layer.add(folder_thief.identikit_item_image)
                cross_image = ItemImage(self.list_identikit_thieves[pos].identikit_item_image.get_left(), self.list_identikit_thieves[pos].identikit_item_image.get_top(), cross_back, None)
                self.list_identikit_crosses.append(cross_image)
                self.list_identikit_thieves[pos].identikit_item_image.add_event_handler(ItemEvent.CLICK, self.identikit_button_click)
                if self.stage.game.datastore.user_character_progress.case.arrest_order_thief == None:
                    self.list_identikit_thieves[pos].identikit_item_image.set_rollover(thief_rollover, self.rollover_sound)
                x += 70

            x = 325
            y += 65

        return

    def update_images(self):
        self.clean_identikit()
        sex = self.selected_sex_feature
        height = self.selected_height_feature
        hair = self.selected_hair_feature
        distinctive_feature = self.selected_distinctive_feature
        for i in range(9):
            if self.list_identikit_thieves[i].thief.sex != sex and sex != 0 or self.list_identikit_thieves[i].thief.height != height and height != 0 or self.list_identikit_thieves[i].thief.hair != hair and hair != 0 or self.list_identikit_thieves[i].thief.distinctive_feature != distinctive_feature and distinctive_feature != 0:
                if not self.identikit_layer.contains(self.list_identikit_crosses[i]):
                    self.identikit_layer.add(self.list_identikit_crosses[i])
                    self.identikit_image_matrix[i] = 'x'

        if self.identikit_image_matrix.count('x') == 8:
            self.arrest_order_box.set_image(self.arrest_order_working_image)
            self.arrest_order_button.set_rollover(self.arrest_order_working_rollover_image, self.rollover_sound, -1, -20)
            self.arrest_order_is_working = True
            pos = self.identikit_image_matrix.index('')
            self.set_circle_outlined_image(pos)
            self.identikit_layer.add(self.circle_outlined_image)
        else:
            self.arrest_order_box.set_image(self.arrest_order_not_working_image)
            self.arrest_order_button.set_rollover(None, None)
            self.arrest_order_is_working = False
        return

    def set_circle_outlined_image(self, position):
        if position == 0 or position == 3 or position == 6:
            self.circle_outlined_image.set_left(325)
        elif position == 1 or position == 4 or position == 7:
            self.circle_outlined_image.set_left(395)
        elif position == 2 or position == 5 or position == 8:
            self.circle_outlined_image.set_left(465)
        if position >= 0 and position <= 2:
            self.circle_outlined_image.set_top(110)
        elif position >= 3 and position <= 5:
            self.circle_outlined_image.set_top(175)
        elif position >= 6 and position <= 8:
            self.circle_outlined_image.set_top(240)
        return

    def clean_identikit(self):
        if self.identikit_layer.contains(self.circle_outlined_image):
            self.identikit_layer.remove(self.circle_outlined_image)
        for item in self.list_identikit_crosses:
            self.identikit_layer.remove(item)

        self.identikit_image_matrix = ["" for x in range(9)]
        return

    def set_up_identikit(self):
        self.set_up_identikit_background()
        self.set_up_identikit_texts()
        self.set_up_identikit_buttons()
        self.load_identikit_data()
        self.set_up_arrest_order_dialog()
        self.identikit_loaded = True
        return

    def set_up_witness(self):
        self.witness_dialog = witness.Witness(self.stage)
        self.set_up_witness_background()
        self.set_up_witness_texts()
        self.set_up_witness_buttons()
        self.witness_loaded = True
        return

    def mark_pending_changes_to_save(self, save_timer):
        self.pending_changes_to_save = True
        if save_timer:
            key = 'save_folder_pending_changes'
            self.stage.stop_timer(key)
            self.stage.start_timer(key, 1000, self.on_save_pending_changes)
        return

    def on_save_pending_changes(self, key, data):
        self.stage.stop_timer(key)
        if self.pending_changes_to_save:
            self.stage.save_progress(False)
            self.pending_changes_to_save = False
        return

    def update_active_layer(self, layer):
        self.clean_screen()
        if self.pending_changes_to_save:
            self.stage.save_progress(False)
            self.pending_changes_to_save = False
        if layer == CASE:
            self.active_layer = CASE
            self.stage.add_layer(self.case_layer)
            self.stage.add_layer(self.case_data_layer)
            self.case_button.set_image(self.case_button_active_image)
            self.case_button.set_rollover_image(None, None)
            self.identikit_button.set_image(self.identikit_button_inactive_image)
            self.identikit_button.set_rollover_image(self.identikit_button_rollover_image, self.rollover_sound)
            self.witness_button.set_image(self.witness_button_inactive_image)
            self.witness_button.set_rollover_image(self.witness_button_rollover_image, self.rollover_sound)
            self.next_button.set_visible(True)
            self.previous_button.set_visible(False)
            self.load_agent_name()
        elif layer == CASE_EXTENDED:
            self.active_layer = CASE_EXTENDED
            self.stage.add_layer(self.case_layer)
            self.stage.add_layer(self.case_extended_layer)
            self.case_button.set_image(self.case_button_active_image)
            self.case_button.set_rollover_image(None, None)
            self.identikit_button.set_image(self.identikit_button_inactive_image)
            self.identikit_button.set_rollover_image(self.identikit_button_rollover_image, self.rollover_sound)
            self.witness_button.set_image(self.witness_button_inactive_image)
            self.witness_button.set_rollover_image(self.witness_button_rollover_image, self.rollover_sound)
            self.next_button.set_visible(False)
            self.previous_button.set_visible(True)
            self.load_case_text()
        elif layer == IDENTIKIT:
            if not self.identikit_loaded:
                self.set_up_identikit()
            self.active_layer = IDENTIKIT
            self.stage.add_layer(self.identikit_layer)
            self.case_button.set_image(self.case_button_inactive_image)
            self.case_button.set_rollover_image(self.case_button_rollover_image, self.rollover_sound)
            self.identikit_button.set_image(self.identikit_button_active_image)
            self.identikit_button.set_rollover_image(None, None)
            self.witness_button.set_image(self.witness_button_inactive_image)
            self.witness_button.set_rollover_image(self.witness_button_rollover_image, self.rollover_sound)
            self.next_button.set_visible(False)
            self.previous_button.set_visible(False)
            case = self.stage.game.datastore.user_character_progress.case
            self.selected_sex_feature = case.list_selected_features[0]
            self.selected_height_feature = case.list_selected_features[1]
            self.selected_hair_feature = case.list_selected_features[2]
            self.selected_distinctive_feature = case.list_selected_features[3]
            self.update_identikit(self.selected_sex_feature)
            if self.stage.game.datastore.user_character_progress.case.arrest_order_thief != None:
                self.identikit_arrest_order_sent()
        elif layer == WITNESS:
            if not self.witness_loaded:
                self.set_up_witness()
            self.active_layer = WITNESS
            self.stage.add_layer(self.witness_layer)
            self.stage.add_layer(self.witness_data_layer)
            self.case_button.set_image(self.case_button_inactive_image)
            self.case_button.set_rollover_image(self.case_button_rollover_image, self.rollover_sound)
            self.identikit_button.set_image(self.identikit_button_inactive_image)
            self.identikit_button.set_rollover_image(self.identikit_button_rollover_image, self.rollover_sound)
            self.witness_button.set_image(self.witness_button_active_image)
            self.witness_button.set_rollover_image(None, None)
            self.next_button.set_visible(False)
            self.previous_button.set_visible(False)
            self.load_witnesses_data()
        self.stage.render()
        self.turn_page_sound.play()
        return

    def disable_identikit_tab(self):
        self.identikit_button.set_rollover_image(None, None)
        self.identikit_button.remove_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def disable_case_tab(self):
        self.case_button.set_rollover_image(None, None)
        self.case_button.remove_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def disable_witness_tab(self):
        self.witness_button.set_rollover_image(None, None)
        self.witness_button.remove_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def disable_close_button(self):
        self.close_button.set_rollover_image(None, None)
        self.close_button.remove_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def disable_previous_button(self):
        self.previous_button.set_rollover_image(None, None)
        self.previous_button.remove_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def enable_identikit_tab(self):
        self.identikit_button.set_rollover_image(self.identikit_button_rollover_image, self.rollover_sound)
        self.identikit_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def enable_case_tab(self):
        self.case_button.set_rollover_image(self.case_button_rollover_image, self.rollover_sound)
        self.case_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def enable_witness_tab(self):
        self.witness_button.set_rollover_image(self.witness_button_rollover_image, self.rollover_sound)
        self.witness_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def enable_close_button(self):
        self.close_button.set_rollover_image(self.close_button_rollover_image, self.rollover_sound)
        self.close_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def enable_previous_button(self):
        self.previous_button.set_rollover_image(self.previous_button_rollover_image, self.rollover_sound)
        self.previous_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def disable_hair_buttons(self):
        self.hair_left_button.set_rollover_image(None, None)
        self.hair_left_button.remove_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.hair_left_button.set_pressed_image(None)
        self.hair_right_button.set_rollover_image(None, None)
        self.hair_right_button.remove_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.hair_right_button.set_pressed_image(None)
        return

    def disable_sex_buttons(self):
        self.sex_left_button.set_rollover_image(None, None)
        self.sex_left_button.remove_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.sex_left_button.set_pressed_image(None)
        self.sex_right_button.set_rollover_image(None, None)
        self.sex_right_button.remove_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.sex_right_button.set_pressed_image(None)
        return

    def disable_distinctive_buttons(self):
        self.distinctive_left_button.set_rollover_image(None, None)
        self.distinctive_left_button.remove_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.distinctive_left_button.set_pressed_image(None)
        self.distinctive_right_button.set_rollover_image(None, None)
        self.distinctive_right_button.remove_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.distinctive_right_button.set_pressed_image(None)
        return

    def disable_height_buttons(self):
        self.height_left_button.set_rollover_image(None, None)
        self.height_left_button.remove_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.height_left_button.set_pressed_image(None)
        self.height_right_button.set_rollover_image(None, None)
        self.height_right_button.remove_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.height_right_button.set_pressed_image(None)
        return

    def enable_hair_buttons(self):
        self.disable_hair_buttons()
        self.hair_left_button.set_rollover_image(self.arrow_left_image_rollover, self.rollover_sound)
        self.hair_left_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.hair_left_button.set_pressed_image(self.arrow_left_image_pressed)
        self.hair_right_button.set_rollover_image(self.arrow_right_image_rollover, self.rollover_sound)
        self.hair_right_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.hair_right_button.set_pressed_image(self.arrow_right_image_pressed)
        return

    def enable_sex_buttons(self):
        self.disable_sex_buttons()
        self.sex_left_button.set_rollover_image(self.arrow_left_image_rollover, self.rollover_sound)
        self.sex_left_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.sex_left_button.set_pressed_image(self.arrow_left_image_pressed)
        self.sex_right_button.set_rollover_image(self.arrow_right_image_rollover, self.rollover_sound)
        self.sex_right_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.sex_right_button.set_pressed_image(self.arrow_right_image_pressed)
        return

    def enable_height_buttons(self):
        self.disable_height_buttons()
        self.height_left_button.set_rollover_image(self.arrow_left_image_rollover, self.rollover_sound)
        self.height_left_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.height_left_button.set_pressed_image(self.arrow_left_image_pressed)
        self.height_right_button.set_rollover_image(self.arrow_right_image_rollover, self.rollover_sound)
        self.height_right_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.height_right_button.set_pressed_image(self.arrow_right_image_pressed)
        return

    def enable_distinctive_buttons(self):
        self.disable_distinctive_buttons()
        self.distinctive_left_button.set_rollover_image(self.arrow_left_image_rollover, self.rollover_sound)
        self.distinctive_left_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.distinctive_left_button.set_pressed_image(self.arrow_left_image_pressed)
        self.distinctive_right_button.set_rollover_image(self.arrow_right_image_rollover, self.rollover_sound)
        self.distinctive_right_button.add_event_handler(ItemEvent.CLICK, self.identikit_arrow_click)
        self.distinctive_right_button.set_pressed_image(self.arrow_right_image_pressed)
        return

    def disable_thieves(self):
        for thief in self.list_identikit_thieves:
            thief.identikit_item_image.remove_event_handler(ItemEvent.CLICK, self.identikit_button_click)
            thief.identikit_item_image.set_rollover(None, None)

        return

    def clean_screen(self):
        if self.active_layer == CASE:
            self.stage.remove_layer(self.case_layer)
            self.stage.remove_layer(self.case_data_layer)
        elif self.active_layer == CASE_EXTENDED:
            self.stage.remove_layer(self.case_layer)
            self.stage.remove_layer(self.case_extended_layer)
        elif self.active_layer == IDENTIKIT:
            self.stage.remove_layer(self.identikit_layer)
        elif self.active_layer == WITNESS:
            self.stage.remove_layer(self.witness_layer)
            self.stage.remove_layer(self.witness_data_layer)
        return

    def add_start_layer(self, start_page=CASE):
        self.stage.add_layer(self.folder_back_layer)
        self.update_active_layer(start_page)
        return

    class FolderThief:

        def __init__(self, thief):
            self.thief = thief
            self.identikit_item_image = ''
            return

    class FolderWitness:

        def __init__(self, witness):
            self.witness = witness
            self.image = ''
            self.name = ''
            self.location = ''
            self.department = ''
            return


