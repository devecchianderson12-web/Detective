from framework.stage import *
from framework import animations, text, web
from framework.animations import BlindDirection
from game.data import datastore, statcodes, datamodel, serialization
import random, des
from . import minigame, merits

class EndReason:
    TIME_UP = 0
    ARRIVED_LOCATION = 1
    ARRIVED_WRONG_LOCATION = 2


class EndGame:

    def __init__(self, stage, reason):
        self.stage = stage
        self.reason = reason
        self.layer = Layer()
        self.font_13 = assets.load_font('evilgeniusbb_reg.ttf', 13)
        self.font_13_bold = assets.load_font('evilgeniusbb_bld.ttf', 13)
        self.font_14 = assets.load_font('evilgeniusbb_reg.ttf', 14)
        self.font_14_bold = assets.load_font('evilgeniusbb_bld.ttf', 14)
        self.font_16 = assets.load_font('evilgeniusbb_reg.ttf', 16)
        self.font_18 = assets.load_font('evilgeniusbb_reg.ttf', 18)
        self.rollover_sound = assets.load_sound('GUI_roll_over.ogg')
        self.continue_sound = assets.load_sound('GUI_Click.ogg')
        if reason == EndReason.TIME_UP:
            self.bell_sound = assets.load_sound('P0_Clock_Ring.ogg')
        else:
            self.right_sound = assets.load_sound('p1_minigame_right.ogg')
            self.medal_sound = assets.load_sound('p0_medal_bugle.ogg')
            self.promotion_sound = assets.load_sound('p0_promotion_bugle.ogg')
        self.case_solved = self.case_is_solved()
        self.caught_thief = self.stage.game.datastore.user_character_progress.case.caught_thief
        self.next_visible = False
        self.continue_visible = False
        self.score_continue_visible = False
        return

    def build_fast_click(self):
        self.screen_mask = ItemMask(0, 0, (600, 450))
        self.screen_mask.add_event_handler(ItemEvent.CLICK, self.screen_click)
        self.layer.add(self.screen_mask)
        return

    def screen_click(self, item, args):
        self.screen_next(True)
        return

    def screen_next(self, fast=False):
        if self.effect_number != 0:
            if not self.continue_button_layer:
                self.stage.stop_timers()
                self.show_blinds_down_effect(fast)
        return

    def show_final_screen(self, blind_background):
        self.layer.empty()
        self.continue_button_layer = None
        self.stage.show_dialog(self.layer, self.final_screen_handle_event)
        self.set_up_final_screen()
        self.effect_number = 0
        self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, blind_background, [], self.blind_show_final_callback)
        self.build_fast_click()
        return

    def blind_show_final_callback(self, layer):
        self.build_left_box()
        return

    def final_screen_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.continue_sound.play()
            if self.continue_visible:
                self.continue_with_next()
            elif self.score_continue_visible:
                self.score_continue()
            else:
                self.screen_next(True)
        return

    def set_up_final_screen(self):
        case = self.stage.game.datastore.user_character_progress.case
        newspaper_image = assets.load_image('p0_endings_newspaper.png')
        newspaper_item_image = ItemImage(59, 27, newspaper_image, None)
        self.layer.add(newspaper_item_image)
        thief_image = assets.load_image(case.thief.identikit_large_image_front)
        thief_image_side = assets.load_image(case.thief.identikit_large_image_side)
        thief_item_image = ItemImage(85, 188, thief_image, None)
        thief_item_image_side = ItemImage(217, 188, thief_image_side, None)
        self.layer.add(thief_item_image)
        self.layer.add(thief_item_image_side)
        if self.case_solved and self.caught_thief:
            header_image = assets.load_image('p0_endings_newspaper_win_header.gif')
            jail_image = assets.load_image('p0_endings_win_jail.png')
            jail_item_image = ItemImage(85, 188, jail_image, None)
            self.layer.add(jail_item_image)
            case = self.stage.game.datastore.user_character_progress.case
            self.calculate_score()
            self.add_resolved_case()
            self.add_medal()
        else:
            header_image = assets.load_image('p0_endings_newspaper_loose_header.gif')
        header_item_image = ItemImage(81, 111, header_image, None)
        self.layer.add(header_item_image)
        return

    def calculate_score(self):
        datastore = self.stage.game.datastore
        character_progress = datastore.user_character_progress
        case = character_progress.case
        level = character_progress.range.level
        self.clues_found = len(case.clues_found)
        self.remaining_turns = case.time_limit - case.time_spend
        self.scores = [
         1000 + level * 1000,
         100 * self.clues_found,
         self.remaining_turns * (100 + level * 100)]
        self.total_score = 0
        for score in self.scores:
            self.total_score += score

        character_progress.score += self.total_score
        datastore.add_score('total', datastore.user_character, character_progress.score)
        datastore.save_highscores()
        return

    def add_resolved_case(self):
        character_progress = self.stage.game.datastore.user_character_progress
        character_progress.resolved_cases += 1
        self.promoted = character_progress.range.update()
        case = character_progress.case
        if case.thief not in character_progress.captured_thieves:
            character_progress.captured_thieves.append(case.thief)
        dep = character_progress.case.crime_location.department
        if dep not in character_progress.list_departments_solved:
            character_progress.list_departments_solved.append(dep)
        return

    def add_tutorial_medal(self):
        character_progress = self.stage.game.datastore.user_character_progress
        case = character_progress.case
        self.medal_name = case.crime_location.department.image
        character_progress.add_medal('tut')
        return

    def add_medal(self):
        character_progress = self.stage.game.datastore.user_character_progress
        case = character_progress.case
        self.medal_name = case.crime_location.department.image
        character_progress.add_medal(case.crime_location.department.image)
        department_medals = {}
        uy_medals = 0
        for department in self.stage.game.datastore.list_departments:
            department_medals[department.image] = 0

        for medal in character_progress.medals:
            if medal.name in department_medals:
                department_medals[medal.name] = medal.count
            elif medal.name == 'uy':
                uy_medals = medal.count

        won_uy_medals = 999
        for (medal, count) in list(department_medals.items()):
            if count < won_uy_medals:
                won_uy_medals = count

        self.won_uy_medal = False
        while uy_medals < won_uy_medals:
            character_progress.add_medal('uy')
            uy_medals += 1
            self.won_uy_medal = True

        return

    def build_continue_button(self, fast=False):
        self.continue_button_layer = Layer()
        continue_image = assets.load_image('p0_endings_btn_continue_normal.png')
        continue_rollover_image = assets.load_image('p0_endings_btn_continue_rollover.png')
        self.continue_button = ItemImage(421, 395, continue_image)
        self.continue_button.set_rollover_image(continue_rollover_image, self.rollover_sound)
        self.continue_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.continue_button_layer.add(self.continue_button)
        if fast:
            self.show_blinds_down_effect()
        else:
            animations.wait(self.stage, 1000, self.show_blinds_down_effect)
        return

    def build_left_box(self):
        self.left_box_layer = Layer()
        left_box = assets.load_image('p0_endings_win+loose_d2_back.png')
        left_box_image = ItemImage(7, 50, left_box)
        self.left_box_layer.add(left_box_image)
        if self.case_solved and self.caught_thief:
            character_name = self.stage.game.datastore.user_character.charinfo.name
            message = '¡Felicitaciones! &#f:f14!Agente&#f!\n\n' + '&#c102,0,0!&#f:f16!' + character_name + '&#f!&#c!\n'
            additional_fonts = {'f14': (self.font_14, 13), 'f16': (
                     self.font_16, 15)}
            text = ItemText(32, 60, self.font_14_bold, 13, message, (54, 45, 45), None, 264, 70, 2, 2, additional_fonts)
            self.left_box_layer.add(text)
        else:
            text1 = ItemText(59, 68, self.font_14_bold, 13, 'Mejor suerte', (54, 45,
                                                                             45), None, 120, 20, 2, 2)
            text2 = ItemText(174, 69, self.font_14, 13, 'La próxima', (54, 45,
                                                                           45), None, 90, 20, 2, 2)
            text3 = ItemText(117, 85, self.font_14, 13, 'vez agente', (54, 45, 45), None, 90, 20, 2, 2)
            self.left_box_layer.add(text3)
            agent_text = ItemText(63, 105, self.font_16, 15, self.stage.game.datastore.user_character.charinfo.name, (102,
                                                                                                                      0,
                                                                                                                      0), None, 196, 20, 2, 2)
            self.left_box_layer.add(agent_text)
            self.left_box_layer.add(text1)
            self.left_box_layer.add(text2)
        self.effect_number = 1
        animations.wait(self.stage, 2500, self.show_blinds_down_effect)
        return

    def show_blinds_down_effect(self, fast=False):
        if self.effect_number != 0:
            if self.effect_number == 1:
                self.stage.add_layer(self.left_box_layer)
                self.effect_number = 2
                self.build_right_box()
            elif self.effect_number == 2:
                self.stage.add_layer(self.right_box_layer)
                self.effect_number = 3
                self.build_continue_button(fast)
            elif self.effect_number == 3:
                self.continue_visible = True
                self.stage.add_layer(self.continue_button_layer)
        return

    def build_right_box(self):
        self.right_box_layer = Layer()
        if self.reason == EndReason.ARRIVED_LOCATION:
            if self.case_solved and self.caught_thief:
                right_box = assets.load_image('p0_endings_win_d3_back.png')
                right_box_image = ItemImage(413, 317, right_box)
                self.right_box_layer.add(right_box_image)
                text1 = ItemText(425, 321, self.font_14_bold, 16, '¡Has resuelto este caso!', (0,
                                                                                                   0,
                                                                                                   0), None, 140, 60, 2, 2)
                self.right_box_layer.add(text1)
            elif self.caught_thief is None:
                right_box = assets.load_image('p0_endings_loose_d3_back.png')
                right_box_image = ItemImage(346, 304, right_box)
                text1 = ItemText(362, 322, self.font_13, 16, 'Debes prestar', (0, 0,
                                                                               0), None, 100, 20, 2, 2)
                text2 = ItemText(441, 320, self.font_13_bold, 16, 'Más atención', (0,
                                                                                          0,
                                                                                          0), None, 150, 20, 2, 2)
                text3 = ItemText(565, 322, self.font_13, 16, 'a', (0, 0, 0), None, 20, 20, 2, 2)
                text4 = ItemText(396, 338, self.font_13, 16, 'los', (0, 0, 0), None, 30, 20, 2, 2)
                text5 = ItemText(423, 336, self.font_13_bold, 16, 'datos', (0, 0, 0), None, 50, 20, 2, 2)
                text6 = ItemText(457, 338, self.font_13, 16, 'que te den', (0, 0, 0), None, 100, 20, 2, 2)
                text7 = ItemText(420, 354, self.font_13, 16, 'los', (0, 0, 0), None, 30, 20, 2, 2)
                text8 = ItemText(448, 352, self.font_13_bold, 16, 'testigos.', (0,
                                                                                0,
                                                                                0), None, 75, 20, 2, 2)
                self.right_box_layer.add(right_box_image)
                self.right_box_layer.add(text1)
                self.right_box_layer.add(text2)
                self.right_box_layer.add(text3)
                self.right_box_layer.add(text4)
                self.right_box_layer.add(text5)
                self.right_box_layer.add(text6)
                self.right_box_layer.add(text7)
                self.right_box_layer.add(text8)
            else:
                right_box = assets.load_image('p0_endings_loose_d3_back.png')
                right_box_image = ItemImage(346, 304, right_box)
                text1 = ItemText(362, 322, self.font_13, 16, 'Intenta ser más rápido', (0,
                                                                                               0,
                                                                                               0), None, 220, 52, 2, 2)
                self.right_box_layer.add(right_box_image)
                self.right_box_layer.add(text1)
        elif self.reason == EndReason.TIME_UP:
            right_box = assets.load_image('p0_endings_loose_d3_back.png')
            right_box_image = ItemImage(346, 304, right_box)
            self.right_box_layer.add(right_box_image)
            text1 = ItemText(348, 301, self.font_14, 16, 'intenta estudiar &#f:bld!más detalladamente&#f! las pistas.', (0,
                                                                                                                             0,
                                                                                                                             0), None, right_box_image.get_width(), right_box_image.get_height(), 2, 2, additional_fonts={'bld': (self.font_14_bold, 18, 0)})
            self.right_box_layer.add(text1)
        animations.wait(self.stage, 1000, self.show_blinds_down_effect)
        return

    def show_opening_dialog(self, blind_background=True):
        if self.caught_thief is not None and not self.caught_thief:
            self.next_button = None
            self.show_final_screen(blind_background)
        else:
            self.stage.show_dialog(self.layer, self.openining_handle_event)
            if blind_background:
                self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, blind_background, [], self.blind_show_opening_callback)
            else:
                self.blind_show_opening_callback()
        return

    def blind_show_opening_callback(self, layer=None):
        self.set_up_opening_dialog()
        self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, False, [])
        if self.reason == EndReason.TIME_UP:
            animations.wait(self.stage, 40, self.play_bell)
        return

    def score_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.continue_sound.play()
            if self.continue_visible:
                self.continue_with_next()
            elif self.score_continue_visible:
                self.score_continue()
            elif self.showing_scores and not self.skip_scores_animation:
                self.skip_scores_animation = True
            elif self.next_visible:
                self.go_next()
        return

    def openining_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.stage.render()
            self.continue_sound.play()
            if self.next_visible:
                self.go_next()
        return

    def play_bell(self):
        self.stage.render()
        self.bell_sound.play()
        return

    def set_up_opening_dialog(self):
        if self.reason == EndReason.ARRIVED_LOCATION:
            if self.case_solved:
                dialog_box_image = assets.load_image('p0_endings_win_d1_back.png')
                left = 95
                top = 15
                box_text_w = 336
                box_text_h = 212
                next_button_x = 282
                next_button_y = 303
            else:
                dialog_box_image = assets.load_image('p0_endings_loose_d1_back.png')
                left = 101
                top = 19
                box_text_w = 336
                box_text_h = 212
                next_button_x = 282
                next_button_y = 330
        elif self.reason == EndReason.ARRIVED_WRONG_LOCATION:
            dialog_box_image = assets.load_image('p0_endings_win_d1_back.png')
            left = 95
            top = 15
            box_text_w = 336
            box_text_h = 212
            next_button_x = 282
            next_button_y = 303
        elif self.reason == EndReason.TIME_UP:
            dialog_box_image = assets.load_image('p0_endings_notime_box.png')
            left = 134
            top = 92
            next_button_x = 282
            next_button_y = 292
        dialog_box = ItemImage(left, top, dialog_box_image, None)
        self.layer.add(dialog_box)
        case = self.stage.game.datastore.user_character_progress.case
        thief = case.thief
        if self.reason == EndReason.ARRIVED_LOCATION:
            thief_name = case.thief.name
            final_department_name = case.list_departments[len(case.list_departments) - 1].name
            stolen_obj = case.stolen_object.description2
            text1 = ItemText(262, 92, self.font_14, 14, 'Al llegar a', (0, 0, 0), None, box_text_w, box_text_h)
            dep_text = ItemText(136, 22, self.font_18, 14, final_department_name, (102,
                                                                                   0,
                                                                                   0), None, box_text_w, box_text_h, 2, 2)
            thief_text = ItemText(135, 117, self.font_18, 14, thief_name + ',', (102,
                                                                                 0,
                                                                                 0), None, box_text_w, box_text_h, 2, 2)
            self.layer.add(dep_text)
            self.layer.add(thief_text)
        elif self.reason == EndReason.ARRIVED_WRONG_LOCATION:
            thief_name = case.thief.name
            department_name = case.last_department_visited.name
            stolen_obj = case.stolen_object.description2
            text1 = ItemText(262, 92, self.font_14, 14, 'Al llegar a', (0, 0, 0), None, box_text_w, box_text_h)
            dep_text = ItemText(136, 26, self.font_18, 14, department_name, (102, 0,
                                                                             0), None, box_text_w, box_text_h, 2, 2)
            self.layer.add(dep_text)
        elif self.reason == EndReason.TIME_UP:
            text = 'Lamentablemente el tiempo que tenías para resolver el caso se &#f:bld!acabó&#f!.\n\n' + 'Seguramente el ladrón se encuentra &#f:bld!demasiado lejos&#f! para poder rastrearlo.'
            text1 = ItemText(182, 168, self.font_14, 14, text, (0, 0, 0), None, 243, 111, 2, 2, additional_fonts={'bld': (self.font_14_bold, 0, -1)})
            self.stage.game.stats.increment_count_event(statcodes.ENDGAME_TIME_UP)
        self.layer.add(text1)
        if self.reason == EndReason.ARRIVED_LOCATION:
            if self.case_solved:
                if self.caught_thief is None:
                    if thief.sex == datastore.MALE:
                        gender = 'o'
                    else:
                        gender = 'a'
                    case.thief_car_color = random.choice(list(datastore.THIEF_CAR_COLORS.keys()))
                    text2 = ItemText(137, 65, self.font_14, 14, 'Te pones rápidamente en contacto con las autoridades locales y luego de algunas indagaciones descubren que', (0,
                                                                                                                                                                                   0,
                                                                                                                                                                                   0), None, box_text_w, box_text_h, 2, 2)
                    text3 = ItemText(134, 144, self.font_14, 14, 'se encuentra huyendo hacia la carretera en un auto color ' + datastore.THIEF_CAR_COLORS[case.thief_car_color], (0,
                                                                                                                                                                                  0,
                                                                                                                                                                                  0), None, box_text_w, box_text_h, 2, 2)
                    stolen_obj_text = ItemText(136, 183, self.font_16, 14, '¡Debes perseguirl' + gender + ' y atraparl' + gender + '!', (102,
                                                                                                                                             0,
                                                                                                                                             0), None, box_text_w, box_text_h, 2, 2)
                    thief_text.set_top(105)
                    self.layer.add(stolen_obj_text)
                elif self.caught_thief:
                    text1.set_visible(False)
                    dep_text.set_visible(False)
                    if thief.sex == datastore.MALE:
                        gender = 'o'
                    else:
                        gender = 'a'
                    text2 = ItemText(137, 34, self.font_14, 14, 'Una vez arrestad' + gender, (0,
                                                                                              0,
                                                                                              0), None, box_text_w, box_text_h, 2, 2)
                    text3 = ItemText(134, 102, self.font_14, 14, 'confiesa el crimen\n y te entrega', (0,
                                                                                                       0,
                                                                                                       0), None, box_text_w, box_text_h, 2, 2)
                    stolen_obj_text = ItemText(136, 137, self.font_18, 14, stolen_obj + '.', (102,
                                                                                              0,
                                                                                              0), None, box_text_w, box_text_h, 2, 2)
                    thief_text.set_top(64)
                    self.layer.add(stolen_obj_text)
                    self.stage.game.stats.increment_count_event(statcodes.ENDGAME_SOLVED)
            else:
                text2 = ItemText(136, 70, self.font_14, 14, 'Te pones rápidamente en contacto con las autoridades locales y luego de algunas indagaciones dan con el paradero del ladrón que resulta ser', (0,
                                                                                                                                                                                                                   0,
                                                                                                                                                                                                                   0), None, box_text_w, box_text_h, 2, 2)
                if thief.sex == datastore.MALE:
                    gender = 'o'
                else:
                    gender = 'a'
                text3 = ItemText(136, 173, self.font_14, 14, 'Lamentablemente no tienes una orden de arresto en su contra.\n\nAsí que te ves obligado a dejarl' + gender + ' en\nlibertad.', (0,
                                                                                                                                                                                                  0,
                                                                                                                                                                                                  0), None, box_text_w, box_text_h, 2, 2)
                self.stage.game.stats.increment_count_event(statcodes.ENDGAME_BAD_ORDER)
            self.layer.add(text2)
            self.layer.add(text3)
        elif self.reason == EndReason.ARRIVED_WRONG_LOCATION:
            text2 = ItemText(136, 85, self.font_14, 14, 'Te pones rápidamente en contacto con las autoridades locales y luego de investigar exhaustivamente &#f:bld!no encuentran rastros de la persona que buscas&#f!.', (0,
                                                                                                                                                                                                                               0,
                                                                                                                                                                                                                               0), None, box_text_w, box_text_h, 2, 2, additional_fonts={'bld': (self.font_14_bold, 0, -1)})
            text3 = ItemText(136, 156, self.font_14, 14, 'Seguramente se encuentre en otro departamento, estudia más detalladamente las pistas que encontraste en su escondite.', (0,
                                                                                                                                                                                       0,
                                                                                                                                                                                       0), None, box_text_w, box_text_h, 2, 2)
            self.layer.add(text2)
            self.layer.add(text3)
        next_image = assets.load_image('p0_button_next_active.png')
        next_rollover_image = assets.load_image('p0_button_next_rollover.png')
        self.next_button = ItemImage(next_button_x, next_button_y, next_image)
        self.next_button.set_rollover_image(next_rollover_image, self.rollover_sound)
        self.next_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.next_visible = True
        self.layer.add(self.next_button)
        if self.reason == EndReason.TIME_UP:
            clock_images = [
             assets.load_image('p0_endings_notime_reloj_stand.png'),
             assets.load_image('p0_endings_notime_reloj_ring1.png'),
             assets.load_image('p0_endings_notime_reloj_ring2.png')]
            clock_iterations = [0]
            clock = ItemImage(245, 67, clock_images[0])
            self.layer.add(clock)

            def animate_clock():
                clock_iterations[0] += 1
                clock.set_image(clock_images[clock_iterations[0] % 3])
                if clock_iterations[0] < 12:
                    animations.wait(self.stage, 80, animate_clock)
                return

            animations.wait(self.stage, 80, animate_clock)
        return

    def button_click(self, item, args):
        self.stage.render()
        self.continue_sound.play()
        if item == self.next_button:
            self.go_next()
        elif item == self.continue_button:
            self.continue_with_next()
        return

    def go_next(self):
        self.next_visible = False
        if self.reason == EndReason.ARRIVED_WRONG_LOCATION:
            hide_background = True
        else:
            hide_background = False
        if self.reason == EndReason.ARRIVED_LOCATION and self.case_solved and self.caught_thief is None:
            self.stage.set_phase(3)
        else:
            self.stage.blind_dialog(self.layer, animations.BlindDirection.HIDE_DOWN, hide_background, [], self.blind_next_callback)
        return

    def continue_with_next(self):
        self.continue_visible = False
        self.hide_layers()
        k = des.des(datastore.SCORE_KEY, des.CBC, datastore.SCORE_IV, pad=None, padmode=des.PAD_PKCS5)
        import base64
        score = base64.b64encode(k.encrypt(str(self.stage.game.datastore.get_highscore_data())))
        web.send_data(datastore.STATS_URL, {'current': (datastore.VERSION), 'stats': (self.stage.game.stats.get_data()), 'score': score}, compressed=True)
        if self.reason != EndReason.ARRIVED_LOCATION or not self.case_solved or not self.caught_thief:
            animations.wait(self.stage, 500, self.restart_game)
        else:
            animations.wait(self.stage, 500, self.show_score)
        return

    def hide_layers(self):
        for layer in self.stage.layers:
            animations.blind_layer(layer, animations.BlindDirection.HIDE_DOWN, None)

        return

    def blind_next_callback(self, layer):
        self.stage.close_dialog(self.layer)
        if self.reason == EndReason.ARRIVED_WRONG_LOCATION:
            self.wrong_location_callback()
        else:
            self.show_final_screen(False)
        return

    def restart_game(self):
        from game.stages import startscreen
        initial_stage = startscreen.StartScreenStage(self.stage.game, True)
        self.stage.game.set_stage(initial_stage)
        datastore = self.stage.game.datastore
        datastore.user_character_stage = None
        datastore.save_character('nc', True)
        datastore.save_characters()
        return

    def show_score(self):
        self.showing_scores = True
        self.skip_scores_animation = False
        self.stage.render()
        self.score_back_layer = Layer()
        self.score_layer = Layer()
        self.score_font_20 = assets.load_font('turkey.ttf', 20)
        self.score_font_24 = assets.load_font('turkey.ttf', 24)
        self.score_font_29 = assets.load_font('turkey.ttf', 29)
        self.score_font_42 = assets.load_font('turkey.ttf', 42)
        self.handcuff_sound = assets.load_sound('p0_score_handcuffs.ogg')
        self.clock_sound = assets.load_sound('GUI_Clock.ogg')
        background_image = assets.load_image('p0_endgame_scores_background.jpg')
        self.background_item = ItemImage(0, 0, background_image)
        self.score_layer.add(self.background_item)
        title_image = assets.load_image('p0_endgame_scores_title.png')
        title_white_image = assets.load_image('p0_endgame_scores_title_white.png')
        x = 172
        self.title = ItemImage(x, 147, title_image)
        self.title_white = ItemImage(x, 182, title_white_image)
        self.continue_normal = assets.load_image('p0_endings_btn_continue_normal.png')
        self.continue_rollover = assets.load_image('p0_endings_btn_continue_rollover.png')
        self.score_loop_sound = assets.load_sound('score_loop.ogg')
        self.score_end_sound = assets.load_sound('score_end.ogg')
        self.timer_big_hands = [
         assets.load_image('p0_timer_70_bighand_001.png'),
         assets.load_image('p0_timer_70_bighand_002.png'),
         assets.load_image('p0_timer_70_bighand_003.png'),
         assets.load_image('p0_timer_70_bighand_004.png'),
         assets.load_image('p0_timer_70_bighand_005.png'),
         assets.load_image('p0_timer_70_bighand_006.png'),
         assets.load_image('p0_timer_70_bighand_007.png'),
         assets.load_image('p0_timer_70_bighand_008.png')]
        self.timer_short_hands = [assets.load_image('p0_timer_70_shorthand_001.png'),
         assets.load_image('p0_timer_70_shorthand_002.png'),
         assets.load_image('p0_timer_70_shorthand_003.png'),
         assets.load_image('p0_timer_70_shorthand_004.png'),
         assets.load_image('p0_timer_70_shorthand_005.png'),
         assets.load_image('p0_timer_70_shorthand_006.png'),
         assets.load_image('p0_timer_70_shorthand_007.png'),
         assets.load_image('p0_timer_70_shorthand_008.png'),
         assets.load_image('p0_timer_70_shorthand_009.png'),
         assets.load_image('p0_timer_70_shorthand_010.png'),
         assets.load_image('p0_timer_70_shorthand_011.png'),
         assets.load_image('p0_timer_70_shorthand_012.png')]
        self.timer_handcenter = assets.load_image('p0_timer_70_handcenter.png')
        self.stage.show_dialog(self.score_back_layer, self.score_handle_event, None)
        self.stage.add_layer(self.score_layer)
        self.stage.blind_dialog(self.score_back_layer, BlindDirection.SHOW_DOWN, False, [], self.blind_show_score_callback)
        return

    def blind_show_score_callback(self, layer):
        self.stage.render()
        self.right_sound.play()
        self.score_layer.add(self.title_white)
        final_title_x = 147
        final_title_y = 300
        if self.skip_scores_animation:
            self.title_white.set_left(final_title_x)
            self.title_white.set_top(final_title_y)
            self.move_score_title_callback(self.title_white)
        else:
            animations.fade_in_item(self.title_white, 300)
            animations.start_move(self.title_white, self.title_white.get_left(), final_title_x, final_title_y, None, None, self.move_score_title_callback)
        return

    def move_score_title_callback(self, item):
        self.score_layer.add(self.title)
        if self.skip_scores_animation:
            self.score_layer.remove(self.title_white)
        else:
            animations.fade_in_item(self.title, 330)
            animations.fade_out_item(self.title_white, True, 330)
        case = self.stage.game.datastore.user_character_progress.case
        self.department_name = case.crime_location.department.name
        department_text = '-' + text.to_upper(self.department_name) + '-'
        x = 171
        y = 195
        self.department = ItemText(x, y, self.score_font_20, 0, department_text, (255,
                                                                                  212,
                                                                                  12), None, 259, 30, 2, 1)
        self.department_shadow = ItemText(x - 2, y + 3, self.score_font_20, 0, department_text, (0,
                                                                                                 0,
                                                                                                 0), None, 259, 30, 2, 1)
        self.score_layer.add(self.department_shadow)
        self.score_layer.add(self.department)
        final_shadow_alpha = 80
        if self.skip_scores_animation:
            self.department_shadow.set_alpha(final_shadow_alpha)
            self.show_title_callback(self.department_shadow)
        else:
            animations.fade_in_item(self.department, 330, None)
            animations.fade_in_item(self.department_shadow, 330, self.show_title_callback, final_shadow_alpha)
        return

    def show_title_callback(self, item):
        if self.skip_scores_animation:
            self.wait_show_title_callback()
        else:
            animations.wait(self.stage, 1500, self.wait_show_title_callback)
        return

    def wait_show_title_callback(self):
        accel = (0.5, 0.5, 1)
        x = self.title.get_left()
        self.score_item = 1
        self.clues_found_icons = 0
        self.score_scene = 1
        title_final_y = 33
        department_final_x = 171
        department_final_y = 81
        department_shadow_final_x = department_final_x - 2
        department_shadow_final_y = department_final_y + 3
        if self.skip_scores_animation:
            self.title.set_top(title_final_y)
            self.department.set_lefttop(department_final_x, department_final_y)
            self.department_shadow.set_lefttop(department_final_x, department_final_y)
            self.add_score_item(self.department_shadow)
        else:
            animations.start_move(self.title, x, title_final_y, 400, accel, None)
            animations.start_move(self.department, department_final_x, department_final_y, 400, accel, None)
            animations.start_move(self.department_shadow, department_shadow_final_x, department_shadow_final_y, 400, accel, None, self.add_score_item)
        return

    def add_score_item(self, item=None):
        if self.score_item == 1:
            item_image = assets.load_image('p0_endgame_scores_s1_optArrested.png')
            x = 73
            y = 133
        elif self.score_item == 2:
            item_image = assets.load_image('p0_endgame_scores_s1_optClues.png')
            x = 73
            y = 168
        elif self.score_item == 3:
            item_image = assets.load_image('p0_endgame_scores_s1_optTime.png')
            x = 75
            y = 204
        elif self.score_item == 4:
            item_image = assets.load_image('p0_endgame_scores_s1_optTotal.png')
            x = 134
            y = 255
        item = ItemImage(x, y, item_image)
        self.score_layer.add(item)
        if self.skip_scores_animation:
            self.add_item_icon(item)
        else:
            animations.fade_in_item(item, 270, self.add_item_icon)
        return

    def add_item_icon(self, item=None):
        if self.score_item == 1:
            icon_image = assets.load_image('p0_endgame_scores_s1_iconArrested.png')
            item = ItemImage(279, 126, icon_image)
            self.score_layer.add(item)
            if not self.skip_scores_animation:
                self.stage.render()
                self.handcuff_sound.play()
            self.dots = 26
            dot_y = 134
        elif self.score_item == 2:
            if self.clues_found_icons == 0:
                self.icon_image = assets.load_image('p0_endgame_scores_s1_iconClues.png')
                self.clue_sound = assets.load_sound('p0_score_clue.ogg')
            x = 269 + self.clues_found_icons * 23
            clue_item = ItemImage(x, 162, self.icon_image)
            self.score_layer.add(clue_item)
            self.clues_found_icons += 1
            if not self.skip_scores_animation:
                self.stage.render()
                self.clue_sound.play()
            if self.clues_found >= 3:
                self.dots = 20 - int((self.clues_found - 3) * 4.5)
            else:
                self.dots = 26
            dot_y = 168
        elif self.score_item == 3:
            icon_image = assets.load_image('p0_timer_70_backclock.png')
            item = ItemImage(283, 199, icon_image)
            self.score_layer.add(item)
            if not self.skip_scores_animation:
                self.stage.render()
                self.clock_sound.play()
            self.timer_days = self.stage.timer_days
            self.timer_hour = self.stage.timer_hour
            self.timer_minute_pos = self.stage.timer_minute_pos
            self.timer_big_hand = ItemImage(289, 207, self.timer_big_hands[self.timer_minute_pos])
            self.score_layer.add(self.timer_big_hand)
            short_hand_image = self.stage.get_short_hand_image(self.timer_hour, self.timer_minute_pos, self.timer_short_hands)
            self.timer_short_hand = ItemImage(289, 208, short_hand_image)
            self.score_layer.add(self.timer_short_hand)
            timer_handcenter = ItemImage(297, 216, self.timer_handcenter)
            self.score_layer.add(timer_handcenter)
            self.dots = 26
            dot_y = 204
        elif self.score_item == 4:
            self.dots = 34
            dot_y = 253
        if self.score_item == 2 and self.clues_found_icons < self.clues_found:
            if self.skip_scores_animation:
                self.add_item_icon()
            else:
                animations.wait(self.stage, 200, self.add_item_icon)
        else:
            if self.score_item <= 3:
                dot_x = 456 - self.score_font_24.size('.' * self.dots)[0]
                font = self.score_font_24
                height = 40
            else:
                dot_x = 203
                font = self.score_font_29
                height = 50
            self.dotted_line = ItemText(dot_x, dot_y, font, 0, '', (244, 208, 11), None, 188, height, 1, 1)
            if self.score_item <= 3:
                dy = 2
            else:
                dy = 3
            self.dotted_line_shadow = ItemText(dot_x - 1, dot_y + dy, font, 0, '', (0,
                                                                                    0,
                                                                                    0), None, 188, height, 1, 1)
            self.score_layer.add(self.dotted_line_shadow)
            self.score_layer.add(self.dotted_line)
            if self.score_item <= 3:
                self.dotted_line_shadow.set_alpha(140)
            if self.skip_scores_animation:
                self.add_next_dot()
            else:
                animations.wait(self.stage, 200, self.add_next_dot)
        return

    def add_next_dot(self):
        if self.dots == 1:
            text = self.dotted_line.get_text() + '.'
            self.dots -= 1
        else:
            text = self.dotted_line.get_text() + '..'
            self.dots -= 2
        self.dotted_line.set_text(text)
        self.dotted_line_shadow.set_text(text)
        if self.dots > 0:
            if self.skip_scores_animation:
                self.add_next_dot()
            else:
                animations.wait(self.stage, 15, self.add_next_dot)
        elif self.skip_scores_animation:
            self.add_item_score()
        else:
            animations.wait(self.stage, 30, self.add_item_score)
        return

    def add_item_score(self, item=None):
        self.score_text_value = 0
        if self.score_item == 1:
            x = 442
            y = 132
            final_value = self.scores[0]
        elif self.score_item == 2:
            x = 442
            y = 166
            final_value = self.scores[1]
        elif self.score_item == 3:
            x = 442
            y = 202
            final_value = self.scores[2]
            character_progress = self.stage.game.datastore.user_character_progress
            time_limit = character_progress.case.get_time_limit()
            self.timer_steps = (time_limit[0] * 12 + time_limit[1] - (self.stage.timer_days * 12 + self.stage.timer_hour)) * len(self.timer_big_hands)
        elif self.score_item == 4:
            x = 380
            y = 252
            final_value = self.total_score
        else:
            x = 321
            y = 322
            character_progress = self.stage.game.datastore.user_character_progress
            final_value = character_progress.score
        if self.score_item <= 3:
            font = self.score_font_24
            color = (255, 144, 0)
            width = 80
            height = 40
        elif self.score_item == 4:
            font = self.score_font_29
            color = (255, 144, 0)
            width = 90
            height = 40
        else:
            font = self.score_font_42
            color = (255, 212, 12)
            width = 170
            height = 60
        score_item = ItemText(x, y, font, 0, '0', color, None, width, height, 3, 1)
        score_item_shadow = ItemText(x - 2, y + 3, font, 0, '0', (0, 0, 0), None, width, height, 3, 1)
        self.score_layer.add(score_item_shadow)
        self.score_layer.add(score_item)
        if self.score_item == 5:
            self.total_score_item = score_item
            self.total_score_item_shadow = score_item_shadow
        self.score_increment = minigame.calculate_score_increment(minigame.SCORE_INCREMENT * 10, final_value, self.scores[0])
        if self.score_item == 3:
            if self.timer_steps != 0:
                self.score_increment = min(self.score_increment, int(_div(final_value , (self.timer_steps * 0.7))))
        if self.score_increment == 0:
            increments = 0
        else:
            increments = _div(final_value , self.score_increment)
        score_time = int(increments * minigame.SCORE_DELAY)
        loop_length = self.score_loop_sound.get_length() * 1000
        sound_loops = int(_div((score_time + minigame.SCORE_END_SOUND_DELAY) , loop_length))
        if increments == 0 or self.skip_scores_animation:
            delay_between_update = 0
        else:
            delay_between_update = max(0, _div((sound_loops * loop_length - minigame.SCORE_END_SOUND_DELAY) , increments))
        if not self.skip_scores_animation:
            self.stage.render()
        self.stage.start_timer('endgame_item_score', delay_between_update, self.update_score, [score_item, score_item_shadow, final_value], False, False)
        if self.score_item == 3:
            if self.timer_steps != 0:
                if self.skip_scores_animation:
                    timer_delay = 0
                else:
                    timer_delay = _div(float(score_time) , self.timer_steps)
                self.stage.start_timer('engame_score_timer', timer_delay, self.update_timer)
        self.score_channel = pygame.mixer.find_channel()
        self.score_channel.set_volume(assets.SOUND_VOLUME)
        if not self.skip_scores_animation:
            if sound_loops > 0:
                self.score_channel.play(self.score_loop_sound.sound, -1)
        return

    def update_score(self, key, data):
        final_value = data[2]
        if final_value >= 0:
            self.score_text_value += self.score_increment
            if self.score_text_value > final_value:
                self.score_text_value = final_value
        else:
            self.score_text_value -= self.score_increment
            if self.score_text_value < final_value:
                self.score_text_value = final_value
        if self.skip_scores_animation:
            self.score_text_value = final_value
        data[0].set_text(text.format_number(self.score_text_value))
        data[1].set_text(text.format_number(self.score_text_value))
        if self.score_text_value == final_value:
            self.stage.stop_timer(key)
            delay = 200
            if self.skip_scores_animation:
                delay = 0
            if self.score_item < 4:
                self.score_item += 1
                animations.wait(self.stage, delay, self.add_score_item)
            elif self.score_item == 4:
                self.score_item += 1
                animations.wait(self.stage, delay, self.add_total_item)
            else:
                animations.wait(self.stage, delay, self.add_score_continue)
            if self.score_channel != None:
                if not self.skip_scores_animation:
                    self.stage.render()
                    self.score_channel.play(self.score_end_sound.sound)
                else:
                    self.score_channel.stop()
        return

    def update_timer(self, key, data):
        timer_updated = False
        while not timer_updated:
            self.timer_minute_pos += 1
            if self.timer_minute_pos >= len(self.timer_big_hands):
                self.timer_minute_pos = 0
                self.timer_hour += 1
                if self.timer_hour >= 24:
                    self.timer_hour = 0
            self.timer_big_hand.set_image(self.timer_big_hands[self.timer_minute_pos])
            self.timer_short_hand.set_image(self.stage.get_short_hand_image(self.timer_hour, self.timer_minute_pos, self.timer_short_hands))
            self.timer_steps -= 1
            if self.timer_steps <= 0:
                self.timer_steps = 0
            if self.skip_scores_animation:
                if self.timer_steps == 0:
                    timer_updated = True
            else:
                timer_updated = True

        if self.timer_steps == 0:
            self.stage.stop_timer(key)
        return

    def add_total_item(self):
        total_image = assets.load_image('p0_endgame_scores_totalscores.png')
        total_item = ItemImage(101, 324, total_image)
        self.score_layer.add(total_item)
        self.total_score_label = total_item
        if self.skip_scores_animation:
            self.add_item_score(total_item)
        else:
            animations.fade_in_item(total_item, 340, self.add_item_score)
        return

    def add_score_continue(self):
        self.next = ItemImage(224, 399, self.continue_normal)
        self.next.set_rollover_image(self.continue_rollover, self.rollover_sound)
        self.next.add_event_handler(ItemEvent.CLICK, self.score_continue_click)
        self.score_layer.add(self.next)
        self.score_continue_visible = True
        if self.skip_scores_animation:
            self.stage.render()
            self.score_end_sound.play()
            self.skip_scores_animation = False
        return

    def score_continue_click(self, item, args):
        self.stage.render()
        self.continue_sound.play()
        self.score_continue()
        return

    def score_continue(self):
        self.showing_scores = False
        if self.score_scene == 1:
            next_scene = 2
        elif self.score_scene == 2:
            if self.won_uy_medal:
                next_scene = 3
            elif self.promoted:
                next_scene = 4
            else:
                next_scene = None
        elif self.score_scene == 3:
            if self.promoted:
                next_scene = 4
            else:
                next_scene = None
        else:
            next_scene = None
        self.score_continue_visible = False
        if next_scene == None:
            self.hide_layers()
            animations.wait(self.stage, 500, self.restart_game)
        elif self.score_scene == 1:
            score_back_items = [
             self.background_item,
             self.title,
             self.department_shadow,
             self.department,
             self.total_score_item_shadow,
             self.total_score_item,
             self.total_score_label]
            for item in score_back_items:
                self.score_layer.remove(item)
                self.score_back_layer.add(item)

        self.next_scene = next_scene
        animations.blind_layer(self.score_layer, animations.BlindDirection.HIDE_DOWN, None, 600, self.blind_next_scene_callback)
        return

    def blind_next_scene_callback(self, layer):
        for item in self.score_back_layer.items:
            item.set_visible(True)

        self.score_layer.empty()
        self.score_layer.set_clip(None)
        self.score_scene = self.next_scene
        if self.score_scene == 2:
            animations.wait_locked(self.stage, 100, self.show_medal_won)
        elif self.score_scene == 3:
            animations.wait_locked(self.stage, 100, self.show_medal_uy_won)
        elif self.score_scene == 4:
            animations.wait_locked(self.stage, 100, self.show_promotion)
        return

    def show_medal_won(self):
        self.stage.render()
        medal_data = merits.MEDALS_DATA[self.medal_name]
        ribbon = medal_data[3]
        if ribbon == None:
            ribbon_image = assets.load_image('p0_merits_medals_big_ribbon_' + self.medal_name + '.png')
        else:
            ribbon_image = assets.load_image('p0_merits_medals_big_ribbon_' + str(ribbon) + '.png')
        ribbon_item = ItemImage(157, 109, ribbon_image)
        self.score_layer.add(ribbon_item)
        base_image = assets.load_image('p0_merits_medals_big_genericbase.png')
        base_item = ItemImage(154, 211, base_image)
        self.score_layer.add(base_item)
        tab_image = assets.load_image('p0_merits_medals_tab_' + self.medal_name + '.jpg')
        tab_item = ItemImage(176, 223, tab_image)
        self.score_layer.add(tab_item)
        text = ItemText(295, 142, self.font_13_bold, 15, 'En reconocimiento a tu\ndesempeño en este caso,\nla intendencia de', (255,
                                                                                                                                    255,
                                                                                                                                    255), None, 215, 63, 1, 1)
        self.score_layer.add(text)
        text = ItemText(295, 199, self.font_16, 15, self.department_name, (255, 212,
                                                                           12), None, 215, 24, 1, 1)
        self.score_layer.add(text)
        text = ItemText(295, 231, self.font_13_bold, 15, '¡ha decidido condecorarte\ncon una medalla!', (255,
                                                                                                             255,
                                                                                                             255), None, 225, 53, 1, 1)
        self.score_layer.add(text)
        self.stage.set_music_volume(0.2, 300)
        animations.wait(self.stage, 200, self.play_medal_sound)
        return

    def play_medal_sound(self):
        self.stage.render()
        self.medal_sound.play()
        animations.wait(self.stage, self.medal_sound.get_length() * 1000, self.play_achievement_sound_callback)
        return

    def play_promotion_sound(self):
        self.stage.render()
        self.promotion_sound.play()
        animations.wait(self.stage, self.medal_sound.get_length() * 1000, self.play_achievement_sound_callback)
        return

    def play_achievement_sound_callback(self):
        self.stage.set_music_volume(1, 300)
        self.add_score_continue()
        return

    def show_medal_tut_won(self, item=None):
        self.stage.render()
        medal_image = assets.load_image('p0_merits_medals_big_tut.png')
        medal_item = ItemImage(122, 95, medal_image)
        self.score_layer.add(medal_item)
        begin_highlight = '&#c255,212,12!'
        end_highlight = '&#c!'
        message = 'Por haber completado\n' + 'satisfactoriamente tu\n' + 'entrenamiento y haber\n' + 'demostrado que eres\n' + 'apto para combatir a la\n' + begin_highlight + 'organización criminal CULT' + end_highlight + ',\n' + 'la División Especial de\n' + 'Detectives te hace entrega\n' + 'de esta medalla.'
        text = ItemText(293, 127, self.font_13_bold, 15, message, (255, 255, 255), None, 291, 144, 1, 1)
        self.score_layer.add(text)
        self.stage.set_music_volume(0.2, 300)
        animations.wait(self.stage, 200, self.play_medal_sound)
        return

    def show_medal_uy_won(self, item=None):
        self.stage.render()
        title_uy_image = assets.load_image('p0_endgame_scores_title_uy.png')
        title_uy = ItemImage(155, 26, title_uy_image)
        self.score_layer.add(title_uy)
        self.title.set_visible(False)
        self.department.set_visible(False)
        self.department_shadow.set_visible(False)
        self.total_score_item_shadow.set_visible(False)
        self.total_score_item.set_visible(False)
        self.total_score_label.set_visible(False)
        medal_image = assets.load_image('p0_merits_medals_big_uy.png')
        medal_item = ItemImage(212, 158, medal_image)
        self.score_layer.add(medal_item)
        begin_bold = '&#f:bold!'
        end_bold = '&#f!'
        message = 'En reconocimiento a tu ' + begin_bold + 'continuo esfuerzo' + end_bold + ' a la hora de\n' + 'combatir a la ' + begin_bold + 'organización criminal CULT' + end_bold + ', y por haber\n' + 'resuelto al menos un caso en ' + begin_bold + 'cada departamento' + end_bold + ' del país,\n' + 'las autoridades de la nación han decidido\n' + 'condecorarte con esta medalla.'
        additional_fonts = {'bold': (self.font_13_bold, 15, -2)}
        text = ItemText(85, 90, self.font_13, 15, message, (255, 255, 255), None, 430, 115, 2, 1, additional_fonts)
        self.score_layer.add(text)
        self.stage.set_music_volume(0.2, 300)
        animations.wait(self.stage, 200, self.play_medal_sound)
        return

    def show_promotion(self):
        self.stage.render()
        character = self.stage.game.datastore.user_character
        character_progress = self.stage.game.datastore.user_character_progress
        resolved_cases = character_progress.resolved_cases
        if resolved_cases == 11 or resolved_cases == 12:
            suffix = 'mo'
        else:
            last_digit = resolved_cases % 10
            if last_digit == 0:
                suffix = 'mo'
            elif last_digit == 1:
                suffix = 'er'
            elif last_digit == 2:
                suffix = 'do'
            elif last_digit == 3:
                suffix = 'er'
            elif last_digit <= 6:
                suffix = 'to'
            elif last_digit == 7:
                suffix = 'mo'
            elif last_digit == 8:
                suffix = 'vo'
            elif last_digit >= 9:
                suffix = 'no'
        begin_highlight = '&#c255,212,12!'
        end_highlight = '&#c!'
        begin_large = '&#f:large!'
        end_large = '&#f!'
        message = 'Por haber resuelto con éxito tu ' + begin_highlight + begin_large + str(character_progress.resolved_cases) + suffix + end_large + end_highlight + ' caso, y haber\n' + 'demostrado grandes habilidades a la hora de combatir a\n' + 'la malvada organización ' + begin_highlight + 'CULT' + end_highlight + ', la División Especial de \n' + 'Detectives ha decidido otorgarte un ascenso.'
        additional_fonts = {'large': (self.font_16, 15, -1)}
        message_item = ItemText(44, 114, self.font_13_bold, 15, message, (255, 255,
                                                                          255), None, 511, 73, 2, 1, additional_fonts)
        self.score_layer.add(message_item)
        congratulations_image = assets.load_image('p0_endgame_scores_s3_congratulations.png')
        congratulations = ItemImage(240, 196, congratulations_image)
        self.score_layer.add(congratulations)
        turkey_30 = assets.load_font('turkey.ttf', 30)
        range_name = text.to_upper(datamodel.get_range_name(character_progress.range.level))
        range_shadow = ItemText(41, 224, turkey_30, 0, range_name, (0, 0, 0), None, 514, 50, 2, 1)
        self.score_layer.add(range_shadow)
        char_range = ItemText(43, 221, turkey_30, 0, range_name, (255, 212, 12), None, 514, 50, 2, 1)
        self.score_layer.add(char_range)
        character_name = text.to_upper(character.charinfo.name)
        name_shadow = ItemText(21, 254, turkey_30, 29, character_name, (0, 0, 0), None, 554, 90, 2, 1)
        self.score_layer.add(name_shadow)
        name = ItemText(23, 251, turkey_30, 29, character_name, (255, 212, 12), None, 554, 90, 2, 1)
        self.score_layer.add(name)
        self.stage.set_music_volume(0.2, 300)
        animations.wait(self.stage, 200, self.play_promotion_sound)
        return

    def case_is_solved(self):
        case = self.stage.game.datastore.user_character_progress.case
        if case.arrest_order_thief:
            if case.thief == case.arrest_order_thief:
                return True
            else:
                return False
        else:
            return False
        return


