import math
from framework import animations, text, web
from game.data import datastore
from framework.assets import *
from framework.stage import *
from . import witness, janitor, minigameshoptender, minigamegardener, minigamelibrarian, minigamebricklayer, endgame
from game.stages.phase0 import Phase0Stage
import random
from . import phase0, phase2

class Phase1Content(phase0.PhaseContent):

    def __init__(self):
        return

    def initialize(self, game, stage):
        self.game = game
        self.stage = stage
        self.witness_dialog = witness.Witness(self.stage)
        self.janitor_dialog = janitor.Janitor(self.stage)
        self.minigames_resolved = 0
        self.load_hideout_raccoon_images()
        self.witness_popup_sound = assets.load_sound('p1_witness_pop_up.ogg')
        self.raccoon_fade_sound = assets.load_sound('p1_racoon_fade.ogg')
        self.music_intro = assets.load_music('p1_music_intro.ogg')
        self.music_loop = assets.load_music('p1_music_loop.ogg')
        self.music_minigame_1 = assets.load_music('p1_bricklayer_gardener_music_loop.ogg')
        self.music_minigame_2 = assets.load_music('p1_shoptender_librarian_music_loop.ogg')
        return

    def get_music(self):
        return (
         self.music_intro, self.music_loop)

    def final_stage_check(self):
        case = self.game.datastore.user_character_progress.case
        last_dep = case.list_departments[len(case.list_departments) - 1]
        if case.last_department_lair == last_dep and case.last_department_visited == last_dep:
            if case.clues_identified:
                self.show_arrived_location_end_game()
            else:
                self.stage.hide_clues(True, self.show_clues_found)
            return True
        return False

    def show_clues_found(self):
        if self.stage.during_night:
            animations.wait(self.stage, 50, self.show_clues_found)
        else:
            self.clues_right_sound = assets.load_sound('p1_minigame_right.ogg')
            case = self.game.datastore.user_character_progress.case
            case.clues_identified = True
            self.set_up_clues_found()
            self.stage.show_dialog(self.clues_found_layer, None)
            self.stage.blind_dialog(self.clues_found_layer, animations.BlindDirection.SHOW_DOWN)
            self.stage.render()
            animations.wait(self.stage, 50, self.play_show_clues_sound)
        return

    def play_show_clues_sound(self):
        self.stage.render()
        self.clues_right_sound.play()
        return

    def set_up_clues_found(self):
        self.clues_found_layer = Layer()
        background_image = assets.load_image('p0_cluesfound_backdrop_2.png')
        background_item = ItemImage(76, 29, background_image)
        self.clues_found_layer.add(background_item)
        font = assets.load_font('evilgeniusbb_reg.ttf', 14)
        font_bold = assets.load_font('evilgeniusbb_bld.ttf', 14)
        x = 158
        k = 1
        case = self.game.datastore.user_character_progress.case
        for (item_mask, item_found) in self.stage.clue_items:
            if k == 1:
                y = 138
            elif k == 2:
                y = 222
            elif k == 3:
                y = 311
            else:
                break
            clue_image = item_found.get_image()
            icon_item = ItemImage(x - clue_image.get_width() / 2, y - clue_image.get_height() / 2, clue_image)
            self.clues_found_layer.add(icon_item)
            message = item_found.stage_clue.build_right_department_message(case.last_department_visited)
            text_item = ItemText(204, y - 30, font, 14, message, (0, 0, 0), None, 241, 60, 1, 2)
            self.clues_found_layer.add(text_item)
            k += 1

        congratulations_item = ItemText(221, 365, font_bold, 13, '¡BUEN TRABAJO!', (153,
                                                                                        0,
                                                                                        0), None, 160, 22, 2, 1)
        self.clues_found_layer.add(congratulations_item)
        close_image = assets.load_image('p0_button_close.png')
        close_rollover_image = assets.load_image('p0_button_close_rollover.png')
        close_item = ItemImage(281, 384, close_image)
        close_item.set_rollover_image(close_rollover_image, self.stage.rollover_sound)
        close_item.add_event_handler(ItemEvent.CLICK, self.close_cluesfound_click)
        self.clues_found_layer.add(close_item)
        return

    def close_cluesfound_click(self, item, args):
        self.stage.render()
        self.stage.click_sound.play()
        self.stage.blind_dialog(self.clues_found_layer, animations.BlindDirection.HIDE_DOWN, False, [], self.close_cluesfound_callback)
        return

    def close_cluesfound_callback(self, layer):
        self.stage.close_dialog(self.clues_found_layer)
        self.show_arrived_location_end_game(False)
        return

    def show_arrived_location_end_game(self, blind_background=True):
        if self.stage.during_night:
            animations.wait(self.stage, 50, self.show_arrived_location_end_game)
        else:
            from . import endgame
            ending = endgame.EndGame(self.stage, endgame.EndReason.ARRIVED_LOCATION)
            ending.show_opening_dialog(blind_background)
            self.stage.save_progress(False)
        return

    def add_content_layers(self):
        self.map_layer = Layer()
        dep = self.game.datastore.user_character_progress.case.last_department_visited
        dep_image = assets.load_image('p1_map_' + dep.image + '.jpg')
        self.dep_item = ItemImage(dep.image_pos[0], dep.image_pos[1], dep_image)
        self.map_layer.add(self.dep_item)
        self.stage.add_layer(self.map_layer)
        return

    def add_above_options_layers(self):
        self.create_tags_layer()
        self.stage.add_layer(self.tags_layer)
        self.create_pins_layer()
        self.stage.add_layer(self.pins_layer)
        self.create_witness_layer()
        return

    def add_above_info_layers(self):
        self.stage.add_layer(self.witness_layer)
        self.raccoon_layer = Layer()
        self.stage.add_layer(self.raccoon_layer)
        self.update_notes()
        self.load_progress()
        return

    def load_progress(self):
        case = self.stage.game.datastore.user_character_progress.case
        case = self.stage.game.datastore.user_character_progress.case
        if case.last_department_lair == case.list_departments[0]:
            for p in self.active_pins[:]:
                if p.witness in case.list_visited_witnesses:
                    self.witness_pin = p
                    self.minigame_solved(True, True)

        clues_found = case.clues_found[:]
        if len(clues_found) > 0:
            self.stage.prepare_items_set(self.stage, True)
            clues = case.list_stage_clues[:3]
            for clue_found in clues_found:
                stage_clue = self.stage.find_clue(clues, clue_found)
                if not self.stage.has_item_found(stage_clue):
                    item = ItemCell(self.stage, clue_found, phase2.ItemState.NORMAL)
                    item.is_clue = True
                    item.stage_clue = stage_clue
                    self.stage.add_item_found(item, False)

            if case.clues_identified:
                self.stage.hide_clues(False, None)
        return

    def check_show_arrived_wrong_location(self):
        user_character_progress = self.game.datastore.user_character_progress
        case = user_character_progress.case
        if case.last_department_visited not in case.list_departments:
            self.stage.set_time_left(0, self.show_arrived_wrong_location)
        return

    def show_arrived_wrong_location(self):
        wait = False
        for layer in self.stage.layers:
            if animations.is_applying_blind(self.stage, layer):
                wait = True
                break

        if wait and self.stage.during_night:
            animations.wait(self.stage, 50, self.show_arrived_wrong_location)
        else:
            ending = endgame.EndGame(self.stage, endgame.EndReason.ARRIVED_WRONG_LOCATION)
            ending.wrong_location_callback = self.wrong_location_callback
            ending.show_opening_dialog()
        return

    def wrong_location_callback(self):
        self.stage.show_clues_with_fade(self.wrong_location_clues_callback)
        return

    def wrong_location_clues_callback(self, item=None):
        self.stage.start_map_help_animation()
        return

    def create_tags_layer(self):
        self.tags_layer = Layer()
        self.city_tag_images = [
         assets.load_image('p1_state_tag_size_1.png'),
         assets.load_image('p1_state_tag_size_2.png'),
         assets.load_image('p1_state_tag_size_3.png')]
        self.tag_font = assets.load_font('evilgeniusbb_reg.ttf', 12)
        return

    def create_pins_layer(self):
        case = self.game.datastore.user_character_progress.case
        dep = case.last_department_visited
        self.pins_layer = Layer()
        pin_glow_image = assets.load_image('p1_map_pin_glow.png')
        self.pin_glow = ItemImage(0, 0, pin_glow_image)
        self.pin_glow.set_visible(False)
        self.pins_layer.add(self.pin_glow)
        self.pin_witnesses = []
        for i in range(len(dep.city_pins)):
            self.pin_witnesses.append(self.game.datastore.user_character_progress.case.list_witnesses[i])

        index = 0
        self.active_pins = []
        if dep == case.list_departments[0]:
            for c in dep.city_pins:
                pin_image = self.load_pin_image(index)
                if c.flipped:
                    pin_image.flip_h()
                pin = ItemImage(c.x, c.y, pin_image)
                pin.city = c
                pin.department = dep
                witness = None
                for w in self.pin_witnesses:
                    if w.city == c:
                        witness = w
                        break

                if witness == None:
                    witness = self.pin_witnesses[index]
                pin.witness = witness
                self._pin_set_events(pin)
                pin.witness_image = assets.load_image(pin.witness.image)
                self.pins_layer.add(pin)
                self.active_pins.append(pin)
                index += 1

            for k in range(len(case.list_departments)):
                if case.list_departments[k] == dep:
                    self.target_pin = self.active_pins[case.list_target_cities[k]]
                    break

        return

    def _pin_set_events(self, pin):
        if hasattr(pin, '_has_events'):
            pin._has_events += 1
        else:
            pin._has_events = 1
        if pin._has_events > 1:
            return
        pin.add_event_handler(ItemEvent.MOUSE_ENTER, self.pin_enter)
        pin.add_event_handler(ItemEvent.MOUSE_LEAVE, self.pin_leave)
        pin.add_event_handler(ItemEvent.CLICK, self.pin_click)
        return

    def _pin_clear_events(self, pin):
        if not pin._has_events:
            return
        pin._has_events -= 1
        if pin._has_events:
            return
        pin.remove_event_handler(ItemEvent.MOUSE_ENTER, self.pin_enter)
        pin.remove_event_handler(ItemEvent.MOUSE_LEAVE, self.pin_leave)
        pin.remove_event_handler(ItemEvent.CLICK, self.pin_click)
        return

    def create_witness_layer(self):
        self.witness_layer = Layer()
        self.witness_layer.set_visible(False)
        witness_box_image = assets.load_image('p1_map_rollover_base.png')
        self.witness_box = ItemImage(0, 0, witness_box_image)
        self.witness_layer.add(self.witness_box)
        self.witness_arrow_image = assets.load_image('p1_map_rollover_arrow.png')
        self.witness_arrow_image_flipped = self.witness_arrow_image.flip_v_copy()
        self.witness_arrow = ItemImage(0, 0, self.witness_arrow_image)
        self.witness_layer.add(self.witness_arrow)
        witness_picholder_image = assets.load_image('pic_holder_testigo.png')
        self.witness_picholder = ItemImage(0, 0, witness_picholder_image)
        self.witness_layer.add(self.witness_picholder)
        font = assets.load_font('powdrft_.ttf', 24)
        self.witness_name = ItemText(0, 0, font, 0, '', (157, 21, 21))
        self.witness_layer.add(self.witness_name)
        font = assets.load_font('powdrft_.ttf', 20)
        self.witness_city = ItemText(0, 0, font, 13, '', (102, 102, 102), None, 169, 30, 1, 3)
        self.witness_layer.add(self.witness_city)
        return

    def load_pin_image(self, index):
        if index == 0:
            return assets.load_image('p1_map_pin_blue.png')
        elif index == 1:
            return assets.load_image('p1_map_pin_green.png')
        elif index == 2:
            return assets.load_image('p1_map_pin_lightblue.png')
        elif index == 3:
            return assets.load_image('p1_map_pin_red.png')
        elif index == 4:
            return assets.load_image('p1_map_pin_violet.png')
        elif index == 5:
            print(('There is no image for pin index', index))
            raise SystemExit
        return

    def load_hideout_raccoon_images(self):
        self.raccoon_images = [
         assets.load_image('p1_thief_hideout_raccoon_tail.png'),
         assets.load_image('p1_thief_hideout_raccoon_body.png'),
         assets.load_image('p1_thief_hideout_raccoon_lids_001.png'),
         assets.load_image('p1_thief_hideout_raccoon_lids_002.png'),
         assets.load_image('p1_thief_hideout_raccoon_hands.png')]
        self.raccoon_animation = [
         self.raccoon_images[2],
         self.raccoon_images[3],
         self.raccoon_images[3],
         None,
         None,
         None,
         None,
         None,
         self.raccoon_images[2],
         self.raccoon_images[3],
         self.raccoon_images[3],
         None]
        return

    def pin_enter(self, item, args):
        self.stage.render()
        self.witness_popup_sound.play()
        self.show_pin_glow(item)
        self.show_witness(item)
        return

    def pin_leave(self, item, args):
        self.pin_glow.set_visible(False)
        self.witness_layer.set_visible(False)
        return

    def check_thief_location_assignement(self):
        if self.minigames_resolved == 2 and not self.witness_pin.witness.witness_statement.location_statement:
            from game.data.datamodel import Statement
            self.witness_pin.witness.witness_statement.location_statement = Statement(generate_thief_location_statement(self.target_pin.city))
        return

    def pin_click(self, item, args):
        self.stage.render()
        self.stage.click_sound.play()
        self.witness_pin = item
        self.set_witness_statement()
        if self.minigames_resolved < 3:
            self.check_thief_location_assignement()
            witness = item.witness
            if item.department == self.game.datastore.user_character_progress.case.last_department_lair:
                self.start_minigame(item.witness.name, self.witness_pin)
            else:
                case = self.game.datastore.user_character_progress.case
                if item.witness.name == 'Almacenera':
                    minigameshoptender_dialog = minigameshoptender.MinigameShoptender(self.stage, self, self.witness_pin.witness)
                    minigameshoptender_dialog.show_wrong_place_dialog()
                    case.wrong_witness_visited = True
                elif item.witness.name == 'Jardinero':
                    minigamegardener_dialog = minigamegardener.MinigameGardener(self.stage, self, self.witness_pin.witness)
                    minigamegardener_dialog.show_wrong_place_dialog()
                    case.wrong_witness_visited = True
                elif item.witness.name == 'Bibliotecario':
                    minigamelibrarian_dialog = minigamelibrarian.MinigameLibrarian(self.stage, self, self.witness_pin.witness)
                    minigamelibrarian_dialog.show_wrong_place_dialog()
                    case.wrong_witness_visited = True
                elif item.witness.name == 'Albañil':
                    minigamebricklayer_dialog = minigamebricklayer.MinigameBricklayer(self.stage, self, self.witness_pin.witness)
                    minigamebricklayer_dialog.show_wrong_place_dialog()
                    case.wrong_witness_visited = True
        else:
            self.target_tag_click('', '')
        return

    def start_minigame(self, name, witness_pin=None):
        if witness_pin == None:
            witness_pin = self.active_pins[0]
            case = self.game.datastore.user_character_progress.case
            witness_pin.witness.witness_statement = case.list_witness_statements[self.minigames_resolved]
            self.witness_pin = None
        if name == 'Almacenera':
            minigameshoptender_dialog = minigameshoptender.MinigameShoptender(self.stage, self, witness_pin.witness)
            minigameshoptender_dialog.show_opening_dialog()
        elif name == 'Jardinero':
            minigamegardener_dialog = minigamegardener.MinigameGardener(self.stage, self, witness_pin.witness)
            minigamegardener_dialog.show_opening_dialog()
        elif name == 'Bibliotecario':
            minigamelibrarian_dialog = minigamelibrarian.MinigameLibrarian(self.stage, self, witness_pin.witness)
            minigamelibrarian_dialog.show_opening_dialog()
        elif name == 'Albañil':
            minigamebricklayer_dialog = minigamebricklayer.MinigameBricklayer(self.stage, self, witness_pin.witness)
            minigamebricklayer_dialog.show_opening_dialog()
        elif name == 'Vendedor':
            self.minigame_solved(True)
        elif name == 'Verdulera':
            self.minigame_solved(True)
        return

    def set_witness_statement(self):
        case = self.game.datastore.user_character_progress.case
        if case.list_departments[0] == case.last_department_lair and case.list_departments[0] == case.last_department_visited:
            self.witness_pin.witness.witness_statement = case.list_witness_statements[self.minigames_resolved]
        return

    def minigame_solved(self, solved, batch=False):
        self.minigame_solved_data = (solved, batch)
        if not batch:
            web.send_data(datastore.STATS_URL, {'current': (datastore.VERSION), 'stats': (self.stage.game.stats.get_data())}, compressed=True)
            animations.wait_locked(self.stage, 80, self.minigame_update_time)
        else:
            self.minigame_update_time()
        return

    def minigame_update_time(self):
        batch = self.minigame_solved_data[1]
        if batch:
            self.minigame_set_time_callback()
        else:
            self.stage.set_time_left(1, self.minigame_set_time_callback)
        return

    def minigame_set_time_callback(self):
        solved = self.minigame_solved_data[0]
        batch = self.minigame_solved_data[1]
        if solved and self.witness_pin != None:
            self.game.datastore.user_character_progress.case.update_visited_witnesses(self.witness_pin.witness)
            self.game.datastore.user_character_progress.show_folder = True
            self.minigames_resolved += 1
            self.disable_witnesses()
            if batch:
                self.mark_city_solved(True)
            else:
                show_help = False
                cp = self.game.datastore.user_character_progress
                case = cp.case
                if case.time_spend < case.time_limit:
                    if case.last_department_visited == case.list_departments[0] and cp.last_help_step_seen <= 1:
                        show_help = True
                        cp.last_help_step_seen = 2
                        animations.wait_locked(self.stage, 1500, self.show_help_dialog_after_minigame_solved)
                    elif cp.last_help_step_seen <= 2:
                        show_help = True
                        cp.last_help_step_seen = 3
                        animations.wait_locked(self.stage, 1500, self.show_help_dialog_after_minigame_solved)
                if show_help:
                    animations.wait_locked(self.stage, 500, self.mark_city_solved_step1)
                else:
                    animations.wait_locked(self.stage, 500, self.mark_city_solved)
                self.stage.save_progress(False)
        return

    def show_help_dialog_after_minigame_solved(self):
        cp = self.game.datastore.user_character_progress
        self.stage.show_help_dialog(cp.last_help_step_seen, 0, None, self.after_close_minigame_solved_help)
        return

    def after_close_minigame_solved_help(self):
        self.mark_city_solved_step2(False)
        return

    def target_tag_click(self, item, args):
        self.stage.render()
        self.stage.click_sound.play()
        (option_texts, right_option) = self.build_option_texts()
        self.janitor_dialog.show_janitor(self.target_pin.city, option_texts, right_option)
        return

    def update_notes(self):
        user_character_progress = self.game.datastore.user_character_progress
        case = user_character_progress.case
        dep = case.last_department_visited
        if dep == case.last_department_lair and len(self.stage.items_found) > 0:
            for item in self.stage.items_found:
                note = item.note_item
                if note not in user_character_progress.notes:
                    user_character_progress.notes.append(note)
                    user_character_progress.new_notes.append(note)
                    user_character_progress.show_notes_animation = True

            return True
        elif dep == case.list_departments[0] and user_character_progress.show_notes_animation:
            self.stage.start_notes_help_animation(300)
            user_character_progress.show_notes_animation = False
        else:
            return False
        return

    def build_option_texts(self):
        case = self.game.datastore.user_character_progress.case
        type = case.list_witness_statements[0].janitor_statement.type
        if type == 1:
            thief_sport = case.thief.sport
            correct_option = thief_sport.name
            possible_sports_list = []
            for sport in self.game.datastore.list_sports:
                if sport.category == thief_sport.category and sport.team == thief_sport.team and sport.ball != thief_sport.ball or sport.category == thief_sport.category and sport.ball == thief_sport.ball and sport.team != thief_sport.team or sport.team == thief_sport.team and sport.ball == thief_sport.ball and sport.category != thief_sport.category:
                    possible_sports_list.append(sport)

            selected_sports = []
            while len(selected_sports) < 2:
                if len(possible_sports_list) > 0:
                    sport = possible_sports_list.pop(possible_sports_list.index(random.choice(possible_sports_list)))
                else:
                    sport = random.choice(self.game.datastore.list_sports)
                if sport != thief_sport:
                    valid = True
                    for selected_sport in selected_sports:
                        if sport.category == selected_sport.category and sport.ball == selected_sport.ball and sport.team == selected_sport.team:
                            valid = False
                            break

                    if valid:
                        selected_sports.append(sport)

            incorrect_option_1 = selected_sports[0].name
            incorrect_option_2 = selected_sports[1].name
        else:
            pet = case.thief.animal
            correct_option = pet.name
            possible_animals_list = []
            for animal in self.game.datastore.list_animals:
                if animal.diet == pet.diet and animal.classification == pet.classification and animal.movement != pet.movement or animal.diet == pet.diet and animal.movement == pet.movement and animal.classification != pet.classification or animal.classification == pet.classification and animal.movement == pet.movement and animal.diet != pet.diet:
                    possible_animals_list.append(animal)

            selected_animals = []
            while len(selected_animals) < 2:
                if len(possible_animals_list) > 0:
                    animal = possible_animals_list.pop(possible_animals_list.index(random.choice(possible_animals_list)))
                else:
                    animal = random.choice(self.game.datastore.list_animals)
                if animal != pet:
                    valid = True
                    for selected_animal in selected_animals:
                        if animal.diet == selected_animal.diet and animal.classification == selected_animal.classification and animal.movement == selected_animal.movement:
                            valid = False
                            break

                    if valid:
                        selected_animals.append(animal)

            incorrect_option_1 = selected_animals[0].name
            incorrect_option_2 = selected_animals[1].name
        options = [correct_option, incorrect_option_1, incorrect_option_2]
        first_place = options.pop(options.index(random.choice(options)))
        second_place = options.pop(options.index(random.choice(options)))
        third_place = options.pop(options.index(random.choice(options)))
        return (
         [
          first_place, second_place, third_place], correct_option)

    def target_tag_enter(self, item, args):
        if self.raccoon_lids.get_alpha() > 125:
            if not self.raccoon_rollover.get_visible():
                self.raccoon_rollover.set_visible(True)
                time_diff = abs(self.raccoon_rollover_hide_timestamp - pygame.time.get_ticks())
                if abs(time_diff) > 10:
                    self.stage.render()
                    self.stage.rollover_sound.stop()
                    self.stage.rollover_sound.play()
        return

    def target_tag_leave(self, item, args):
        self.raccoon_rollover.set_visible(False)
        self.raccoon_rollover_hide_timestamp = pygame.time.get_ticks()
        return

    def on_prepare_dialog(self, animate):
        if animate:
            animations.blind_layer(self.raccoon_layer, animations.BlindDirection.HIDE_DOWN, None)
            animations.blind_layer(self.map_layer, animations.BlindDirection.HIDE_DOWN, None)
            animations.blind_layer(self.pins_layer, animations.BlindDirection.HIDE_DOWN, None)
            animations.blind_layer(self.tags_layer, animations.BlindDirection.HIDE_DOWN, None)
        else:
            self.raccoon_layer.set_visible(False)
            self.map_layer.set_visible(False)
            self.pins_layer.set_visible(False)
            self.tags_layer.set_visible(False)
        return

    def on_reset_dialog(self, animate):
        self.raccoon_layer.set_visible(True)
        self.map_layer.set_visible(True)
        self.pins_layer.set_visible(True)
        self.tags_layer.set_visible(True)
        if animate:
            animations.blind_layer(self.raccoon_layer, animations.BlindDirection.SHOW_UP, None)
            animations.blind_layer(self.map_layer, animations.BlindDirection.SHOW_UP, None)
            animations.blind_layer(self.pins_layer, animations.BlindDirection.SHOW_UP, None)
            animations.blind_layer(self.tags_layer, animations.BlindDirection.SHOW_UP, None)
        return

    def mark_city_solved(self, batch=False):
        self.mark_city_solved_step1(batch)
        self.mark_city_solved_step2(batch)
        return

    def mark_city_solved_step1(self, batch=False):
        self.active_pins.remove(self.witness_pin)
        if batch:
            self.witness_pin.get_layer().remove(self.witness_pin)
        else:
            animations.fade_out_item(self.witness_pin, True)
        if self.pin_glow.get_visible():
            self.pin_glow.set_visible(False)
            self.witness_layer.set_visible(False)
        self.add_city_tag(self.witness_pin, not batch)
        if self.minigames_resolved < 3:
            self.enable_witnesses()
        if not batch:
            self.stage.render()
            self.stage.fade_sound.play()
        return

    def mark_city_solved_step2(self, batch=False):
        if batch:
            wait = False
        elif self.stage.during_night:
            wait = True
        else:
            wait = False
            for layer in self.stage.layers:
                if animations.is_applying_blind(self.stage, layer):
                    wait = True
                    break

        if wait:
            animations.wait(self.stage, 50, self.mark_city_solved_step2)
        elif self.minigames_resolved < 3:
            if not batch:
                self.stage.start_folder_help_animation(0)
        else:
            for pin in self.active_pins:
                if batch:
                    pin.get_layer().remove(pin)
                else:
                    animations.fade_out_item(pin, True)
                self.add_city_tag(pin, not batch)

            if batch:
                self.show_target_city(batch)
            else:
                animations.wait_locked(self.stage, 1000, self.show_target_city)
            if not batch:
                if not self.stage.during_night:
                    self.stage.set_music_volume(0.2, 200)
                self.stage.render()
                self.stage.fade_sound.play()
        return

    def show_target_city(self, batch=False):
        if self.target_pin != None:
            help_shown = self.add_raccoon(self.target_pin, not batch)
            if not batch and not help_shown:
                self.stage.start_folder_help_animation(2000)
        else:
            self.enable_witnesses()
        return

    def add_raccoon(self, pin, fade=True):
        (tag_x, tag_y) = pin.city.tag_pos
        size = pin.city.tag_size
        if size == 1:
            x = tag_x + 14
            y = tag_y - 34
        elif size == 2:
            x = tag_x + 27
            y = tag_y - 34
        elif size == 3:
            x = tag_x + 26
            y = tag_y - 34
        if size < 3:
            mask_image = assets.load_mask('p1_thief_hideout_raccoon_mask_1.gif')
            if size == 1:
                raccoon_mask = ItemMask(tag_x + 17, tag_y - 34, mask_image)
            else:
                raccoon_mask = ItemMask(tag_x + 30, tag_y - 34, mask_image)
        else:
            mask_image = assets.load_mask('p1_thief_hideout_raccoon_mask_2.gif')
            raccoon_mask = ItemMask(tag_x + 31, tag_y - 34, mask_image)
        self.raccoon_rollover = ItemImage(x - 11, y - 10, self.pin_glow)
        self.raccoon_rollover.set_visible(False)
        self.raccoon_rollover_hide_timestamp = 0
        raccoon_tail = ItemImage(x, y, self.raccoon_images[0])
        raccoon_body = ItemImage(x, y, self.raccoon_images[1])
        self.raccoon_lids = ItemImage(x, y, None)
        raccoon_hands = ItemImage(x, y, self.raccoon_images[4])
        self.tags_layer.add(self.raccoon_rollover, 0)
        self.tags_layer.add(raccoon_mask, 1)
        self.raccoon_layer.add(raccoon_tail)
        self.raccoon_layer.add(raccoon_body)
        self.raccoon_layer.add(self.raccoon_lids)
        self.raccoon_layer.add(raccoon_hands)
        if fade:
            animations.fade_in_item(raccoon_tail, 500)
            animations.fade_in_item(raccoon_body, 500)
            animations.fade_in_item(self.raccoon_lids, 500)
            animations.fade_in_item(raccoon_hands, 500)
            animations.wait_locked(self.stage, 500, self.raccon_fade_in_callback)
        tag_item = pin.tag_items[0]
        tag_item.add_event_handler(ItemEvent.CLICK, self.target_tag_click)
        raccoon_mask.add_event_handler(ItemEvent.CLICK, self.target_tag_click)
        tag_item.add_event_handler(ItemEvent.MOUSE_ENTER, self.target_tag_enter)
        tag_item.add_event_handler(ItemEvent.MOUSE_LEAVE, self.target_tag_leave)
        raccoon_mask.add_event_handler(ItemEvent.MOUSE_ENTER, self.target_tag_enter)
        raccoon_mask.add_event_handler(ItemEvent.MOUSE_LEAVE, self.target_tag_leave)
        self.enable_witnesses()
        if fade:
            milliseconds = random.randint(2, 4) * 1000
            animations.wait(self.stage, milliseconds, self.show_raccoon_animation)
        cp = self.stage.game.datastore.user_character_progress
        case = cp.case
        show_help = False
        if case.time_spend < case.time_limit and cp.last_help_step_seen <= 3:
            if fade:
                help_delay = 2000
            else:
                help_delay = 800
            animations.wait_locked(self.stage, help_delay, self.show_help_raccon)
            cp.last_help_step_seen = 4
            show_help = True
        if not self.stage.during_night and fade:
            self.stage.render()
            self.raccoon_fade_sound.play()
            animations.wait(self.stage, self.raccoon_fade_sound.get_length() * 1000, self.raccoon_fade_sound_callback)
        return show_help

    def raccon_fade_in_callback(self):
        return

    def raccoon_fade_sound_callback(self):
        animations.wait(self.stage, 300, self.restore_music_after_raccoon)
        return

    def restore_music_after_raccoon(self):
        if not self.stage.during_night:
            self.stage.set_music_volume(1, 500)
        return

    def show_help_raccon(self):
        self.stage.show_help_dialog(4, 0, None, self.stage.start_folder_help_animation)
        return

    def show_raccoon_animation(self):
        animations.start_image_sequence(self.raccoon_lids, self.raccoon_animation, 25, 0)
        milliseconds = random.randint(3, 7) * 1000
        animations.wait(self.stage, milliseconds, self.show_raccoon_animation)
        return

    def add_city_tag(self, pin, fade=True):
        size = pin.city.tag_size
        tag_image = self.city_tag_images[size - 1]
        (x, y) = pin.city.tag_pos
        tag = ItemImage(x, y, tag_image)
        self.tags_layer.add(tag)
        city_name = text.to_upper(pin.city.name)
        if size == 1:
            text1 = ItemText(x + 5, y + 7, self.tag_font, 10, city_name, (0, 0, 0), None, 70, 10, 2, 2)
            text2 = None
            self.tags_layer.add(text1)
        elif size == 2:
            text1 = ItemText(x + 6, y + 7, self.tag_font, 10, city_name, (0, 0, 0), None, 96, 10, 2, 2)
            text2 = None
            self.tags_layer.add(text1)
        elif size == 3:
            break_index = -1
            for i in range(pin.city.tag_separation):
                break_index = city_name.find(' ', break_index + 1)

            if break_index == -1:
                name1 = city_name
                name2 = ''
            else:
                name1 = city_name[0:break_index]
                name2 = city_name[break_index + 1:]
            text1 = ItemText(x + 6, y + 6, self.tag_font, 10, name1, (0, 0, 0), None, 96, 10, 2, 2)
            self.tags_layer.add(text1)
            text2 = ItemText(x + 6, y + 15, self.tag_font, 10, name2, (0, 0, 0), None, 96, 10, 2, 2)
            self.tags_layer.add(text2)
        pin.tag_items = [tag, text1, text2]
        if fade:
            callback = None
            animations.fade_in_item(tag, 1000)
            animations.fade_in_item(text1, 1000)
            if text2 != None:
                animations.fade_in_item(text2, 1000)
        return

    def remove_city_tag(self, pin):
        for tag_item in pin.tag_items:
            if tag_item != None:
                animations.fade_out_item(tag_item, True)

        return

    def show_pin_glow(self, item):
        left = item.get_left() - (self.pin_glow.get_width() - item.get_width()) / 2 + 5
        top = item.get_top() - (self.pin_glow.get_height() - item.get_height()) / 2 + 5
        if item.city.flipped:
            left -= 10
        self.pin_glow.set_left(left)
        self.pin_glow.set_top(top)
        self.pin_glow.set_visible(True)
        return

    def show_witness(self, item):
        box_height = self.witness_box.get_height()
        box_width = self.witness_box.get_width()
        box_top = item.get_top() - box_height - 5
        arrow_left = item.get_left() + 9 - 20
        if item.city.flipped:
            arrow_left += 14
        box_left = arrow_left - 105
        window_width = self.game.get_window_size()[0]
        if box_left + box_width + 5 > window_width:
            box_left -= box_left + box_width + 5 - window_width
        if box_left < 5:
            box_left = 5
        if box_top < 0:
            flipv = True
            arrow_top = box_top + box_height + 47
            if item.city.flipped:
                arrow_left -= 10
            else:
                arrow_left += 5
            box_top = arrow_top + self.witness_arrow_image.get_height() - 9
        else:
            flipv = False
            arrow_top = box_top + box_height - 10
        if not flipv:
            self.witness_arrow.set_image(self.witness_arrow_image)
        else:
            self.witness_arrow.set_image(self.witness_arrow_image_flipped)
        self.witness_box.set_top(box_top)
        self.witness_box.set_left(box_left)
        self.witness_arrow.set_top(arrow_top)
        self.witness_arrow.set_left(arrow_left)
        self.witness_picholder.set_left(box_left + 13)
        self.witness_picholder.set_top(box_top + 13)
        self.witness_name.set_left(box_left + 80)
        self.witness_name.set_top(box_top + 10)
        self.witness_city.set_left(box_left + 80)
        self.witness_city.set_top(box_top + 35)
        self.witness_picholder.set_image(item.witness_image)
        self.witness_name.set_text(item.witness.name)
        self.witness_city.set_text(item.city.name)
        self.witness_layer.set_visible(True)
        return

    def disable_witnesses(self):
        for pin in self.active_pins:
            self._pin_clear_events(pin)

        return

    def enable_witnesses(self):
        for pin in self.active_pins:
            self._pin_set_events(pin)

        return


def generate_thief_location_statement(city):
    city_name = city.name
    article = city.article
    if article != '':
        article += ' '
    return 'Mencionó que se estaba hospedando en\n' + article + '&#c144,22,22!&#f:bold!' + city_name + '&#f!&#c!.'


