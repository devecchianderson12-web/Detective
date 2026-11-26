from framework import assets, animations
from framework.stage import *
from pygame.time import delay
import random, bisect
from .minigame import Minigame
from game.data import statcodes
GRID_ORIGIN = (
 308, 206)
GRID_CELL_WIDTH = 34
GRID_CELL_HEIGHT = 18
GRID_SIZE = (10, 10)
ITEM_TAGS = [
 'Soil', 'Item', 'Selection']
ITEM_STATES = [IsoState('Normal', '')]
PLACE_HOLDER_TAGS = ['Normal']

class MinigameGardener(Minigame):

    def __init__(self, stage, phase1content, witness):
        Minigame.__init__(self, stage, phase1content, witness, statcodes.MG_GARDENER, statcodes.MG_GARDENER_SOLVED, statcodes.MG_GARDENER_NOTSOLVED, 'gardener')
        self.painting = False
        self.shovel_sound = assets.load_sound('p1_minigame_gardener_shovel.ogg')
        self.minigame_solved_sound = assets.load_sound('p1_minigame_right.ogg')
        self.wrong_sound = assets.load_sound('p1_minigame_wrong.ogg')
        self.witness_minigame_box_image = assets.load_image('p1_minigame_flux_gardener_dialogue1.png')
        gardener_image = assets.load_image('p1_minigame_gardener.png')
        self.witness_item = ItemImage(438, 83, gardener_image, None)
        self.max_help_stages = 4
        self.start_time = None
        self.pause_start_time = None
        self.pause_total_time = 0
        self.title = 'JARDINERO'
        self.question_intro = 'El Jardinero se encuentra muy ocupado\nen este momento, quizás si lo ayudas\npuedas interrogarlo luego.'
        self.question = '¿Te ofreces a ayudarlo?'
        self.request_text = 'La señora de la casa me pidió que\nplantara su jardín como se\nmuestra en la lista.'
        self.request_question_text = '¿Puedes ayudarme a resolverlo?'
        self.thanks_text = '¡Muchas gracias!\n\nQuedó perfecto, la señora va a estar muy conforme con el trabajo.'
        return

    def get_music(self):
        return self.phase1content.music_minigame_1

    def blind_show_minigame_callback(self, layer):
        if not self.stage.game.datastore.user_character_progress.minigame_gardener_help_seen:
            self.stop_minigame(False)
            self.show_help_dialog()
            self.stage.game.datastore.user_character_progress.minigame_gardener_help_seen = True
        else:
            self.start_minigame()
        return

    def load_help_data(self):
        if self.help_stage == 1:
            background_image = assets.load_image('p1_minigame_gardener_help_d1.jpg')
            back_left = 124
            back_top = 132
            upper_help_text = 'El jardín está dividido en 100 partes iguales.'
            upper_text_left = 205
            upper_text_top = 92
            upper_text_width = 192
            upper_text_height = 37
            lower_help_text = 'x 100'
            lower_text_left = 304
            lower_text_top = 334
            lower_text_width = 49
            lower_text_height = 16
            self.help_previous_button.set_visible(False)
        elif self.help_stage == 2:
            background_image = assets.load_image('p1_minigame_gardener_help_d2.jpg')
            back_left = 124
            back_top = 167
            upper_help_text = 'En la lista aparecen los diferentes tipos de plantas con las que debemos llenar el jardín y las proporciones correspondientes.'
            upper_text_left = 157
            upper_text_top = 93
            upper_text_width = 288
            upper_text_height = 66
        elif self.help_stage == 3:
            background_image = assets.load_image('p1_minigame_gardener_help_d25.jpg')
            back_left = 124
            back_top = 132
            upper_help_text = 'Podemos plantar de a una casilla haciendo click en ella.'
            upper_text_left = 156
            upper_text_top = 93
            upper_text_width = 288
            upper_text_height = 42
            lower_help_text = 'O podemos plantar de a varias, dejando apretado el botón izquierdo del ratón\ny moviendo el cursor.'
            lower_text_left = 151
            lower_text_top = 308
            lower_text_width = 298
            lower_text_height = 54
        elif self.help_stage == 4:
            background_image = assets.load_image('p1_minigame_gardener_help_d3.jpg')
            back_left = 124
            back_top = 153
            upper_help_text = 'al completar la cantidad correspondiente a cada planta, cambiará el color en la lista a rojo.'
            upper_text_left = 154
            upper_text_top = 93
            upper_text_width = 288
            upper_text_height = 56
            lower_help_text = 'cuando se complete toda la lista, se dará por concluída la tarea.'
            lower_text_left = 157
            lower_text_top = 313
            lower_text_width = 288
            lower_text_height = 39
        background_help_image_item = ItemImage(0, 0, None, None)
        background_help_image_item.set_image(background_image)
        background_help_image_item.set_lefttop(back_left, back_top)
        self.help_current_layer.add(background_help_image_item)
        if self.help_stage != 2:
            self.lower_help_text_item = ItemText(lower_text_left, lower_text_top, self.font_14, 16, lower_help_text, (183,
                                                                                                                      35,
                                                                                                                      35), None, lower_text_width, lower_text_height, 2)
            self.help_current_layer.add(self.lower_help_text_item)
        self.upper_help_text_item = ItemText(upper_text_left, upper_text_top, self.font_14, 16, upper_help_text, (183,
                                                                                                                  35,
                                                                                                                  35), None, upper_text_width, upper_text_height, 2)
        self.help_current_layer.add(self.upper_help_text_item)
        return

    def start_minigame(self):
        self.play_music()
        self.start_play_stats_event()
        if self.start_time == None:
            self.start_time = pygame.time.get_ticks()
        else:
            self.pause_total_time += pygame.time.get_ticks() - self.pause_start_time
            self.pause_start_time = None
        return

    def stop_minigame(self, solved):
        self.end_play_stats_event(solved)
        self.pause_start_time = pygame.time.get_ticks()
        return

    def set_up_minigame(self):
        character_progress = self.stage.game.datastore.user_character_progress
        minigame_level = character_progress.range.minigame_level
        if minigame_level == 1:
            n_fractions = 0
        elif minigame_level == 2:
            n_fractions = 5
        else:
            n_fractions = random.randint(2, 3)
        self.average_time = 90
        self.build_list(n_fractions)
        self.prepare_grid()
        self.set_up_game_background_items()
        self.set_up_witness()
        self.set_up_options()
        self.set_up_buttons()
        self.set_up_texts()
        self.stage.add_layer(self.grid_layer)
        self.stage.add_layer(self.grid_selection_layer)
        self.stage.add_layer(self.grid_goodjob_layer)
        self.stage.set_prerender_buffer(self.grid_layer)
        return

    def build_list(self, n_fractions):
        self.list = []
        random.seed()
        (percentages, fractions) = self.generate_values(n_fractions)
        added_flowers = []
        while len(added_flowers) < 4:
            flower = random.randint(1, 5)
            if flower not in added_flowers:
                if flower == 1:
                    option_icon = assets.load_image('p1_minigame_gardener_opt_daisy.png')
                    text_icon = assets.load_image('p1_minigame_gardener_icon_daisy.png')
                    item = ListItem(option_icon, 'MARGARITAS', text_icon, percentages[len(added_flowers)], fractions[len(added_flowers)], 'i010', 0)
                    self.list.append(item)
                elif flower == 2:
                    option_icon = assets.load_image('p1_minigame_gardener_opt_carnation.png')
                    text_icon = assets.load_image('p1_minigame_gardener_icon_carnation.png')
                    item = ListItem(option_icon, 'CLAVELES', text_icon, percentages[len(added_flowers)], fractions[len(added_flowers)], 'i011', 0)
                    self.list.append(item)
                elif flower == 3:
                    option_icon = assets.load_image('p1_minigame_gardener_opt_rose.png')
                    text_icon = assets.load_image('p1_minigame_gardener_icon_rose.png')
                    item = ListItem(option_icon, 'ROSAS', text_icon, percentages[len(added_flowers)], fractions[len(added_flowers)], 'i014', 0)
                    self.list.append(item)
                elif flower == 4:
                    option_icon = assets.load_image('p1_minigame_gardener_opt_jazmin.png')
                    text_icon = assets.load_image('p1_minigame_gardener_icon_jazmin.png')
                    item = ListItem(option_icon, 'JAZMINES', text_icon, percentages[len(added_flowers)], fractions[len(added_flowers)], 'i013', 0)
                    self.list.append(item)
                else:
                    option_icon = assets.load_image('p1_minigame_gardener_opt_tulip_y.png')
                    text_icon = assets.load_image('p1_minigame_gardener_icon_tulip_y.png')
                    item = ListItem(option_icon, 'TULIPANES', text_icon, percentages[len(added_flowers)], fractions[len(added_flowers)], 'i012', 0)
                    self.list.append(item)
                added_flowers.append(flower)

        option_icon = assets.load_image('p1_minigame_gardener_opt_soil.png')
        text_icon = assets.load_image('p1_minigame_gardener_icon_soil.png')
        item = ListItem(option_icon, 'TIERRA', text_icon, percentages[4], fractions[4], 'soil', GRID_SIZE[0] * GRID_SIZE[1])
        self.list.append(item)
        return

    def generate_values(self, n_fractions):
        n_items = 5
        percentages = [0 for i in range(n_items)]
        fractions = [None for i in range(n_items)]
        total = 0
        fractions_assigned = 0
        while fractions_assigned < n_fractions or n_fractions < n_items and total >= 100:
            if n_fractions == n_items:
                fraction_sets = [
                 [('1_4', 25), ('1_4', 25), ('1_5', 20), ('1_5', 20), ('1_10', 10)],
                 [('2_5', 40), ('3_10', 30), ('1_10', 10), ('1_10', 10), ('1_10', 10)],
                 [('2_5', 40), ('1_5', 20), ('1_5', 20), ('1_10', 10), ('1_10', 10)],
                 [('3_10', 30), ('3_10', 30), ('1_5', 20), ('1_10', 10), ('1_10', 10)]]
                fractions_options = random.choice(fraction_sets)
            else:
                fractions_options = [('1_2', 50), ('1_4', 25), ('1_5', 20), ('1_10', 10), ('2_4', 50), ('2_5', 40), ('3_10', 30)]
            fractions_assigned = 0
            percentages = [0 for i in range(n_items)]
            fractions = [None for i in range(n_items)]
            indexes = [i for i in range(n_items)]
            total = 0
            while fractions_assigned < n_fractions and len(fractions_options) > 0:
                f = random.choice(fractions_options)
                fractions_options.remove(f)
                percentage = f[1]
                if total + percentage <= 100:
                    index = random.choice(indexes)
                    indexes.remove(index)
                    percentages[index] += percentage
                    fractions[index] = f
                    total += percentage
                    fractions_assigned += 1

        while total < 100:
            index = random.randint(0, n_items - 1)
            if percentages[index] < 65 and fractions[index] == None:
                percentages[index] += 5
                total += 5

        return (
         percentages, fractions)

    def set_up_game_background_items(self):
        garden_image = assets.load_image('p1_minigame_gardener_background.png')
        garden_item_image = ItemImage(14, 57, garden_image)
        self.layer.add(garden_item_image)
        grid_image = assets.load_image('p1_minigame_gardener_grid.png')
        grid_item_image = ItemImage(137, 206, grid_image)
        self.layer.add(grid_item_image)
        grid_mask = assets.load_mask('p1_minigame_gardener_grid_mask.gif')
        self.grid_mask_item = ItemMask(134, 209, grid_mask)
        self.grid_mask_item.add_event_handler(ItemEvent.MOUSE_ENTER, self.grid_enter)
        self.grid_mask_item.add_event_handler(ItemEvent.MOUSE_LEAVE, self.grid_leave)
        self.grid_mask_item.add_event_handler(ItemEvent.MOUSE_MOVE, self.grid_mousemove)
        self.grid_mask_item.add_event_handler(ItemEvent.CLICK, self.grid_click)
        self.layer.add(self.grid_mask_item)
        return

    def set_up_options(self):
        self.option_image_normal = assets.load_image('p1_minigame_gardener_opt_button.png')
        self.option_image_rollover = assets.load_image('p1_minigame_gardener_opt_rollover.png')
        self.option_image_selected = assets.load_image('p1_minigame_gardener_opt_selected.png')
        self.add_option(8, 180, self.list[0])
        self.add_option(52, 180, self.list[1])
        self.add_option(95, 180, self.list[2])
        self.add_option(31, 225, self.list[3])
        self.add_option(74, 225, self.list[4])
        self.selected_option = None
        self.mouse_option_cursor = ItemImage(0, 0, None)
        return

    def add_option(self, x, y, list_item):
        option_item = ItemImage(x, y, self.option_image_normal)
        option_item.set_rollover_image(self.option_image_rollover, self.rollover_sound)
        option_item.list_item = list_item
        option_item.add_event_handler(ItemEvent.CLICK, self.tool_option_item_click)
        self.layer.add(option_item)
        icon_item = ItemImage(x, y, list_item.option_icon)
        self.layer.add(icon_item)
        return option_item

    def set_up_buttons(self):
        close_image = assets.load_image('p1_minigames_btn_close_normal.png')
        rollover_image = assets.load_image('p1_minigames_btn_close_active.png')
        close_item = ItemImage(268, 49, close_image)
        close_item.set_rollover_image(rollover_image, self.rollover_sound)
        close_item.add_event_handler(ItemEvent.CLICK, self.close_click)
        self.layer.add(close_item)
        help_image = assets.load_image('p1_minigames_btn_help_normal.png')
        rollover_image = assets.load_image('p1_minigames_btn_help_active.png')
        help_item = ItemImage(303, 49, help_image)
        help_item.set_rollover_image(rollover_image, self.rollover_sound)
        help_item.add_event_handler(ItemEvent.CLICK, self.help_click)
        self.layer.add(help_item)
        return

    def set_up_texts(self):
        self.add_list_item(109, 112, self.list[0])
        self.add_list_item(109, 132, self.list[1])
        self.add_list_item(109, 151, self.list[2])
        self.add_list_item(311, 122, self.list[3])
        self.add_list_item(311, 142, self.list[4])
        self.update_items_text()
        return

    def add_list_item(self, x, y, list_item):
        icon_item = ItemImage(x, y, list_item.text_icon)
        self.layer.add(icon_item)
        text = list_item.text + '.................'
        text_item = ItemText(x + 26, y + 4, self.font_12_bld, 0, text, (80, 70, 70), None, 108, 19)
        self.layer.add(text_item)
        if list_item.fraction == None:
            if list_item.percentage < 10:
                text = ' ' + str(list_item.percentage)
            else:
                text = str(list_item.percentage)
            percentage_item = ItemText(x + 135, y - 1, self.font_18, 0, text, (80,
                                                                               70,
                                                                               70))
            self.layer.add(percentage_item)
            percentage_symbol_item = ItemText(x + 160, y + 4, self.font_12_bld, 0, '%', (80,
                                                                                         70,
                                                                                         70))
            self.layer.add(percentage_symbol_item)
        else:
            text = list_item.fraction[0].replace('_', '/')
            percentage_item = ItemText(x + 135, y - 1, self.font_18, 0, text, (80,
                                                                               70,
                                                                               70))
            self.layer.add(percentage_item)
            percentage_symbol_item = None
        list_item.text_items = [text_item, percentage_item, percentage_symbol_item]
        return

    def prepare_grid(self):
        self.grid_layer = Layer()
        self.grid_positions = []
        self.grid_goodjob_layer = Layer()
        self.grid_selection_layer = Layer()
        self.stage.set_tags(ITEM_TAGS)
        self.stage.set_grid_definition(GRID_ORIGIN, GRID_CELL_WIDTH, GRID_CELL_HEIGHT, 1)
        self.stage.set_items('p1gs01')
        self.grid_data = [[None for i in range(10)] for j in range(10)]
        self.selection_grid = [[ItemCell(self.stage, 'i001', ITEM_STATES[0], False, j, i) for i in range(10)] for j in range(10)]
        return

    def close_click(self, item, args):
        self.stop_minigame(False)
        self.phase1content.minigame_solved(False)
        self.close_minigame()
        return

    def grid_enter(self, item, args):
        if self.selected_option != None:
            item_type = self.selected_option.list_item.item_type
            if item_type == 'soil':
                self.stage.set_mouse_cursor(None)
            else:
                item_image = self.stage.load_item_image(item_type, ITEM_STATES[0])
                item_definition = self.stage.get_item_definition(item_type)
                self.mouse_option_cursor.set_image(item_image)
                self.stage.set_mouse_cursor(self.mouse_option_cursor, item_definition.center)
        return

    def grid_leave(self, item, args):
        if not self.painting:
            self.stage.set_mouse_cursor(None)
            self.grid_selection_layer.empty()
        return

    def grid_mousemove(self, item, args):
        if not self.painting and self.selected_option != None:
            (row, col) = self.stage.get_rowcol(args.x, args.y)
            if row >= 0 and row < GRID_SIZE[0] and col >= 0 and col < GRID_SIZE[1]:
                self.grid_selection_layer.empty()
                cell = self.selection_grid[row][col]
                filled_items = self.get_items_filled()
                selection_type = self.selected_option.list_item.item_type
                selection_filled = self.get_selection_filled(selection_type, filled_items)
                self.set_selection_cell_type(row, col, selection_type, cell, selection_filled, filled_items)
                self.grid_selection_layer.add(cell)
            else:
                self.grid_selection_layer.empty()
        return

    def grid_click(self, item, args):
        if self.selected_option != None:
            (row, col) = self.stage.get_rowcol(args.x, args.y)
            if row >= 0 and row < GRID_SIZE[0] and col >= 0 and col < GRID_SIZE[1]:
                self.painting = True
                self.painting_from = (row, col)
                self.stage.capture_leftmousedown(self.grid_mask_item, self.mouse_paint)
        return

    def mouse_paint(self, mouse_args, released):
        (row, col) = self.stage.get_rowcol(mouse_args.x, mouse_args.y)
        if row >= 0 and row < GRID_SIZE[0] and col >= 0 and col < GRID_SIZE[1]:
            mouse_inside = True
        else:
            if row < 0:
                row = 0
            elif row >= GRID_SIZE[0]:
                row = GRID_SIZE[0] - 1
            if col < 0:
                col = 0
            elif col >= GRID_SIZE[1]:
                col = GRID_SIZE[1] - 1
            mouse_inside = False
        self.painting_to = (
         row, col)
        if released:
            self.painting = False
            minigame_solved = self.paint_items(mouse_args.x, mouse_args.y)
            self.grid_selection_layer.empty()
            if not mouse_inside or minigame_solved:
                self.stage.set_mouse_cursor(None)
            else:
                self.grid_selection_layer.empty()
                self.grid_selection_layer.add(self.selection_grid[row][col])
        else:
            self.update_paint_region()
        return

    def update_paint_region(self):
        from_row = min(self.painting_from[0], self.painting_to[0])
        from_col = min(self.painting_from[1], self.painting_to[1])
        to_row = max(self.painting_from[0], self.painting_to[0])
        to_col = max(self.painting_from[1], self.painting_to[1])
        filled_items = self.get_items_filled()
        selection_type = self.selected_option.list_item.item_type
        selection_filled = self.get_selection_filled(selection_type, filled_items)
        for r in range(0, 10):
            for c in range(0, 10):
                cell = self.selection_grid[r][c]
                if r >= from_row and r <= to_row and c >= from_col and c <= to_col:
                    self.set_selection_cell_type(r, c, selection_type, cell, selection_filled, filled_items)
                    if cell.get_layer() == None:
                        self.grid_selection_layer.add(cell)
                elif cell.get_layer() != None:
                    self.grid_selection_layer.remove(cell)

        return

    def set_selection_cell_type(self, r, c, selection_type, selection_cell, selection_filled, filled_items):
        if selection_type == 'soil':
            selection_cell.set_type('i001')
        elif selection_filled:
            selection_cell.set_type('i002')
        elif self.grid_data[r][c] != None:
            item_type = self.grid_data[r][c].get_type()
            if item_type == selection_type:
                selection_cell.set_type('i001')
            else:
                filled = False
                for item in filled_items:
                    if item.item_type == item_type:
                        filled = True
                        break

                if filled:
                    selection_cell.set_type('i002')
                else:
                    selection_cell.set_type('i001')
        else:
            selection_cell.set_type('i001')
        return

    def get_selection_filled(self, selection_type, filled_items):
        filled = False
        for item in filled_items:
            if item.item_type == selection_type:
                filled = True
                break

        return filled

    def paint_items(self, x, y):
        if self.selected_option == None:
            return False
        else:
            item_type = self.selected_option.list_item.item_type
            old_filled_items = self.get_items_filled()
            has_filled_item = self.has_selection_filled_item(item_type, old_filled_items)
            if has_filled_item:
                self.stage.render()
                self.wrong_sound.play()
                return False
            (from_row, from_col) = self.painting_from
            (to_row, to_col) = self.painting_to
            for r in range(min(from_row, to_row), max(from_row, to_row) + 1):
                for c in range(min(from_col, to_col), max(from_col, to_col) + 1):
                    if self.grid_data[r][c] != None:
                        cell = self.grid_data[r][c]
                        if item_type != cell.get_type():
                            self.substract_item(cell.get_type())
                            if item_type != 'soil':
                                cell.set_type(item_type)
                                self.sum_item(item_type)
                            else:
                                self.grid_data[r][c] = None
                                self.grid_layer.remove(cell)
                                self.grid_positions.remove(r + c)
                                self.sum_item('soil')
                    elif item_type != 'soil':
                        item_type = self.selected_option.list_item.item_type
                        cell = ItemCell(self.stage, item_type, ITEM_STATES[0])
                        cell.set_position(r, c)
                        self.grid_data[r][c] = cell
                        index = bisect.bisect(self.grid_positions, r + c)
                        self.grid_layer.add(cell, index)
                        self.grid_positions.insert(index, r + c)
                        self.substract_item('soil')
                        self.sum_item(item_type)

            new_filled_items = self.update_items_text(old_filled_items)
            self.stage.render()
            self.shovel_sound.play()
            if len(new_filled_items) > 0:
                center_row = _div(float(from_row + to_row) , 2)
                center_col = _div(float(from_col + to_col) , 2)
                (x, y) = self.stage.get_xy(center_row, center_col)
                separation = 95
                x -= _div((len(new_filled_items) - 1) * separation , 2)
                y -= 20
                for item in new_filled_items:
                    if item.percentage != 0:
                        self.start_goodjob_animation(item, x, y)
                        x += separation

                self.stage.render()
                self.minigame_solved_sound.play()
            return self.check_minigame_solved()
        return

    def has_selection_filled_item(self, selection_item_type, filled_items):
        if selection_item_type == 'soil':
            return False
        for item in filled_items:
            if item.item_type == selection_item_type:
                return True

        (from_row, from_col) = self.painting_from
        (to_row, to_col) = self.painting_to
        for r in range(min(from_row, to_row), max(from_row, to_row) + 1):
            for c in range(min(from_col, to_col), max(from_col, to_col) + 1):
                if self.grid_data[r][c] != None:
                    cell = self.grid_data[r][c]
                    if selection_item_type != cell.get_type():
                        for item in filled_items:
                            if item.item_type == cell.get_type():
                                return True

        return False

    def sum_item(self, item_type):
        for item in self.list:
            if item.item_type == item_type:
                item.count += 1
                break

        return

    def substract_item(self, item_type):
        for item in self.list:
            if item.item_type == item_type:
                item.count -= 1
                break

        return

    def get_items_filled(self):
        filled_items = []
        total = GRID_SIZE[0] * GRID_SIZE[1]
        for item in self.list:
            current_percentage = int(_div(float(item.count) , total) * 100)
            if current_percentage == item.percentage:
                filled_items.append(item)

        return filled_items

    def update_items_text(self, exclude_filled_items=[]):
        filled_items = []
        total = GRID_SIZE[0] * GRID_SIZE[1]
        for item in self.list:
            current_percentage = int(_div(float(item.count) , total) * 100)
            if current_percentage == item.percentage:
                for item_text in item.text_items:
                    if item_text != None:
                        item_text.set_color((154, 4, 4))

                if item not in exclude_filled_items:
                    filled_items.append(item)
            else:
                for item_text in item.text_items:
                    if item_text != None:
                        item_text.set_color((80, 70, 70))

        return filled_items

    def start_goodjob_animation(self, item, x, y):
        animation = GoodJobAnimation(self.stage, self.grid_goodjob_layer, item, x, y)
        animation.start()
        return

    def tool_option_item_click(self, item, args):
        self.stage.render()
        self.stage.click_sound.play()
        self.set_selected_option(item)
        return

    def set_selected_option(self, item):
        if self.selected_option != None:
            self.selected_option.set_image(self.option_image_normal)
            self.selected_option.set_rollover_image(self.option_image_rollover, self.rollover_sound)
        self.selected_option = item
        item.set_image(self.option_image_selected)
        item.set_rollover_image(None, None)
        return

    def check_minigame_solved(self):
        solved = True
        total = GRID_SIZE[0] * GRID_SIZE[1]
        for item in self.list:
            current_percentage = int(_div(float(item.count) , total) * 100)
            if current_percentage != item.percentage:
                solved = False
                break

        if solved:
            self.stop_minigame(True)
            self.grid_selection_layer.empty()
            animations.wait_locked(self.stage, 2000, self.minigame_solved_callback)
        return solved

    def create_character_happy_item(self):
        gardener_happy_image = assets.load_image('p1_minigame_gardener_happy.png')
        return ItemImage(438, 83, gardener_happy_image, None)

    def calculate_solved_score(self):
        if self.pause_start_time != None:
            self.pause_total_time += pygame.time.get_ticks() - self.pause_start_time
            self.pause_start_time = None
        elapsed_time = _div((pygame.time.get_ticks() - self.start_time - self.pause_total_time) , 1000)
        if elapsed_time <= self.average_time:
            time_score = _div(128 * (self.average_time - elapsed_time) , self.average_time)
        else:
            time_score = 0
        return [100,
         time_score]


