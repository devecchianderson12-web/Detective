from framework import assets, animations, text
from framework.stage import *
from pygame.time import delay
import random
WRONG_PLACE_DIALOG = 0
OPENING_DIALOG = 1
WITNESS_REQUEST = 2
WITNESS_MINIGAME = 3
WITNESS_GOODBYE = 4
WITNESS_THANKS = 5
WITNESS_AID = 6
WITNESS_AID_2 = 7
WITNESS_HELP = 8
SCORE_DIALOG = 9
SCORE_INCREMENT = 6
SCORE_DELAY = 35
SCORE_END_SOUND_DELAY = 0

class Minigame():

    def __init__(self, stage, phase1content, witness, play_statcode, solved_statcode, not_solved_statcode, score_category):
        self.stage = stage
        self.phase1content = phase1content
        self.witness = witness
        self.play_statcode = play_statcode
        self.solved_statcode = solved_statcode
        self.not_solved_statcode = not_solved_statcode
        self.score_category = score_category
        self.layer = Layer()
        self.score_layer = Layer()
        self.character_layer = Layer()
        self.witness_layer = Layer()
        self.help_layer = Layer()
        self.help_previous_layer = Layer()
        self.help_current_layer = Layer()
        self.active_dialog = None
        self.next = ''
        self.playing_minigame_music = False
        self.start_stage_music = False
        self.help_stage = 1
        self.max_help_stages = 3
        self.witness_opening_box_image = assets.load_image('p1_minigame_flux_dialogue1.png')
        self.witness_titler = assets.load_image('p1_minigame_flux_titler.png')
        self.font_24 = assets.load_font('powdrft_.ttf', 24)
        self.font_18 = assets.load_font('evilgeniusbb_bld.ttf', 18)
        self.font_13 = assets.load_font('evilgeniusbb_reg.ttf', 13)
        self.font_13_bld = assets.load_font('evilgeniusbb_bld.ttf', 13)
        self.font_12 = assets.load_font('evilgeniusbb_reg.ttf', 12)
        self.font_12_bld = assets.load_font('evilgeniusbb_bld.ttf', 12)
        self.font_14_bld = assets.load_font('evilgeniusbb_bld.ttf', 14)
        self.font_14 = assets.load_font('evilgeniusbb_reg.ttf', 14)
        self.option_hover_image = assets.load_image('p1_minigame_opening_flux_optionselector.gif')
        self.avatar_box_image = assets.load_image('p1_minigame_opening_flux_avatarboxdialogue.png')
        self.previous_image = assets.load_image('p0_button_previous_active.png')
        self.previous_rollover_image = assets.load_image('p0_button_previous_rollover.png')
        self.next_image = assets.load_image('p0_button_next_active.png')
        self.next_rollover_image = assets.load_image('p0_button_next_rollover.png')
        self.rollover_sound = self.stage.rollover_sound
        self.continue_sound = self.stage.click_sound
        self.help_sound = assets.load_sound('p0_help.ogg')
        return

    def show_witness_minigame(self):
        self.layer.empty()
        self.active_dialog = WITNESS_MINIGAME
        self.stage.prepare_dialog(self.character_layer)
        self.set_up_witness()
        self.stage.show_dialog(self.layer, self.minigame_dialog_handle_event)
        self.stage.add_layer(self.character_layer)
        self.stage.add_layer(self.witness_layer)
        self.set_up_minigame()
        ignore_layers = [self.character_layer, self.witness_layer]
        self.stage.set_music_volume(0, 600)
        self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, False, ignore_layers, self.blind_show_minigame_callback)
        return

    def show_opening_dialog(self):
        self.active_dialog = OPENING_DIALOG
        self.playing_minigame_music = False
        self.start_stage_music = False
        self.stop_stage_music()
        self.stage.prepare_dialog(self.character_layer, False, True)
        self.stage.show_dialog(self.layer, self.handle_event)
        self.stage.add_layer(self.character_layer)
        ignore_layers = [self.character_layer]
        self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, True, ignore_layers, self.blind_show_opening_callback)
        return

    def escape_key_event(self):
        return False

    def handle_event(self, e):
        if e.type == KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.stage.render()
                self.stage.click_sound.play()
                if self.active_dialog == OPENING_DIALOG:
                    self.close_minigame()
                    return True
                else:
                    self.show_next()
                    return True
            mod = self.get_common_modifiers(e.mod)
            if mod == pygame.KMOD_LSHIFT and e.key == K_z and self.stage.game.get_development_mode():
                self.stage.remove_layer(self.witness_layer)
                self.show_happy_character()
                self.stage.close_dialog(self.layer)
                self.active_dialog = WITNESS_AID
                self.show_witness_dialog(True)
        return

    def minigame_dialog_handle_event(self, e):
        if e.type == KEYDOWN:
            if e.key == pygame.K_ESCAPE and not self.escape_key_event():
                self.stage.render()
                self.stage.click_sound.play()
                if self.active_dialog == WITNESS_MINIGAME:
                    self.phase1content.minigame_solved(False)
                    self.close_minigame()
                else:
                    self.show_next()
                return True
        return self.minigame_handle_event(e)

    def minigame_handle_event(self, e):
        return

    def blind_show_opening_callback(self, layer):
        self.set_up_question_dialog()
        self.stage.add_layer(self.witness_layer)
        layers = [self.character_layer]
        self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, False, layers)
        return

    def set_up_question_dialog(self):
        self.set_up_witness_message_box(True)
        self.set_up_witness()
        self.set_up_avatar_box()
        return

    def set_up_score(self):
        self.scores = self.calculate_solved_score()
        self.total = 0
        for i in range(len(self.scores)):
            self.scores[i] = min(9999, max(-9999, int(self.scores[i])))
            self.total += self.scores[i]

        if self.total < 0:
            self.total = 0
        datastore = self.stage.game.datastore
        character_progress = datastore.user_character_progress
        character_progress.score += self.total
        datastore.add_score(self.score_category, datastore.user_character, self.total)
        datastore.add_score('total', datastore.user_character, character_progress.score)
        datastore.save_highscores()
        topbar_image = assets.load_image('p1_minigame_scores_topbar.png')
        topbar_item = ItemImage(0, 69, topbar_image)
        self.score_layer.add(topbar_item)
        bottombar_image = assets.load_image('p1_minigame_scores_bottombar.png')
        bottombar_item = ItemImage(0, 330, bottombar_image)
        self.score_layer.add(bottombar_item)
        self.score_font_24 = assets.load_font('turkey.ttf', 24)
        self.score_font_29 = assets.load_font('turkey.ttf', 29)
        self.score_loop_sound = assets.load_sound('score_loop.ogg')
        self.score_end_sound = assets.load_sound('score_end.ogg')
        return

    def add_score_item(self, item=None):
        score_count = len(self.scores)
        if self.score_item == 1:
            item_image = assets.load_image('p1_minigame_scores_game.png')
            if score_count == 3:
                self.score_text_top = 142
                self.score_value_top = 139
            else:
                self.score_text_top = 132
                self.score_value_top = 129
        elif self.score_item == 2:
            item_image = assets.load_image('p1_minigame_scores_bonus.png')
            if score_count == 3:
                self.score_text_top = 170
                self.score_value_top = 171
            else:
                self.score_text_top = 159
                self.score_value_top = 160
        elif self.score_item == 3 and score_count == 4:
            item_image = assets.load_image('p1_minigame_scores_usedletters.png')
            self.score_text_top = 194
            self.score_value_top = 191
        elif self.score_item == 4 or score_count == 3:
            item_image = assets.load_image('p1_minigame_scores_mistakes.png')
            if score_count == 3:
                self.score_text_top = 204
                self.score_value_top = 203
            else:
                self.score_text_top = 223
                self.score_value_top = 222
        item = ItemImage(120, self.score_text_top, item_image)
        self.score_layer.add(item)
        if self.skip_scores_animation:
            self.score_item_callback(item)
        else:
            animations.fade_in_item(item, 600, self.score_item_callback)
        return

    def add_total_item(self):
        score_count = len(self.scores)
        if score_count == 3:
            self.score_text_top = 258
            self.score_value_top = 254
        else:
            self.score_text_top = 268
            self.score_value_top = 264
        total_image = assets.load_image('p1_minigame_scores_total.png')
        total_item = ItemImage(120, self.score_text_top, total_image)
        self.score_layer.add(total_item)
        if self.skip_scores_animation:
            self.score_item_callback(total_item)
        else:
            animations.fade_in_item(total_item, 600, self.score_item_callback)
        return

    def add_score_continue(self):
        continue_normal = assets.load_image('p0_endings_btn_continue_normal.png')
        continue_rollover = assets.load_image('p0_endings_btn_continue_rollover.png')
        self.next = ItemImage(219, 322, continue_normal)
        self.next.set_rollover_image(continue_rollover, self.rollover_sound)
        self.next.add_event_handler(ItemEvent.CLICK, self.option_click)
        self.score_layer.add(self.next)
        self.score_continue_visible = True
        if self.skip_scores_animation:
            self.stage.render()
            self.score_end_sound.play()
            self.skip_scores_animation = False
        return

    def score_item_callback(self, item):
        if self.score_item <= len(self.scores):
            final_value = self.scores[self.score_item - 1]
        else:
            final_value = self.total
        self.score_increment = calculate_score_increment(SCORE_INCREMENT, final_value, self.scores[0])
        increments = _div(final_value , self.score_increment)
        score_time = int(increments * SCORE_DELAY)
        loop_length = self.score_loop_sound.get_length() * 1000
        sound_loops = int(_div((score_time + SCORE_END_SOUND_DELAY) , loop_length))
        if not self.skip_scores_animation:
            self.score_loop_sound.play(-1)
        self.score_text_value = 0
        if self.score_item <= len(self.scores):
            score_texts = self.add_text_with_shadow(self.score_layer, 391, self.score_value_top, self.score_font_24, text.format_number(self.score_text_value), (255,
                                                                                                                                                                 103,
                                                                                                                                                                 28), 51, 35, 3, 1, -3, 4)
        else:
            score_texts = self.add_text_with_shadow(self.score_layer, 381, self.score_value_top, self.score_font_29, text.format_number(self.score_text_value), (255,
                                                                                                                                                                 144,
                                                                                                                                                                 0), 67, 55, 3, 1, -3, 4)
        if increments == 0 or self.skip_scores_animation:
            delay_between_update = 0
        else:
            delay_between_update = max(0, _div((sound_loops * loop_length - SCORE_END_SOUND_DELAY) , increments))
        self.stage.start_timer('minigame_item_score', delay_between_update, self.update_score, score_texts, False, False)
        return

    def update_score(self, key, score_texts):
        if self.score_item <= len(self.scores):
            final_value = self.scores[self.score_item - 1]
        else:
            final_value = self.total
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
        for item in score_texts:
            item.set_text(text.format_number(self.score_text_value))

        if self.score_text_value == final_value:
            self.stage.stop_timer(key)
            delay = 200
            if self.skip_scores_animation:
                delay = 0
            if self.score_item < len(self.scores):
                self.score_item += 1
                animations.wait(self.stage, delay, self.add_score_item)
            elif self.score_item == len(self.scores):
                self.score_item += 1
                animations.wait(self.stage, delay, self.add_total_item)
            else:
                animations.wait(self.stage, delay, self.add_score_continue)
            self.stage.render()
            self.score_loop_sound.stop()
            if not self.skip_scores_animation:
                self.score_end_sound.play()
        return

    def add_text_with_shadow(self, layer, left, top, font, text, color, width, height, h_align, v_align, shadow_dx=-1, shadow_dy=2):
        shadow_item = ItemText(left + shadow_dx, top + shadow_dy, font, 0, text, (0,
                                                                                  0,
                                                                                  0), None, width, height, h_align, v_align)
        layer.add(shadow_item)
        text_item = ItemText(left, top, font, 0, text, color, None, width, height, h_align, v_align)
        layer.add(text_item)
        return (
         text_item, shadow_item)

    def set_up_witness_message_box(self, opening_dialog):
        if opening_dialog:
            image = self.witness_opening_box_image
        else:
            image = self.witness_minigame_box_image
        witness_box = ItemImage(56, 96, image, None)
        self.layer.add(witness_box)
        titler = ItemImage(136, 80, self.witness_titler)
        title_text = ItemText(142, 87, self.font_24, 0, self.title, (157, 21, 21), None, 272, 30, 2, 2)
        self.layer.add(titler)
        self.layer.add(title_text)
        if opening_dialog:
            text = self.question_intro
            self.box_text = ItemText(111, 134, self.font_13, 16, text, (0, 0, 0), None, 328, 68, 2, 2)
            self.layer.add(self.box_text)
            text = self.question
            self.box_text = ItemText(111, 212, self.font_14_bld, 16, text, (0, 0, 0), None, 328, 20, 2)
            self.layer.add(self.box_text)
        return

    def set_up_witness(self):
        self.witness_layer.remove(self.witness_item)
        self.witness_layer.add(self.witness_item)
        return

    def set_up_avatar_box(self):
        avatar_box = ItemImage(183, 280, self.avatar_box_image)
        self.layer.add(avatar_box)
        self.option_text_yes = ItemText(211, 294, self.font_13_bld, 0, 'SI', (79, 79,
                                                                              79), None, self.option_hover_image.get_width(), self.option_hover_image.get_height(), 2, 2)
        self.option_text_no = ItemText(211, 319, self.font_13_bld, 0, 'NO', (79, 79,
                                                                             79), None, self.option_hover_image.get_width(), self.option_hover_image.get_height(), 2, 2)
        self.option_text_yes.set_rollover(self.option_hover_image, self.rollover_sound, 0, 1)
        self.option_text_no.set_rollover(self.option_hover_image, self.rollover_sound, 0, 1)
        self.option_text_yes.set_rollover_color((132, 15, 15), None)
        self.option_text_no.set_rollover_color((132, 15, 15), None)
        self.option_text_yes.add_event_handler(ItemEvent.CLICK, self.option_click)
        self.option_text_no.add_event_handler(ItemEvent.CLICK, self.option_click)
        self.layer.add(self.option_text_yes)
        self.layer.add(self.option_text_no)
        return

    def option_click(self, item, args):
        self.stage.render()
        self.continue_sound.play()
        if item == self.next:
            self.show_next()
        elif item == self.option_text_yes:
            self.stage.close_dialog(self.layer)
            self.active_dialog = WITNESS_REQUEST
            self.show_witness_dialog(True)
        elif item == self.option_text_no:
            self.close_minigame()
        return

    def show_next(self):
        if self.active_dialog == WITNESS_REQUEST:
            self.stage.close_dialog(self.layer)
            self.show_witness_minigame()
        elif self.active_dialog == WITNESS_GOODBYE:
            self.phase1content.minigame_solved(False)
            self.close_minigame()
        elif self.active_dialog == SCORE_DIALOG:
            if self.score_continue_visible:
                self.stage.close_dialog(self.layer)
                self.active_dialog = WITNESS_THANKS
                self.show_witness_dialog(True)
            else:
                self.skip_scores_animation = True
        elif self.active_dialog == WITNESS_THANKS:
            self.stage.close_dialog(self.layer)
            self.active_dialog = WITNESS_AID
            self.show_witness_dialog(True)
        elif self.active_dialog == WITNESS_AID:
            self.stage.close_dialog(self.layer)
            self.active_dialog = WITNESS_AID_2
            self.show_witness_dialog(True)
        elif self.active_dialog == WITNESS_AID_2:
            self.close_minigame(1)
        elif self.active_dialog == WRONG_PLACE_DIALOG:
            self.close_minigame(2)
        return

    def show_witness_dialog(self, transition=False, blind_witness=False):
        self.layer.empty()
        self.stage.prepare_dialog(self.character_layer, False, True)
        self.stage.show_dialog(self.layer, self.handle_event)
        if len(self.score_layer.items) > 0:
            self.stage.add_layer(self.score_layer)
            animations.blind_layer(self.score_layer, animations.BlindDirection.HIDE_DOWN, None, 450, self.hide_score_callback)
        self.set_up_witness_message_box(False)
        self.set_up_witness()
        self.stage.add_layer(self.character_layer)
        self.stage.add_layer(self.witness_layer)
        text2 = ''
        if self.active_dialog == WITNESS_REQUEST:
            text2 = self.request_text
            text3 = self.request_question_text
            request_line_count = len(text3.splitlines())
            if request_line_count <= 1:
                box_text3 = ItemText(86, 195, self.font_14_bld, 16, text3, (0, 0, 0), None, 378, 34, 2, 3)
            else:
                box_text3 = ItemText(86, 195, self.font_12_bld, 16, text3, (0, 0, 0), None, 378, 36, 2, 3)
            self.layer.add(box_text3)
        elif self.active_dialog == WITNESS_GOODBYE:
            text2 = 'Gracias de todos modos.\nQuizás puedas ayudarme en otro momento.'
        elif self.active_dialog == WITNESS_THANKS:
            text2 = self.thanks_text
        elif self.active_dialog == WITNESS_AID:
            text2 = self.witness.witness_statement.intro_statement.text + '\n\n' + self.witness.witness_statement.janitor_statement.text
        elif self.active_dialog == WITNESS_AID_2:
            text2 = self.witness.witness_statement.identikit_statement.text
            if self.witness.witness_statement.location_statement:
                text2 += '\n\n' + self.witness.witness_statement.location_statement.text
        elif self.active_dialog == WRONG_PLACE_DIALOG:
            text2 = self.stage.game.datastore.list_statements[0].text
        if self.active_dialog != WITNESS_REQUEST:
            additional_fonts = {'bold': (self.font_14_bld, 15, -1)}
            x = 100
            from game.stages import minigamebricklayer
            if isinstance(self, minigamebricklayer.MinigameBricklayer):
                x -= 4
            self.box_text2 = ItemText(x, 116, self.font_14, 16, text2, (0, 0, 0), None, 340, 130, 2, 2, additional_fonts)
        elif request_line_count <= 1:
            self.box_text2 = ItemText(86, 129, self.font_13, 16, text2, (0, 0, 0), None, 378, 78, 2, 2)
        else:
            self.box_text2 = ItemText(86, 122, self.font_13, 16, text2, (0, 0, 0), None, 378, 78, 2, 2)
        self.layer.add(self.box_text2)
        if self.active_dialog == WRONG_PLACE_DIALOG:
            image = self.previous_image
            rollover_image = self.previous_rollover_image
        else:
            image = self.next_image
            rollover_image = self.next_rollover_image
        self.next = ItemImage(252, 232, image)
        self.next.set_rollover_image(rollover_image, self.rollover_sound)
        self.next.add_event_handler(ItemEvent.CLICK, self.option_click)
        self.layer.add(self.next)
        ignore_layers = [
         self.character_layer, self.score_layer]
        if transition and not blind_witness:
            ignore_layers.append(self.witness_layer)
        self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, not transition, ignore_layers)
        return

    def hide_score_callback(self, layer):
        self.score_layer.empty()
        return

    def show_dialog(self, active_dialog):
        self.active_dialog = active_dialog
        self.stop_stage_music()
        self.stage.prepare_dialog(self.character_layer, False, True)
        self.stage.show_dialog(self.layer, self.handle_event)
        self.stage.add_layer(self.character_layer)
        ignore_layers = [self.character_layer]
        self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, True, ignore_layers, self.blind_show_dialog_callback)
        return

    def stop_stage_music(self):
        if not self.start_stage_music and not self.playing_minigame_music:
            self.stage.set_music_volume(0, 450)
            self.start_stage_music = True
        return

    def show_score(self):
        self.active_dialog = SCORE_DIALOG
        self.score_continue_visible = False
        self.skip_scores_animation = False
        self.stage.prepare_dialog(self.character_layer, False, True)
        self.stage.show_dialog(self.layer, self.handle_event)
        self.set_up_score()
        self.set_up_witness()
        for l in self.minigame_above_layers:
            self.stage.add_layer(l)

        self.stage.add_layer(self.score_layer)
        self.stage.add_layer(self.character_layer)
        self.show_happy_character()
        if self.playing_minigame_music:
            self.stage.set_music_volume(0.7, 400)
        animations.blind_layer(self.score_layer, animations.BlindDirection.SHOW_DOWN, None, 450, self.show_score_callback)
        animations.blind_layer(self.witness_layer, animations.BlindDirection.SHOW_DOWN, None, 450, None)
        animations.blind_layer(self.layer, animations.BlindDirection.HIDE_DOWN, None, 450, None)
        animations.blind_layer(self.witness_worried_layer, animations.BlindDirection.HIDE_DOWN, None, 450, None)
        for l in self.minigame_above_layers:
            animations.blind_layer(l, animations.BlindDirection.HIDE_DOWN, None, 450, None)

        return

    def show_happy_character(self):
        self.witness_worried_layer = self.witness_layer
        self.stage.add_layer(self.witness_worried_layer)
        self.witness_layer = Layer()
        self.witness_item = self.create_character_happy_item()
        self.witness_layer.add(self.witness_item)
        self.stage.add_layer(self.witness_layer)
        return

    def show_score_callback(self, layer):
        self.layer.empty()
        self.score_item = 1
        self.add_score_item()
        return

    def show_wrong_place_dialog(self):
        self.show_dialog(WRONG_PLACE_DIALOG)
        return

    def blind_show_dialog_callback(self, layer):
        self.stage.close_dialog(self.layer)
        self.show_witness_dialog(True, True)
        return

    def close_minigame(self, result=0):
        self.stop_minigame_music()
        self.stop_minigame(result != 1)
        self.close_result = result
        ignore_layers = [self.character_layer]
        self.stage.blind_dialog(self.layer, animations.BlindDirection.HIDE_UP, True, ignore_layers, self.blind_close_callback)
        self.stage.reset_dialog(False, True)
        return

    def stop_minigame_music(self, fadems=400):
        if self.playing_minigame_music:
            self.playing_minigame_music = False
            self.start_stage_music = True
            self.stage.set_music_volume(0, fadems)
        return

    def blind_close_callback(self, layer):
        self.stage.close_dialog(self.layer)
        self.stage.reset_dialog()
        if self.start_stage_music:
            self.start_stage_music = False
            self.stage.play_phase_music()
        if self.close_result == 1:
            self.phase1content.minigame_solved(True)
        elif self.close_result == 2:
            self.stage.show_clues_with_fade(self.start_map_help_animation)
        return

    def start_map_help_animation(self, item=None):
        self.stage.start_map_help_animation()
        return

    def minigame_solved_callback(self):
        self.minigame_above_layers = []
        layer_found = False
        for l in self.stage.layers:
            if layer_found:
                if l != self.character_layer and l != self.witness_layer:
                    self.minigame_above_layers.append(l)
            elif l == self.layer:
                layer_found = True

        self.stop_minigame_music()
        self.stage.close_dialog(self.layer)
        self.show_score()
        return

    def show_help_dialog(self, close_callback=None):
        self.stage.show_dialog(self.help_layer, self.help_handle_event, callback=close_callback)
        self.stage.blind_dialog(self.help_layer, animations.BlindDirection.SHOW_DOWN, True, [], self.blind_show_help_callback)
        return

    def close_help_dialog(self):
        self.active_dialog = WITNESS_MINIGAME
        self.stage.blind_dialog(self.help_layer, animations.BlindDirection.HIDE_DOWN, True, [], self.blind_close_help_callback)
        return

    def help_handle_event(self, e):
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                self.stage.render()
                self.stage.click_sound.play()
                self.close_help_dialog()
                return True
        return

    def blind_show_help_callback(self, layer):
        self.set_up_help_dialog()
        self.set_up_help_data()
        self.stage.add_layer(self.help_previous_layer)
        self.stage.add_layer(self.help_current_layer)
        self.stage.blind_dialog(self.help_layer, animations.BlindDirection.SHOW_DOWN, False, [], None)
        self.stage.render()
        animations.wait(self.stage, 100, self.play_help_sound)
        return

    def play_help_sound(self):
        self.help_sound.play()
        return

    def set_up_help_dialog(self):
        self.font_14 = assets.load_font('evilgeniusbb_reg.ttf', 14)
        background_image = assets.load_image('p1_minigame_help_background.png')
        background_image_item = ItemImage(112, 24, background_image, None)
        self.help_layer.add(background_image_item)
        close_button_image = assets.load_image('p1_minigames_btn_play_normal.png')
        close_button_rollover_image = assets.load_image('p1_minigames_btn_play_rollover.png')
        self.next_button_image = assets.load_image('p1_minigames_btn_next_normal.png')
        self.next_button_rollover_image = assets.load_image('p1_minigames_btn_next_rollover.png')
        self.previous_button_image = assets.load_image('p1_minigames_btn_prev_normal.png')
        self.previous_button_rollover_image = assets.load_image('p1_minigames_btn_prev_rollover.png')
        self.help_close_button = ItemImage(262, 371, close_button_image, None)
        self.help_close_button.set_rollover_image(close_button_rollover_image, self.rollover_sound)
        self.help_next_button = ItemImage(356, 374, self.next_button_image, None)
        self.help_next_button.set_rollover_image(self.next_button_rollover_image, self.rollover_sound)
        self.help_previous_button = ItemImage(220, 374, self.previous_button_image, None)
        self.help_previous_button.set_rollover_image(self.previous_button_rollover_image, self.rollover_sound)
        self.help_close_button.add_event_handler(ItemEvent.CLICK, self.help_button_click)
        self.help_next_button.add_event_handler(ItemEvent.CLICK, self.help_button_click)
        self.help_previous_button.add_event_handler(ItemEvent.CLICK, self.help_button_click)
        self.help_layer.add(self.help_close_button)
        self.help_layer.add(self.help_next_button)
        self.help_layer.add(self.help_previous_button)
        return

    def help_button_click(self, item, args):
        self.stage.render()
        self.continue_sound.play()
        if item == self.help_close_button:
            self.close_help_dialog()
        elif self.active_dialog == WITNESS_HELP:
            if item == self.help_next_button:
                self.help_stage += 1
            else:
                self.help_stage -= 1
            self.help_previous_button.set_visible(self.help_stage > 1)
            self.help_next_button.set_visible(self.help_stage < self.max_help_stages)
            self.set_up_help_data()
        elif item == self.help_previous_button:
            self.help_stage -= 1
            self.set_up_help_data()
            if self.help_stage == self.max_help_stages - 1:
                self.help_next_button.set_visible(True)
            elif self.help_stage == 2:
                self.help_previous_button.set_visible(False)
        return

    def clean_help_dialog(self):
        if self.active_dialog == WITNESS_MINIGAME:
            self.active_dialog = WITNESS_HELP
            self.help_stage = 1
            self.help_previous_button.set_visible(False)
        return

    def set_up_help_data(self):
        items = []
        for item in self.help_current_layer.items:
            items.append(item)

        self.help_previous_layer.empty()
        self.help_current_layer.empty()
        for item in items:
            self.help_previous_layer.add(item)

        self.clean_help_dialog()
        self.load_help_data()
        if len(self.help_previous_layer.items) > 0:
            animations.stop_blind_layer(self.help_current_layer)
            animations.stop_blind_layer(self.help_previous_layer)
            self.help_previous_layer.set_clip(None)
            animations.blind_layer(self.help_current_layer, animations.BlindDirection.SHOW_DOWN, self.help_current_layer.get_bounds(), 350, None, False)
            animations.blind_layer(self.help_previous_layer, animations.BlindDirection.HIDE_DOWN, self.help_previous_layer.get_bounds(), 350, None, False)
        return

    def blind_close_help_callback(self, layer):
        self.help_layer.empty()
        self.help_previous_layer.empty()
        self.help_current_layer.empty()
        self.stage.close_dialog(self.help_layer)
        self.start_minigame()
        return

    def help_click(self, item, args):
        self.stop_minigame(False)
        self.stage.set_music_volume(0, 600)
        self.show_help_dialog()
        return

    def loose_game(self):
        self.active_dialog = WITNESS_GOODBYE
        self.stage.close_dialog(self.layer)
        self.stage.reset_dialog()
        self.show_witness_dialog(True)
        return

    def stop_minigame(self, solved):
        return

    def start_minigame(self):
        return

    def start_play_stats_event(self):
        self.stage.game.stats.start_time_event(self.play_statcode)
        return

    def end_play_stats_event(self, solved):
        if solved:
            accumulate = self.solved_statcode
        else:
            accumulate = self.not_solved_statcode
        self.stage.game.stats.end_time_event(self.play_statcode, accumulate)
        return

    def play_music(self):
        music_loop = self.get_music()
        self.stage.play_music(None, music_loop)
        self.playing_minigame_music = True
        return

    def set_up_minigame(self):
        raise Exception('minigame not implemented')
        return

    def get_common_modifiers(self, mod):
        return mod & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL | pygame.KMOD_LALT | pygame.KMOD_RALT | pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT)


def calculate_score_increment(score_increment, final_value, base_score):
    increment = max(score_increment, max(_div(final_value , 30), _div(base_score , 30)))
    increment -= increment % 10
    increment += 8
    return increment


