from game.data import statcodes
from game.stages import notes, folder, map, merits, help
from framework import animations, text
from framework.assets import *
from framework.stage import *
from framework.animations import BlindDirection
from . import endgame
GRID_ORIGIN = (
 300, 105)
GRID_CELL_WIDTH = 24
GRID_CELL_HEIGHT = 12
GRID_SIZE = (22, 22)

class Phase0Stage(StageIso):

    def __init__(self, game, initial_phase, save_state=True):
        StageIso.__init__(self, game, None, None, None)
        self.seting_timer = False
        self.checking_ending = False
        self.phase_number = initial_phase
        self.load_phase_number = initial_phase
        self.phase = None
        self.loading_phase = False
        self.during_night = False
        self.initialized = False
        self.minigame = None
        self.minigame_started = False
        self.showing_help = False
        self.showing_mainmenu = False
        self.update_time_callbacks = []
        self.arrest_order_warning_shown = False
        self.save_state_on_next_load_phase = save_state
        self.folder_animation_locks = 0
        self.pending_folder_animation = False
        if self.game.get_development_mode():
            import sys
            if '--medals' in sys.argv:
                character_progress = self.game.datastore.user_character_progress
                if len(character_progress.medals) == 0:
                    character_progress.add_medal('uy')
                    for department in self.game.datastore.list_departments:
                        character_progress.add_medal(department.image)

        return

    def initialize(self):
        self.__load_phase(self.load_phase_number)
        return

    def close(self):
        self.game.stats.end_time_event(statcodes.PHASE_PREFIX + str(self.phase_number))
        return

    def initialize_stage(self):
        self.items_found = []
        self.clue_items = []
        self.bar_7_rounds = 72
        self.options_layer = Layer()
        self.info_layer = Layer()
        self.night_layer = Layer()
        self.background_layer = Layer()
        self.background_layer.add(ItemImage(0, 0, assets.load_image('p0_stage_background.jpg')))
        self.click_sound = assets.load_sound('GUI_Click.ogg')
        self.rollover_sound = assets.load_sound('GUI_roll_over.ogg')
        self.popup_sound = assets.load_sound('GUI_Pop_Up.ogg')
        self.witness_popup_sound = assets.load_sound('GUI_Witness_Popup.ogg')
        self.open_map_sound = assets.load_sound('GUI_Map.ogg')
        self.case_open_sound = assets.load_sound('GUI_Turn_Page.ogg')
        self.notes_open_sound = assets.load_sound('GUI_Notes_Open.ogg')
        self.bounce_sound = assets.load_sound('GUI_bounce.ogg')
        self.night_sound = assets.load_sound('Night.ogg')
        self.clock_sound = assets.load_sound('GUI_Clock.ogg')
        self.fade_sound = assets.load_sound('fade.ogg')
        self.font = assets.load_font('freesansbold.ttf', 13)
        self.set_up_options()
        self.set_up_locator()
        self.set_up_timer()
        self.set_up_character()
        self.info_items = self.info_layer.items[:]
        self.map = map.Map(self, True, False)
        self.folder = folder.Folder(self)
        self.folder_default_tab = folder.CASE
        return

    def set_phase(self, phase, force_reload=False):
        if self.load_phase_number != phase or force_reload:
            self.loading_phase = True
            self.game.stats.end_time_event(statcodes.PHASE_PREFIX + str(self.phase_number))
            self.load_phase_number = phase
            self.save_state_on_next_load_phase = True
            self.stop_music()
            self.set_music(None, None)
            self.stop_timer('load_phase')
            if self.initialized:
                loading_image = 'p0_loading_slides_00' + str(phase) + '.jpg'
                self.game.show_loading(self.__show_loading_callback, loading_image)
        return

    def prepare_items_set(self, stage, large, item_definitions=None):
        set_name = 'p2s01'
        if large:
            stage.set_grid_definition(GRID_ORIGIN, GRID_CELL_WIDTH, GRID_CELL_HEIGHT, 2)
            stage.set_items(set_name, 'l', item_definitions)
        else:
            stage.set_grid_definition(GRID_ORIGIN, GRID_CELL_WIDTH, GRID_CELL_HEIGHT, 1)
            stage.set_items(set_name)
        return

    def start_minigame(self, name):
        self.minigame = name
        return

    def set_up_locator(self):
        dep = self.game.datastore.user_character_progress.case.last_department_visited
        image = assets.load_image('p0_locator_backbar.png')
        self.locator_bar = ItemImage(10, 19, image)
        self.info_layer.add(self.locator_bar)
        image = assets.load_image('p0_locator_backmap.png')
        self.locator_back = ItemImage(18, 10, image)
        self.info_layer.add(self.locator_back)
        image = assets.load_image('p0_locator_dept_' + dep.image + '.png')
        locator_pos = dep.locator_pos
        self.locator_sel = ItemImage(locator_pos[0], locator_pos[1], image)
        self.info_layer.add(self.locator_sel)
        self.locator_font = assets.load_font('evilgeniusbb_reg.ttf', 14)
        dep_name = text.to_upper(dep.name)
        self.locator_text = ItemText(75, 22, self.locator_font, 0, dep_name, (255,
                                                                              255,
                                                                              255))
        self.info_layer.add(self.locator_text)
        return

    def set_up_timer(self):
        self.timer_items = []
        image = assets.load_image('p0_timer_backbar.png')
        self.timer_backbar = ItemImage(401, 19, image)
        self.info_layer.add(self.timer_backbar)
        self.timer_items.append(self.timer_backbar)
        image = assets.load_image('p0_timer_backclock.png')
        timer_backclock = ItemImage(531, 5, image)
        self.info_layer.add(timer_backclock)
        self.timer_items.append(timer_backclock)
        self.timer_big_hands = [
         assets.load_image('p0_timer_bighand_001.png'),
         assets.load_image('p0_timer_bighand_002.png'),
         assets.load_image('p0_timer_bighand_003.png'),
         assets.load_image('p0_timer_bighand_004.png'),
         assets.load_image('p0_timer_bighand_005.png'),
         assets.load_image('p0_timer_bighand_006.png'),
         assets.load_image('p0_timer_bighand_007.png'),
         assets.load_image('p0_timer_bighand_008.png')]
        self.timer_short_hands = [assets.load_image('p0_timer_shorthand_001.png'),
         assets.load_image('p0_timer_shorthand_002.png'),
         assets.load_image('p0_timer_shorthand_003.png'),
         assets.load_image('p0_timer_shorthand_004.png'),
         assets.load_image('p0_timer_shorthand_005.png'),
         assets.load_image('p0_timer_shorthand_006.png'),
         assets.load_image('p0_timer_shorthand_007.png'),
         assets.load_image('p0_timer_shorthand_008.png'),
         assets.load_image('p0_timer_shorthand_009.png'),
         assets.load_image('p0_timer_shorthand_010.png'),
         assets.load_image('p0_timer_shorthand_011.png'),
         assets.load_image('p0_timer_shorthand_012.png')]
        last_snore = assets.load_image('p0_timer_snore_006.png')
        self.timer_snoore_animation = [assets.load_image('p0_timer_snore_001.png'),
         assets.load_image('p0_timer_snore_002.png'),
         assets.load_image('p0_timer_snore_003.png'),
         assets.load_image('p0_timer_snore_004.png'),
         assets.load_image('p0_timer_snore_005.png'),
         last_snore,
         last_snore,
         last_snore,
         last_snore]
        self.timer_snore = ItemImage(52, 213, self.timer_snoore_animation[0])
        self.timer_big_hand = ItemImage(538, 16, self.timer_big_hands[0])
        self.info_layer.add(self.timer_big_hand)
        self.timer_items.append(self.timer_big_hand)
        self.timer_short_hand = ItemImage(538, 17, self.timer_short_hands[0])
        self.info_layer.add(self.timer_short_hand)
        self.timer_items.append(self.timer_short_hand)
        image = assets.load_image('p0_timer_handcenter.png')
        timer_handcenter = ItemImage(550, 29, image)
        self.info_layer.add(timer_handcenter)
        self.timer_items.append(timer_handcenter)
        self.timer_text = ItemText(402, 22, self.locator_font, 0, '', (255, 255, 255), None, 128, 18, 3, 1)
        self.info_layer.add(self.timer_text)
        self.timer_items.append(self.timer_text)
        self.timer_days = 99999
        self.timer_hour = 99999
        self.timer_minute_pos = 0
        return

    def fade_out_timer(self, callback=None):
        for item in self.timer_items:
            animations.fade_out_item(item, False, 450, callback)
            callback = None

        return

    def fade_in_timer(self, callback=None):
        for item in self.timer_items:
            animations.fade_in_item(item, 450, callback)
            callback = None

        return

    def __set_timer_position(self, pos):
        x_base, y_base = self.timer_backbar.get_left(), self.timer_backbar.get_top()
        for item in self.timer_items:
            x_rel, y_rel = item.get_left() - x_base, item.get_top() - y_base
            item.set_lefttop(pos[0] + x_rel, pos[1] + y_rel)

        return

    def __animate_timer(self, end, time, callback):
        x_base, y_base = self.timer_backbar.get_left(), self.timer_backbar.get_top()
        dx = end[0] - x_base

        def animate_callback(item):
            if callback:
                callback()
            return

        for item in self.timer_items:
            x_rel, y_rel = item.get_left() - x_base, item.get_top() - y_base
            animations.start_move(item, end[0] + x_rel, end[1] + y_rel, time, (0.2,
                                                                               0.2,
                                                                               1), None, animate_callback)
            animate_callback = None

        return

    def update_timer_clock(self, item, data):
        self.stop_timer('timer_clock')
        if self.timer_days > self.timer_to_days or self.timer_days == self.timer_to_days and self.timer_hour > self.timer_to_hour:
            self.timer_days = self.timer_to_days
            self.timer_hour = self.timer_to_hour
            self.timer_minute_pos = 0
            update_text = True
        else:
            self.timer_minute_pos += 1
            if self.timer_minute_pos < 8:
                update_text = False
            else:
                update_text = True
                self.timer_minute_pos = 0
                self.timer_hour += 1
                if self.timer_hour >= 24:
                    self.timer_hour = 0
                    self.timer_days += 1
        if self.timer_hour >= 12 and self.timer_hour < 20:
            turns = self.game.datastore.user_character_progress.case.get_turns(self.timer_days, self.timer_hour)
            turns_left = self.time_limit - turns
            if turns_left <= 4:
                self.timer_text.set_color((104, 0, 0))
            elif turns_left <= 8:
                self.timer_text.set_color((247, 207, 69))
            else:
                self.timer_text.set_color((255, 255, 255))
        self.timer_big_hand.set_image(self.timer_big_hands[self.timer_minute_pos])
        short_hand_image = self.get_short_hand_image(self.timer_hour, self.timer_minute_pos, self.timer_short_hands)
        self.timer_short_hand.set_image(short_hand_image)
        if update_text:
            text = 'DÍA ' + str(self.timer_days) + ' - '
            if self.timer_hour < 10:
                text += '0' + str(self.timer_hour)
            else:
                text += str(self.timer_hour)
            text += ':00 HS.'
            self.timer_text.set_text(text)
        if self.timer_minute_pos == 0:
            if self.timer_hour == 20:
                if not self.contains_layer(self.night_layer):
                    self.render()
                    self.start_night()
            elif self.timer_hour == 8:
                if self.contains_layer(self.night_layer):
                    self.render()
                    self.end_night()
        if self.timer_hour == self.timer_to_hour and self.timer_days == self.timer_to_days:
            self.release_folder_help()
            self.unlock_ui()
            self.invoke_update_timer_callbacks()
            self.check_ending()
        else:
            self.start_timer('timer_clock', 32, self.update_timer_clock, None)
            if self.timer_minute_pos == 0:
                if self.timer_hour >= 12 and self.timer_hour < 20:
                    self.clock_sound.play()
        return

    def get_short_hand_image(self, day_hour, minute_pos, timer_short_hands):
        if day_hour >= 12:
            day_hour -= 12
        short_pos = day_hour * 4 + _div(minute_pos , 2)
        if short_pos < 12:
            return timer_short_hands[short_pos]
        elif short_pos < 24:
            return timer_short_hands[11 - (short_pos - 12)].flip_v_copy()
        elif short_pos < 36:
            return timer_short_hands[short_pos - 24].flip_hv_copy()
        else:
            return timer_short_hands[11 - (short_pos - 36)].flip_h_copy()
        return

    def start_night(self):
        if not self.__ending_visible:
            self.during_night = True
            self.render()
            self.night_sound.play()
            self.set_music_volume(0.2, 500)
            self.night_character_layer = self.character_icon.get_layer()
            if self.night_character_layer != None:
                self.night_character_layer.remove(self.character_icon)
            self.update_character_rollover()
            self.night_layer.add(self.character_icon)
            self.night_layer.add(self.character_asleep_icon)
            self.show_dialog(self.night_layer, None, (1, 35, 84, 178))
            self.blind_dialog(self.night_layer, animations.BlindDirection.SHOW_DOWN, True, [self.night_layer], self.start_night_callback)
            animations.fade_in_item(self.character_asleep_icon, 350)
            animations.wait(self, 50, self.night_hide_character)
        return

    def night_hide_character(self):
        animations.fade_out_item(self.character_icon, 130)
        return

    def start_night_callback(self, layer):
        self.timer_snore.set_image(self.timer_snoore_animation[0])
        self.night_layer.add(self.timer_snore)
        animations.fade_in_item(self.timer_snore, 235)
        animations.start_image_sequence(self.timer_snore, self.timer_snoore_animation, 7, -1)
        (x, y) = self.game.datastore.user_character.avatar_asleep_pos
        self.timer_snore.set_left(self.character_asleep_icon.get_left() + x - _div(self.timer_snore.get_width() , 2))
        self.timer_snore.set_top(self.character_asleep_icon.get_top() + y - 2 - self.timer_snoore_animation[0].get_height())
        animations.start_move(self.timer_snore, self.timer_snore.get_left(), self.timer_snore.get_top() - 15, 235)
        return

    def end_night(self):
        animations.fade_out_item(self.timer_snore, True, 235, self.end_night_snoore_callback)
        animations.start_move(self.timer_snore, self.timer_snore.get_left(), self.timer_snore.get_top() + 15, 235)
        return

    def end_night_snoore_callback(self, item):
        self.night_layer.remove(self.character_icon)
        self.night_layer.add(self.character_icon)
        animations.fade_in_item(self.character_icon, 350)
        animations.fade_out_item(self.character_asleep_icon, 175)
        self.blind_dialog(self.night_layer, animations.BlindDirection.HIDE_UP, True, [self.night_layer], self.end_night_callback)
        return

    def end_night_callback(self, layer):
        self.night_layer.remove(self.character_asleep_icon)
        if self.night_character_layer != None:
            self.night_character_layer.add(self.character_icon)
        self.close_dialog(self.night_layer)
        self.during_night = False
        self.update_character_rollover()
        self.set_music_volume(1, 500)
        return

    def update_locator(self):
        dep = self.game.datastore.user_character_progress.case.last_department_visited
        dep_name = text.to_upper(dep.name)
        self.locator_text.set_text(dep_name)
        image = assets.load_image('p0_locator_dept_' + dep.image + '.png')
        locator_pos = dep.locator_pos
        self.locator_sel.set_lefttop(locator_pos[0], locator_pos[1])
        self.locator_sel.set_image(image)
        return

    def set_time_left(self, time=0, callback=None):
        self.game.datastore.user_character_progress.case.time_spend += time
        key = 'update_time_left'
        self.stop_timer(key)
        if callback != None:
            self.update_time_callbacks.append(callback)
        self.start_timer('update_time_left', 10, self.update_time_left, None, True, False)
        return

    def update_time_left(self, key, data):
        self.stop_timer(key)
        appling_blind = False
        for layer in self.layers:
            if animations.is_applying_blind(self, layer):
                appling_blind = True
                break

        if appling_blind:
            self.start_timer(key, 50, self.update_time_left, None, True, False)
        else:
            (days, hour) = self.game.datastore.user_character_progress.case.actual_days()
            if self.timer_hour != hour or self.timer_days != days:
                self.timer_to_hour = hour
                self.timer_to_days = days
                if not self.is_timer_started('timer_clock'):
                    self.lock_folder_help()
                    self.lock_ui()
                    self.start_timer_clock()
            else:
                self.invoke_update_timer_callbacks()
        return

    def invoke_update_timer_callbacks(self):
        callbacks = self.update_time_callbacks[:]
        self.update_time_callbacks = []
        for callback in callbacks:
            callback()

        return

    def start_timer_clock(self):
        self.time_limit = self.game.datastore.user_character_progress.case.time_limit
        self.start_timer('timer_clock', 32, self.update_timer_clock, None)
        if self.timer_hour != 99999:
            self.render()
            self.clock_sound.play()
        return

    def set_up_options(self):
        self.backbar_image = assets.load_image('p0_bottomgui_backbar.png')
        self.backbar_item = ItemImage(0, 361, self.backbar_image)
        self.options_layer.add(self.backbar_item)
        self.glow_image = assets.load_image('p0_bottomgui_icon_glow.png')
        self.map_image = assets.load_image('p0_bottomgui_map_icon.png')
        self.map_icon = ItemImage(375, 397, self.map_image)
        self.options_layer.add(self.map_icon)
        self.map_icon.add_event_handler(ItemEvent.CLICK, self.map_click)
        self.map_icon.set_rollover(self.glow_image, self.rollover_sound, -5, -15)
        self.folder_image = assets.load_image('p0_bottomgui_case_icon.png')
        self.folder_icon = ItemImage(445, 398, self.folder_image)
        self.options_layer.add(self.folder_icon)
        self.folder_icon.select_witnesses = False
        self.folder_icon.add_event_handler(ItemEvent.CLICK, self.folder_click)
        self.folder_icon.set_rollover(self.glow_image, self.rollover_sound, -10, -15)
        self.notes_image = assets.load_image('p0_bottomgui_notes_icon.png')
        self.notes_icon = ItemImage(520, 394, self.notes_image)
        self.options_layer.add(self.notes_icon)
        self.notes_icon.add_event_handler(ItemEvent.CLICK, self.notes_click)
        self.notes_icon.set_rollover(self.glow_image, self.rollover_sound, -15, -11)
        return

    def set_up_character(self):
        self.character_icon = self.create_character_item()
        self.character_asleep_icon = self.create_character_asleep_item()
        self.info_layer.add(self.character_icon)
        self.update_character_rollover()
        return

    def prepare_dialog(self, layer, only_character=False, animate=False):
        self.phase.on_prepare_dialog(animate)
        if only_character:
            item = self.character_icon
            item_layer = item.get_layer()
            if item_layer != None:
                item_layer.remove(item)
            layer.add(item)
        else:
            for item in self.info_items:
                item_layer = item.get_layer()
                if item_layer != None:
                    item_layer.remove(item)

        for item in self.info_items:
            layer.add(item)

        self.update_character_rollover()
        return

    def reset_dialog(self, restore_info_items=True, animate=False):
        self.phase.on_reset_dialog(animate)
        if restore_info_items:
            for item in self.info_items:
                item_layer = item.get_layer()
                if item_layer != None:
                    item_layer.remove(item)

            for item in self.info_items:
                self.info_layer.add(item)

        self.update_character_rollover()
        return

    def create_character_item(self):
        avatar_image = self.game.datastore.user_character.avatar_image
        height = avatar_image.get_height()
        item = ItemImage(0, 450 - height, avatar_image)
        item.add_event_handler(ItemEvent.CLICK, self.character_click)
        return item

    def create_character_asleep_item(self):
        avatar_asleep_image = self.game.datastore.user_character.avatar_asleep_image
        height = avatar_asleep_image.get_height()
        return ItemImage(7, 450 - height, avatar_asleep_image)

    def update_character_rollover(self):
        if self.character_icon.get_layer() == self.info_layer and not self.during_night:
            self.character_icon.set_rollover_image(self.game.datastore.user_character.avatar_rollover_image, self.rollover_sound)
        else:
            self.character_icon.set_rollover_image(None, None)
        return

    def add_content_layers(self):
        return

    def add_above_options_layers(self):
        return

    def add_above_info_layers(self):
        return

    def character_click(self, item, args):
        if self.character_icon.get_layer() == self.info_layer and not self.during_night:
            self.render()
            self.click_sound.play()
            merits_dialog = merits.Merits(self)
            merits_dialog.show_merits()
        return

    def notes_click(self, item, args):
        self.notes = notes.Notes(self)
        self.show_dialog(self.notes.layer, self.notes_handle_event)
        self.notes.select_first_page()
        self.render()
        self.notes_open_sound.play()
        return

    def notes_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.render()
            self.click_sound.play()
            self.notes.close_notes()
        return

    def folder_click(self, item, args):
        if self.game.datastore.user_character_progress.show_folder:
            item.select_witnesses = True
        self.show_dialog(self.folder.base_layer, self.folder_handle_event)
        if item.select_witnesses:
            self.folder.add_start_layer(folder.WITNESS)
            if self.game.datastore.user_character_progress.show_folder:
                self.game.datastore.user_character_progress.show_folder = False
            self.folder_icon.select_witnesses = False
        else:
            self.folder.add_start_layer(self.folder_default_tab)
        return

    def folder_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.render()
            self.click_sound.play()
            self.folder.close_folder()
        return

    def map_click(self, item, args):
        case = self.game.datastore.user_character_progress.case
        last_dep = case.list_departments[len(case.list_departments) - 1]
        if case.last_department_lair == last_dep and case.arrest_order_thief == None and self.phase_number == 2 and not self.arrest_order_warning_shown:
            self.arrest_order_warning_shown = True
            self.show_arrest_order_warning()
        else:
            self.map.set_up(True, False)
            self.show_dialog(self.map.map_layer, self.map_handle_event)
            self.map.add_other_layer()
            self.render()
            self.open_map_sound.play()
        return

    def map_handle_event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            return
            self.render()
            self.click_sound.play()
            self.map.close_map()
        return

    def disable_map(self):
        self.map_icon.set_alpha(120)
        return

    def disable_folder(self):
        self.folder_icon.set_alpha(120)
        return

    def disable_notes(self):
        self.notes_icon.set_alpha(120)
        return

    def enable_map(self):
        self.map_icon.set_alpha(255)
        return

    def enable_folder(self):
        self.folder_icon.set_alpha(255)
        return

    def enable_notes(self):
        self.notes_icon.set_alpha(255)
        return

    def hide_clues(self, fade, callback):
        for (item_mask, item_found) in self.clue_items:
            item_mask.set_visible(False)
            if fade:
                animations.fade_out_item(item_found, False, 500)
            else:
                item_found.set_visible(False)

        if fade:
            self.render()
            self.fade_sound.play()
        if callback != None:
            animations.wait(self, 500, callback)
        return

    def show_clues_with_fade(self, callback):
        show = False
        for (item_mask, item_found) in self.clue_items:
            if not item_found.get_visible():
                item_mask.set_visible(True)
                item_found.set_visible(True)
                if not show:
                    animations.fade_in_item(item_found, 500, callback)
                    show = True
                else:
                    animations.fade_in_item(item_found, 500)

        if not show:
            callback(None)
        else:
            self.render()
            self.fade_sound.play()
        return

    def find_clue(self, stage_clues, item_type):
        for stage_clue in stage_clues:
            if stage_clue.clue.id == item_type:
                return stage_clue

        raise Exception('There is no clue for item_type = ' + item_type)
        return

    def has_item_found(self, clue):
        return clue in self.items_found

    def add_item_found(self, item, show_animation):
        x = 174
        y = 422
        item_image = item.get_image()
        item_found = ItemImage(x + len(self.items_found) * 60 - _div(item_image.get_width() , 2), y - _div(item_image.get_height() , 2), item_image)
        item_found.stage_clue = item.stage_clue
        item_mask = ItemMask(x + len(self.items_found) * 60 - 17, y - 17, (34, 34))
        item_mask.item = item_found
        item_mask.add_event_handler(ItemEvent.CLICK, self._clue_click)
        item_mask.set_rollover(self.glow_image, self.rollover_sound, _div(-item_mask.get_width() , 2) - 2)
        self.options_layer.add(item_mask)
        self.options_layer.add(item_found)
        self.items_found.append(item.stage_clue)
        self.clue_items.append([item_mask, item_found])
        return item_found

    def show_arrest_order_warning(self):
        layer = Layer()
        back_image = assets.load_image('p0_warning_noID_back.png')
        back_item = ItemImage(43, 33, back_image)
        layer.add(back_item)
        self.warning_sound = assets.load_sound('p0_warning.ogg')
        font = assets.load_font('evilgeniusbb_reg.ttf', 13)
        font_bold = assets.load_font('evilgeniusbb_bld.ttf', 13)
        message = 'Estás &#f:bold!muy cerca&#f! de encontrar al ladrón\n' + 'y aún no tienes una &#c144,22,22!&#f:bold!orden de arresto&#f!&#c! en su contra.\n' + '\n' + 'Para hacerla ve a la solapa de &#c144,22,22!&#f:bold!identikit&#f!&#c! dentro de la\n' + '&#c144,22,22!&#f:bold!carpeta&#f!&#c! y &#f:bold!completa la información&#f! con los datos\n' + 'que te dieron los &#f:bold!testigos&#f!.'
        additional_fonts = {'bold': (font_bold, 13, -2)}
        text_item = ItemText(88, 75, font, 16, message, (0, 0, 0), None, 405, 160, 2, 2, additional_fonts)
        layer.add(text_item)
        close_image = assets.load_image('p0_button_close.png')
        close_rollover_image = assets.load_image('p0_button_close_rollover.png')
        close_item = ItemImage(276, 328, close_image)
        close_item.set_rollover_image(close_rollover_image, self.rollover_sound)
        close_item.add_event_handler(ItemEvent.CLICK, self._close_arrest_order_warning_click)
        layer.add(close_item)
        self.warning_dialog = layer
        self.show_dialog(layer, self.arrest_order_warning_dialog_handle_event)
        self.blind_dialog(layer, animations.BlindDirection.SHOW_DOWN)
        self.set_music_volume(0.2, 200)
        animations.wait(self, 300, self.play_warning_sound)
        return

    def play_warning_sound(self):
        self.warning_sound.play()
        animations.wait(self, 300, self.play_music_after_warning)
        return

    def play_music_after_warning(self):
        self.set_music_volume(1, 500)
        return

    def arrest_order_warning_dialog_handle_event(self, e):
        if e.type == KEYDOWN and pygame.K_ESCAPE:
            self.render()
            self.click_sound.play()
            self.close_arrest_order_warning_dialog()
            return True
        return

    def show_help_dialog(self, page, delay=0, call_before_show=None, call_after_close=None):
        if self.during_night_or_applying_blind():
            self.start_timer('show_help_dialog', 10, self.show_help_dialog_timer, (page, delay, call_before_show, call_after_close), True, False)
        elif delay > 0:
            animations.wait_locked(self, delay, self.show_help_dialog_wait_callback, (page, 0, call_before_show, call_after_close))
        elif not self.showing_help:
            self.showing_help = True
            self.help_call_after_close = call_after_close
            help_dialog = help.Help(self)
            if call_before_show != None:
                call_before_show()
            help_dialog.show_help(page, False, True, self.close_help_callback)
        return

    def close_help_callback(self):
        self.showing_help = False
        if self.help_call_after_close != None:
            self.help_call_after_close()
        return

    def show_help_dialog_timer(self, key, data):
        self.stop_timer(key)
        self.show_help_dialog(data[0], data[1], data[2], data[3])
        return

    def show_help_dialog_wait_callback(self, data):
        self.show_help_dialog(data[0], data[1], data[2], data[3])
        return

    def _close_arrest_order_warning_click(self, item, args):
        self.close_arrest_order_warning_dialog()
        return

    def close_arrest_order_warning_dialog(self):
        self.blind_dialog(self.warning_dialog, animations.BlindDirection.HIDE_DOWN, True, [], self._blind_arrest_order_warning_callback)
        return

    def _blind_arrest_order_warning_callback(self, layer):
        self.close_dialog(layer)
        return

    def _clue_click(self, item, args):
        self.clue_dialog = self.show_clue_message(item.item, False, True, self._close_clue_dialog)
        return

    def _close_clue_dialog(self):
        self.close_dialog(self.clue_dialog)
        self.reset_dialog()
        return

    def show_clue_message(self, item, from_stage, play_sound, close_callback):
        font = assets.load_font('evilgeniusbb_reg.ttf', 13)
        dialog = Layer()
        image = assets.load_image('p2_avatar_dialog_aclue.png')
        box = ItemImage(62, 135, image)
        dialog.add(box)
        message = ''
        if from_stage:
            message = 'mmmm... '
        message += item.stage_clue.build_item_message()
        message = text.to_upper(message)
        if not message.endswith('.'):
            message += '.'
        text_item = ItemText(92, 214, font, 0, message, (0, 0, 0), None, 280, 70, 2, 2)
        dialog.add(text_item)
        close_x = 356
        close_y = 157
        item_image = item.get_image()
        dialog_item = ItemImage(229 - _div(item_image.get_width() , 2), 180 - _div(item_image.get_height() , 2), item.get_image())
        dialog.add(dialog_item)
        image = assets.load_image('btn_testigo_x_normal.png')
        rollover_image = assets.load_image('btn_testigo_x_rollover.png')
        close_button = ItemImage(close_x, close_y, image, None, True)
        close_button.set_rollover_image(rollover_image, self.rollover_sound)
        close_button.add_event_handler(ItemEvent.CLICK, self.clue_dialog_close_click)
        dialog.add(close_button)
        self.clue_dialog = dialog
        self.clue_dialog_close_callback = close_callback
        self.prepare_dialog(dialog)
        self.show_dialog(dialog, self.clue_dialog_handle_event)
        if play_sound:
            self.render()
            self.popup_sound.play()
        return dialog

    def clue_dialog_close_click(self, item=None, args=None):
        self.close_clue_dialog()
        return

    def clue_dialog_handle_event(self, e):
        if e.type == KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.render()
                self.click_sound.play()
                self.close_clue_dialog()
                return True
        return

    def close_clue_dialog(self):
        self.clue_dialog_close_callback()
        return

    def blind_layers(self, direction, area, duration=450, callback=None):
        call = callback
        for layer in self.layers:
            animations.blind_layer(layer, direction, None, duration, call)
            call = None

        return

    def start_map_help_animation(self):
        self.start_timer('start_map_animation', 30, self.__start_map_help_animation_preinvoke_timer, True)
        return

    def __start_map_help_animation_preinvoke_timer(self, key, data):
        if not self.__check_timer_moving():
            self.stop_timer(key)
            self.map_animation_times = 0
            self.map_animation_dy = 30
            self.__map_help_animation_up()
            self.render()
            self.bounce_sound.play()
        return

    def __map_help_animation_up(self, item=None):
        if self.map_animation_times >= 4:
            self.map_animation_dy *= 0.5
        else:
            self.map_animation_dy *= 0.9
        self.map_animation_times += 1
        if self.map_animation_times <= 8:
            self.map_icon.set_lefttop(375, 397)
            duration = 60 + _div(float(self.map_animation_dy) , 30) * 250
            animations.start_move(self.map_icon, 375, 397 - self.map_animation_dy, duration, (0.2,
                                                                                              0.5,
                                                                                              1), None, self.__map_help_animation_down)
        return

    def __map_help_animation_down(self, item=None):
        delay = 40 + _div(float(self.map_animation_dy) , 30) * 160
        animations.start_move(self.map_icon, 375, 397, delay, (0.7, 0.5, 1), None, self.__map_help_animation_up)
        return

    def start_notes_help_animation(self, delay=0):
        self.start_timer('start_notes_animation', 30, self.__start_notes_help_animation_preinvoke_timer, [delay], True)
        return

    def __start_notes_help_animation_preinvoke_timer(self, key, data):
        if not self.__check_timer_moving():
            self.stop_timer(key)
            delay = data[0]
            if self.notes_icon.get_alpha() < 255:
                return
            if delay != 0:
                self.animation_times = 0
                animations.wait_locked(self, delay, self.__start_notes_help_animation_wait)
            else:
                self.notes_animation_times = 0
                self.notes_animation_dy = 30
                self.__notes_help_animation_up()
                self.render()
                self.bounce_sound.play()
        return

    def __start_notes_help_animation_wait(self, item=None):
        self.start_notes_help_animation()
        return

    def __notes_help_animation_up(self, item=None):
        if self.notes_animation_times >= 4:
            self.notes_animation_dy *= 0.5
        else:
            self.notes_animation_dy *= 0.9
        self.notes_animation_times += 1
        if self.notes_animation_times <= 8:
            self.notes_icon.set_lefttop(520, 394)
            duration = 60 + _div(float(self.notes_animation_dy) , 30) * 250
            animations.start_move(self.notes_icon, 520, 394 - self.notes_animation_dy, duration, (0.2,
                                                                                                  0.5,
                                                                                                  1), None, self.__notes_help_animation_down)
        return

    def __notes_help_animation_down(self, item=None):
        delay = 40 + _div(float(self.notes_animation_dy) , 30) * 160
        animations.start_move(self.notes_icon, 520, 394, delay, (0.7, 0.5, 1), None, self.__notes_help_animation_up)
        return

    def lock_folder_help(self):
        self.folder_animation_locks += 1
        return

    def release_folder_help(self):
        self.folder_animation_locks -= 1
        if self.pending_folder_animation:
            self.start_folder_help_animation()
        return

    def start_folder_help_animation(self, delay=0):
        self.start_timer('start_folder_animation', 30, self.__start_folder_help_animation_preinvoke_timer, [delay], True)
        return

    def __start_folder_help_animation_preinvoke_timer(self, key, data):
        if not self.__check_timer_moving():
            self.stop_timer(key)
            delay = data[0]
            if self.folder_animation_locks > 0:
                self.pending_folder_animation = True
                return
            self.pending_folder_animation = False
            if self.folder_icon.get_alpha() < 255:
                return
            if delay != 0:
                self.animation_times = 0
                animations.wait_locked(self, delay, self.__start_folder_help_animation_wait)
            else:
                self.folder_animation_times = 0
                self.folder_animation_dy = 30
                self.__folder_help_animation_up()
                self.render()
                self.bounce_sound.play()
        return

    def __start_folder_help_animation_wait(self, item=None):
        self.start_folder_help_animation()
        return

    def __folder_help_animation_up(self, item=None):
        if self.folder_animation_times >= 4:
            self.folder_animation_dy *= 0.5
        else:
            self.folder_animation_dy *= 0.9
        self.folder_animation_times += 1
        if self.folder_animation_times <= 8:
            self.folder_icon.set_lefttop(445, 398)
            duration = 60 + _div(float(self.folder_animation_dy) , 30) * 250
            animations.start_move(self.folder_icon, 445, 398 - self.folder_animation_dy, duration, (0.2,
                                                                                                    0.5,
                                                                                                    1), None, self.__folder_help_animation_down)
        return

    def __folder_help_animation_down(self, item=None):
        delay = 40 + _div(float(self.folder_animation_dy) , 30) * 160
        animations.start_move(self.folder_icon, 445, 398, delay, (0.7, 0.5, 1), None, self.__folder_help_animation_up)
        return

    def __check_timer_moving(self):
        (days, hour) = self.game.datastore.user_character_progress.case.actual_days()
        return self.timer_days < days or self.timer_days == days and self.timer_hour < hour

    def __show_loading_callback(self, layer):
        self.start_timer('load_phase', 0, self.__load_phase_callback)
        return

    def __hide_loading_callback(self, layer=None, inital_phase=False):
        self.set_time_left(0, self.__loading_set_time_callback)
        return

    def __loading_set_time_callback(self):
        self.loading_phase = False
        self.seting_timer = True
        if not self.minigame_started and self.phase_number != 3:
            animations.wait_locked(self, 50, self.__show_dialog_step_callback)
        return

    def __show_dialog_step_callback(self):
        if self.during_night_or_applying_blind():
            animations.wait(self, 50, self.__show_dialog_step_callback)
        else:
            self.seting_timer = False
            if self.phase_number == 1:
                self.check_ending()
            if not self.__ending_visible:
                cp = self.game.datastore.user_character_progress
                case = cp.case
                if case.time_spend < case.time_limit:
                    if self.phase_number == 1:
                        if cp.last_help_step_seen <= 0:
                            self.show_help_dialog(1, 1000)
                            cp.last_help_step_seen = 1
                        self.phase.check_show_arrived_wrong_location()
                    elif self.phase_number == 2:
                        if cp.last_help_step_seen <= 4:
                            self.show_help_dialog(5, 1000)
                            cp.last_help_step_seen = 5
        return

    def __load_phase_callback(self, key, data):
        self.stop_timer(key)
        self.__load_phase(self.load_phase_number)
        return

    def __load_phase(self, phase):
        self.loading_phase = True
        if not self.initialized:
            self.initialize_stage()
            self.initialized = True
            initial_phase = True
        else:
            initial_phase = False
        self.empty_layers()
        if self.phase != None:
            self.reset_dialog()
        self.set_mouse_cursor(None)
        self.set_items('')
        self.stop_timers()
        self.phase = None
        self.map_icon.set_lefttop(375, 397)
        self.folder_icon.set_lefttop(445, 398)
        self.notes_icon.set_lefttop(520, 394)
        gc.collect()
        if phase == 1:
            from . import phase1
            self.phase = phase1.Phase1Content()
            self.update_locator()
        elif phase == 2:
            from . import phase2
            self.phase = phase2.Phase2Content()
            self.arrest_order_warning_shown = False
        elif phase == 3:
            from . import phase3
            self.phase = phase3.Phase3Content()
        else:
            raise Exception("Phase '" + str(phase) + "' not implemented.")
        self.phase_number = phase
        self.add_layer(self.background_layer)
        self.phase.initialize(self.game, self)
        self.phase.add_content_layers()
        self.add_layer(self.options_layer)
        self.phase.add_above_options_layers()
        self.add_layer(self.info_layer)
        self.phase.add_above_info_layers()
        if self.save_state_on_next_load_phase:
            self.save_progress(True)
            self.save_state_on_next_load_phase = False
        else:
            self.save_state_on_next_load_phase = True
        self.play_phase_music()
        self.__ending_visible = False
        if phase == 1 and self.minigame != None:
            self.phase.start_minigame(self.minigame)
            self.minigame_started = True
        else:
            self.minigame_started = False
        self.minigame = None
        self.game.stats.start_time_event(statcodes.PHASE_PREFIX + str(self.phase_number))
        if self.phase_number == 3:
            self.__hide_loading_callback
        else:
            self.game.hide_loading(self.__hide_loading_callback)
        return

    def save_progress(self, check_save_in_development, save_character_list=False):
        self.game.datastore.save_character('p' + str(self.phase_number), check_save_in_development)
        if save_character_list:
            self.game.datastore.save_characters()
        return

    def play_phase_music(self):
        music = self.phase.get_music()
        if music != None:
            self.play_music(music[0], music[1])
        return

    def check_ending(self):
        self.checking_ending = True
        if not self.loading_phase:
            if self.during_night_or_applying_blind():
                animations.wait(self, 50, self.check_ending)
            else:
                self.checking_ending = False
                if self.game.datastore.user_character_progress.case.time_spend >= self.game.datastore.user_character_progress.case.time_limit:
                    if not self.__ending_visible:
                        self.__ending_visible = True
                        self.show_time_up_end_game()
                    return
                from . import phase1
                if isinstance(self.phase, phase1.Phase1Content):
                    if not self.__ending_visible and self.phase.final_stage_check():
                        self.__ending_visible = True
        return

    def during_night_or_applying_blind(self):
        if self.during_night:
            return True
        else:
            for layer in self.layers:
                if animations.is_applying_blind(self, layer):
                    return True

            return False
        return

    def show_time_up_end_game(self):
        if self.during_night_or_applying_blind():
            animations.wait(self, 50, self.show_time_up_end_game)
        else:
            ending = endgame.EndGame(self, endgame.EndReason.TIME_UP)
            ending.show_opening_dialog()
            self.save_progress(False)
        return

    def show_mainmenu(self):
        if not self.showing_mainmenu:
            self.pause_music(450)
            from . import mainmenu
            main = mainmenu.MainMenu(self)
            self.showing_mainmenu = True
            main.show_mainmenu(True, self.close_mainmenu_callback)
        return

    def close_mainmenu_callback(self):
        self.showing_mainmenu = False
        self.unpause_music()
        return

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE and not self.checking_ending and not self.__ending_visible and not self.seting_timer and not self.loading_phase:
                self.render()
                self.click_sound.play()
                self.show_mainmenu()
            if self.game.get_development_mode():
                mod = self.get_common_modifiers(e.mod)
                if mod == pygame.KMOD_LSHIFT and e.key == pygame.K_g:
                    if self.phase_number == 2:
                        case = self.game.datastore.user_character_progress.case
                        case.thief_lair_set[1] = None
                        self.phase.build_stage()
                elif mod == pygame.KMOD_LCTRL and e.key == pygame.K_c:
                    if self.phase_number == 1:
                        self.phase.show_clues_found()
                elif mod == pygame.KMOD_LSHIFT:
                    if e.key == pygame.K_h and self.phase_number == 2:
                        case = self.game.datastore.user_character_progress.case
                        lair_sets = self.game.datastore.list_lair_sets
                        index = lair_sets.index(case.thief_lair_set[0]) + 1
                        case.thief_lair_set[0] = lair_sets[(index + 1) % len(lair_sets)]
                        case.thief_lair_set[1] = None
                        self.phase.build_stage()
                if mod == pygame.KMOD_LSHIFT and e.key == pygame.K_j:
                    if self.phase_number == 1:
                        active_pins = self.phase.active_pins[:]
                        k = 0
                        while self.phase.minigames_resolved < 3:
                            active_pin = active_pins[k]
                            k += 1
                            self.phase.witness_pin = active_pin
                            self.phase.set_witness_statement()
                            self.phase.minigame_solved(True, True)

                        case = self.game.datastore.user_character_progress.case
                elif mod == pygame.KMOD_LSHIFT and e.key == pygame.K_v:
                    final_stage = endgame.EndGame(self, 2)
                    final_stage.wrong_location_callback = self.phase.wrong_location_callback
                    final_stage.show_opening_dialog()
                elif mod == pygame.KMOD_LSHIFT and e.key == pygame.K_x:
                    final_stage = endgame.EndGame(self, 0)
                    final_stage.show_opening_dialog()
                elif mod == pygame.KMOD_LSHIFT and e.key == pygame.K_z:
                    final_stage = endgame.EndGame(self, 1)
                    final_stage.show_opening_dialog()
                elif mod == pygame.KMOD_LSHIFT and e.key == pygame.K_a:
                    case = self.game.datastore.user_character_progress.case
                    case.arrest_order_thief = case.thief
                    last_dep = case.list_departments[len(case.list_departments) - 1]
                    case.last_department_lair = last_dep
                    case.last_department_visited = last_dep
                    case.clues_found = []
                    for clue in case.list_stage_clues[:3]:
                        case.clues_found.append(clue.clue.id)

                    self.game.datastore.user_character_progress.case.caught_thief = 1
                    self.timer_days = 2
                    self.timer_hour = 14
                    final_stage = endgame.EndGame(self, 1)
                    final_stage.show_opening_dialog()
                elif mod == pygame.KMOD_LSHIFT and e.key == pygame.K_s:
                    case = self.game.datastore.user_character_progress.case
                    case.arrest_order_thief = case.thief
                    last_dep = case.list_departments[len(case.list_departments) - 1]
                    case.last_department_lair = last_dep
                    case.last_department_visited = last_dep
                    final_stage = endgame.EndGame(self, 1)
                    final_stage.show_opening_dialog()
                elif mod == pygame.KMOD_LSHIFT and e.key == pygame.K_d:
                    character_progress = self.game.datastore.user_character_progress
                    case = character_progress.case
                    case.arrest_order_thief = case.thief
                    for department in self.game.datastore.list_departments:
                        if department != case.crime_location.department:
                            character_progress.add_medal(department.image)

                    final_stage = endgame.EndGame(self, 1)
                    final_stage.show_opening_dialog()
                elif mod == pygame.KMOD_LSHIFT and e.key == pygame.K_f:
                    case = self.game.datastore.user_character_progress.case
                    case.arrest_order_thief = case.thief
                    final_stage = endgame.EndGame(self, 1)
                    final_stage.show_opening_dialog()
                elif mod == pygame.KMOD_LSHIFT and e.key == pygame.K_2:
                    self.set_phase(2, True)
                elif mod == pygame.KMOD_LSHIFT and e.key == pygame.K_t:
                    self.set_time_left(1)
                elif mod == pygame.KMOD_LSHIFT and e.key == pygame.K_c:
                    character_progress = self.game.datastore.user_character_progress
                    character_progress.resolved_cases += 3
                    character_progress.range.update()
                elif mod == pygame.KMOD_LSHIFT | pygame.KMOD_LCTRL and e.key == pygame.K_n:
                    notes = self.game.datastore.user_character_progress.notes
                    for note in self.game.datastore.list_history_facts:
                        if note not in notes:
                            notes.append(note)

                    for note in self.game.datastore.list_rivers:
                        if note not in notes:
                            notes.append(note)

                    for note in self.game.datastore.list_lagoons:
                        if note not in notes:
                            notes.append(note)

                    for note in self.game.datastore.list_hills:
                        if note not in notes:
                            notes.append(note)

                    for note in self.game.datastore.list_locations:
                        if note not in notes:
                            notes.append(note)

                    for note in self.game.datastore.list_writers:
                        if note not in notes:
                            notes.append(note)

                elif mod == pygame.KMOD_LSHIFT | pygame.KMOD_LCTRL and e.key == pygame.K_m:
                    notes = self.game.datastore.user_character_progress.notes
                    new_notes = self.game.datastore.user_character_progress.new_notes
                    for note in self.game.datastore.list_history_facts:
                        if note not in new_notes:
                            new_notes.append(note)
                        if note not in notes:
                            notes.append(note)

                    for note in self.game.datastore.list_rivers:
                        if note not in new_notes:
                            new_notes.append(note)
                        if note not in notes:
                            notes.append(note)

                    for note in self.game.datastore.list_lagoons:
                        if note not in new_notes:
                            new_notes.append(note)
                        if note not in notes:
                            notes.append(note)

                    for note in self.game.datastore.list_hills:
                        if note not in new_notes:
                            new_notes.append(note)
                        if note not in notes:
                            notes.append(note)

                    for note in self.game.datastore.list_locations:
                        if note not in new_notes:
                            new_notes.append(note)
                        if note not in notes:
                            notes.append(note)

                    for note in self.game.datastore.list_writers:
                        if note not in new_notes:
                            new_notes.append(note)
                        if note not in notes:
                            notes.append(note)

                elif mod == pygame.KMOD_LSHIFT and e.key == pygame.K_m:
                    character_progress = self.game.datastore.user_character_progress
                    character_progress.add_medal('uy')
                    character_progress.add_medal('uy')
                    k = 1
                    for department in self.game.datastore.list_departments:
                        for i in range(k):
                            character_progress.add_medal(department.image)

                        k += 1

        return

    def get_common_modifiers(self, mod):
        return mod & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL | pygame.KMOD_LALT | pygame.KMOD_RALT | pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT)


class PhaseContent():

    def __init__(self):
        return

    def initialize(self, game, stage):
        return

    def add_content_layers(self):
        return

    def get_music(self):
        return

    def add_above_options_layers(self):
        return

    def add_above_info_layers(self):
        return

    def on_prepare_dialog(self, animate):
        return

    def on_reset_dialog(self, animate):
        return


