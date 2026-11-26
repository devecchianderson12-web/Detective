from framework import assets, animations
from framework.stage import *
from pygame.time import delay
from random import randint
import random
from .minigame import Minigame
from game.data import statcodes

class MinigameShoptender(Minigame):

    def __init__(self, stage, phase1content, witness):
        Minigame.__init__(self, stage, phase1content, witness, statcodes.MG_SHOPTENDER, statcodes.MG_SHOPTENDER_SOLVED, statcodes.MG_SHOPTENDER_NOTSOLVED, 'shoptender')
        self.correct_answers = 0
        self.wrong_answers = 0
        self.animation_on = False
        self.font_35 = assets.load_font('jstart.ttf', 35)
        self.bell_sound = assets.load_sound('p1_minigame_bell.ogg')
        self.correct_choice = assets.load_sound('p1_minigame_right.ogg')
        self.incorrect_choice = assets.load_sound('p1_minigame_wrong.ogg')
        self.timer = assets.load_sound('p1_minigame_timer.ogg')
        shoptender_image = assets.load_image('p1_minigame_shoptender.png')
        self.witness_item = ItemImage(459, 44, shoptender_image, None)
        self.witness_minigame_box_image = assets.load_image('p1_minigame_flux_shoptender_dialogue1.png')
        self.title = 'ALMACENERA'
        self.question_intro = 'La Almacenera se encuentra muy ocupada\nen este momento, quizás si la ayudas\npuedas interrogarla luego.'
        self.question = '¿Te ofreces a ayudarla?'
        self.request_text = 'Estaba pasando las ventas de hoy al libro de\ncuentas, pero se me manchó la libreta\ndonde hago las operaciones y\nno puedo ver su signo.'
        self.request_question_text = '¿Me ayudas a completarlas?'
        self.thanks_text = '¡Muchas gracias!\n\nAhora puedo terminar de actualizar\n el libro de cuentas.'
        self.wait_wrong_symbol_key = None
        self.fade_stain_key = None
        return

    def get_music(self):
        return self.phase1content.music_minigame_2

    def blind_show_minigame_callback(self, layer):
        if not self.stage.game.datastore.user_character_progress.minigame_shoptender_help_seen:
            self.stop_minigame(False)
            self.stage.game.datastore.user_character_progress.minigame_shoptender_help_seen = True
            self.show_help_dialog()
        else:
            self.start_minigame()
        return

    def set_up_minigame(self):
        self.set_up_game_background_items()
        self.set_up_game_symbols()
        self.set_up_timer()
        self.set_up_witness()
        self.set_up_counters()
        return

    def set_up_counters(self):
        self.actual_counter = 0
        counter_back = assets.load_image('p1_minigame_shoptender_counter_bkg.png')
        self.counter1_on_image = assets.load_image('p1_minigame_shoptender_counter_s1_on.png')
        self.counter2_on_image = assets.load_image('p1_minigame_shoptender_counter_s2_on.png')
        self.counter3_on_image = assets.load_image('p1_minigame_shoptender_counter_s3_on.png')
        self.counter4_on_image = assets.load_image('p1_minigame_shoptender_counter_s4_on.png')
        self.counter5_on_image = assets.load_image('p1_minigame_shoptender_counter_s5_on.png')
        self.counter1_off_image = assets.load_image('p1_minigame_shoptender_counter_s1_off.png')
        self.counter2_off_image = assets.load_image('p1_minigame_shoptender_counter_s2_off.png')
        self.counter3_off_image = assets.load_image('p1_minigame_shoptender_counter_s3_off.png')
        self.counter4_off_image = assets.load_image('p1_minigame_shoptender_counter_s4_off.png')
        self.counter5_off_image = assets.load_image('p1_minigame_shoptender_counter_s5_off.png')
        counter_back = ItemImage(217, 84, counter_back, None)
        self.counter1_item = ItemImage(217, 85, self.counter1_off_image, None)
        self.counter2_item = ItemImage(252, 85, self.counter2_off_image, None)
        self.counter3_item = ItemImage(285, 85, self.counter3_off_image, None)
        self.counter4_item = ItemImage(319, 85, self.counter4_off_image, None)
        self.counter5_item = ItemImage(354, 84, self.counter5_off_image, None)
        self.layer.add(counter_back)
        self.layer.add(self.counter1_item)
        self.layer.add(self.counter2_item)
        self.layer.add(self.counter3_item)
        self.layer.add(self.counter4_item)
        self.layer.add(self.counter5_item)
        return

    def set_up_timer(self):
        character_progress = self.stage.game.datastore.user_character_progress
        level = character_progress.range.level
        if level == 0:
            self.average_time = 50
            self.timer_complete_time = 75
        elif level == 1:
            self.average_time = 43
            self.timer_complete_time = 65
        elif level == 2:
            self.average_time = 36
            self.timer_complete_time = 54
        elif level == 3:
            self.average_time = 29
            self.timer_complete_time = 44
        elif level == 4:
            self.average_time = 22
            self.timer_complete_time = 33
        else:
            self.average_time = 15
            self.timer_complete_time = 23
        timer_backbar_image = assets.load_image('p1_minigame_shoptender_timer_backbar.jpg')
        timer_topbar_image = assets.load_image('p1_minigame_shoptender_timer_topbar.png')
        timer_barshadow_image = assets.load_image('p1_minigame_shoptender_timer_barshadow.png')
        timer_front_image = assets.load_image('p1_minigame_shoptender_timer_front.png')
        timer_ringer_image = assets.load_image('p1_minigame_shoptender_timer_ringer_001.png')
        timer_backbar_item = ItemImage(144, 129, timer_backbar_image, None)
        self.timer_line_item = ItemRect(149, 136, 11, 128, None, 0, '', (0, 0, 0), (236,
                                                                                    14,
                                                                                    36))
        self.adjustement_value = float(self.timer_line_item.get_height()) / self.timer_complete_time
        self.timer_topbar_item = ItemImage(146, 122, timer_topbar_image, None)
        timer_barshadow_item = ItemImage(142, 128, timer_barshadow_image, None)
        timer_front_item = ItemImage(135, 118, timer_front_image, None)
        self.timer_ringer_item = ItemImage(104, 253, timer_ringer_image, None)
        self.layer.add(timer_backbar_item)
        self.layer.add(self.timer_line_item)
        self.layer.add(self.timer_topbar_item)
        self.layer.add(timer_barshadow_item)
        self.layer.add(timer_front_item)
        self.layer.add(self.timer_ringer_item)
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
            self.correct_answers = 0
            self.wrong_answers = 0
            self.animation_on = True
            animations.wait_locked(self.stage, 2000, self.loose_game)
        return

    def load_help_data(self):
        back_left = 125
        back_top = 154
        if self.help_stage == 1:
            background_image = assets.load_image('p1_minigame_shoptender_help_d1.jpg')
            upper_help_text = 'En la libreta aparece la cuenta con el signo tapado por la mancha.'
            upper_text_left = 203
            upper_text_top = 96
            upper_text_width = 193
            upper_text_height = 52
            lower_help_text = None
            self.help_previous_button.set_visible(False)
        elif self.help_stage == 2:
            background_image = assets.load_image('p1_minigame_shoptender_help_d2.jpg')
            upper_help_text = 'Debajo de la libreta, debemos elegir el signo que corresponda a la cuenta.'
            upper_text_left = 157
            upper_text_top = 104
            upper_text_width = 288
            upper_text_height = 43
            lower_help_text = None
        elif self.help_stage == 3:
            background_image = assets.load_image('p1_minigame_shoptender_help_d3.jpg')
            upper_help_text = 'Debemos completar correctamente 5 cuentas antes de que se acabe el tiempo y suene la campana.'
            upper_text_left = 157
            upper_text_top = 96
            upper_text_width = 288
            upper_text_height = 52
            lower_help_text = 'Cada error resta un acierto.'
            lower_text_left = 159
            lower_text_top = 341
            lower_text_width = 289
            lower_text_height = 18
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
        if not self.stage.is_timer_started('timer_shoptender'):
            self.play_music()
            self.stage.start_timer('timer_shoptender', int(1000 / self.adjustement_value), self.update_timer)
            self.timer.play(-1)
        self.build_operation()
        self.start_play_stats_event()
        return

    def stop_minigame(self, solved):
        if self.stage.is_timer_started('timer_shoptender'):
            self.stage.stop_timer('timer_shoptender')
            self.timer.stop()
            self.stop_minigame_music()
        self.end_play_stats_event(solved)
        return

    def set_up_game_background_items(self):
        notepad_image = assets.load_image('p1_minigame_shoptender_background.png')
        notepad_item_image = ItemImage(26, 14, notepad_image)
        self.layer.add(notepad_item_image)
        exit_image = assets.load_image('p1_minigames_btn_close_normal.png')
        exit_image_rollover = assets.load_image('p1_minigames_btn_close_active.png')
        self.exit_button = ItemImage(261, 45, exit_image)
        self.exit_button.set_rollover_image(exit_image_rollover, self.rollover_sound)
        self.layer.add(self.exit_button)
        self.exit_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        help_image = assets.load_image('p1_minigames_btn_help_normal.png')
        help_image_rollover = assets.load_image('p1_minigames_btn_help_active.png')
        self.help_button = ItemImage(296, 45, help_image)
        self.help_button.set_rollover_image(help_image_rollover, self.rollover_sound)
        self.help_button.add_event_handler(ItemEvent.CLICK, self.help_click)
        self.layer.add(self.help_button)
        stain_image = assets.load_image('p1_minigame_shoptender_stain.png')
        self.stain_item_image = ItemImage(194, 147, stain_image)
        self.layer.add(self.stain_item_image)
        self.success_symbols_list = []
        symbol_image_add = assets.load_image('p1_minigame_shoptender_add.png')
        symbol_item_add = ItemImage(232, 179, symbol_image_add)
        self.success_symbols_list.append(symbol_item_add)
        symbol_image_sub = assets.load_image('p1_minigame_shoptender_substract.png')
        symbol_item_sub = ItemImage(232, 179, symbol_image_sub)
        self.success_symbols_list.append(symbol_item_sub)
        symbol_image_mul = assets.load_image('p1_minigame_shoptender_multiply.png')
        symbol_item_mul = ItemImage(232, 179, symbol_image_mul)
        self.success_symbols_list.append(symbol_item_mul)
        symbol_image_div = assets.load_image('p1_minigame_shoptender_divide.png')
        symbol_item_div = ItemImage(232, 179, symbol_image_div)
        self.success_symbols_list.append(symbol_item_div)
        for s in self.success_symbols_list:
            s.set_visible(False)
            self.layer.add(s)

        self.number_lines_list = []
        line_text1 = ItemText(220, 154, self.font_35, 0, '', (71, 71, 130), None, 140, 36, 3)
        line_text2 = ItemText(220, 198, self.font_35, 0, '', (71, 71, 130), None, 140, 36, 3)
        line_text3 = ItemText(220, 258, self.font_35, 0, '', (71, 71, 130), None, 140, 36, 3)
        self.number_lines_list.append(line_text1)
        self.number_lines_list.append(line_text2)
        self.number_lines_list.append(line_text3)
        self.layer.add(line_text1)
        self.layer.add(line_text2)
        self.layer.add(line_text3)
        return

    def set_up_game_symbols(self):
        self.symbol_list = []
        self.symbol_list_wrong = []
        for i in range(4):
            standby_image = 'p1_minigame_shoptender_btn_00' + str(i + 1) + '_standby.png'
            symbol_image = assets.load_image(standby_image)
            hover_image = 'p1_minigame_shoptender_btn_00' + str(i + 1) + '_hover.png'
            symbol_image_rollover = assets.load_image(hover_image)
            symbol_item = ItemImage(207 + i * 50, 312, symbol_image)
            symbol_item.set_rollover_image(symbol_image_rollover, self.rollover_sound)
            self.symbol_list.append(symbol_item)
            wrong_image = 'p1_minigame_shoptender_btn_00' + str(i + 1) + '_wrong.png'
            symbol_image_wrong = assets.load_image(wrong_image)
            symbol_item_wrong = ItemImage(207 + i * 50, 312, symbol_image_wrong)
            self.symbol_list_wrong.append(symbol_item_wrong)
            self.layer.add(symbol_item)
            symbol_item_wrong.set_visible(False)
            self.layer.add(symbol_item_wrong)
            symbol_item.add_event_handler(ItemEvent.CLICK, self.button_click)

        return

    def update_counters(self, success):
        if success:
            self.actual_counter += 1
            if self.actual_counter == 1:
                self.counter1_item.set_image(self.counter1_on_image)
            elif self.actual_counter == 2:
                self.counter2_item.set_image(self.counter2_on_image)
            elif self.actual_counter == 3:
                self.counter3_item.set_image(self.counter3_on_image)
            elif self.actual_counter == 4:
                self.counter4_item.set_image(self.counter4_on_image)
            elif self.actual_counter == 5:
                self.counter5_item.set_image(self.counter5_on_image)
        elif self.actual_counter > 0:
            self.actual_counter -= 1
            if self.actual_counter == 0:
                self.counter1_item.set_image(self.counter1_off_image)
            elif self.actual_counter == 1:
                self.counter2_item.set_image(self.counter2_off_image)
            elif self.actual_counter == 2:
                self.counter3_item.set_image(self.counter3_off_image)
            elif self.actual_counter == 3:
                self.counter4_item.set_image(self.counter4_off_image)
            elif self.actual_counter == 4:
                self.counter5_item.set_image(self.counter5_off_image)
        return

    def button_click(self, item, args):
        if item == self.exit_button:
            self.correct_answers = 0
            self.stop_minigame(False)
            self.phase1content.minigame_solved(False)
            self.close_minigame()
        elif item in self.symbol_list:
            self.symbol_click(item)
        return

    def minigame_handle_event(self, e):
        if e.type == KEYDOWN:
            if self.stage.is_timer_started('timer_shoptender'):
                if e.str == '+':
                    self.symbol_click(self.symbol_list[0])
                elif e.str == '-':
                    self.symbol_click(self.symbol_list[1])
                elif e.str == '*':
                    self.symbol_click(self.symbol_list[2])
                elif e.str == '/':
                    self.symbol_click(self.symbol_list[3])
        return

    def symbol_click(self, item):
        if not self.animation_on and self.timer_line_item.get_height() > 1:
            self.animation_on = True
            if self.symbol_list.index(item) in self.operation_correct_answer:
                self.correct_answers += 1
                self.success_symbols_list[self.symbol_list.index(item)].set_visible(True)
                self.update_counters(True)
                self.correct_choice.play()
                self.check_for_minigame_finished()
                self.stage.lock_ui()
                self.fade_stain_key = animations.fade_out_item(self.stain_item_image, False, 500, self.animations_resolution)
            else:
                self.wrong_answers += 1
                if self.correct_answers > 0:
                    self.correct_answers -= 1
                self.check_for_minigame_finished()
                self.set_wrong_symbol_list(True)
                self.update_counters(False)
                self.stage.render()
                self.incorrect_choice.play()
                self.wait_wrong_symbol_key = animations.wait_locked(self.stage, 500, self.set_wrong_symbol_list)
        return

    def check_for_minigame_finished(self):
        if self.timer_line_item.get_height() <= 1 or self.correct_answers == 5:
            self.stop_minigame(True)
        return

    def animations_resolution(self, item):
        if self.correct_answers < 5:
            self.check_for_minigame_finished()
            animations.fade_in_item(self.stain_item_image, 500, self.final_resolution)
        else:
            animations.wait_locked(self.stage, 500, self.final_resolution)
        return

    def final_resolution(self, item=None):
        self.stage.unlock_ui()
        for s in self.success_symbols_list:
            if s.get_visible():
                s.set_visible(False)

        if self.correct_answers < 5:
            self.check_for_minigame_finished()
            if self.timer_line_item.get_height() > 1:
                self.start_minigame()
        else:
            self.minigame_solved_callback()
        self.animation_on = False
        return

    def set_wrong_symbol_list(self, state=False):
        for i in range(len(self.symbol_list_wrong)):
            self.symbol_list_wrong[i].set_visible(state)
            self.symbol_list[i].set_visible(not state)

        if state != True:
            self.animation_on = False
            self.check_for_minigame_finished()
            if self.timer_line_item.get_height() > 1:
                self.start_minigame()
        return

    def build_operation(self):
        random.seed()
        type_operation = random.randint(0, 3)
        max_number_accepted = 100
        if type_operation == 0:
            n1 = random.randint(1, max_number_accepted)
            n2 = random.randint(0, max_number_accepted - n1)
            n3 = n1 + n2
        if type_operation == 1:
            n1 = random.randint(1, max_number_accepted)
            n2 = random.randint(1, n1)
            n3 = n1 - n2
        if type_operation == 2:
            controled_range = max_number_accepted / 2
            n1 = random.randint(1, controled_range / 2)
            n2 = random.randint(0, max_number_accepted / n1)
            n3 = n1 * n2
        elif type_operation == 3:
            tries = 1
            while tries < 5:
                n1 = random.randint(2, max_number_accepted)
                remaining = 1
                while remaining != 0:
                    n2 = random.randint(2, n1)
                    n3 = n1 / n2
                    remaining = n1 % n2

                if n3 != 1 and n3 != 2:
                    break
                else:
                    tries += 1

        self.operation_correct_answer = []
        if n1 + n2 == n3:
            self.operation_correct_answer.append(0)
        if n1 - n2 == n3:
            self.operation_correct_answer.append(1)
        if n1 * n2 == n3:
            self.operation_correct_answer.append(2)
        if n2 != 0:
            if n1 / n2 == n3:
                self.operation_correct_answer.append(3)
        self.number_lines_list[0].set_text(str(n1))
        self.number_lines_list[1].set_text(str(n2))
        self.number_lines_list[2].set_text(str(n3))
        return

    def calculate_solved_score(self):
        remaining_time = min(self.timer_complete_time, self.timer_line_item.get_height() / self.adjustement_value)
        elapsed_time = self.timer_complete_time - remaining_time
        if elapsed_time <= self.average_time:
            time_score = 142.85 * (self.average_time - elapsed_time) / self.average_time
        else:
            time_score = 0
        return [100,
         time_score,
         -10 * self.wrong_answers]

    def create_character_happy_item(self):
        shoptender_happy_image = assets.load_image('p1_minigame_shoptender_happy.png')
        return ItemImage(459, 44, shoptender_happy_image, None)


