from framework import assets, text, animations
from framework.stage import *
from game.data import datamodel
import random
from . import characterid
MEDALS_DATA = {'artigas': (97, 123, 'ARTIGAS', 1), 
   'canelones': (143, 123, 'CANELONES', 3), 
   'cerrolargo': (190, 123, 'CERRO LARGO', None), 
   'colonia': (236, 123, 'COLONIA', 3), 
   'durazno': (282, 123, 'DURAZNO', None), 
   'flores': (328, 123, 'FLORES', 3), 
   'florida': (375, 123, 'FLORIDA', None), 
   'lavalleja': (421, 123, 'LAVALLEJA', 1), 
   'maldonado': (467, 123, 'MALDONADO', 2), 
   'montevideo': (76, 202, 'MONTEVIDEO', 2), 
   'paysandu': (123, 202, 'PAYSANDÚ', 2), 
   'rionegro': (170, 202, 'RÍO NEGRO', 2), 
   'rivera': (218, 202, 'RIVERA', 1), 
   'rocha': (265, 202, 'ROCHA', 1), 
   'salto': (312, 202, 'SALTO', None), 
   'sanjose': (359, 202, 'SAN JOSÉ', 1), 
   'soriano': (407, 202, 'SORIANO', 3), 
   'tacuarembo': (454, 202, 'TACUAREMBÓ', 2), 
   'treintaytres': (501, 202, 'TREINTA Y TRES', 2)}

