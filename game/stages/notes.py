from framework.stage import *
from framework import assets, animations
import random, functools
LETTER_ROLLOVER_TIMER_KEY = 'show_note_letter_rollover'

class Notes(Item):

    def __init__(self, stage):
        self.stage = stage
        self.layer = Layer()
        self.popup_layer = None
        self.selected_letter = None
        self.page_items = []
        self.pending_changes_to_save = False
        self.last_hover_show = None
        self.line_font = assets.load_font('gapstown.ttf', 22)
        self.click_sound = stage.click_sound
        self.rollover_sound = stage.rollover_sound
        self.popup_sound = stage.witness_popup_sound
        self.notes_close_sound = assets.load_sound('GUI_Notes_Close.ogg')
        self.turn_page_sound = assets.load_sound('GUI_Turn_Page.ogg')
        self.note_fade_in_sound = assets.load_sound('fade.ogg')
        self.set_up()
        return

    def close_notes(self):
        self.stage.close_dialog(self.layer)
        return

    def select_first_page(self):
        self.select_letter(self.letters_data[0])
        return

    def set_letters_data(self):
        self.letters_data = [['A', 150, 5, None, 143, 2, True, 152, 13],
         ['B', 174, 5, None, 167, 2, True, 176, 13],
         ['C', 200, 5, None, 193, 2, True, 203, 13],
         ['D', 225, 5, None, 218, 2, True, 227, 13],
         ['E', 249, 5, None, 242, 2, True, 251, 13],
         ['F', 271, 5, None, 265, 2, True, 273, 13],
         ['G', 294, 5, None, 286, 2, True, 295, 13],
         ['H', 317, 5, None, 310, 2, True, 319, 13],
         ['I', 338, 5, None, 332, 2, True, 340, 13],
         ['J', 359, 5, None, 353, 2, True, 363, 13],
         ['K', 381, 5, None, 374, 2, True, 383, 13],
         ['L', 402, 5, None, 395, 2, True, 404, 13],
         ['M', 119, 31, None, 110, 26, True, 120, 37],
         ['N', 143, 31, None, 135, 26, True, 144, 37],
         ['Ñ', 165, 31, None, 156, 26, True, 165, 37],
         ['O', 187, 31, None, 179, 26, True, 188, 37],
         ['P', 210, 31, None, 202, 26, True, 210, 37],
         ['Q', 233, 31, None, 225, 26, True, 233, 37],
         ['R', 257, 31, None, 249, 26, True, 258, 37],
         ['S', 282, 31, None, 274, 26, True, 283, 37],
         ['T', 305, 31, None, 297, 26, True, 306, 37],
         ['U', 328, 31, None, 320, 26, True, 329, 37],
         ['V', 351, 31, None, 343, 26, True, 351, 37],
         ['W', 373, 31, None, 365, 26, True, 373, 37],
         ['X', 398, 31, None, 391, 26, True, 399, 37],
         ['Y', 418, 31, None, 410, 26, True, 419, 37],
         ['Z', 441, 31, None, 432, 26, True, 442, 37]]
        return

    def set_up(self):
        self.set_letters_data()
        self.set_background()
        self.set_up_menu_buttons()
        self.set_up_letters()
        self.set_up_new_notes()
        self.set_up_page()
        return

    def set_background(self):
        background_center_image = assets.load_image('p0_notes_center.jpg')
        background_center = ItemImage(43, 61, background_center_image, None)
        self.layer.add(background_center)
        background_top_image = assets.load_image('p0_notes_top.png')
        background_top = ItemImage(15, 31, background_top_image, None)
        self.layer.add(background_top)
        background_bottom_image = assets.load_image('p0_notes_bottom.png')
        background_bottom = ItemImage(22, 421, background_bottom_image, None)
        self.layer.add(background_bottom)
        background_left_image = assets.load_image('p0_notes_left.png')
        background_left = ItemImage(2, 61, background_left_image, None)
        self.layer.add(background_left)
        background_right_image = assets.load_image('p0_notes_right.png')
        background_right = ItemImage(545, 61, background_right_image, None)
        self.layer.add(background_right)
        return

    def set_up_menu_buttons(self):
        self.close_button_image = assets.load_image('p0_button_close.png')
        self.close_button_image_rollover = assets.load_image('p0_button_close_rollover.png')
        self.next_button_image = assets.load_image('p0_button_next_active.png')
        self.next_button_image_rollover = assets.load_image('p0_button_next_rollover.png')
        self.previous_button_image = assets.load_image('p0_button_previous_active.png')
        self.previous_button_image_rollover = assets.load_image('p0_button_previous_rollover.png')
        self.close_button = ItemImage(275, 392, self.close_button_image, None)
        self.close_button.set_rollover_image(self.close_button_image_rollover, self.rollover_sound)
        self.next_button = ItemImage(305, 392, self.next_button_image, None)
        self.next_button.set_rollover_image(self.next_button_image_rollover, self.rollover_sound)
        self.previous_button = ItemImage(245, 392, self.previous_button_image, None)
        self.previous_button.set_rollover_image(self.previous_button_image_rollover, self.rollover_sound)
        self.close_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.next_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.previous_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.layer.add(self.close_button)
        self.layer.add(self.next_button)
        self.layer.add(self.previous_button)
        return

    def set_up_letters(self):
        menu_back_image = assets.load_image('p0_notes_menuback.png')
        self.menu_back = ItemImage(101, 5, menu_back_image, None)
        self.menu_back.add_event_handler(ItemEvent.CLICK, self.letters_click)
        self.menu_back.add_event_handler(ItemEvent.MOUSE_MOVE, self.letters_mousemove)
        self.menu_back.add_event_handler(ItemEvent.MOUSE_LEAVE, self.letters_leave)
        self.layer.add(self.menu_back)
        letter_hover_image = assets.load_image('p0_notes_menuhover.png')
        self.letter_hover = ItemImage(101, 5, letter_hover_image, None)
        self.letter_hover.set_visible(False)
        self.layer.add(self.letter_hover)
        letter_selected_top_image = assets.load_image('p0_notes_menuselected_top.png')
        self.letter_selected_top = ItemImage(101, 5, letter_selected_top_image, None)
        self.letter_selected_top.set_visible(False)
        self.layer.add(self.letter_selected_top)
        letter_selected_bottom_image = assets.load_image('p0_notes_menuselected_bottom.png')
        self.letter_selected_bottom = ItemImage(101, 5, letter_selected_bottom_image, None)
        self.letter_selected_bottom.set_visible(False)
        self.layer.add(self.letter_selected_bottom)
        letters = []
        notes = self.stage.game.datastore.user_character_progress.notes
        for note in notes:
            letter = self.get_note_letter(note)
            if letter not in letters:
                letters.append(letter)

        for letter_data in self.letters_data:
            if letter_data[0] in letters:
                color = 'red'
            else:
                color = 'grey'
            letter_char = self.get_letter_image_char(letter_data[0])
            image_name = 'p0_notes_menuwords_' + color + '_' + letter_char + '.png'
            letter_image = assets.load_image(image_name)
            item = ItemImage(letter_data[7], letter_data[8], letter_image)
            self.layer.add(item)

        return

    def set_up_new_notes(self):
        new_letters = []
        index = self.layer.index_of(self.letter_hover) + 1
        new_notes = self.stage.game.datastore.user_character_progress.new_notes
        for note in new_notes:
            letter = self.get_note_letter(note)
            if letter not in new_letters:
                new_letters.append(letter)

        self.new_notes_letters = {}
        if len(new_letters) > 0:
            letter_selected_image = assets.load_image('p0_notes_menuselected.png')
            new_letters.sort()
            for letter in new_letters:
                letter_data = None
                for l in self.letters_data:
                    if l[0] == letter:
                        letter_data = l
                        break

                item = ItemImage(letter_data[1] - 5, letter_data[2] + 3, letter_selected_image)
                self.layer.add(item, index + 1)
                index += 1
                self.new_notes_letters[letter] = item

        return

    def set_up_page(self):
        headerline_image = assets.load_image('p0_notes_headerline.jpg')
        self.headerline = ItemImage(66, 69, headerline_image)
        self.layer.add(self.headerline)
        self.dot_image = assets.load_image('p0_notes_dot.png')
        self.item_hoversmall_image = assets.load_image('p0_notes_hoversmall.png')
        self.item_hoverbig_image = assets.load_image('p0_notes_hoverbig.png')
        return

    def set_up_popup_layer(self):
        self.popup_layer = Layer()
        background_image = assets.load_image('p0_notes_popupbkg.png')
        background = ItemImage(69, 21, background_image)
        self.popup_layer.add(background)
        font24 = assets.load_font('powdrft_.ttf', 24)
        font20 = assets.load_font('powdrft_.ttf', 20)
        self.popup_title = ItemText(106, 50, font24, 18, '', (157, 21, 21), None, 320, 37)
        self.popup_layer.add(self.popup_title)
        self.popup_subtitle1 = ItemText(106, 91, font20, 14, '', (51, 51, 51), None, 320, 18)
        self.popup_layer.add(self.popup_subtitle1)
        self.popup_subtitle2 = ItemText(106, 108, font20, 14, '', (102, 102, 102), None, 320, 18)
        self.popup_layer.add(self.popup_subtitle2)
        self.popup_description = ItemText(106, 158, font20, 16, '', (0, 0, 0), None, 380, 220)
        self.popup_layer.add(self.popup_description)
        close_button_image = assets.load_image('btn_testigo_x_normal.png')
        close_button_image_rollover = assets.load_image('btn_testigo_x_rollover.png')
        close_button = ItemImage(483, 40, close_button_image, None, True)
        close_button.set_rollover(close_button_image_rollover, self.rollover_sound)
        close_button.add_event_handler(ItemEvent.CLICK, self.popup_close_click)
        self.popup_layer.add(close_button)
        return

    def button_click(self, item, args):
        if item == self.close_button:
            self.stage.render()
            self.notes_close_sound.play()
            if self.pending_changes_to_save:
                self.stage.save_progress(False)
                self.pending_changes_to_save = False
            self.close_notes()
        if item == self.next_button:
            has_items = self.load_letter_page(self.current_page + 1)[0]
            if not has_items:
                index = self.letters_data.index(self.selected_letter)
                if index + 1 < len(self.letters_data):
                    self.select_letter(self.letters_data[index + 1])
                else:
                    self.load_letter_page(self.current_page - 1)
        elif item == self.previous_button:
            if self.current_page > 1:
                self.load_letter_page(self.current_page - 1)
            else:
                index = self.letters_data.index(self.selected_letter)
                if index > 0:
                    self.select_letter(self.letters_data[index - 1], True)
        if item in [self.previous_button, self.next_button]:
            self.stage.render()
            self.turn_page_sound.play()
        return

    def popup_close_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        self.close_popup()
        return

    def popup_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.click_sound.play()
            self.close_popup()
        return

    def close_popup(self):
        self.stage.close_dialog(self.popup_layer)
        return

    def letters_click(self, item, args):
        letter = self.get_letter_at(args.x, args.y)
        if letter != None:
            if (self.selected_letter != letter or self.current_page != 1) and letter[5]:
                self.letter_hover.set_visible(False)
                self.select_letter(letter)
                self.stage.render()
                self.turn_page_sound.play()
        return

    def letters_mousemove(self, item, args):
        letter = self.get_letter_at(args.x, args.y)
        if letter == None or letter == self.selected_letter:
            self.stage.stop_timer(LETTER_ROLLOVER_TIMER_KEY)
            self.letter_hover.set_visible(False)
            self.letter_hover.set_left(0)
            self.letter_hover.set_top(0)
        elif letter[5]:
            letter_left = letter[4]
            letter_top = letter[5]
            if self.letter_hover.get_left() != letter_left or self.letter_hover.get_top() != letter_top:
                self.letter_hover.set_left(letter_left)
                self.letter_hover.set_top(letter_top)
                self.letter_hover.set_visible(False)
                self.stage.stop_timer(LETTER_ROLLOVER_TIMER_KEY)
                self.stage.start_timer(LETTER_ROLLOVER_TIMER_KEY, 50, self.show_letter_rollover)
                self.last_hover_show = pygame.time.get_ticks()
        return

    def show_letter_rollover(self, key, data):
        self.stage.stop_timer(key)
        self.letter_hover.set_visible(True)
        self.rollover_sound.stop()
        self.stage.render()
        self.rollover_sound.play()
        self.last_hover_show = pygame.time.get_ticks()
        return

    def letters_leave(self, item, args):
        self.stage.stop_timer(LETTER_ROLLOVER_TIMER_KEY)
        self.letter_hover.set_visible(False)
        return

    def note_click(self, item, args):
        if self.popup_layer == None:
            self.set_up_popup_layer()
        self.load_note_data(item.note)
        self.stage.show_dialog(self.popup_layer, self.popup_handle_event)
        self.stage.render()
        self.popup_sound.play()
        return

    def load_note_data(self, note):
        self.popup_title.set_text(note.get_full_name())
        if note.type == 'HISTORY_FACT':
            self.popup_subtitle1.set_text('(' + note.date + ')')
            self.popup_subtitle2.set_text('')
            self.popup_description.set_text(self.get_joint_description(note))
        elif note.type == 'RIVER':
            self.popup_subtitle1.set_text('Longitud: ' + note.length)
            self.popup_subtitle2.set_text('Cuenca: ' + note.basin)
            self.popup_description.set_text(self.get_joint_description(note))
        elif note.type == 'LAGOON':
            self.popup_subtitle1.set_text('Superficie: ' + note.surface)
            self.popup_subtitle2.set_text('')
            self.popup_description.set_text(self.get_joint_description(note))
        elif note.type == 'HILL':
            self.popup_subtitle1.set_text('Altura: ' + note.height)
            self.popup_subtitle2.set_text('')
            self.popup_description.set_text(self.get_joint_description(note))
        elif note.type == 'LOCATION':
            self.popup_subtitle1.set_text(note.location_type)
            self.popup_subtitle2.set_text('Población: ' + note.population)
            self.popup_description.set_text(note.description)
        elif note.type == 'WRITER':
            self.popup_subtitle1.set_text(note.dates)
            self.popup_subtitle2.set_text('')
            self.popup_description.set_text(note.description)
        return

    def get_joint_description(self, note):
        s = note.description1
        if note.description2 != None:
            s += '\n\n' + note.description2
        return s

    def get_letter_at(self, x, y):
        for letter_data in self.letters_data:
            if letter_data[2] + 2 <= y and y < letter_data[2] + 28 and letter_data[1] <= x and x < letter_data[1] + 26:
                return letter_data

        return

    def select_letter(self, letter, load_last_page=False):
        if letter[0] in self.new_notes_letters:
            self.layer.remove(self.new_notes_letters[letter[0]])
            del self.new_notes_letters[letter[0]]
        if letter[2] < 20:
            self.letter_selected_top.set_left(letter[1])
            self.letter_selected_top.set_top(letter[2])
            self.letter_selected_top.set_visible(True)
            self.letter_selected_bottom.set_visible(False)
        else:
            self.letter_selected_bottom.set_left(letter[1])
            self.letter_selected_bottom.set_top(letter[2])
            self.letter_selected_bottom.set_visible(True)
            self.letter_selected_top.set_visible(False)
        letter_item = letter[3]
        if letter_item == None:
            letter_char = self.get_letter_image_char(letter[0])
            letter_image = assets.load_image('p0_notes_' + letter_char + '.jpg')
            letter_item = ItemImage(66, 69, letter_image)
            letter[3] = letter_item
        if self.selected_letter != None and self.selected_letter[3] != None:
            self.layer.remove(self.selected_letter[3])
        self.layer.add(letter_item)
        self.selected_letter = letter
        self.load_letter_notes(letter[0])
        if not load_last_page:
            self.load_letter_page(1)
        else:
            last_page = self.load_letter_page(99999)[1]
            self.load_letter_page(last_page)
        return

    def get_letter_image_char(self, letter):
        letter_char = letter[0].lower()
        if letter_char == 'ñ' or letter_char == 'Ñ':
            letter_char = 'nn'
        return letter_char

    def load_letter_notes(self, letter):
        notes = self.stage.game.datastore.user_character_progress.notes
        self.letter_notes = []
        for note in notes:
            note_letter = self.get_note_letter(note)
            if note_letter == letter:
                self.letter_notes.append(note)

        self.letter_notes.sort(key=functools.cmp_to_key(self.note_compare))
        return

    def get_note_letter(self, note):
        letter = note.name[0].upper()
        if letter == 'Á' or letter == 'á':
            letter = 'A'
        elif letter == 'É' or letter == 'é':
            letter = 'E'
        elif letter == 'Í' or letter == 'í':
            letter = 'I'
        elif letter == 'Ó' or letter == 'ó':
            letter = 'O'
        elif letter == 'Ú' or letter == 'ú':
            letter = 'U'
        return letter

    def note_compare(self, note1, note2):
        if note1.get_full_name() > note2.get_full_name():
            return 1
        elif note1.get_full_name() == note2.get_full_name():
            return 0
        else:
            return -1
        return

    def load_letter_page(self, page_number):
        for item in self.page_items:
            self.layer.remove(item)

        index = self.layer.index_of(self.menu_back)
        if page_number == 1:
            self.headerline.set_visible(True)
            self.selected_letter[3].set_visible(True)
        else:
            self.headerline.set_visible(False)
            self.selected_letter[3].set_visible(False)
        current_page = 1
        text_x = 86
        text_y = 175
        self.current_page = page_number
        has_items = False
        self.page_items = []
        last_page = True
        play_new_notes = False
        for note in self.letter_notes:
            (text_width, text_height) = self.line_font.size(note.get_full_name())
            if text_width > 188:
                text_height = 44
            else:
                text_height = 22
            if text_y + text_height > 380:
                if text_x < 100:
                    text_x = 335
                else:
                    text_x = 83
                    current_page += 1
                text_y = 65
            if current_page == page_number:
                if text_height <= 30:
                    hover_image = self.item_hoversmall_image
                else:
                    hover_image = self.item_hoverbig_image
                mask = ItemMask(text_x - 20, text_y, hover_image.get_size())
                mask.set_rollover(hover_image, self.rollover_sound)
                mask.note = note
                mask.add_event_handler(ItemEvent.CLICK, self.note_click)
                self.layer.add(mask, index)
                index += 1
                self.page_items.append(mask)
                text = ItemText(text_x, text_y, self.line_font, 22, note.get_full_name(), (55,
                                                                                           62,
                                                                                           92), None, 188)
                self.layer.add(text, index)
                index += 1
                self.page_items.append(text)
                dot_item = ItemImage(text_x - 12, text_y + 8, self.dot_image)
                self.layer.add(dot_item, index)
                index += 1
                self.page_items.append(dot_item)
                new_notes = self.stage.game.datastore.user_character_progress.new_notes
                if note in new_notes:
                    new_notes.remove(note)
                    self.pending_changes_to_save = True
                    animations.fade_in_item(text)
                    animations.fade_in_item(dot_item)
                    play_new_notes = True
                has_items = True
            elif current_page > page_number:
                last_page = False
                break
            text_y += text_height

        self.update_buttons_enabled(page_number, last_page)
        if play_new_notes:
            self.stage.render()
            self.note_fade_in_sound.play()
        return (
         has_items, current_page)

    def update_buttons_enabled(self, page_number, last_page):
        if self.selected_letter != self.letters_data[0] or page_number > 1:
            self.previous_button.set_visible(True)
        else:
            self.previous_button.set_visible(False)
        if self.selected_letter != self.letters_data[len(self.letters_data) - 1] or not last_page:
            self.next_button.set_visible(True)
        else:
            self.next_button.set_visible(False)
        return

    def set_letters_state(self, letters, enabled):
        if letters:
            for letter in letters:
                for data in self.letters_data:
                    if data[0] == letter:
                        data[5] = enabled
                        break

        else:
            for letter in self.letters_data:
                letter[5] = enabled

        return

    def disable_letters(self, letters=None):
        self.set_letters_state(letters, False)
        return

    def enable_letters(self, letters=None):
        self.set_letters_state(letters, True)
        return

    def disable_next_button(self):
        self.next_button.set_rollover_image(None, None)
        self.next_button.remove_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def disable_previous_button(self):
        self.previous_button.set_rollover_image(None, None)
        self.previous_button.remove_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def disable_close_button(self):
        self.close_button.set_rollover_image(None, None)
        self.close_button.remove_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def enable_next_button(self):
        self.next_button.set_rollover_image(self.next_button_image_rollover, self.rollover_sound)
        self.next_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def enable_previous_button(self):
        self.previous_button.set_rollover_image(self.previous_button_image_rollover, self.rollover_sound)
        self.previous_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def enable_close_button(self):
        self.close_button.set_rollover_image(self.close_button_image_rollover, self.rollover_sound)
        self.close_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def disable_notes(self):
        return


