from .stage import *
from . import leveldesigner
clipboard_layer = None
clipboard_item = None

class SetItemsStage(StageIso):

    def __init__(self, game, origin, cell_width, cell_height, grid_size, tags, place_holder_tags, states, set_prefix):
        StageIso.__init__(self, game, tags)
        (window_width, window_height) = game.get_window_size()
        file_name = self.get_state_file_name()
        state_loaded = False
        try:
            data = assets.load_data(file_name, ';', False)
            if data != None:
                state_set_prefix = data[0][0]
                set_number = int(data[1][0])
                item_index = int(data[2][0])
                zoom = int(data[3][0])
                place_holders_visible = int(data[4][0]) == 1
                default_state_name = data[5][0]
                state_loaded = True
        except Exception as message:
            print(('Cannot read set designer state:', file_name))
            raise SystemExit(message)

        if not state_loaded or state_set_prefix != set_prefix:
            set_number = 1
            item_index = 0
            zoom = 2
            place_holders_visible = True
            default_state_name = ''
        self.tags = tags
        self.place_holder_tags = place_holder_tags
        self.states = states
        self.zoom = zoom
        self.origin = origin
        self.set_grid_definition(self.get_adjusted_origin(), cell_width, cell_height, self.zoom)
        self.grid_size = grid_size
        self.pending_save = False
        self.set_closed_handler(self.on_closed)
        self.items_layer = Layer()
        self.add_layer(self.items_layer)
        self.grid_layer = Layer()
        self.add_layer(self.grid_layer)
        self.grid = None
        self.current_place_holder = 0
        self.current_place_holder_visible = -1
        self.place_holder_items = []
        self.place_holders_layer = LayerBuffered(window_width, window_height, True)
        self.place_holders_layer.set_visible(place_holders_visible)
        self.add_layer(self.place_holders_layer)
        self.font = assets.load_font('freesansbold.ttf', 12)
        (window_width, window_height) = game.get_window_size()
        text_color = (0, 0, 10)
        text_background = (215, 232, 237, 150)
        name_width = 95
        self.item_type_item = ItemRect(5, window_height - 23 - 18 - 5, name_width, 18, self.font, 0, '', text_color, (241,
                                                                                                                      242,
                                                                                                                      201,
                                                                                                                      150))
        self.stage_name_item = ItemRect(5, window_height - 23, name_width, 18, self.font, 0, '', text_color, text_background)
        self.tag_name_item = ItemRect(window_width - name_width - 5, 5, name_width, 18, self.font, 0, '', text_color, text_background)
        self.move_placeholder_item = ItemRect(5 + name_width + 5, window_height - 46, window_width - name_width - 15, 18, self.font, 0, 'xxxxx', (255,
                                                                                                                                                  255,
                                                                                                                                                  255), None)
        self.state_items = []
        self.options_item = ItemRect(5 + name_width + 5, window_height - 23, window_width - name_width - 15, 18, self.font, 0, '', text_color, text_background)
        self.options_layer = LayerBuffered(window_width, window_height, True)
        self.options_layer.add(self.item_type_item)
        self.options_layer.add(self.stage_name_item)
        self.options_layer.add(self.tag_name_item)
        self.options_layer.add(self.move_placeholder_item)
        self.options_layer.add(self.options_item)
        self.add_layer(self.options_layer)
        self.current_options_mod = None
        self.start_timer('update_options', 50, self.update_options_text)
        self.current_item = None
        self.items = []
        self.item_states = {}
        self.set_prefix = set_prefix
        self.load_set(set_number)
        self.item_index = item_index
        self.current_item = None
        self.move_placeholder_mode = False
        self.show_current_item(default_state_name)
        self.update_move_placeholder_text()
        self.update_options_text(None, None)
        return

    def select_item_type(self, type):
        for index in range(len(self.items)):
            item = self.items[index]
            if item.get_type() == type:
                self.item_index = index
                self.current_place_holder = 0
                self.show_current_item()
                break

        return

    def update_grid(self):
        if self.grid != None:
            self.grid_layer.remove(self.grid)
        if self.current_item == None:
            mark_size = None
        else:
            mark_size = self.current_item.get_definition().size
        place_holder_cell = None
        if self.current_item != None and self.move_placeholder_mode:
            definition = self.current_item.get_definition()
            if self.current_place_holder < len(definition.place_holders):
                selected_place_holder = definition.place_holders[self.current_place_holder]
                place_holder_cell = self.current_item.get_place_holder_rowcol(selected_place_holder)
                if place_holder_cell[0] < 0 or place_holder_cell[1] < 0:
                    place_holder_cell = None
        self.grid = create_grid(self, self.grid_size, True, mark_size, place_holder_cell)
        self.grid_layer.add(self.grid)
        return

    def update_options_text(self, key, data):
        mod = get_common_modifiers(pygame.key.get_mods())
        if mod == pygame.KMOD_NONE:
            text = 'Arrows = Move'
            if not self.move_placeholder_mode:
                text += ' | Q/A = Change type'
            else:
                text += ' | Q/A = Back/Forw.'
            text += ' | S = State | T = Tag | '
            if self.move_placeholder_mode:
                text += 'Tab = Focus | '
            text += 'Z = Zoom'
            self.options_item.set_text(text)
        elif mod == pygame.KMOD_LSHIFT or mod == pygame.KMOD_RSHIFT:
            if self.move_placeholder_mode:
                text = 'T = Previous Tag'
            else:
                text = ''
            self.options_item.set_text(text)
        elif mod == pygame.KMOD_LCTRL or mod == pygame.KMOD_RCTRL:
            text = 'Arrows = Resize'
            if not self.move_placeholder_mode:
                text += ' | Page Up/Down = Change set'
            self.options_item.set_text(text)
        elif mod == pygame.KMOD_LALT or mod == pygame.KMOD_RALT:
            if self.place_holders_layer.get_visible():
                hide_text = 'Hide'
            else:
                hide_text = 'Show'
            self.options_item.set_text('N = New | M = Move | S = Select | T = Tag | Del = Delete | H = ' + hide_text)
        else:
            self.options_item.set_text('')
        self.current_options_mod = mod
        return

    def get_set_file_name(self):
        return self.set_name + '.tcs'

    def get_state_file_name(self):
        return 'setdesigner.sta'

    def get_key_repeat(self):
        return (200, 10)

    def load_set(self, set_number):
        set_name = self.set_prefix + 's' + str(set_number).zfill(2)
        self.set_number = set_number
        self.set_name = set_name
        self.stage_name_item.set_text(set_name)
        if os.path.isfile(os.path.join('data', self.get_set_file_name())):
            item_definitions = None
        else:
            item_definitions = {}
        self.set_items(self.set_name, '', item_definitions)
        item_definitions = self.get_item_definitions()
        original_item_definitions = item_definitions.copy()
        default_state = None
        for state in self.states:
            if state.suffix == '':
                default_state = state
                break

        if default_state == None:
            raise Exception('There is no default state defined')
        self.items = []
        self.item_states = {}
        multiplier = self.get_grid_multiplier()
        for name in os.listdir('images'):
            if name.startswith(self.set_name):
                item_type = name[len(self.set_name):]
                k = item_type.rfind('.')
                if k != -1:
                    item_type = item_type[:k]
                if item_type.rfind('$') == -1:
                    type_len = len(item_type)
                    if type_len > 0 and item_type[type_len - 1].isdigit():
                        if multiplier != 1:
                            image = self.load_item_image(item_type, default_state, False)
                            (width, height) = image.surface.get_size()
                            image.surface = pygame.transform.scale(image.surface, (width * multiplier, height * multiplier))
                        definition = item_type in item_definitions or IsoDefinition((0,
                                                                                           0), (1,
                                                                                                1), [], self.tags[0], [])
                        new_definition = True
                    else:
                        definition = item_definitions[item_type]
                        new_definition = False
                        definition = IsoDefinition(definition.center, definition.size, definition.place_holders, definition.tag, [])
                    item_definitions[item_type] = definition
                    item = ItemCell(self, item_type, default_state, False, 0, 0)
                    if new_definition:
                        center_x = _div(_div(item.get_width() , multiplier) , 2)
                        center_y = _div(_div(item.get_height() , multiplier) , 2)
                        definition.center = (center_x, center_y)
                        item.reload_definition()
                    self.items.append(item)
                else:
                    full_item_type = item_type
                    k = item_type.rfind('_')
                    if k != -1:
                        state_suffix = item_type[k + 1:]
                        item_type = item_type[:k]
                        state_name = None
                        for state in self.states:
                            if state.suffix == state_suffix:
                                item_state = state
                                state_name = state.name
                                break

                        if state_name != None:
                            type_len = len(item_type)
                            if type_len > 0:
                                if item_type[type_len - 1].isdigit():
                                    if multiplier != 1:
                                        image = self.load_item_image(item_type, item_state, False)
                                        (width, height) = image.surface.get_size()
                                        image.surface = pygame.transform.scale(image.surface, (width * multiplier, height * multiplier))
                                    if item_type in self.item_states:
                                        states = self.item_states[item_type]
                                    else:
                                        states = []
                                        self.item_states[item_type] = states
                                    state_center = None
                                    if item_type in original_item_definitions:
                                        definition = original_item_definitions[item_type]
                                        for state in definition.states:
                                            if state.name == state_name:
                                                state_center = state.center
                                                break

                                    if state_center == None:
                                        center_x = _div(_div(item.get_width() , multiplier) , 2)
                                        center_y = _div(_div(item.get_height() , multiplier) , 2)
                                        state_center = (center_x, center_y)
                                    clip = os.path.exists('images/' + self.set_name + full_item_type + '$x.png')
                                    states.append(IsoDefState(state_name, state_center, clip))

        for item in self.items:
            item_type = item.get_type()
            if item_type in self.item_states:
                item.get_definition().states = self.item_states[item_type]

        self.items.sort(key=ItemCell.get_type)
        return

    def notify_set_changed(self):
        self.pending_save = True
        self.stop_timer('auto_save')
        self.start_timer('auto_save', 5000, self.save_set, None)
        return

    def on_closed(self, stage):
        self.save_set(None, None)
        file_name = self.get_state_file_name()
        try:
            data = []
            data.append([self.set_prefix])
            data.append([str(self.set_number)])
            data.append([str(self.item_index)])
            data.append([str(self.zoom)])
            if self.place_holders_layer.get_visible():
                data.append(['1'])
            else:
                data.append(['0'])
            if self.current_item == None:
                data.append([''])
            else:
                data.append([self.current_item.get_state().name])
            assets.save_data(file_name, data)
        except Exception as message:
            print(('Cannot save set designer state:', file_name))
            raise SystemExit(message)

        return

    def save_set(self, key, data):
        self.stop_timer('auto_save')
        if self.pending_save:
            self.pending_save = False
            file_name = self.get_set_file_name()
            try:
                data = []
                for item in self.items:
                    item_line = []
                    item_line.append(item.get_type())
                    definition = item.get_definition()
                    item_line.append(str(definition.center[0]))
                    item_line.append(str(definition.center[1]))
                    item_line.append(str(definition.size[0]))
                    item_line.append(str(definition.size[1]))
                    first = True
                    placeholders_text = []
                    for place_holder in definition.place_holders:
                        if first:
                            first = False
                        else:
                            placeholders_text.append('|')
                        placeholders_text.append(place_holder.tag)
                        placeholders_text.append(',')
                        placeholders_text.append(str(place_holder.x))
                        placeholders_text.append(',')
                        placeholders_text.append(str(place_holder.y))

                    item_line.append(('').join(placeholders_text))
                    item_line.append(definition.tag)
                    first = True
                    state_text = []
                    for state in definition.states:
                        if first:
                            first = False
                        else:
                            state_text.append('|')
                        state_text.append(state.name)
                        state_text.append(',')
                        state_text.append(str(state.center[0]))
                        state_text.append(',')
                        state_text.append(str(state.center[1]))
                        state_text.append(',')
                        if state.clip:
                            state_text.append('1')
                        else:
                            state_text.append('0')

                    item_line.append(('').join(state_text))
                    data.append(item_line)

                assets.save_data(file_name, data)
            except Exception as message:
                print(('Cannot save items data:', file_name))
                raise SystemExit(message)

        return

    def show_current_item(self, default_state_name=None):
        if self.current_item != None:
            self.items_layer.remove(self.current_item)
            self.current_item = None
        if len(self.items) > 0:
            self.current_item = self.items[self.item_index]
            self.items_layer.add(self.current_item)
            self.item_type_item.set_text(self.current_item.get_type())
            if default_state_name != None:
                type = self.current_item.get_type()
                if type in self.item_states:
                    item_states = self.item_states[type]
                    valid_state = False
                    for state in item_states:
                        if state.name == default_state_name:
                            valid_state = True
                            break

                    if valid_state:
                        default_state = None
                        for state in self.states:
                            if state.name == default_state_name:
                                default_state = state
                                break

                        if default_state != None:
                            self.current_item.set_state(default_state)
        else:
            self.item_type_item.set_text('')
        self.update_place_holders()
        self.update_item_tag()
        self.update_grid()
        self.show_item_states()
        self.update_current_state()
        return

    def show_item_states(self):
        for state_item in self.state_items:
            self.options_layer.remove(state_item[1])

        self.state_items = []
        if self.current_item != None:
            text_color = (0, 0, 10)
            text_background = (241, 242, 201, 150)
            left = self.tag_name_item.get_left()
            top = self.tag_name_item.get_top() + self.tag_name_item.get_height() + 5
            width = self.tag_name_item.get_width()
            height = self.tag_name_item.get_height()
            font = self.tag_name_item.get_font()
            default_state = None
            for state in self.states:
                if state.suffix == '':
                    default_state = state
                    break

            if default_state != None:
                state_item = ItemRect(left, top, width, height, font, 0, default_state.name, text_color, text_background)
                self.options_layer.add(state_item)
                self.state_items.append((default_state.name, state_item))
                top += height + 5
            definition = self.current_item.get_definition()
            for state in definition.states:
                state_item = ItemRect(left, top, width, height, font, 0, state.name, text_color, text_background)
                self.options_layer.add(state_item)
                self.state_items.append((state.name, state_item))
                top += height + 5

        return

    def update_current_state(self):
        normal_background = (241, 242, 201, 150)
        selected_background = (248, 237, 120, 150)
        if self.current_item == None:
            current_state = None
        else:
            current_state = self.current_item.get_state()
        for state_item in self.state_items:
            if current_state == None or state_item[0] != current_state.name:
                state_item[1].set_background(normal_background)
            else:
                state_item[1].set_background(selected_background)

        return

    def update_item_tag(self):
        if self.current_item == None:
            self.tag_name_item.set_text('')
        else:
            definition = self.current_item.get_definition()
            self.tag_name_item.set_text(definition.tag)
        return

    def get_adjusted_origin(self):
        return (
         _div(self.origin[0] , self.zoom), _div(self.origin[1] , self.zoom))

    def handle_event(self, e):
        if e.type == MOUSEBUTTONDOWN:
            item = self.hit_test(e.pos[0], e.pos[1])
            if item != None:
                if item.get_layer() == self.place_holders_layer:
                    if hasattr(item, 'place_holder_index'):
                        self.current_place_holder = item.place_holder_index
                        self.move_placeholder_mode = True
                        self.update_move_placeholder_text()
                        self.update_place_holders()
                        self.update_grid()
                elif item == self.tag_name_item:
                    self.set_next_tag()
                else:
                    k = 0
                    for state_item in self.state_items:
                        if state_item[1] == item:
                            for state in self.states:
                                if state.name == state_item[0]:
                                    new_state = state

                            self.current_item.set_state(new_state)
                            self.update_current_state()
                            self.update_place_holders()
                            self.update_grid()
                            break
                        k += 1

        elif e.type == KEYDOWN:
            mod = get_common_modifiers(e.mod)
            if mod == pygame.KMOD_NONE:
                if e.key == K_RETURN:
                    if self.move_placeholder_mode:
                        self.move_placeholder_mode = False
                        self.update_move_placeholder_text()
                        self.update_place_holders()
                        self.update_grid()
                if e.key == K_LEFT:
                    if self.current_item != None:
                        if self.move_placeholder_mode:
                            if self.place_holders_layer.get_visible():
                                definition = self.current_item.get_definition()
                                if self.current_place_holder < len(definition.place_holders):
                                    place_holder = definition.place_holders[self.current_place_holder]
                                    place_holder.x -= 1
                                    self.update_place_holders()
                                    self.update_grid()
                                    self.notify_set_changed()
                        else:
                            definition = self.current_item.get_definition()
                            current_state = self.current_item.get_state()
                            if current_state.suffix == '':
                                center = definition.center
                                definition.center = (center[0] + 1, center[1])
                            else:
                                for state in definition.states:
                                    if state.name == current_state.name:
                                        center = state.center
                                        state.center = (center[0] + 1, center[1])
                                        break

                            self.current_item.reload_definition()
                            self.update_place_holders()
                            self.update_grid()
                            self.notify_set_changed()
                elif e.key == K_RIGHT:
                    if self.current_item != None:
                        if self.move_placeholder_mode:
                            if self.place_holders_layer.get_visible():
                                definition = self.current_item.get_definition()
                                if self.current_place_holder < len(definition.place_holders):
                                    place_holder = definition.place_holders[self.current_place_holder]
                                    place_holder.x += 1
                                    self.update_place_holders()
                                    self.update_grid()
                                    self.notify_set_changed()
                        else:
                            definition = self.current_item.get_definition()
                            current_state = self.current_item.get_state()
                            if current_state.suffix == '':
                                center = definition.center
                                definition.center = (center[0] - 1, center[1])
                            else:
                                for state in definition.states:
                                    if state.name == current_state.name:
                                        center = state.center
                                        state.center = (center[0] - 1, center[1])
                                        break

                            self.current_item.reload_definition()
                            self.update_place_holders()
                            self.update_grid()
                            self.notify_set_changed()
                elif e.key == K_UP:
                    if self.current_item != None:
                        if self.move_placeholder_mode:
                            if self.place_holders_layer.get_visible():
                                definition = self.current_item.get_definition()
                                if self.current_place_holder < len(definition.place_holders):
                                    place_holder = definition.place_holders[self.current_place_holder]
                                    place_holder.y -= 1
                                    self.update_place_holders()
                                    self.update_grid()
                                    self.notify_set_changed()
                        else:
                            definition = self.current_item.get_definition()
                            current_state = self.current_item.get_state()
                            if current_state.suffix == '':
                                center = definition.center
                                definition.center = (center[0], center[1] + 1)
                            else:
                                for state in definition.states:
                                    if state.name == current_state.name:
                                        center = state.center
                                        state.center = (center[0], center[1] + 1)
                                        break

                            self.current_item.reload_definition()
                            self.update_place_holders()
                            self.update_grid()
                            self.notify_set_changed()
                elif e.key == K_DOWN:
                    if self.current_item != None:
                        if self.move_placeholder_mode:
                            if self.place_holders_layer.get_visible():
                                definition = self.current_item.get_definition()
                                if self.current_place_holder < len(definition.place_holders):
                                    place_holder = definition.place_holders[self.current_place_holder]
                                    place_holder.y += 1
                                    self.update_place_holders()
                                    self.update_grid()
                                    self.notify_set_changed()
                        else:
                            definition = self.current_item.get_definition()
                            current_state = self.current_item.get_state()
                            if current_state.suffix == '':
                                center = definition.center
                                definition.center = (center[0], center[1] - 1)
                            else:
                                for state in definition.states:
                                    if state.name == current_state.name:
                                        center = state.center
                                        state.center = (center[0], center[1] - 1)
                                        break

                            self.current_item.reload_definition()
                            self.update_place_holders()
                            self.update_grid()
                            self.notify_set_changed()
                elif e.key == K_q:
                    if self.move_placeholder_mode:
                        if self.place_holders_layer.get_visible():
                            definition = self.current_item.get_definition()
                            if self.current_place_holder < len(definition.place_holders):
                                if self.current_place_holder > 0:
                                    place_holder = definition.place_holders[self.current_place_holder]
                                    del definition.place_holders[self.current_place_holder]
                                    definition.place_holders.insert(self.current_place_holder - 1, place_holder)
                                    self.current_place_holder -= 1
                                    self.update_place_holders()
                                    self.update_grid()
                                    self.notify_set_changed()
                    elif self.item_index < len(self.items) - 1:
                        self.item_index += 1
                        self.current_place_holder = 0
                        self.show_current_item()
                elif e.key == K_a:
                    if self.move_placeholder_mode:
                        if self.place_holders_layer.get_visible():
                            definition = self.current_item.get_definition()
                            if self.current_place_holder < len(definition.place_holders):
                                if self.current_place_holder + 1 < len(definition.place_holders):
                                    place_holder = definition.place_holders[self.current_place_holder]
                                    del definition.place_holders[self.current_place_holder]
                                    definition.place_holders.insert(self.current_place_holder + 1, place_holder)
                                    self.current_place_holder += 1
                                    self.update_place_holders()
                                    self.update_grid()
                                    self.notify_set_changed()
                    elif self.item_index > 0:
                        self.item_index -= 1
                        self.current_place_holder = 0
                        self.show_current_item()
                elif e.key == K_t:
                    if self.move_placeholder_mode:
                        if self.place_holders_layer.get_visible():
                            self.change_place_holder_tag()
                    else:
                        self.set_next_tag()
                elif e.key == K_DELETE:
                    if self.move_placeholder_mode:
                        if self.current_item != None:
                            if self.place_holders_layer.get_visible():
                                self.delete_current_place_holder()
                elif e.key == K_TAB:
                    if self.move_placeholder_mode:
                        definition = self.current_item.get_definition()
                        self.current_place_holder_visible += 1
                        if self.current_place_holder_visible >= len(definition.place_holders):
                            self.current_place_holder_visible = -1
                        self.update_place_holders()
                        self.update_grid()
                    else:
                        self.set_next_tag()
                elif e.key == K_s:
                    if self.current_item.get_type() in self.item_states:
                        current_state = self.current_item.get_state()
                        item_states = self.item_states[self.current_item.get_type()]
                        k = 0
                        state_index = -1
                        for state in item_states:
                            if state.name == current_state.name:
                                state_index = k
                                break
                            k += 1

                        new_state_index = state_index + 1
                        if new_state_index < len(item_states):
                            new_state_name = item_states[new_state_index].name
                            for state in self.states:
                                if state.name == new_state_name:
                                    new_state = state

                        else:
                            for state in self.states:
                                if state.suffix == '':
                                    new_state = state

                        self.current_item.set_state(new_state)
                        self.update_current_state()
                        self.update_place_holders()
                        self.update_grid()
                elif e.key == K_z:
                    if self.zoom == 2:
                        self.zoom = 1
                    else:
                        self.zoom = 2
                    definition = self.get_grid_definition()
                    cell_width = definition[1]
                    cell_height = definition[2]
                    self.set_grid_definition(self.get_adjusted_origin(), cell_width, cell_height, self.zoom)
                    self.update_grid()
                    self.save_set(None, None)
                    state = self.current_item.get_state()
                    self.load_set(self.set_number)
                    self.show_current_item()
                    self.current_item.set_state(state)
                    self.update_current_state()
            elif mod == pygame.KMOD_LSHIFT or mod == pygame.KMOD_RSHIFT:
                if e.key == K_t:
                    if self.move_placeholder_mode:
                        if self.place_holders_layer.get_visible():
                            self.change_place_holder_tag(True)
            elif mod == pygame.KMOD_LCTRL or mod == pygame.KMOD_RCTRL:
                if e.key == K_LEFT:
                    if self.current_item != None:
                        definition = self.current_item.get_definition()
                        if definition.size[1] > 1:
                            definition.size = (
                             definition.size[0], definition.size[1] - 1)
                            self.notify_set_changed()
                            self.update_grid()
                            self.update_place_holders()
                elif e.key == K_RIGHT:
                    if self.current_item != None:
                        definition = self.current_item.get_definition()
                        definition.size = (definition.size[0], definition.size[1] + 1)
                        self.notify_set_changed()
                        self.update_grid()
                        self.update_place_holders()
                elif e.key == K_UP:
                    if self.current_item != None:
                        definition = self.current_item.get_definition()
                        if definition.size[0] > 1:
                            definition.size = (
                             definition.size[0] - 1, definition.size[1])
                            self.notify_set_changed()
                            self.update_grid()
                            self.update_place_holders()
                elif e.key == K_DOWN:
                    if self.current_item != None:
                        definition = self.current_item.get_definition()
                        definition.size = (definition.size[0] + 1, definition.size[1])
                        self.notify_set_changed()
                        self.update_grid()
                        self.update_place_holders()
                elif e.key == K_PAGEUP or e.key == K_PAGEDOWN:
                    if not self.move_placeholder_mode:
                        self.save_set(None, None)
                        update_set = False
                        if e.key == K_PAGEDOWN:
                            if self.set_number < 99:
                                set_number = self.set_number + 1
                                update_set = True
                        elif e.key == K_PAGEUP:
                            if self.set_number > 1:
                                set_number = self.set_number - 1
                                update_set = True
                        if update_set:
                            self.load_set(set_number)
                            self.item_index = 0
                            self.current_place_holder = 0
                            self.show_current_item()
            elif mod == pygame.KMOD_LALT or mod == pygame.KMOD_RALT:
                if e.key == K_n:
                    if self.current_item != None:
                        if self.place_holders_layer.get_visible() and len(self.place_holder_tags) > 0:
                            definition = self.current_item.get_definition()
                            definition.place_holders.append(IsoPlaceHolder(self.place_holder_tags[0][0], 0, 0))
                            self.current_place_holder = len(definition.place_holders) - 1
                            self.move_placeholder_mode = True
                            self.update_move_placeholder_text()
                            self.update_place_holders()
                            self.update_grid()
                            self.notify_set_changed()
                elif e.key == K_m:
                    self.move_placeholder_mode = not self.move_placeholder_mode
                    self.update_move_placeholder_text()
                    self.update_place_holders()
                    self.update_grid()
                elif e.key == K_t:
                    if self.current_item != None:
                        if self.place_holders_layer.get_visible():
                            self.change_place_holder_tag()
                elif e.key == K_s:
                    if self.current_item != None:
                        if self.place_holders_layer.get_visible():
                            definition = self.current_item.get_definition()
                            if self.current_place_holder + 1 < len(definition.place_holders):
                                self.current_place_holder += 1
                            else:
                                self.current_place_holder = 0
                            self.update_place_holders()
                            self.update_grid()
                elif e.key == K_DELETE:
                    if self.current_item != None:
                        if self.place_holders_layer.get_visible():
                            self.delete_current_place_holder()
                elif e.key == K_h:
                    self.place_holders_layer.set_visible(not self.place_holders_layer.get_visible())
        return

    def delete_current_place_holder(self):
        definition = self.current_item.get_definition()
        if self.current_place_holder < len(definition.place_holders):
            del definition.place_holders[self.current_place_holder]
            if self.current_place_holder >= len(definition.place_holders) and self.current_place_holder > 0:
                self.current_place_holder -= 1
            if len(definition.place_holders) == 0:
                self.move_placeholder_mode = False
                self.update_move_placeholder_text()
            self.update_place_holders()
            self.update_grid()
            self.notify_set_changed()
        return

    def change_place_holder_tag(self, previous=False):
        definition = self.current_item.get_definition()
        if len(self.place_holder_tags) > 0 and self.current_place_holder < len(definition.place_holders):
            place_holder = definition.place_holders[self.current_place_holder]
            k = -1
            for i in range(len(self.place_holder_tags)):
                if self.place_holder_tags[i][0] == place_holder.tag:
                    k = i
                    break

            if previous:
                k -= 1
                if k < 0:
                    k = len(self.place_holder_tags) - 1
            else:
                k += 1
                if k >= len(self.place_holder_tags):
                    k = 0
            place_holder.tag = self.place_holder_tags[k][0]
            self.update_place_holders()
            self.notify_set_changed()
        return

    def update_move_placeholder_text(self):
        if self.move_placeholder_mode:
            self.move_placeholder_item.set_text('Move Placeholder Mode (Press Enter to exit)')
            self.move_placeholder_item.set_visible(True)
        else:
            self.move_placeholder_item.set_visible(False)
        return

    def set_next_tag(self):
        if len(self.tags) > 0:
            definition = self.current_item.get_definition()
            if definition.tag in self.tags:
                k = self.tags.index(definition.tag)
            else:
                k = -1
            k += 1
            if k >= len(self.tags):
                k = 0
            definition.tag = self.tags[k]
            self.update_item_tag()
            self.notify_set_changed()
        return

    def update_place_holders(self):
        self.place_holders_layer.empty()
        for item in self.place_holder_items:
            self.items_layer.remove(item)

        if self.current_item != None:
            definition = self.current_item.get_definition()
            if self.current_place_holder < len(definition.place_holders):
                selected_place_holder = definition.place_holders[self.current_place_holder]
            else:
                selected_place_holder = None
            height_index = self.place_holders_layer.get_count()
            index = 0
            for place_holder in definition.place_holders:
                size = 6
                if self.current_place_holder_visible == -1 or self.current_place_holder_visible == index:
                    place_holder_cell = self.current_item.get_place_holder_rowcol(place_holder)
                    if place_holder_cell[0] >= definition.size[0] or place_holder_cell[1] >= definition.size[1]:
                        name = '[Out of Bounds]'
                    else:
                        name = place_holder.tag
                    place_holder_tag = self.get_place_holder_tag(name)
                    if place_holder_tag != None:
                        if len(place_holder_tag) >= 2:
                            items = place_holder_tag[1]
                            if len(items) > 0:
                                place_holder_item = ItemCell(self, items[0], self.states[0])
                                below = name.startswith('Below')
                                if below:
                                    add_index = self.items_layer.items.index(self.current_item)
                                else:
                                    add_index = len(self.items_layer.items)
                                self.items_layer.add(place_holder_item, add_index)
                                self.place_holder_items.append(place_holder_item)
                                place_holder_item.set_to_place_holder(self.current_item, place_holder, below)
                        if place_holder == selected_place_holder:
                            text_color = self.move_placeholder_mode or (255, 255, 255)
                            height_color = (255, 255, 255, 100)
                        else:
                            text_color = (55, 255, 55)
                            height_color = (55, 255, 55, 100)
                    else:
                        text_color = (140, 140, 140)
                        height_color = (255, 255, 255, 50)
                    center = self.current_item.get_center()
                    text = ItemText(self.current_item.get_left() + center[0] * self.zoom + place_holder.x * self.zoom - 3 * self.zoom, self.current_item.get_top() + center[1] * self.zoom + place_holder.y * self.zoom - 9 - 4 * self.zoom, self.font, 0, name, text_color)
                    text.set_left(text.get_left() - text.get_width())
                    text.place_holder_index = index
                    self.place_holders_layer.add(text)
                    mark_x = self.current_item.get_left() + center[0] * self.zoom + place_holder.x * self.zoom
                    mark_y = self.current_item.get_top() + center[1] * self.zoom + place_holder.y * self.zoom
                    item = ItemCustomDraw(mark_x - _div(size * self.zoom , 2), mark_y - _div(size * self.zoom , 2), size * self.zoom, size * self.zoom, self.draw_place_holder)
                    item.place_holder_index = index
                    item.place_holder_color = text_color
                    self.place_holders_layer.add(item)
                index += 1

        return

    def get_place_holder_tag(self, id):
        for tag in self.place_holder_tags:
            if tag[0] == id:
                return tag

        return

    def draw_place_holder(self, item, target):
        bounds = item.get_bounds()
        color = item.place_holder_color
        target.fill(color, Rect(bounds.left + _div(bounds.width , 2) - _div(5 * self.zoom , 2), bounds.top + _div(bounds.height , 2) - _div(self.zoom , 2), 5 * self.zoom, self.zoom))
        target.fill(color, Rect(bounds.left + _div(bounds.width , 2) - _div(self.zoom , 2), bounds.top + _div(bounds.height , 2) - _div(5 * self.zoom , 2), self.zoom, 5 * self.zoom))
        return

    def draw_place_holder_height(self, item, target):
        bounds = item.get_bounds()
        color = item.place_holder_color
        target.draw_line(color, (bounds[0], bounds[1]), (bounds[0], bounds[1] + bounds[3] - 1), bounds[2])
        return