class Merits:

    def __init__(self, stage):
        self.stage = stage
        self.main_layer = Layer()
        self.medals_layer = None
        self.highscores_layer = None
        self.medal_popup_layer = None
        self.rollover_sound = self.stage.rollover_sound
        self.click_sound = self.stage.click_sound
        self.common_loaded = False
        return

    def show_merits(self, show_empty_dialog=True):
        self.stage.show_dialog(self.main_layer, self.merits_handle_event)
        if not show_empty_dialog:
            self.blind_show_merits_callback(self.main_layer, True)
        else:
            self.stage.blind_dialog(self.main_layer, animations.BlindDirection.SHOW_DOWN, True, [], self.blind_show_merits_callback)
        return

    def close_merits(self):
        self.stage.blind_dialog(self.main_layer, animations.BlindDirection.HIDE_UP, True, [], self.blind_main_back_callback)
        return

    def merits_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.close_merits()
        return

    def blind_show_merits_callback(self, layer, blind_background=False):
        self.set_up_common()
        self.set_up_main()
        self.stage.blind_dialog(self.main_layer, animations.BlindDirection.SHOW_DOWN, blind_background, [])
        return

    def set_up_common(self):
        if not self.common_loaded:
            self.back_standby_image = assets.load_image('p0_merits_backbutton_standby.png')
            self.back_rollover_image = assets.load_image('p0_merits_backbutton_rollover.png')
            self.common_loaded = True
        return

    def set_up_main(self):
        character = self.stage.game.datastore.user_character
        character_progress = self.stage.game.datastore.user_character_progress
        font_11 = assets.load_font('evilgeniusbb_bld.ttf', 11)
        font_16 = assets.load_font('evilgeniusbb_reg.ttf', 16)
        font_20 = assets.load_font('turkey.ttf', 20)
        font_42 = assets.load_font('turkey.ttf', 42)
        background_image = assets.load_image('p0_merits_main_background.jpg')
        background_item = ItemImage(0, 0, background_image)
        self.main_layer.add(background_item)
        back_item = ItemImage(258, 399, self.back_standby_image)
        back_item.set_rollover_image(self.back_rollover_image, self.rollover_sound)
        back_item.add_event_handler(ItemEvent.CLICK, self.main_back_click)
        self.main_layer.add(back_item)
        score_text = text.format_number(character_progress.score)
        self.add_text_with_shadow(self.main_layer, 341, 11, font_42, score_text, (255,
                                                                                  212,
                                                                                  12), 157, 65, 2, 1, -2, 3)
        self.characterid = characterid.CharacterId()
        self.characterid.set_up_id(self.main_layer, character.charinfo, 120, 87, False)
        resolved_cases = character_progress.resolved_cases
        resolved_cases_text = text.format_number(resolved_cases)
        self.add_text_with_shadow(self.main_layer, 359, 335, font_20, resolved_cases_text, (255,
                                                                                            212,
                                                                                            12), 50, 30, 1, 1, -2, 3)
        if character_progress.range.next_range_cases != None:
            next_promotion_cases = character_progress.range.next_range_cases - resolved_cases
            next_promotion_cases_text = text.format_number(next_promotion_cases)
            self.add_text_with_shadow(self.main_layer, 432, 363, font_20, next_promotion_cases_text, (255,
                                                                                                      212,
                                                                                                      12), 50, 30, 1, 1, -2, 3)
        medals_normal_image = assets.load_image('p0_merits_main_btn_medals_normal.png')
        medals_rollover_image = assets.load_image('p0_merits_main_btn_medals_rollover.png')
        medals_item = ItemImage(13, 291, medals_normal_image, None, True)
        medals_item.set_rollover_image(medals_rollover_image, self.rollover_sound)
        medals_item.add_event_handler(ItemEvent.CLICK, self.medals_click)
        self.main_layer.add(medals_item)
        highscores_normal_image = assets.load_image('p0_merits_main_btn_highscore_normal.png')
        highscores_rollover_image = assets.load_image('p0_merits_main_btn_highscore_rollover.png')
        highscores_item = ItemImage(458, 293, highscores_normal_image, None, True)
        highscores_item.set_rollover_image(highscores_rollover_image, self.rollover_sound)
        highscores_item.add_event_handler(ItemEvent.CLICK, self.highscores_click)
        self.main_layer.add(highscores_item)
        return

    def set_up_medals(self):
        font_14 = assets.load_font('turkey.ttf', 14)
        font_18 = assets.load_font('turkey.ttf', 18)
        self.medals_layer = Layer()
        background_image = assets.load_image('p0_merits_medals_background.jpg')
        background_item = ItemImage(0, 0, background_image)
        self.medals_layer.add(background_item)
        back_item = ItemImage(258, 399, self.back_standby_image)
        back_item.set_rollover_image(self.back_rollover_image, self.rollover_sound)
        back_item.add_event_handler(ItemEvent.CLICK, self.medals_back_click)
        self.medals_layer.add(back_item)
        self.generic_backglow_image = assets.load_image('p0_merits_medals_backglow_generic.png')
        self.medal_rollover_item = ItemImage(0, 0, None)
        self.medal_rollover_item.set_visible(False)
        self.medals_layer.add(self.medal_rollover_item)
        self.medal_text_items = self.add_text_with_shadow(self.medals_layer, 223, 85, font_14, '', (252,
                                                                                                    193,
                                                                                                    45), 155, 20, 2, 1, -1, 2)
        self.medal_text_items[0].set_visible(False)
        self.medal_text_items[1].set_visible(False)
        character_progress = self.stage.game.datastore.user_character_progress
        medal_uy = None
        for medal in character_progress.medals:
            if medal.name == 'uy':
                medal_uy = medal
            else:
                self.add_tiny_medal(medal.name, medal.count, font_18)

        if medal_uy != None:
            count = medal_uy.count
        else:
            count = 0
        self.add_bottom_medal('uy', 'URUGUAY', count, 271, 287, -26, -21, 5, -4, 211, 53, font_18)
        return

    def add_tiny_medal(self, name, count, font):
        image = assets.load_image('p0_merits_medals_tiny_' + name + '.png')
        data = MEDALS_DATA[name]
        item = ItemImage(data[0], data[1], image)
        item.add_event_handler(ItemEvent.MOUSE_ENTER, self.medal_enter)
        item.add_event_handler(ItemEvent.MOUSE_LEAVE, self.medal_leave)
        item.add_event_handler(ItemEvent.CLICK, self.medal_click)
        item.touch_preview = True
        self.medals_layer.add(item)
        if count > 1:
            self.add_text_with_shadow(self.medals_layer, data[0] + 1, data[1] - 3, font, str(count), (254,
                                                                                                      227,
                                                                                                      0), 35, 28, 3, 1, -1, 3, 255)
        item.medal_department = True
        item.medal_name = name
        item.medal_text = data[2]
        item.medal_backglow = (-22, -21)
        item.medal_backglow_image = self.generic_backglow_image
        item.ribbon = data[3]
        return

    def add_bottom_medal(self, name, text, count, medal_x, medal_y, backglow_x, backglow_y, count_dx, count_dy, big_x, big_y, font):
        if count != 0:
            medal_image = assets.load_image('p0_merits_medals_tiny_' + name + '.png')
            backglow_image = assets.load_image('p0_merits_medals_backglow_' + name + '.png')
            item = ItemImage(medal_x, medal_y, medal_image)
            item.add_event_handler(ItemEvent.MOUSE_ENTER, self.medal_enter)
            item.add_event_handler(ItemEvent.MOUSE_LEAVE, self.medal_leave)
            item.add_event_handler(ItemEvent.CLICK, self.medal_click)
            item.touch_preview = True
            self.medals_layer.add(item)
            if count > 1:
                self.add_text_with_shadow(self.medals_layer, medal_x + count_dx, medal_y + count_dy, font, str(count), (254,
                                                                                                                        227,
                                                                                                                        0), 45, 28, 3, 1, -1, 3, 255)
            item.medal_department = False
            item.medal_name = name
            item.medal_text = text
            item.medal_backglow = (backglow_x, backglow_y)
            item.medal_backglow_image = backglow_image
            item.medal_big_pos = (big_x, big_y)
        return

    def medal_enter(self, item, args):
        self.stage.render()
        self.rollover_sound.stop()
        self.rollover_sound.play()
        self.medal_rollover_item.set_image(item.medal_backglow_image)
        self.medal_rollover_item.set_left(item.get_left() + item.medal_backglow[0])
        self.medal_rollover_item.set_top(item.get_top() + item.medal_backglow[1])
        self.medal_rollover_item.set_visible(True)
        self.medal_text_items[0].set_text(item.medal_text)
        self.medal_text_items[1].set_text(item.medal_text)
        self.medal_text_items[0].set_visible(True)
        self.medal_text_items[1].set_visible(True)
        return

    def medal_leave(self, item, args):
        self.medal_rollover_item.set_visible(False)
        self.medal_text_items[0].set_visible(False)
        self.medal_text_items[1].set_visible(False)
        return

    def medal_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        if self.medal_popup_layer == None:
            self.set_up_medal_popup()
        self.set_big_medal(item)
        self.stage.show_dialog(self.medal_popup_layer, self.medal_popup_handle_event, (0,
                                                                                       0,
                                                                                       0,
                                                                                       150))
        self.stage.blind_dialog(self.medal_popup_layer, animations.BlindDirection.SHOW_DOWN, True, [])
        return

    def set_up_medal_popup(self):
        font_24 = assets.load_font('turkey.ttf', 24)
        self.medal_popup_layer = Layer()
        back_center_image = assets.load_image('p0_merits_medals_popup_back_center.jpg')
        back_center_item = ItemImage(153, 131, back_center_image)
        self.medal_popup_layer.add(back_center_item)
        back_top_image = assets.load_image('p0_merits_medals_popup_back_top.png')
        back_top_item = ItemImage(105, 69, back_top_image)
        self.medal_popup_layer.add(back_top_item)
        back_bottom_image = assets.load_image('p0_merits_medals_popup_back_bottom.png')
        back_bottom_item = ItemImage(73, 341, back_bottom_image)
        self.medal_popup_layer.add(back_bottom_item)
        back_left_image = assets.load_image('p0_merits_medals_popup_back_left.png')
        back_left_item = ItemImage(79, 131, back_left_image)
        self.medal_popup_layer.add(back_left_item)
        back_right_image = assets.load_image('p0_merits_medals_popup_back_right.png')
        back_right_item = ItemImage(451, 131, back_right_image)
        self.medal_popup_layer.add(back_right_item)
        back_item = ItemImage(258, 399, self.back_standby_image)
        back_item.set_rollover_image(self.back_rollover_image, self.rollover_sound)
        back_item.add_event_handler(ItemEvent.CLICK, self.medal_popup_back_click)
        self.medal_popup_layer.add(back_item)
        self.ribbon_item = ItemImage(246, 66, None)
        self.medal_popup_layer.add(self.ribbon_item)
        base_image = assets.load_image('p0_merits_medals_big_genericbase.png')
        self.base_item = ItemImage(243, 168, base_image)
        self.medal_popup_layer.add(self.base_item)
        self.tab_item = ItemImage(265, 180, None)
        self.medal_popup_layer.add(self.tab_item)
        self.big_medal_item = ItemImage(0, 0, None)
        self.medal_popup_layer.add(self.big_medal_item)
        self.big_name_items = self.add_text_with_shadow(self.medal_popup_layer, 204, 284, font_24, '', (252,
                                                                                                        193,
                                                                                                        45), 195, 35, 2, 1, -2, 3, 255)
        return

    def set_big_medal(self, item):
        self.big_name_items[0].set_text(item.medal_text)
        self.big_name_items[1].set_text(item.medal_text)
        if not item.medal_department:
            big_medal_image = assets.load_image('p0_merits_medals_big_' + item.medal_name + '.png')
            self.big_medal_item.set_left(item.medal_big_pos[0])
            self.big_medal_item.set_top(item.medal_big_pos[1])
            self.big_medal_item.set_image(big_medal_image)
            self.big_medal_item.set_visible(True)
            self.ribbon_item.set_visible(False)
            self.base_item.set_visible(False)
            self.tab_item.set_visible(False)
        else:
            self.big_medal_item.set_visible(False)
            if item.ribbon == None:
                ribbon_image = assets.load_image('p0_merits_medals_big_ribbon_' + item.medal_name + '.png')
            else:
                ribbon_image = assets.load_image('p0_merits_medals_big_ribbon_' + str(item.ribbon) + '.png')
            self.ribbon_item.set_image(ribbon_image)
            self.ribbon_item.set_visible(True)
            self.base_item.set_visible(True)
            tab_image = assets.load_image('p0_merits_medals_tab_' + item.medal_name + '.jpg')
            self.tab_item.set_image(tab_image)
            self.tab_item.set_visible(True)
        return

    def set_up_highscores(self):
        self.highscores_layer = Layer()
        self.highscore_font = assets.load_font('turkey.ttf', 17)
        background_image = assets.load_image('p0_merits_highscores_background.jpg')
        background_item = ItemImage(0, 0, background_image)
        self.highscores_layer.add(background_item)
        self.highscores_left_up_image = assets.load_image('p0_merits_highscores_button_up.png')
        self.highscores_left_rollover_image = assets.load_image('p0_merits_highscores_button_rollover.png')
        self.highscores_left_center_image = assets.load_image('p0_merits_highscores_button_center.png')
        self.highscores_left_down_image = assets.load_image('p0_merits_highscores_button_down.png')
        self.highscores_right_up_image = self.highscores_left_up_image.flip_h_copy()
        self.highscores_right_rollover_image = self.highscores_left_rollover_image.flip_h_copy()
        self.highscores_right_center_image = self.highscores_left_center_image.flip_h_copy()
        self.highscores_right_down_image = self.highscores_left_down_image.flip_h_copy()
        self.highscores_left_button = ItemImage(398, 80, self.highscores_left_up_image)
        self.highscores_left_button.add_event_handler(ItemEvent.CLICK, self.highscores_left_click)
        self.highscores_left_button.add_event_handler(ItemEvent.MOUSE_ENTER, self.highscores_left_enter)
        self.highscores_left_button.add_event_handler(ItemEvent.MOUSE_LEAVE, self.highscores_left_leave)
        self.highscores_left_state = 0
        self.highscores_layer.add(self.highscores_left_button)
        self.highscores_right_button = ItemImage(502, 80, self.highscores_right_up_image)
        self.highscores_right_button.add_event_handler(ItemEvent.CLICK, self.highscores_right_click)
        self.highscores_right_button.add_event_handler(ItemEvent.MOUSE_ENTER, self.highscores_right_enter)
        self.highscores_right_button.add_event_handler(ItemEvent.MOUSE_LEAVE, self.highscores_right_leave)
        self.highscores_right_state = 0
        self.highscores_layer.add(self.highscores_right_button)
        self.highscores_labels = []
        self.highscores_label_index = 0
        total_image = assets.load_image('p0_merits_highscores_label_total.png')
        self.highscores_labels.append((total_image, 'total'))
        gardener_image = assets.load_image('p0_merits_highscores_label_gardener.png')
        self.highscores_labels.append((gardener_image, 'gardener'))
        librarian_image = assets.load_image('p0_merits_highscores_label_librarian.png')
        self.highscores_labels.append((librarian_image, 'librarian'))
        puzzle_image = assets.load_image('p0_merits_highscores_label_puzzle.png')
        self.highscores_labels.append((puzzle_image, 'bricklayer'))
        shoptender_image = assets.load_image('p0_merits_highscores_label_shoptender.png')
        self.highscores_labels.append((shoptender_image, 'shoptender'))
        self.highscore_label_item = ItemImage(433, 74, self.highscores_labels[0][0])
        self.highscores_layer.add(self.highscore_label_item)
        self.highscores_items = []
        self.load_highscores()
        back_item = ItemImage(258, 399, self.back_standby_image)
        back_item.set_rollover_image(self.back_rollover_image, self.rollover_sound)
        back_item.add_event_handler(ItemEvent.CLICK, self.highscores_back_click)
        self.highscores_layer.add(back_item)
        return

    def load_highscores(self):
        datastore = self.stage.game.datastore
        highscores = datastore.get_highscores()
        characters = []
        category = self.highscores_labels[self.highscores_label_index][1]
        if highscores != None and category in highscores:
            characters = highscores[category]
        for i in self.highscores_items:
            self.highscores_layer.remove(i)

        y = 120
        if len(characters) > 10:
            characters = characters[:10]
        for c in characters:
            (i1, i2) = self.add_text_with_shadow(self.highscores_layer, 66, y, self.highscore_font, c.name.upper(), (255,
                                                                                                                     212,
                                                                                                                     12), 350, 24, 1, 2, 1, 3)
            self.highscores_items.append(i1)
            self.highscores_items.append(i2)
            score_text = text.format_number(c.score)
            (i1, i2) = self.add_text_with_shadow(self.highscores_layer, 410, y, self.highscore_font, score_text, (255,
                                                                                                                  212,
                                                                                                                  12), 85, 24, 3, 2, 1, 3)
            self.highscores_items.append(i1)
            self.highscores_items.append(i2)
            y += 25

        return

    def highscores_left_click(self, item, args):
        self.start_left_down()
        self.stage.capture_leftmousedown(item, self.highscores_left_mousecapture)
        return

    def start_left_down(self):
        self.highscores_left_state = 2
        self.highscores_left_button.set_image(self.highscores_left_center_image)
        self.stage.stop_timer('highscores_left_down')
        self.stage.start_timer('highscores_left_down', 50, self.show_left_down)
        return

    def show_left_down(self, key, data):
        self.stage.stop_timer('highscores_left_down')
        if self.highscores_left_state == 2:
            self.highscores_left_button.set_image(self.highscores_left_down_image)
        return

    def highscores_left_enter(self, item, args):
        self.stage.render()
        self.rollover_sound.play()
        if self.highscores_left_state == 0:
            self.highscores_left_button.set_image(self.highscores_left_rollover_image)
        else:
            self.start_left_down()
        return

    def highscores_left_leave(self, item, args):
        if self.highscores_left_state == 0:
            self.highscores_left_button.set_image(self.highscores_left_up_image)
        else:
            self.highscores_left_state = 1
            self.highscores_left_button.set_image(self.highscores_left_up_image)
        return

    def highscores_left_mousecapture(self, args, released):
        if released:
            self.highscores_left_state = 0
            if self.stage.get_over_item() == self.highscores_left_button:
                self.stage.render()
                self.click_sound.play()
                if self.highscores_label_index == 0:
                    self.highscores_label_index = len(self.highscores_labels) - 1
                else:
                    self.highscores_label_index -= 1
                self.highscore_label_item.set_image(self.highscores_labels[self.highscores_label_index][0])
                self.load_highscores()
                self.highscores_left_button.set_image(self.highscores_left_rollover_image)
        return

    def highscores_right_click(self, item, args):
        self.start_right_down()
        self.stage.capture_leftmousedown(item, self.highscores_right_mousecapture)
        return

    def start_right_down(self):
        self.highscores_right_state = 2
        self.highscores_right_button.set_image(self.highscores_right_center_image)
        self.stage.stop_timer('highscores_right_down')
        self.stage.start_timer('highscores_right_down', 50, self.show_right_down)
        return

    def show_right_down(self, key, data):
        self.stage.stop_timer('highscores_right_down')
        if self.highscores_right_state == 2:
            self.highscores_right_button.set_image(self.highscores_right_down_image)
        return

    def highscores_right_enter(self, item, args):
        self.stage.render()
        self.rollover_sound.play()
        if self.highscores_right_state == 0:
            self.highscores_right_button.set_image(self.highscores_right_rollover_image)
        else:
            self.start_right_down()
        return

    def highscores_right_leave(self, item, args):
        if self.highscores_right_state == 0:
            self.highscores_right_button.set_image(self.highscores_right_up_image)
        else:
            self.highscores_right_state = 1
            self.highscores_right_button.set_image(self.highscores_right_up_image)
        return

    def highscores_right_mousecapture(self, args, released):
        if released:
            self.highscores_right_state = 0
            if self.stage.get_over_item() == self.highscores_right_button:
                self.stage.render()
                self.click_sound.play()
                if self.highscores_label_index == len(self.highscores_labels) - 1:
                    self.highscores_label_index = 0
                else:
                    self.highscores_label_index += 1
                self.highscore_label_item.set_image(self.highscores_labels[self.highscores_label_index][0])
                self.load_highscores()
                self.highscores_right_button.set_image(self.highscores_right_rollover_image)
        return

    def add_text_with_shadow(self, layer, left, top, font, text, color, width, height, h_align, v_align, shadow_dx, shadow_dy, alpha=153):
        shadow_item = ItemText(left + shadow_dx, top + shadow_dy, font, 0, text, (0,
                                                                                  0,
                                                                                  0), None, width, height, h_align, v_align)
        shadow_item.set_alpha(alpha)
        layer.add(shadow_item)
        text_item = ItemText(left, top, font, 0, text, color, None, width, height, h_align, v_align)
        layer.add(text_item)
        return (
         text_item, shadow_item)

    def medals_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        if self.medals_layer == None:
            self.set_up_medals()
        self.stage.show_dialog(self.medals_layer, self.medals_handle_event, None)
        self.stage.blind_dialog(self.medals_layer, animations.BlindDirection.SHOW_DOWN, True, [])
        return

    def medals_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.close_medals()
        return

    def close_medals(self):
        self.stage.blind_dialog(self.medals_layer, animations.BlindDirection.HIDE_UP, True, [], self.blind_medals_back_callback)
        return

    def highscores_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.show_highscores()
        return

    def show_highscores(self):
        if self.highscores_layer == None:
            self.set_up_common()
            self.set_up_highscores()
        self.load_highscores()
        self.stage.show_dialog(self.highscores_layer, self.highscores_handle_event, None)
        self.stage.blind_dialog(self.highscores_layer, animations.BlindDirection.SHOW_DOWN, True, [])
        return

    def highscores_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.close_highscores()
        return

    def close_highscores(self):
        self.stage.blind_dialog(self.highscores_layer, animations.BlindDirection.HIDE_UP, True, [], self.blind_highscores_back_callback)
        return

    def main_back_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.close_merits()
        return

    def blind_main_back_callback(self, layer):
        self.stage.close_dialog(self.main_layer)
        return

    def medals_back_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.close_medals()
        return

    def blind_medals_back_callback(self, layer):
        self.stage.close_dialog(self.medals_layer)
        return

    def medal_popup_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.close_medal_popup()
        return

    def medal_popup_back_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.close_medal_popup()
        return

    def close_medal_popup(self):
        self.stage.blind_dialog(self.medal_popup_layer, animations.BlindDirection.HIDE_UP, True, [], self.blind_medal_popup_back_callback)
        return

    def blind_medal_popup_back_callback(self, layer):
        self.stage.close_dialog(self.medal_popup_layer)
        return

    def highscores_back_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.close_highscores()
        return

    def blind_highscores_back_callback(self, layer):
        self.stage.close_dialog(self.highscores_layer)
        return