class ListItem():

    def __init__(self, option_icon, text, text_icon, percentage, fraction, item_type, count):
        self.option_icon = option_icon
        self.text = text
        self.text_icon = text_icon
        self.percentage = percentage
        self.fraction = fraction
        self.item_type = item_type
        self.count = count
        return


class GoodJobAnimation():

    def __init__(self, stage, grid_goodjob_layer, item, x, y):
        self.stage = stage
        self.grid_goodjob_layer = grid_goodjob_layer
        if item.fraction == None:
            if item.percentage < 10:
                number_str = '0' + str(item.percentage)
            else:
                number_str = str(item.percentage)
            self.color_image = assets.load_image('p1_minigame_gardener_goodjob_n' + number_str + '.png')
            self.white_image = assets.load_image('p1_minigame_gardener_goodjob_w' + number_str + '.png')
        else:
            fraction_str = item.fraction[0]
            self.color_image = assets.load_image('p1_minigame_gardener_goodjob_f' + fraction_str + '.png')
            self.white_image = assets.load_image('p1_minigame_gardener_goodjob_w' + fraction_str + '.png')
        left = x - _div(self.color_image.get_width() , 2)
        top = y - _div(self.color_image.get_height() , 2)
        self.color_item = ItemImage(left, top, self.color_image)
        self.white_item = ItemImage(left, top, self.white_image)
        return

    def start(self):
        self.grid_goodjob_layer.add(self.color_item)
        self.grid_goodjob_layer.add(self.white_item)
        from_size = (
         int(float(self.color_image.get_width()) * 0.82), int(float(self.color_image.get_height()) * 0.82))
        animations.start_resize(self.color_item, self.color_image, from_size, self.color_image.get_size(), 230, 1, self.__resize_callback)
        to_size = (int(float(self.white_image.get_width()) * 0.82), int(float(self.white_image.get_height()) * 0.82))
        animations.start_resize(self.white_item, self.white_image, from_size, self.white_image.get_size(), 230, 1)
        self.white_item.set_alpha(200)
        animations.fade_out_item(self.white_item, True, 230)
        return

    def __resize_callback(self, item):
        animations.wait(self.stage, 100, self.__wait_callback)
        return

    def __wait_callback(self):
        if self.grid_goodjob_layer.get_stage() != None:
            animations.start_move(self.color_item, self.color_item.get_left(), self.color_item.get_top() - 83, 560)
            animations.fade_out_item(self.color_item, True, 560)
        return