class LevelDesignerStage(StageIso):

    def __init__(self, game, origin, cell_width, cell_height, grid_size, tags, place_holder_tags, states, set_prefix):
        StageIso.__init__(self, game, tags)
        self.set_grid_definition(origin, cell_width, cell_height, 1)
        self.grid_size = grid_size
        self.place_holder_tags = place_holder_tags
        self.pending_save = []
        self.set_closed_handler(self.on_closed)
        self.grid_layer = Layer()
        self.add_layer(self.grid_layer)
        grid = create_grid(self, self.grid_size, False, None, None)
        self.grid_layer.add(grid)
        font = assets.load_font('freesansbold.ttf', 12)
        (window_width, window_height) = game.get_window_size()
        text_color = (0, 0, 10)
        text_background = (215, 232, 237, 150)
        name_width = 95
        self.level_name_item = ItemRect(5, window_height - 23, name_width, 18, font, 0, '', text_color, text_background)
        self.options_item = ItemRect(5 + name_width + 5, window_height - 23, window_width - name_width - 15, 18, font, 0, '', text_color, text_background)
        self.options_layer = LayerBuffered(window_width, window_height, True)
        self.options_layer.add(self.level_name_item)
        self.options_layer.add(self.options_item)
        file_name = self.get_state_file_name()
        state_loaded = False
        try:
            data = assets.load_data(file_name, ';', False)
            if data != None:
                state_set_prefix = data[0][0]
                set_number = int(data[1][0])
                current_layers = data[2]
                select_layer = int(data[3][0])
                current_item_index = int(data[4][0])
                state_loaded = True
        except Exception as message:
            print(('Cannot read set designer state:', file_name))
            raise SystemExit(message)

        if not state_loaded or state_set_prefix != set_prefix:
            set_prefix = 'p2'
            set_number = 1
            current_layers = []
            select_layer = 0
            current_item_index = 0
        self.states = states
        self.default_state = None
        for state in self.states:
            if state.suffix == '':
                self.default_state = state
                break

        if self.default_state == None:
            raise Exception('There is no default state defined')
        self.items = []
        self.set_prefix = set_prefix
        self.current_item = None
        self.zorder_selection = -1
        self.load_set(set_number)
        self.selection_layer = Layer()
        self.selection_item = ItemRect(0, 0, 0, 0, None, 0, '', None, None, (200, 0,
                                                                             0))
        self.selection_layer.add(self.selection_item)
        self.item_layers = []
        self.layer_current_item = []
        self.current_layer = -1
        for i in range(4):
            layer = Layer()
            letter = chr(ord('a') + i)
            if i < len(current_layers):
                number = int(current_layers[i * 2])
                if current_layers[i * 2 + 1] == 'H':
                    layer.set_visible(False)
            else:
                number = 1
            name = 'l' + str(number).zfill(3) + letter
            text_color = (0, 0, 10)
            text_background = (241, 242, 201, 150)
            text_item = ItemRect(5, self.level_name_item.get_top() - 23 * (i + 1), name_width, 18, font, 0, '', text_color, text_background)
            self.options_layer.add(text_item)
            layer_tuple = self.build_layer(letter, layer, name, text_item, number)
            self.item_layers.append(layer_tuple)
            self.set_layer_text(layer_tuple)
            self.layer_current_item.append(None)
            self.add_layer(layer)
            self.load_level(name, layer)

        self.add_layer(self.selection_layer)
        self.select_layer(select_layer, current_item_index)
        self.add_layer(self.options_layer)
        self.current_options_mod = None
        self.update_options_text(None, None)
        self.start_timer('update_options', 50, self.update_options_text)
        return

    def select_layer(self, layer, default_select_item=0):
        if self.current_layer != layer:
            if self.current_layer != -1:
                self.item_layers[self.current_layer][3].set_background((241, 242, 201,
                                                                        150))
                self.layer_current_item[self.current_layer] = self.current_item
            self.current_layer = layer
            self.item_layers[self.current_layer][3].set_background((248, 237, 120,
                                                                    150))
            self.update_current_layer(default_select_item)
        return

    def set_layer_text(self, layer_tuple):
        s = 'Layer ' + layer_tuple[0].upper()
        if not layer_tuple[1].get_visible():
            s += ' (H)'
        else:
            s += ' (' + str(layer_tuple[4]) + ')'
        layer_tuple[3].set_text(s)
        return

    def update_current_layer(self, default_select_item=0):
        self.level_name_item.set_text(self.set_name + self.item_layers[self.current_layer][2])
        self.current_item = self.layer_current_item[self.current_layer]
        layer = self.item_layers[self.current_layer][1]
        if self.current_item == None or self.current_item not in layer.items:
            l = len(layer.items)
            if l > 0:
                if default_select_item < l:
                    self.current_item = layer.items[default_select_item]
                else:
                    self.current_item = layer.items[0]
            else:
                self.current_item = None
        self.update_current_item_selection()
        return

    def update_current_item_selection(self):
        if self.current_item == None:
            visible = False
        elif self.current_layer == -1:
            visible = False
        else:
            layer_tuple = self.item_layers[self.current_layer]
            layer = layer_tuple[1]
            visible = layer.get_visible()
        if not visible:
            self.selection_item.set_visible(False)
        else:
            self.selection_item.set_left(self.current_item.get_left() - 2)
            self.selection_item.set_top(self.current_item.get_top() - 2)
            self.selection_item.set_width(self.current_item.get_width() + 4)
            self.selection_item.set_height(self.current_item.get_height() + 4)
            self.selection_item.set_visible(True)
        return

    def build_layer(self, letter, layer, name, text_item, number):
        return (
         letter, layer, name, text_item, number)

    def update_options_text(self, key, data):
        mod = get_common_modifiers(pygame.key.get_mods())
        if mod == pygame.KMOD_NONE:
            self.options_item.set_text('N = New | Tab = Select | Q/A = Change | F - Flip | S - State | Del - Delete')
        elif mod == pygame.KMOD_LCTRL or mod == pygame.KMOD_RCTRL:
            self.options_item.set_text('C/V = Copy/Paste | Up/Down = Send back/forward | Page Up/Down = Change set')
        elif mod == pygame.KMOD_LALT or mod == pygame.KMOD_RALT:
            layer = self.item_layers[self.current_layer][1]
            if layer.get_visible():
                h_text = 'Hide layer'
            else:
                h_text = 'Show layer'
            self.options_item.set_text('C/V/H = Copy/Paste/' + h_text + ' | Up/Down = Layer | Left/Right = Level')
        elif mod == pygame.KMOD_LSHIFT or mod == pygame.KMOD_RSHIFT:
            self.options_item.set_text('Z/X = Z-order Next/Previous | C = Show All | R = Reset')
        else:
            self.options_item.set_text('')
        self.current_options_mod = mod
        return

    def load_set(self, set_number):
        set_name = self.set_prefix + 's' + str(set_number).zfill(2)
        self.set_number = set_number
        self.set_name = set_name
        if os.path.isfile(os.path.join('data', self.get_set_file_name())):
            item_definitions = None
        else:
            item_definitions = {}
        self.set_items(self.set_name, '', item_definitions)
        self.item_types = list(self.get_item_definitions().keys())
        self.item_types.sort()
        return

    def get_key_repeat(self):
        return (200, 50)

    def get_set_file_name(self):
        return self.set_name + '.tcs'

    def get_level_file_name(self, level_name):
        return self.set_name + level_name + '.tcl'

    def get_state_file_name(self):
        return 'leveldesigner.sta'

    def load_level(self, level_name, layer):
        if os.path.isfile(os.path.join('data', self.get_level_file_name(level_name))):
            StageIso.load_level(self, level_name, layer, self.states, self.add_item_event_handlers)
            l = len(layer.items)
            if l == 0:
                self.current_item = None
            else:
                self.current_item = layer.items[l - 1]
            self.update_current_item_selection()
        return

    def notify_level_changed(self):
        level = self.item_layers[self.current_layer]
        if level not in self.pending_save:
            self.pending_save.append(level)
        self.stop_timer('auto_save')
        self.start_timer('auto_save', 5000, self.save_current_levels, None)
        return

    def on_closed(self, stage):
        self.save_current_levels(None, None)
        file_name = self.get_state_file_name()
        try:
            data = []
            data.append([self.set_prefix])
            data.append(str(self.set_number))
            layers_line = []
            for layer in self.item_layers:
                layers_line.append(str(layer[4]))
                if layer[1].get_visible():
                    layers_line.append('V')
                else:
                    layers_line.append('H')

            data.append(layers_line)
            data.append(str(self.current_layer))
            if self.current_item == None:
                selected_item_index = 0
            else:
                items_layer = self.item_layers[self.current_layer][1]
                selected_item_index = items_layer.items.index(self.current_item)
                if selected_item_index == -1:
                    selected_item_index = 0
            data.append(str(selected_item_index))
            assets.save_data(file_name, data)
        except Exception as message:
            print(('Cannot save set designer state:', file_name))
            raise SystemExit(message)

        return

    def save_current_levels(self, key, data):
        self.stop_timer('auto_save')
        if len(self.pending_save) > 0:
            for layer in self.pending_save:
                if len(layer[1].items) == 0:
                    file_name = self.get_level_file_name(layer[2])
                    full_name = os.path.join('data', file_name)
                    if os.path.isfile(full_name):
                        os.remove(full_name)
                else:
                    StageIso.save_level(self, layer[2], layer[1])

            self.pending_save = []
        return

    def handle_event(self, e):
        if e.type == MOUSEBUTTONDOWN:
            item = self.hit_test(e.pos[0], e.pos[1])
            if item != None:
                k = 0
                for layer in self.item_layers:
                    if layer[3] == item:
                        self.select_layer(k)
                    k += 1

        elif e.type == KEYDOWN:
            mod = get_common_modifiers(e.mod)
            if mod == pygame.KMOD_NONE:
                items_layer = self.item_layers[self.current_layer][1]
                if items_layer.get_visible():
                    if e.key == K_n:
                        if len(self.item_types) > 0:
                            new_item = self.create_item(self.item_types[0], self.default_state, False, 0, 0)
                            if self.current_item != None:
                                new_item.set_type(self.current_item.get_type())
                                (row, col) = self.current_item.get_position()
                                size = new_item.get_definition().size
                                if col + size[1] + 1 <= self.grid_size[1]:
                                    col += 1
                                elif row + size[0] + 1 <= self.grid_size[0]:
                                    col = 0
                                    row += 1
                                new_item.set_position(row, col)
                            items_layer = self.item_layers[self.current_layer][1]
                            items_layer.add(new_item)
                            self.current_item = new_item
                            self.update_current_item_selection()
                            self.notify_level_changed()
                    elif e.key == K_LEFT:
                        if self.current_item != None:
                            (row, col) = self.current_item.get_position()
                            new_col = col - 1
                            if new_col >= 0:
                                self.current_item.set_position(row, new_col)
                                self.notify_level_changed()
                                self.update_current_item_selection()
                    elif e.key == K_RIGHT:
                        if self.current_item != None:
                            (row, col) = self.current_item.get_position()
                            size = self.current_item.get_definition().size
                            new_col = col + 1
                            if new_col + size[1] <= self.grid_size[1]:
                                self.current_item.set_position(row, new_col)
                                self.notify_level_changed()
                                self.update_current_item_selection()
                    elif e.key == K_UP:
                        if self.current_item != None:
                            (row, col) = self.current_item.get_position()
                            new_row = row - 1
                            if new_row >= 0:
                                self.current_item.set_position(new_row, col)
                                self.notify_level_changed()
                                self.update_current_item_selection()
                    elif e.key == K_DOWN:
                        if self.current_item != None:
                            (row, col) = self.current_item.get_position()
                            size = self.current_item.get_definition().size
                            new_row = row + 1
                            if new_row + size[0] <= self.grid_size[0]:
                                self.current_item.set_position(new_row, col)
                                self.notify_level_changed()
                                self.update_current_item_selection()
                    elif e.key == K_q:
                        if self.current_item != None:
                            k = self.item_types.index(self.current_item.get_type())
                            if k != -1 and k + 1 < len(self.item_types):
                                self.current_item.set_type(self.item_types[k + 1])
                                self.notify_level_changed()
                                self.update_current_item_selection()
                    elif e.key == K_a:
                        if self.current_item != None:
                            k = self.item_types.index(self.current_item.get_type())
                            if k != -1 and k > 0:
                                self.current_item.set_type(self.item_types[k - 1])
                                self.notify_level_changed()
                                self.update_current_item_selection()
                    elif e.key == K_TAB:
                        if self.current_item != None:
                            items_layer = self.item_layers[self.current_layer][1]
                            k = items_layer.items.index(self.current_item)
                            l = len(items_layer.items)
                            if k + 1 < l:
                                k += 1
                            else:
                                k = 0
                            self.current_item = items_layer.items[k]
                            self.update_current_item_selection()
                    elif e.key == K_f:
                        if self.current_item != None:
                            self.current_item.set_flip_h(not self.current_item.get_flip_h())
                            self.notify_level_changed()
                            self.update_current_item_selection()
                    elif e.key == K_s:
                        if self.current_item != None:
                            current_state = self.current_item.get_state()
                            state_index = -1
                            states = self.current_item.get_definition().states
                            k = 0
                            for state in states:
                                if state.name == current_state.name:
                                    state_index = k
                                    break
                                k += 1

                            state_index += 1
                            if state_index >= len(states):
                                self.current_item.set_state(self.default_state)
                            else:
                                for state in self.states:
                                    if state.name == states[state_index].name:
                                        self.current_item.set_state(state)
                                        break

                    elif e.key == K_DELETE:
                        if self.current_item != None:
                            items_layer = self.item_layers[self.current_layer][1]
                            k = items_layer.items.index(self.current_item)
                            items_layer.remove(self.current_item)
                            l = len(items_layer.items)
                            if k >= l:
                                k = l - 1
                            if k < 0:
                                self.current_item = None
                            else:
                                self.current_item = items_layer.items[k]
                            self.notify_level_changed()
                            self.update_current_item_selection()
            elif mod == pygame.KMOD_LCTRL or mod == pygame.KMOD_RCTRL:
                if e.key == K_c:
                    (row, col) = self.current_item.get_position()
                    leveldesigner.clipboard_item = (self.current_item.get_type(), row, col, self.current_item.get_flip_h(), self.current_item.get_state())
                elif e.key == K_v:
                    if leveldesigner.clipboard_item != None:
                        new_item = self.create_item(leveldesigner.clipboard_item[0], leveldesigner.clipboard_item[4], leveldesigner.clipboard_item[3], leveldesigner.clipboard_item[1], leveldesigner.clipboard_item[2])
                        items_layer = self.item_layers[self.current_layer][1]
                        items_layer.add(new_item, False)
                        self.current_item = new_item
                        self.update_current_item_selection()
                        self.notify_level_changed()
                elif e.key == K_UP:
                    if self.current_item != None:
                        items_layer = self.item_layers[self.current_layer][1]
                        k = items_layer.items.index(self.current_item)
                        if k >= 1:
                            items_layer.remove(self.current_item)
                            items_layer.add(self.current_item, k - 1)
                            self.notify_level_changed()
                            self.update_current_item_selection()
                elif e.key == K_DOWN:
                    if self.current_item != None:
                        items_layer = self.item_layers[self.current_layer][1]
                        k = items_layer.items.index(self.current_item)
                        l = len(items_layer.items)
                        if k + 1 < l:
                            items_layer.remove(self.current_item)
                            items_layer.add(self.current_item, k + 1)
                            self.notify_level_changed()
                            self.update_current_item_selection()
                elif e.key == K_PAGEUP or e.key == K_PAGEDOWN:
                    self.save_current_levels(None, None)
                    update_set = False
                    if e.key == K_PAGEDOWN:
                        if self.set_number < 99:
                            set_number = self.set_number + 1
                            update_set = True
                    elif e.key == K_PAGEUP:
                        if self.set_number > 1:
                            set_number = self.set_number - 1
                            update_set = True
                    if update_set:
                        self.load_set(set_number)
                        for layer in self.item_layers:
                            layer[1].empty()
                            self.load_level(layer[2], layer[1])

                        self.item_index = 0
                        layer = self.item_layers[self.current_layer][1]
                        l = len(layer.items)
                        if l > 0:
                            self.current_item = layer.items[0]
                        else:
                            self.current_item = None
                        self.update_current_layer()
                        self.update_current_item_selection()
            elif mod == pygame.KMOD_LALT or mod == pygame.KMOD_RALT:
                if e.key == K_c:
                    layer = self.item_layers[self.current_layer][1]
                    leveldesigner.clipboard_layer = []
                    for item in layer.items:
                        (row, col) = item.get_position()
                        leveldesigner.clipboard_layer.append((item.get_type(), row, col, item.get_flip_h(), item.get_state()))

                elif e.key == K_v:
                    if leveldesigner.clipboard_layer != None:
                        items_layer = self.item_layers[self.current_layer][1]
                        for item in leveldesigner.clipboard_layer:
                            exists = False
                            for current_item in items_layer.items:
                                (row, col) = current_item.get_position()
                                if current_item.get_type() == item[0] and row == item[1] and row == item[1]:
                                    exists = True

                            if not exists:
                                new_item = self.create_item(item[0], item[4], item[3], item[1], item[2])
                                items_layer.add(new_item)
                                self.current_item = new_item

                        self.update_current_item_selection()
                        self.notify_level_changed()
                elif e.key == K_h:
                    layer_tuple = self.item_layers[self.current_layer]
                    layer = layer_tuple[1]
                    layer.set_visible(not layer.get_visible())
                    self.set_layer_text(layer_tuple)
                    self.update_current_item_selection()
                elif e.key == K_UP:
                    if self.current_layer + 1 < len(self.item_layers):
                        self.select_layer(self.current_layer + 1)
                elif e.key == K_DOWN:
                    if self.current_layer > 0:
                        self.select_layer(self.current_layer - 1)
                elif e.key == K_LEFT or e.key == K_RIGHT:
                    layer = self.item_layers[self.current_layer]
                    number = layer[4]
                    update_layer = False
                    if e.key == K_LEFT:
                        if number > 1:
                            number -= 1
                            update_layer = True
                    elif number < 999:
                        number += 1
                        update_layer = True
                    if update_layer:
                        self.save_current_levels(None, None)
                        name = 'l' + str(number).zfill(3) + layer[0]
                        layer = self.build_layer(layer[0], layer[1], name, layer[3], number)
                        self.item_layers[self.current_layer] = layer
                        layer[1].empty()
                        self.load_level(name, layer[1])
                        self.update_current_layer()
                        self.update_current_item_selection()
                        self.set_layer_text(layer)
            elif mod == pygame.KMOD_LSHIFT or mod == pygame.KMOD_RSHIFT:
                if e.key == K_z:
                    layer = self.item_layers[self.current_layer][1]
                    self.zorder_selection += 1
                    if self.zorder_selection >= len(layer.items):
                        self.zorder_selection = 0
                    for item in layer.items:
                        item.set_visible(False)

                    layer.items[self.zorder_selection].set_visible(True)
                    self.current_item = layer.items[self.zorder_selection]
                    self.update_current_item_selection()
                elif e.key == K_x:
                    layer = self.item_layers[self.current_layer][1]
                    self.zorder_selection -= 1
                    if self.zorder_selection < 0:
                        self.zorder_selection = len(layer.items) - 1
                    for item in layer.items:
                        item.set_visible(False)

                    layer.items[self.zorder_selection].set_visible(True)
                    self.current_item = layer.items[self.zorder_selection]
                    self.update_current_item_selection()
                elif e.key == K_c:
                    layer = self.item_layers[self.current_layer][1]
                    for item in layer.items:
                        item.set_visible(True)

                elif e.key == K_r:
                    layer = self.item_layers[self.current_layer][1]
                    for item in layer.items:
                        item.set_visible(True)

                    self.zorder_selection = -1
        return

    def create_item(self, type, state, flip_h=False, row=-999, col=-999):
        item = ItemCell(self, type, state, flip_h, row, col)
        self.add_item_event_handlers(item)
        return item

    def add_item_event_handlers(self, item):
        item.add_event_handler(ItemEvent.CLICK, self.item_click)
        item.add_event_handler(ItemEvent.DBLCLICK, self.item_dblclick)
        return

    def item_click(self, item, args):
        item_layer = item.get_layer()
        if self.item_layers[self.current_layer][1] != item_layer:
            return False
        else:
            self.current_item = item
            self.notify_level_changed()
            self.update_current_item_selection()
        return

    def item_dblclick(self, item, args):
        item_layer = item.get_layer()
        if self.item_layers[self.current_layer][1] != item_layer:
            return False
        else:
            definition = self.get_grid_definition()
            origin = definition[0]
            cell_width = definition[1]
            cell_height = definition[2]
            setitems_stage = leveldesigner.SetItemsStage(self.game, origin, cell_width, cell_height, self.grid_size, self.get_tags(), self.place_holder_tags, self.states, self.set_prefix)
            setitems_stage.select_item_type(item.get_type())
            self.game.set_stage(setitems_stage)
        return


