from framework import assets, animations
from framework.stage import *
from pygame.time import delay
from random import randint
import random
from .minigame import Minigame
from game.data import statcodes

class MinigameLibrarian(Minigame):

    def __init__(self, stage, phase1content, witness):
        Minigame.__init__(self, stage, phase1content, witness, statcodes.MG_LIRARIAN, statcodes.MG_LIRARIAN_SOLVED, statcodes.MG_LIRARIAN_NOTSOLVED, 'librarian')
        self.word_max_length = 6
        self.correct_words_to_win = 5
        self.letters = None
        self.correct_words = 0
        self.wrong_words = 0
        self.letters_used = 0
        self.animation_on = False
        self.powdrf_18 = assets.load_font('powdrft_.ttf', 18)
        self.powdrf_23 = assets.load_font('powdrft_.ttf', 23)
        self.bell_sound = assets.load_sound('p1_minigame_bell.ogg')
        self.type_sound = assets.load_sound('p1_minigame_type.ogg')
        self.erase_sound = assets.load_sound('p1_minigame_erase.ogg')
        self.correct_choice = assets.load_sound('p1_minigame_right.ogg')
        self.incorrect_choice = assets.load_sound('p1_minigame_wrong.ogg')
        self.timer = assets.load_sound('p1_minigame_timer.ogg')
        librarian_image = assets.load_image('p1_minigame_librarian_librarian.png')
        self.witness_item = ItemImage(447, 77, librarian_image, None)
        self.witness_minigame_box_image = assets.load_image('p1_minigame_flux_librarian_dialogue1.png')
        self.max_help_stages = 4
        self.title = 'BIBLIOTECARIO'
        self.question_intro = 'El Bibliotecario se encuentra muy ocupado\nen este momento, quizás si lo ayudas\npuedas interrogarlo luego.'
        self.question = '¿Te ofreces a ayudarlo?'
        self.request_text = 'Estoy intentando restaurar unos libros antiguos y\nalgunas palabras no se ven bien. Tengo una\nlista de las letras que podrían formarlas.'
        self.request_question_text = '¿Puedes ayudarme a formar\npalabras con ellas?'
        self.thanks_text = '¡Muchas gracias!\n\nYa puedo terminar de restaurar los libros.'
        self.dictionary_small = assets.load_data('words_small.tcd')
        self.dictionary_full = assets.load_data('words_full.tcd')
        return

    def get_music(self):
        return self.phase1content.music_minigame_2

    def blind_show_minigame_callback(self, layer):
        if not self.stage.game.datastore.user_character_progress.minigame_librarian_help_seen:
            self.stop_minigame(False)
            self.stage.game.datastore.user_character_progress.minigame_librarian_help_seen = True
            self.show_help_dialog()
        else:
            self.start_minigame()
        return

    def set_up_minigame(self):
        character_progress = self.stage.game.datastore.user_character_progress
        minigame_level = character_progress.range.minigame_level
        if minigame_level == 1:
            self.letters_count = 7
        elif minigame_level == 2:
            self.letters_count = 7
        else:
            self.letters_count = 6
        level = character_progress.range.level
        if level == 0:
            self.average_time = 90
            self.timer_complete_time = 135
        elif level == 1:
            self.average_time = 76
            self.timer_complete_time = 114
        elif level == 2:
            self.average_time = 62
            self.timer_complete_time = 93
        elif level == 3:
            self.average_time = 48
            self.timer_complete_time = 72
        elif level == 4:
            self.average_time = 34
            self.timer_complete_time = 51
        else:
            self.average_time = 20
            self.timer_complete_time = 30
        self.set_up_game_background_items()
        self.set_up_timer()
        self.set_up_letters()
        self.set_up_game_buttons()
        self.set_up_typed_text()
        self.set_up_witness()
        self.good_color_image = assets.load_image('p1_minigame_librarian_popup_good.png')
        self.good_white_image = assets.load_image('p1_minigame_librarian_popup_good_white.png')
        self.bad_color_image = assets.load_image('p1_minigame_librarian_popup_bad.png')
        self.bad_white_image = assets.load_image('p1_minigame_librarian_popup_bad_white.png')
        self.rightmark_image = assets.load_image('p1_minigame_librarian_rightmark.png')
        self.result_layer = Layer()
        self.stage.add_layer(self.result_layer)
        return

    def set_up_timer(self):
        timer_backbar_image = assets.load_image('p1_minigame_shoptender_timer_backbar.jpg')
        timer_topbar_image = assets.load_image('p1_minigame_shoptender_timer_topbar.png')
        timer_barshadow_image = assets.load_image('p1_minigame_shoptender_timer_barshadow.png')
        timer_front_image = assets.load_image('p1_minigame_shoptender_timer_front.png')
        timer_ringer_image = assets.load_image('p1_minigame_shoptender_timer_ringer_001.png')
        timer_backbar_item = ItemImage(92, 111, timer_backbar_image, None)
        self.timer_line_item = ItemRect(97, 118, 11, 128, None, 0, '', (0, 0, 0), (236,
                                                                                   14,
                                                                                   36))
        self.adjustement_value = _div(float(self.timer_line_item.get_height()) , self.timer_complete_time)
        self.timer_topbar_item = ItemImage(94, 104, timer_topbar_image, None)
        timer_barshadow_item = ItemImage(90, 110, timer_barshadow_image, None)
        timer_front_item = ItemImage(83, 100, timer_front_image, None)
        self.timer_ringer_item = ItemImage(52, 235, timer_ringer_image, None)
        self.layer.add(timer_backbar_item)
        self.layer.add(self.timer_line_item)
        self.layer.add(self.timer_topbar_item)
        self.layer.add(timer_barshadow_item)
        self.layer.add(timer_front_item)
        self.layer.add(self.timer_ringer_item)
        return

    def set_up_letters(self):
        self.letter_items = []
        if self.letters_count == 7:
            self.add_letter(158, 93, 167, 105)
            self.add_letter(199, 90, 208, 101)
            self.add_letter(238, 90, 248, 102)
            self.add_letter(278, 89, 288, 100)
            self.add_letter(318, 90, 328, 101)
            self.add_letter(358, 92, 369, 103)
            self.add_letter(398, 95, 410, 106)
        elif self.letters_count == 6:
            self.add_letter(178, 93, 187, 105)
            self.add_letter(219, 91, 227, 102)
            self.add_letter(258, 90, 269, 102)
            self.add_letter(300, 90, 310, 102)
            self.add_letter(340, 92, 351, 103)
            self.add_letter(380, 95, 392, 106)
        return

    def add_letter(self, button_x, button_y, letter_x, letter_y):
        k = str(len(self.letter_items) + 1)
        standby_image = assets.load_image('p1_minigame_librarian_btn_00' + k + '_standby.png')
        rollover_image = assets.load_image('p1_minigame_librarian_btn_00' + k + '_rollover.png')
        back_item = ItemImage(button_x, button_y, standby_image)
        back_item.set_rollover_image(rollover_image, self.rollover_sound)
        back_item.add_event_handler(ItemEvent.CLICK, self.letter_click)
        self.layer.add(back_item)
        item = ItemText(letter_x, letter_y, self.powdrf_23, 0, '', (80, 49, 19), None, 30, 30, 2)
        back_item.letter_item = item
        self.layer.add(item)
        self.letter_items.append((item, back_item))
        return

    def set_up_game_buttons(self):
        accept_standby_image = assets.load_image('p1_minigame_librarian_btn_accept_standby.jpg')
        accept_rollover_image = assets.load_image('p1_minigame_librarian_btn_accept_rollover.jpg')
        self.accept_button = ItemImage(204, 143, accept_standby_image)
        self.accept_button.set_rollover_image(accept_rollover_image, self.rollover_sound)
        self.accept_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.layer.add(self.accept_button)
        delete_standby_image = assets.load_image('p1_minigame_librarian_btn_delete_standby.jpg')
        delete_rollover_image = assets.load_image('p1_minigame_librarian_btn_delete_rollover.jpg')
        self.delete_button = ItemImage(303, 143, delete_standby_image)
        self.delete_button.set_rollover_image(delete_rollover_image, self.rollover_sound)
        self.delete_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.layer.add(self.delete_button)
        return

    def set_up_typed_text(self):
        self.typed_text = ''
        self.typed_letter_items = []
        self.add_typed_letter(214, 204)
        self.add_typed_letter(244, 205)
        self.add_typed_letter(274, 204)
        self.add_typed_letter(304, 204)
        self.add_typed_letter(334, 204)
        self.add_typed_letter(364, 204)
        return

    def add_typed_letter(self, x, y):
        item = ItemText(x, y, self.font_24, 0, '', (150, 20, 15), None, 26, 30, 2)
        self.typed_letter_items.append(item)
        self.layer.add(item)
        return

    def start_bell_animation(self):
        timer_ringer_image = self.timer_ringer_item.get_image()
        timer_ringer_image2 = assets.load_image('p1_minigame_shoptender_timer_ringer_002.png')
        timer_ringer_image3 = assets.load_image('p1_minigame_shoptender_timer_ringer_003.png')
        timer_ringer_image4 = assets.load_image('p1_minigame_shoptender_timer_ringer_004.png')
        animations.start_image_sequence(self.timer_ringer_item, [timer_ringer_image2, timer_ringer_image3, timer_ringer_image4, timer_ringer_image], 60, 10, None)
        return

    def update_timer(self, item, args):
        self.timer_topbar_item.set_top(self.timer_topbar_item.get_top() + 1)
        self.timer_line_item.set_top(self.timer_line_item.get_top() + 1)
        self.timer_line_item.set_height(self.timer_line_item.get_height() - 1)
        if self.timer_line_item.get_height() == 1:
            self.stop_minigame(False)
            self.stop_minigame_music(0)
            self.start_bell_animation()
            self.bell_sound.play()
            self.correct_words = 0
            self.wrong_words = 0
            self.letters_used = 0
            self.animation_on = True
            animations.wait_locked(self.stage, 2000, self.loose_game)
        return

    def load_help_data(self):
        if self.help_stage == 1:
            background_image = assets.load_image('p1_minigame_librarian_help_d1.jpg')
            back_left = 125
            back_top = 165
            upper_help_text = 'En la parte superior de la pantalla aparecerán las letras que debemos usar para formar palabras.'
            upper_text_left = 157
            upper_text_top = 102
            upper_text_width = 288
            upper_text_height = 67
            lower_help_text = None
            self.help_previous_button.set_visible(False)
        elif self.help_stage == 2:
            background_image = assets.load_image('p1_minigame_librarian_help_d2.jpg')
            back_left = 125
            back_top = 139
            upper_help_text = 'Puedes seleccionarlas haciendo clic sobre ellas o escribiendolas en el teclado.'
            upper_text_left = 164
            upper_text_top = 86
            upper_text_width = 275
            upper_text_height = 49
            lower_help_text = 'Lo mismo para el botón de borrar.'
            lower_text_left = 217
            lower_text_top = 326
            lower_text_width = 163
            lower_text_height = 34
        elif self.help_stage == 3:
            background_image = assets.load_image('p1_minigame_librarian_help_d3.jpg')
            back_left = 125
            back_top = 157
            upper_help_text = 'Una vez que hayas escrito la palabra debes apretar el botón de aceptar o la tecla "enter" del teclado.'
            upper_text_left = 156
            upper_text_top = 92
            upper_text_width = 288
            upper_text_height = 56
            lower_help_text = None
        elif self.help_stage == 4:
            background_image = assets.load_image('p1_minigame_librarian_help_d4.jpg')
            back_left = 125
            back_top = 152
            upper_help_text = 'Debes completar 5 palabras de al menos 3 letras cada una antes de que se acabe el tiempo y suene la campana.'
            upper_text_left = 155
            upper_text_top = 92
            upper_text_width = 288
            upper_text_height = 56
            lower_help_text = None
        background_help_image_item = ItemImage(0, 0, None, None)
        background_help_image_item.set_image(background_image)
        background_help_image_item.set_lefttop(back_left, back_top)
        self.help_current_layer.add(background_help_image_item)
        self.upper_help_text_item = ItemText(upper_text_left, upper_text_top, self.font_14, 16, upper_help_text, (183,
                                                                                                                  35,
                                                                                                                  35), None, upper_text_width, upper_text_height, 2)
        self.help_current_layer.add(self.upper_help_text_item)
        if lower_help_text != None:
            self.lower_help_text_item = ItemText(lower_text_left, lower_text_top, self.font_14, 16, lower_help_text, (183,
                                                                                                                      35,
                                                                                                                      35), None, lower_text_width, lower_text_height, 2)
            self.help_current_layer.add(self.lower_help_text_item)
        return

    def start_minigame(self, animation_item=None):
        self.stage.render()
        if self.letters == None:
            self.select_letters()
            self.reset_text()
        if not self.stage.is_timer_started('timer_librarian'):
            self.play_music()
            self.stage.start_timer('timer_librarian', int(_div(1000 , self.adjustement_value)), self.update_timer)
            self.timer.play(-1)
        self.start_play_stats_event()
        return

    def stop_minigame(self, solved):
        if self.stage.is_timer_started('timer_librarian'):
            self.stage.stop_timer('timer_librarian')
            self.timer.stop()
            self.stop_minigame_music()
        self.end_play_stats_event(solved)
        return

    def set_up_game_background_items(self):
        back_center_image = assets.load_image('p1_minigame_librarian_back_center.jpg')
        back_center_item = ItemImage(111, 79, back_center_image)
        self.layer.add(back_center_item)
        back_left_image = assets.load_image('p1_minigame_librarian_back_left.png')
        back_left_item = ItemImage(91, 79, back_left_image)
        self.layer.add(back_left_item)
        back_right_image = assets.load_image('p1_minigame_librarian_back_right.png')
        back_right_item = ItemImage(501, 79, back_right_image)
        self.layer.add(back_right_item)
        back_top_image = assets.load_image('p1_minigame_librarian_back_top.png')
        back_top_item = ItemImage(98, 50, back_top_image)
        self.layer.add(back_top_item)
        back_bottom_image = assets.load_image('p1_minigame_librarian_back_bottom.png')
        back_bottom_item = ItemImage(91, 356, back_bottom_image)
        self.layer.add(back_bottom_item)
        exit_image = assets.load_image('p1_minigames_btn_close_normal.png')
        exit_image_rollover = assets.load_image('p1_minigames_btn_close_active.png')
        self.exit_button = ItemImage(264, 47, exit_image)
        self.exit_button.set_rollover_image(exit_image_rollover, self.rollover_sound)
        self.layer.add(self.exit_button)
        self.exit_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        help_image = assets.load_image('p1_minigames_btn_help_normal.png')
        help_image_rollover = assets.load_image('p1_minigames_btn_help_active.png')
        self.help_button = ItemImage(299, 47, help_image)
        self.help_button.set_rollover_image(help_image_rollover, self.rollover_sound)
        self.help_button.add_event_handler(ItemEvent.CLICK, self.help_click)
        self.layer.add(self.help_button)
        return

    def letter_click(self, item, args):
        self.type_letter(item.letter, (item.letter_item, item))
        return

    def button_click(self, item, args):
        if item == self.delete_button:
            self.delete_letter()
        elif item == self.accept_button:
            self.accept_text()
        elif item == self.exit_button:
            self.correct_words = 0
            self.wrong_words = 0
            self.letters_used = 0
            self.stop_minigame(False)
            self.phase1content.minigame_solved(False)
            self.close_minigame()
        return

    def check_for_minigame_finished(self):
        if self.timer_line_item.get_height() <= 1 or self.correct_words == self.correct_words_to_win:
            self.stop_minigame(True)
            animations.wait_locked(self.stage, 1500, self.final_resolution)
        return

    def final_resolution(self, item=None):
        self.minigame_solved_callback()
        self.animation_on = False
        return

    def select_letters(self):
        self.correct_word_list = []
        self.letters = self.generate_letters()
        i = 0
        for letter in self.letters:
            self.letter_items[i][0].set_text(self.to_upper(letter))
            self.letter_items[i][1].letter = letter
            i += 1

        return

    def get_matches(self, dictionary):
        matches = []
        words = dictionary[0]
        for word in words:
            missing_letters = 0
            available_letters = self.letters[:]
            for letter in word:
                if letter in available_letters:
                    available_letters.remove(letter)
                else:
                    missing_letters += 1

            if missing_letters == 0:
                matches.append(word)

        return matches

    def generate_letters(self):
        words = self.dictionary_small[0]
        if self.letters_count >= 7:
            min_matches = 4 * self.correct_words_to_win
        else:
            min_matches = 3 * self.correct_words_to_win
        random.seed()
        while True:
            letters = []
            while len(letters) < self.letters_count:
                missing_letter_score = {}
                for word in words:
                    missing_letters = 0
                    available_letters = letters[:]
                    for letter in word:
                        if letter in available_letters:
                            available_letters.remove(letter)
                        else:
                            missing_letters += 1

                    if missing_letters > 0 and missing_letters <= self.letters_count - len(letters):
                        if missing_letters == 1:
                            word_score = 150
                        elif missing_letters == 2:
                            word_score = 20
                        elif missing_letters == 3:
                            word_score = 10
                        elif missing_letters == 4:
                            word_score = 5
                        elif missing_letters == 5:
                            word_score = 2
                        else:
                            word_score = 1
                        available_letters = letters[:]
                        for letter in word:
                            if letter in available_letters:
                                available_letters.remove(letter)
                            else:
                                if letter in missing_letter_score:
                                    score = missing_letter_score[letter]
                                else:
                                    score = 0
                                score += word_score
                                missing_letter_score[letter] = score

                top_letter_scores = []
                top_letters = []
                while len(top_letters) < 4:
                    max_letter = ''
                    max_score = 0
                    for (letter, score) in list(missing_letter_score.items()):
                        if score > max_score and letter not in top_letters:
                            max_letter = letter
                            max_score = score

                    if max_score == 0:
                        break
                    top_letter_scores.append((max_score, max_letter))
                    top_letters.append(max_letter)

                if len(top_letters) > 0:
                    letters.append(random.choice(top_letters))
                else:
                    letter_selected = False
                    while not letter_selected:
                        word = random.choice(words)
                        for letter in word:
                            if letter not in letters:
                                letters.append(letter)
                                letter_selected = True
                                break

            matches = 0
            for word in words:
                missing_letters = 0
                available_letters = letters[:]
                for letter in word:
                    if letter in available_letters:
                        available_letters.remove(letter)
                    else:
                        missing_letters += 1

                if missing_letters == 0:
                    matches += 1

            if matches >= min_matches:
                return letters

        return

    def type_letter(self, letter, letter_items=None):
        if len(self.typed_text) < len(self.typed_letter_items):
            if letter_items == None:
                for (item, back_item) in self.letter_items:
                    if back_item.letter == letter and back_item.get_visible():
                        letter_items = (
                         item, back_item)
                        break

            if letter_items != None:
                self.typed_text += letter
                self.typed_letter_items[len(self.typed_text) - 1].set_text(self.to_upper(letter))
                letter_items[0].set_visible(False)
                letter_items[1].set_visible(False)
                self.stage.render()
                self.type_sound.play()
        return

    def to_upper(self, letter):
        if letter == 'á':
            return 'Á'
        elif letter == 'é':
            return 'É'
        elif letter == 'í':
            return 'Í'
        elif letter == 'ó':
            return 'Ó'
        elif letter == 'ú':
            return 'Ú'
        elif letter == 'ñ':
            return 'Ñ'
        elif letter == 'ü':
            return 'Ü'
        else:
            return letter.upper()
        return

    def delete_letter(self):
        if len(self.typed_text) > 0:
            letter = self.typed_text[len(self.typed_text) - 1]
            letter_item = None
            for (item, back_item) in self.letter_items:
                if back_item.letter == letter and not back_item.get_visible():
                    letter_item = (
                     item, back_item)
                    break

            letter_item[0].set_visible(True)
            letter_item[1].set_visible(True)
            self.typed_text = self.typed_text[:len(self.typed_text) - 1]
            self.typed_letter_items[len(self.typed_text)].set_text('')
            self.stage.render()
            self.erase_sound.play()
        return

    def accept_text(self):
        if len(self.typed_text) > 0:
            if self.typed_text in self.dictionary_full[0]:
                index = self.dictionary_full[0].index(self.typed_text)
                word_to_add = self.dictionary_full[1][index]
            else:
                word_to_add = None
            if word_to_add != None and word_to_add not in self.correct_word_list:
                self.add_correct_word(word_to_add)
                self.start_result_animation(True)
                self.stage.render()
                self.correct_choice.play()
                self.check_for_minigame_finished()
            elif word_to_add not in self.correct_word_list:
                self.wrong_words += 1
            self.start_result_animation(False)
            self.stage.render()
            self.incorrect_choice.play()
            self.reset_text()
        return

    def reset_text(self):
        self.typed_text = ''
        for (item, back_item) in self.letter_items:
            item.set_visible(True)
            back_item.set_visible(True)

        for item in self.typed_letter_items:
            item.set_text('')

        return

    def add_correct_word(self, word):
        if word not in self.correct_word_list:
            if self.correct_words == 0:
                number_x = 233
                number_y = 295
                tick_x = 344
                tick_y = 279
                text_x = 249
                text_y = 289
            elif self.correct_words == 1:
                number_x = 233
                number_y = 315
                tick_x = 344
                tick_y = 299
                text_x = 249
                text_y = 312
            elif self.correct_words == 2:
                number_x = 233
                number_y = 337
                tick_x = 344
                tick_y = 321
                text_x = 249
                text_y = 332
            elif self.correct_words == 3:
                number_x = 233
                number_y = 356
                tick_x = 344
                tick_y = 342
                text_x = 249
                text_y = 352
            elif self.correct_words == 4:
                number_x = 233
                number_y = 379
                tick_x = 344
                tick_y = 364
                text_x = 249
                text_y = 375
            number = str(self.correct_words + 1)
            number_image = assets.load_image('p1_minigame_librarian_' + number + 'listed.jpg')
            number_item = ItemImage(number_x, number_y, number_image)
            self.layer.add(number_item)
            rightmark_item = ItemImage(tick_x, tick_y, self.rightmark_image)
            self.layer.add(rightmark_item)
            word_upper = ''
            for c in word:
                word_upper += self.to_upper(c)

            text = ItemText(text_x, text_y, self.powdrf_18, 0, word_upper, (150, 20,
                                                                            15), None, 103, 25, 2)
            self.layer.add(text)
            self.correct_words += 1
            self.correct_word_list.append(word)
            self.letters_used += len(word)
        return

    def minigame_handle_event(self, e):
        if e.type == KEYDOWN:
            if self.stage.is_timer_started('timer_librarian'):
                if e.key == K_BACKSPACE:
                    self.delete_letter()
                elif e.key == K_RETURN:
                    self.accept_text()
                else:
                    valid = True
                    for c in e.unicode:
                        if ord(c) not in list(range(256)):
                            valid = False
                            break

                    if valid:
                        letter = e.unicode.lower()
                        if letter in self.letters:
                            self.type_letter(letter)
        Minigame.minigame_handle_event(self, e)
        return

    def start_result_animation(self, good):
        animation = ResultAnimation(self.stage, self, self.result_layer, good)
        animation.start()
        return

    def calculate_solved_score(self):
        remaining_time = min(self.timer_complete_time, _div(self.timer_line_item.get_height() , self.adjustement_value))
        elapsed_time = self.timer_complete_time - remaining_time
        if elapsed_time <= self.average_time:
            time_score = _div(128 * (self.average_time - elapsed_time) , self.average_time)
        else:
            time_score = 0
        return [100,
         time_score,
         self.letters_used * 1,
         -10 * self.wrong_words]

    def create_character_happy_item(self):
        librarian_happy_image = assets.load_image('p1_minigame_librarian_happy.png')
        return ItemImage(447, 77, librarian_happy_image, None)


class ResultAnimation():

    def __init__(self, stage, minigame, result_layer, good):
        self.stage = stage
        self.result_layer = result_layer
        if good:
            self.color_image = minigame.good_color_image
            self.white_image = minigame.good_white_image
        else:
            self.color_image = minigame.bad_color_image
            self.white_image = minigame.bad_white_image
        self.color_item = ItemImage(240, 160, self.color_image)
        self.white_item = ItemImage(240, 160, self.white_image)
        return

    def start(self):
        self.result_layer.add(self.color_item)
        self.result_layer.add(self.white_item)
        animations.fade_out_item(self.white_item, True, 167, self.__fade_out_callback)
        return

    def __fade_out_callback(self, item):
        animations.wait(self.stage, 167, self.__wait_callback)
        return

    def __wait_callback(self):
        if self.result_layer.get_stage() != None:
            animations.start_move(self.color_item, self.color_item.get_left(), self.color_item.get_top() - 95, 400)
            animations.fade_out_item(self.color_item, True, 400)
        return