def get_common_modifiers(mod):
    return mod & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL | pygame.KMOD_LALT | pygame.KMOD_RALT | pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT)


def create_grid(stage, grid_size, mark_center, mark_size, mark_cell):
    definition = stage.get_grid_definition()
    origin = definition[0]
    multiplier = definition[3]
    grid = ItemImage(0, origin[1] * multiplier, draw_grid(stage, grid_size, mark_center, mark_size, mark_cell))
    return grid


def draw_grid(stage, grid_size, mark_center, mark_size, mark_cell):
    (width, height) = stage.game.get_window_size()
    (origin, cell_width, cell_height, multiplier) = stage.get_grid_definition()
    grid_definition = (origin, cell_width, cell_height, multiplier)
    grid_height = height - origin[1] * multiplier
    target = CustomDraw(width, grid_height)
    target.clear((0, 0, 0, 0))
    grid_color = (255, 255, 255, 50)
    start_pos = get_grid_pos(0, 0, grid_definition)
    end_pos = get_grid_pos(grid_size[0], 0, grid_definition)
    col = 0
    while col <= grid_size[1]:
        target.draw_line(grid_color, start_pos, end_pos)
        col += 1
        start_pos = get_grid_pos(0, col, grid_definition)
        end_pos = get_grid_pos(grid_size[0], col, grid_definition)

    start_pos = get_grid_pos(0, 0, grid_definition)
    end_pos = get_grid_pos(0, grid_size[1], grid_definition)
    row = 0
    while row <= grid_size[0]:
        target.draw_line(grid_color, start_pos, end_pos)
        row += 1
        start_pos = get_grid_pos(row, 0, grid_definition)
        end_pos = get_grid_pos(row, grid_size[1], grid_definition)

    if mark_center:
        mark_color = (255, 0, 0, 200)
        target.fill(mark_color, (origin[0] * multiplier - _div(5 * multiplier , 2), _div(cell_height * multiplier , 2) - _div(multiplier , 2), 5 * multiplier, multiplier))
        target.fill(mark_color, (origin[0] * multiplier - _div(multiplier , 2), _div(cell_height * multiplier , 2) - _div(5 * multiplier , 2), multiplier, 5 * multiplier))
    if mark_size != None:
        size_color = (255, 255, 0, 150)
        start_pos = get_grid_pos(0, 0, grid_definition)
        end_pos = get_grid_pos(mark_size[0], 0, grid_definition)
        target.draw_line(size_color, start_pos, end_pos)
        start_pos = get_grid_pos(0, mark_size[1], grid_definition)
        end_pos = get_grid_pos(mark_size[0], mark_size[1], grid_definition)
        target.draw_line(size_color, start_pos, end_pos)
        start_pos = get_grid_pos(0, 0, grid_definition)
        end_pos = get_grid_pos(0, mark_size[1], grid_definition)
        target.draw_line(size_color, start_pos, end_pos)
        start_pos = get_grid_pos(mark_size[0], 0, grid_definition)
        end_pos = get_grid_pos(mark_size[0], mark_size[1], grid_definition)
        target.draw_line(size_color, start_pos, end_pos)
    if mark_cell != None:
        cell_color = (255, 0, 0, 150)
        start_pos = get_grid_pos(mark_cell[0], mark_cell[1], grid_definition)
        end_pos = get_grid_pos(mark_cell[0] + 1, mark_cell[1], grid_definition)
        target.draw_line(cell_color, start_pos, end_pos, 3)
        start_pos = get_grid_pos(mark_cell[0], mark_cell[1] + 1, grid_definition)
        end_pos = get_grid_pos(mark_cell[0] + 1, mark_cell[1] + 1, grid_definition)
        target.draw_line(cell_color, start_pos, end_pos, 3)
        start_pos = get_grid_pos(mark_cell[0], mark_cell[1], grid_definition)
        end_pos = get_grid_pos(mark_cell[0], mark_cell[1] + 1, grid_definition)
        target.draw_line(cell_color, start_pos, end_pos, 3)
        start_pos = get_grid_pos(mark_cell[0] + 1, mark_cell[1], grid_definition)
        end_pos = get_grid_pos(mark_cell[0] + 1, mark_cell[1] + 1, grid_definition)
        target.draw_line(cell_color, start_pos, end_pos, 3)
    return assets.Image(target.surface)


def get_grid_pos(row, col, grid_definition):
    origin = grid_definition[0]
    cell_width = grid_definition[1]
    cell_height = grid_definition[2]
    multiplier = grid_definition[3]
    x = origin[0] * multiplier + _div((col - row) * cell_width * multiplier , 2)
    y = 1 + _div((row + col) * cell_height * multiplier , 2)
    return (
     x, y)


