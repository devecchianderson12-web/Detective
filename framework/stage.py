import gc, os, pygame, math, sys
import os as _os
IS_ANDROID = 'ANDROID_ARGUMENT' in _os.environ or 'ANDROID_PRIVATE' in _os.environ


def _touch_text_events(events):
    """Android: el teclado en pantalla manda TEXTINPUT; se convierte en KEYDOWN con su caracter (como
    los recibía el juego en la PC) y se ignoran los KEYDOWN de letras para no escribir dos veces."""
    if not IS_ANDROID:
        return events
    out = []
    for e in events:
        if e.type == pygame.TEXTINPUT:
            for ch in e.text:
                out.append(pygame.event.Event(pygame.KEYDOWN, key=ord(ch) if ord(ch) < 128 else 0, mod=0, unicode=ch, scancode=0))
        elif e.type == pygame.KEYDOWN and getattr(e, 'unicode', '') and e.unicode.isprintable():
            continue
        elif e.type in (pygame.KEYDOWN, pygame.KEYUP) and e.key == pygame.K_AC_BACK:
            # botón "atrás" de Android = Escape (cierra diálogos como en la PC)
            out.append(pygame.event.Event(e.type, key=pygame.K_ESCAPE, mod=0, unicode='\x1b', scancode=0))
        else:
            out.append(e)
    return out
from . import assets, engine, sounds
from pygame.locals import *
MUSIC_ENDSOUND_EVENT = pygame.locals.USEREVENT
STREAM_MUSIC = False
DBLCLICK_DELAY = 500

class Stage():

    def __init__(self, game, background_image=None, target_surface=None):
        self.game = game
        self.layers = []
        self.initialized = False
        self.__dialogs = []
        self.__changed_handler = None
        self.__closed_handler = None
        self.__last_click = None
        self.__update_prerender_buffer = False
        self.__locks = 0
        self.target_surface = target_surface
        self.__load_background(background_image)
        self.__background_dirty = True
        self.__timers = []
        self.__music = None
        self.__music_data = None
        self.__over_item = None
        self.__focused_item = None
        self.__prerender_to_layer = None
        self.__prerender_buffer = None
        self.__mouse_layer = None
        self.__mouse_cursor = None
        self.__mouse_snap_to_cursor = False
        self.__mouse_update = False
        self.__mouse_real_pos = None
        self.__use_mouse_layer = False
        self.__mouse_pointer = (0, 0)
        self.__leftmousedown_handlers = []
        if target_surface != None:
            self.__default_mouse_cursor = None
        else:
            default_mouse_cursor = game.get_default_mouse_cursor()
            if default_mouse_cursor != None:
                self.__default_mouse_cursor = ItemImage(0, 0, default_mouse_cursor)
                self.set_mouse_cursor(self.__default_mouse_cursor)
            else:
                self.__default_mouse_cursor = None
        self.__previous_active = True
        return

    def initialize(self):
        return

    def close(self):
        return

    def set_prerender_buffer(self, to_layer):
        self.__prerender_to_layer = to_layer
        if self.__prerender_buffer == None:
            if self.target_surface == None:
                (window_width, window_height) = self.game.get_window_size()
                self.__prerender_buffer = pygame.Surface((window_width, window_height))
            else:
                self.__prerender_buffer = pygame.Surface((self.target_surface.get_width(), self.target_surface.get_height()))
        self.__update_prerender_buffer = True
        return

    def add_layer(self, layer, index=-1):
        layer.set_stage(self)
        if index == -1:
            self.layers.append(layer)
        else:
            self.layers.insert(index, layer)
        layer.set_dirty()
        self.__mouse_update = True
        return

    def remove_layer(self, layer):
        if layer in self.layers:
            if self.__focused_item != None and self.__focused_item[0].get_layer() == layer:
                self.set_focus(None)
            layer.set_stage(None)
            self.layers.remove(layer)
            self.redraw()
            if self.__prerender_to_layer == layer:
                self.set_prerender_buffer(None)
            for dialog in self.__dialogs:
                if dialog[0] == layer:
                    self.__dialogs.remove(dialog)
                    break

            self.__mouse_update = True
        return

    def empty_layers(self, except_layers=None):
        if except_layers == None:
            for l in self.layers:
                l.set_stage(None)

            del self.layers[:]
        else:
            k = len(self.layers) - 1
            while k >= 0:
                l = self.layers[k]
                if l not in except_layers:
                    l.set_stage(None)
                    del self.layers[k]
                k -= 1

        del self.__dialogs[:]
        self.set_prerender_buffer(None)
        self.redraw()
        return

    def contains_layer(self, layer):
        return layer in self.layers

    def show_dialog(self, layer, event_handler, background_color=(0, 0, 0, 180), prerender_below=True, callback=None):
        if layer in self.layers:
            raise Exception('The layer must be a layer of the stage if you want to use it as a dialog')
        if prerender_below:
            previous_prerender_layer = self.__prerender_to_layer
            if len(self.layers) > 0:
                self.set_prerender_buffer(self.layers[len(self.layers) - 1])
        else:
            previous_prerender_layer = None
        if background_color == None:
            background_layer = None
        else:
            (window_width, window_height) = self.game.get_window_size()
            background_surface = pygame.Surface((_div(window_width , 2), _div(window_height , 2)), pygame.SRCALPHA, 32)
            background_surface.fill(background_color)
            background_image = assets.Image(background_surface)
            background_layer = Layer()
            background_item = ItemImage(0, 0, background_image)
            background_layer.add(background_item)
            background_item = ItemImage(_div(window_width , 2), 0, background_image)
            background_layer.add(background_item)
            background_item = ItemImage(0, _div(window_height , 2), background_image)
            background_layer.add(background_item)
            background_item = ItemImage(_div(window_width , 2), _div(window_height , 2), background_image)
            background_layer.add(background_item)
            self.add_layer(background_layer)
        if pygame.event.get_grab():
            pygame.event.set_grab(False)
        self.add_layer(layer)
        self.__dialogs.append((layer, event_handler, background_layer, previous_prerender_layer, callback))
        self.set_mouse_cursor(None)
        return

    def close_dialog(self, layer):
        callback = None
        for dialog in self.__dialogs:
            if dialog[0] == layer:
                callback = dialog[4]
                self.__dialogs.remove(dialog)
                k = 0
                while k < len(self.layers):
                    if self.layers[k] == layer:
                        self.remove_layer(layer)
                        while k < len(self.layers):
                            self.remove_layer(self.layers[k])

                    k += 1

                background_layer = dialog[2]
                if background_layer != None:
                    self.remove_layer(background_layer)
                    del background_layer
                previous_prerender_layer = dialog[3]
                if previous_prerender_layer != None:
                    if previous_prerender_layer in self.layers:
                        self.set_prerender_buffer(previous_prerender_layer)
                    else:
                        self.set_prerender_buffer(None)

        key = 'run gc'
        self.stop_timer(key)
        self.start_timer(key, 0, self.__run_gc)
        if callback != None:
            callback()
        return

    def has_dialog_opened(self):
        return len(self.__dialogs) > 0

    def blind_dialog(self, layer, direction, background=True, ignore_layers=[], callback=None):
        from . import animations
        layers_to_blind = []
        for dialog in self.__dialogs:
            if dialog[0] == layer:
                duration = 450
                area = None
                count = len(self.layers)
                if dialog[2] != None and background:
                    background_layer = dialog[2]
                    layers_to_blind.append(background_layer)
                if layer not in ignore_layers:
                    layers_to_blind.append(layer)
                if layer in self.layers:
                    k = self.layers.index(layer)
                    k += 1
                    while k < count:
                        above_layer = self.layers[k]
                        if above_layer not in ignore_layers:
                            layers_to_blind.append(above_layer)
                        k += 1

                break

        callback_assigned = False
        for i in range(len(layers_to_blind)):
            if i == len(layers_to_blind) - 1:
                blind_callback = callback
                callback_assigned = True
            else:
                blind_callback = None
            animations.blind_layer(layers_to_blind[i], direction, area, duration, blind_callback)

        if not callback_assigned and callback != None:
            callback(layer)
        return

    def lock_ui(self):
        self.__locks += 1
        self.__mouse_update = True
        return

    def unlock_ui(self):
        self.__locks -= 1
        self.__mouse_update = True
        return

    def update_mouse(self):
        self.__mouse_update = True
        return

    def hit_test(self, x, y):
        if self.__locks == 0:
            if len(self.__dialogs) == 0:
                i = len(self.layers) - 1
                while i >= 0:
                    layer = self.layers[i]
                    if layer.get_visible() and layer.is_inside_clip(x, y):
                        for item in reversed(layer.items):
                            if item.get_visible() and item.is_over(x, y):
                                return item

                    i -= 1

            else:
                dialog_layer = self.__dialogs[len(self.__dialogs) - 1][0]
                i = len(self.layers) - 1
                while i >= 0:
                    layer = self.layers[i]
                    if layer.get_visible() and layer.is_inside_clip(x, y):
                        for item in reversed(layer.items):
                            if item.get_visible() and item.is_over(x, y):
                                return item

                    if layer == dialog_layer:
                        break
                    else:
                        i -= 1

        return

    def hit_test_stack(self, x, y, ignore_clip=False):
        stack = []
        l = len(self.layers)
        if self.__locks > 0:
            i = l
        elif len(self.__dialogs) == 0:
            i = 0
        else:
            dialog_layer = self.__dialogs[len(self.__dialogs) - 1][0]
            i = l - 1
            while i > 0:
                layer = self.layers[i]
                if layer == dialog_layer:
                    break
                else:
                    i -= 1

        while i < l:
            layer = self.layers[i]
            if layer.get_visible() and (ignore_clip or layer.is_inside_clip(x, y)):
                k = len(layer.items) - 1
                while k >= 0:
                    item = layer.items[k]
                    if item.get_visible() and item.is_over(x, y, ignore_clip):
                        stack.append(item)
                    k -= 1

            i += 1

        return stack

    def set_music(self, intro, loop):
        if intro == None and loop == None:
            self.__music = None
        else:
            self.__music = (
             intro, loop)
        return

    def get_music(self):
        return self.__music

    def same_music(self, stage):
        return self.__music == stage.__music

    def play_music(self, intro=None, loop=None):
        self.stop_music()
        if intro == None and loop == None and self.__music != None:
            intro = self.__music[0]
            loop = self.__music[1]
        if intro != None or loop != None:
            if STREAM_MUSIC:
                if intro != None:
                    pygame.mixer.music.load(intro)
                    pygame.mixer.music.queue(loop)
                    pygame.mixer.music.set_endevent(MUSIC_ENDSOUND_EVENT)
                    pygame.mixer.music.play()
                else:
                    pygame.mixer.music.load(loop)
                    pygame.mixer.music.play(-1)
                self.__music_data = loop
            else:
                self.__music_data = (
                 intro, loop)
                music_channel = pygame.mixer.Channel(0)
                music_channel.set_volume(1)
                if intro != None:
                    music_channel.play(intro.sound, 0, 0)
                    music_channel.queue(loop.sound)
                    music_channel.set_endevent(MUSIC_ENDSOUND_EVENT)
                else:
                    music_channel.play(loop.sound, -1)
        return

    def set_music_volume(self, volume, fadems=200, pause=False):
        self.stop_timer('set_music_volume')
        if STREAM_MUSIC:
            current_volume = pygame.mixer.music.get_volume()
        else:
            music_channel = pygame.mixer.Channel(0)
            current_volume = music_channel.get_volume()
        self.start_timer('set_music_volume', 1, self.__on_set_music_volume, (current_volume, volume, fadems, pygame.time.get_ticks(), pause), True, False)
        return

    def pause_music(self, fadems=450):
        self.set_music_volume(0, fadems, True)
        return

    def unpause_music(self, fadems=450):
        if STREAM_MUSIC:
            pygame.mixer.music.unpause()
        else:
            music_channel = pygame.mixer.Channel(0)
            music_channel.unpause()
        self.set_music_volume(1, fadems)
        return

    def stop_music(self):
        self.stop_timer('set_music_volume')
        if self.__music_data != None:
            self.__music_data = None
            if STREAM_MUSIC:
                pygame.mixer.music.set_endevent()
                pygame.event.clear(MUSIC_ENDSOUND_EVENT)
                pygame.mixer.music.fadeout(200)
            else:
                music_channel = pygame.mixer.Channel(0)
                music_channel.set_endevent()
                empty_sound = self.game.get_empty_sound()
                music_channel.queue(empty_sound.sound)
                music_channel.fadeout(200)
        return

    def stop_sounds(self):
        if STREAM_MUSIC:
            pygame.mixer.stop()
        else:
            total = pygame.mixer.get_num_channels()
            try:
                for i in range(1, total):
                    channel = pygame.mixer.Channel(i)
                    channel.stop()

            except:
                pass

        return

    def get_mouse_cursor(self):
        return self.__mouse_cursor

    def set_mouse_cursor(self, cursor, pointer=(0, 0), use_mouse_layer=True, update_item_pos=True, move_area=None):
        if self.__mouse_cursor != cursor:
            if use_mouse_layer:
                if self.__mouse_layer == None:
                    self.__mouse_layer = Layer()
                    self.__mouse_layer.set_stage(self)
                if cursor == None:
                    self.__mouse_layer.empty()
                elif not self.__mouse_layer.contains(cursor):
                    self.__mouse_layer.empty()
                    self.__mouse_layer.add(cursor)
            elif self.__mouse_layer != None:
                self.__mouse_layer.empty()
            if update_item_pos and cursor != None:
                if self.__mouse_snap_to_cursor:
                    if self.__mouse_cursor != None:
                        x = self.__mouse_cursor.get_left() + self.__mouse_pointer[0]
                        y = self.__mouse_cursor.get_top() + self.__mouse_pointer[1]
                        cursor.set_lefttop(x - pointer[0], y - pointer[1])
                else:
                    (x, y) = pygame.mouse.get_pos()
                    x = int(_div(x , engine.SCREEN_FACTOR))
                    y = int(_div(y , engine.SCREEN_FACTOR))
                    cursor.set_lefttop(x - pointer[0], y - pointer[1])
            self.__mouse_cursor = cursor
            self.__use_mouse_layer = use_mouse_layer
            self.__mouse_move_area = move_area
            self.__mouse_pointer = pointer
            self.__mouse_update = True
            if cursor != None and not update_item_pos:
                self.__mouse_snap_to_cursor = True
            if cursor == None:
                if self.__default_mouse_cursor != None:
                    self.set_mouse_cursor(self.__default_mouse_cursor)
                    pygame.mouse.set_visible(False)
                    self.__mouse_snap_to_cursor = False
                else:
                    pygame.mouse.set_visible(True)
            else:
                pygame.mouse.set_visible(False)
        return

    def set_mouse_pos(self, x, y):
        if self.__mouse_cursor != None:
            self.__mouse_cursor.set_lefttop(x - self.__mouse_pointer[0], y - self.__mouse_pointer[1])
            self.__mouse_snap_to_cursor = True
        return

    def redraw_mouse(self):
        if self.__mouse_layer != None:
            self.__mouse_layer.set_dirty()
        return

    def capture_leftmousedown(self, item, handler):
        button1 = pygame.mouse.get_pressed()[0]
        if not button1:
            key = 'mouse_button_keys'
            if self.is_timer_started(key):
                data = self.get_timer_data(key)
                if data != None:
                    if data[0]:
                        button1 = True
        if not button1:
            # El botón ya se soltó (un toque rápido): termina en el lugar del toque.
            (x, y) = self._last_touch_pos if getattr(self, '_last_touch_pos', None) else pygame.mouse.get_pos()
            x = int(_div(x , engine.SCREEN_FACTOR))
            y = int(_div(y , engine.SCREEN_FACTOR))
            args = ItemEventArgsMouse(x, y)
            handler(args, True)
        else:
            handler_defined = False
            for handler_data in self.__leftmousedown_handlers:
                if handler_data[0] == item and handler_data[1] == handler:
                    handler_defined = True
                    break

            if not handler_defined:
                self.__leftmousedown_handlers.append((item, handler))
        return

    def start_timer(self, key, milliseconds, func, data=None, drop_ticks=False, render_first=False):
        i = 0
        while i < len(self.__timers):
            if self.__timers[i].key == key:
                self.stop_timer(key)
                break
            i += 1

        milliseconds = max(1, milliseconds)
        self.__timers.append(Stage.TimerData(key, milliseconds, func, data, drop_ticks, render_first))
        return

    def stop_timer(self, key):
        i = 0
        while i < len(self.__timers):
            if self.__timers[i].key == key:
                data = self.__timers[i].data
                del self.__timers[i]
                return data
            i += 1

        return

    def stop_timers(self):
        while len(self.__timers) > 0:
            del self.__timers[len(self.__timers) - 1]

        return

    def is_timer_started(self, key):
        i = 0
        while i < len(self.__timers):
            if self.__timers[i].key == key:
                return True
            i += 1

        return False

    def get_timer_data(self, key):
        i = 0
        while i < len(self.__timers):
            if self.__timers[i].key == key:
                return self.__timers[i].data
            i += 1

        return

    def get_key_repeat(self):
        return

    def get_changed_handler(self):
        return self.__changed_handler

    def set_changed_handler(self, changed_handler):
        self.__changed_handler = changed_handler
        return

    def get_closed_handler(self):
        return self.__closed_handler

    def set_closed_handler(self, closed_handler):
        self.__closed_handler = closed_handler
        return

    def set_focus(self, item, set_focus_data=None):
        old_focused_item = self.__focused_item
        if old_focused_item != None:
            old_item = old_focused_item[0]
            old_data = old_focused_item[1]
        else:
            old_item = None
        if old_item != item:
            self.__focused_item = None
            if old_item != None:
                old_item.on_lost_focus(self, old_data)
                old_item.fire_event(ItemEvent.LOST_FOCUS, ItemEventArgs())
            if item == None:
                self.__focused_item = None
            else:
                data = item.on_got_focus(set_focus_data)
                self.__focused_item = (item, data)
                item.fire_event(ItemEvent.GOT_FOCUS, ItemEventArgs())
        return

    def get_focus(self):
        if self.__focused_item == None:
            return
        else:
            return self.__focused_item[0]
        return

    def get_focus_data(self):
        if self.__focused_item == None:
            return
        else:
            return self.__focused_item[1]
        return

    def get_over_item(self):
        return self.__over_item

    def notify_tick(self):
        if self.__locks > 0:
            event_handler = None
        elif len(self.__dialogs) == 0:
            event_handler = self.handle_event
        else:
            event_handler = self.__dialogs[len(self.__dialogs) - 1][1]
        mouse_rel = [
         0, 0]
        mouse_motion_args = None
        for event in _touch_text_events(pygame.event.get()):
            processed = False
            if event.type == MOUSEMOTION:
                mouse_rel[0] += event.rel[0]
                mouse_rel[1] += event.rel[1]
                mouse_motion_args = [event.pos[0], event.pos[1], event.buttons, mouse_rel[0], mouse_rel[1]]
            elif event.type == QUIT:
                self.game.quit()
                processed = True
            elif event.type == KEYDOWN:
                if event.key == K_f and event.mod & (KMOD_CTRL | KMOD_ALT):
                    self.game.set_show_fps(not self.game.get_show_fps())
                    processed = True
                elif event.key == K_ESCAPE:
                    if self.game.get_quit_on_escape():
                        self.game.quit()
                        processed = True
                elif event.key == K_F10 or event.mod == pygame.KMOD_LSHIFT and event.key == pygame.K_0:
                    design_stage = self.game.get_design_stage()
                    if design_stage != None and self.game.get_development_mode():
                        self.game.set_stage(design_stage)
                        processed = True
                elif event.mod == pygame.KMOD_LSHIFT and event.key == pygame.K_1:
                    test_stage = self.game.get_test_stage()
                    if test_stage != None and self.game.get_development_mode():
                        self.game.set_stage(test_stage)
                        processed = True
            elif event.type == MOUSEBUTTONDOWN:
                self.__on_mouse_button_down(event.pos[0], event.pos[1], event.button)
            elif event.type == MOUSEBUTTONUP:
                self.__on_mouse_button_up(event.pos[0], event.pos[1], event.button)
            elif event.type == ACTIVEEVENT:
                if event.gain:
                    if not self.__previous_active:
                        if self.__use_mouse_layer:
                            if self.__mouse_layer != None and not self.__mouse_layer.contains(self.__mouse_cursor):
                                self.__mouse_layer.add(self.__mouse_cursor)
                        self.__previous_active = True
                elif self.__previous_active:
                    if self.__mouse_layer != None:
                        self.__mouse_layer.empty()
                    self.__previous_active = False
            elif event.type == MUSIC_ENDSOUND_EVENT:
                if self.__music_data != None:
                    if STREAM_MUSIC:
                        pygame.mixer.music.load(self.__music_data[0])
                        pygame.mixer.music.play(-1)
                    else:
                        music_channel = pygame.mixer.Channel(0)
                        music_channel.queue(self.__music_data[1].sound)
                    if STREAM_MUSIC:
                        pygame.mixer.music.set_endevent()
            if not processed:
                if self.__focused_item != None:
                    if self.__focused_item[0].handle_event_focused(event, self.__focused_item[1]):
                        processed = True
                if not processed and event_handler != None:
                    event_handler(event)
                processed or self.__process_mouse_keys(event)

        if mouse_motion_args:
            self.__on_mouse_move(*mouse_motion_args)
        if self.__mouse_update:
            self.__mouse_update = False
            self.render(True)
        else:
            self.render(False)
        return

    def __on_set_music_volume(self, key, data):
        start_volume = data[0]
        target_volume = data[1]
        fadems = data[2]
        start_time = data[3]
        pause = data[4]
        elapsed_time = pygame.time.get_ticks() - start_time
        end_of_set = False
        if elapsed_time >= fadems:
            volume = target_volume
            self.stop_timer(key)
            end_of_set = True
        else:
            volume = start_volume + _div((target_volume - start_volume) , fadems) * elapsed_time
        if STREAM_MUSIC:
            pygame.mixer.music.set_volume(volume)
            if end_of_set and pause:
                pygame.mixer.music.pause()
        else:
            music_channel = pygame.mixer.Channel(0)
            music_channel.set_volume(volume)
            if end_of_set and pause:
                music_channel.pause()
        return

    def __on_mouse_move(self, x, y, buttons, rel_x, rel_y):
        data = self.get_timer_data('mouse_button_keys')
        if data != None:
            buttons = data[0]
        if self.__use_mouse_layer:
            if self.__mouse_layer != None and not self.__mouse_layer.contains(self.__mouse_cursor):
                self.__mouse_layer.add(self.__mouse_cursor)
        self.__previous_active = True
        event = pygame.event.Event(MOUSEMOTION, {'pos': (int(_div(x , engine.SCREEN_FACTOR)), int(_div(y , engine.SCREEN_FACTOR))), 'rel': (
                 int(_div(rel_x , engine.SCREEN_FACTOR)), int(_div(rel_y , engine.SCREEN_FACTOR))), 
           'buttons': buttons})
        (x, y) = event.pos
        item_stack = self.__update_over_item(x, y)
        self.__fire_routed_event(item_stack, ItemEvent.MOUSE_MOVE, ItemEventArgsMouse(x, y))
        if event.buttons[0] == 1 and len(self.__leftmousedown_handlers) > 0:
            x = event.pos[0]
            y = event.pos[1]
            args = ItemEventArgsMouse(x, y)
            for handler_data in self.__leftmousedown_handlers:
                handler_data[1](args, False)

        return

    def __on_mouse_button_down(self, x, y, button):
        event = pygame.event.Event(MOUSEBUTTONDOWN, {'pos': (int(_div(x , engine.SCREEN_FACTOR)), int(_div(y , engine.SCREEN_FACTOR))), 'button': button})
        if event.button == 1:
            item_stack = None
            # Táctil: se toca donde está el dedo (event.pos), no donde quedó el cursor dibujado; el cursor
            # se mueve ahí para que el resto del juego (arrastres, rollovers) lo vea en el mismo lugar.
            x = event.pos[0]
            y = event.pos[1]
            self._last_touch_pos = (x, y)
            if self.__mouse_cursor != None:
                self.set_mouse_pos(x, y)
                if pygame.event.get_grab():
                    item_stack = [self.__mouse_cursor]
            if item_stack == None:
                item_stack = self.hit_test_stack(x, y)
            if self.__focused_item != None:
                if self.__focused_item[0] not in item_stack:
                    self.set_focus(None)
            dblclick = False
            if self.__last_click != None:
                if pygame.time.get_ticks() - self.__last_click < DBLCLICK_DELAY:
                    dblclick = True
            if dblclick:
                self.__last_click = None
            else:
                self.__last_click = pygame.time.get_ticks()
            if item_stack != None and len(item_stack) > 0:
                self.__fire_routed_event(item_stack, ItemEvent.CLICK, ItemEventArgsMouse(x, y))
                if dblclick:
                    self.__fire_routed_event(item_stack, ItemEvent.DBLCLICK, ItemEventArgsMouse(x, y))
        return

    def __on_mouse_button_up(self, x, y, button):
        event = pygame.event.Event(MOUSEBUTTONUP, {'pos': (int(_div(x , engine.SCREEN_FACTOR)), int(_div(y , engine.SCREEN_FACTOR))), 'button': button})
        if event.button == 1 and len(self.__leftmousedown_handlers) > 0:
            x = event.pos[0]
            y = event.pos[1]
            args = ItemEventArgsMouse(x, y)
            for handler_data in self.__leftmousedown_handlers:
                handler_data[1](args, True)

            self.__leftmousedown_handlers = []
            self.__update_over_item(x, y)
        return

    def __process_mouse_keys(self, event):
        if event.type == KEYDOWN:
            if event.key == K_KP4 or event.key == K_KP6 or event.key == K_KP2 or event.key == K_KP8:
                key = 'mouse_pos_keys'
                data = self.get_timer_data(key)
                if data == None:
                    data = [
                     1]
                self.start_timer(key, 30, self.__update_mouse_position_keys, data)
                self.__update_mouse_position_keys(key, data)
            elif event.key == K_KP7 or event.key == K_KP9 or event.key == K_KP1 or event.key == K_KP3:
                key = 'mouse_button_keys'
                data = self.get_timer_data(key)
                if data == None:
                    data = [
                     [
                      False, False, False]]
                self.start_timer(key, 30, self.__update_mouse_button_keys, data)
                self.__update_mouse_button_keys(key, data)
        return

    def __update_mouse_position_keys(self, key, data):
        increment = data[0]
        if increment < 30:
            data[0] += 1
        increment *= engine.SCREEN_FACTOR
        pressed = pygame.key.get_pressed()
        (x, y) = pygame.mouse.get_pos()
        processed = False
        if pressed[K_KP4]:
            x -= increment
            processed = True
        if pressed[K_KP6]:
            x += increment
            processed = True
        if pressed[K_KP8]:
            y -= increment
            processed = True
        if pressed[K_KP2]:
            y += increment
            processed = True
        if not processed:
            self.stop_timer(key)
        elif x < 0:
            x = 0
        if y < 0:
            y = 0
        screen_width = engine.SCREEN_WIDTH * engine.SCREEN_FACTOR
        screen_height = engine.SCREEN_HEIGHT * engine.SCREEN_FACTOR
        if x >= screen_width:
            x = screen_width - 1
        if y >= screen_height:
            y = screen_height - 1
        pygame.mouse.set_pos(x, y)
        return

    def __update_mouse_button_keys(self, key, data):
        old_state = data[0]
        new_state = [False, False, False]
        data[0] = new_state
        pressed = pygame.key.get_pressed()
        processed = False
        if pressed[K_KP3]:
            new_state[0] = True
            processed = True
        for i in range(len(old_state)):
            if old_state[i] != new_state[i]:
                (x, y) = pygame.mouse.get_pos()
                if new_state[i]:
                    self.__on_mouse_button_down(x, y, i + 1)
                else:
                    self.__on_mouse_button_up(x, y, i + 1)

        if not processed:
            self.stop_timer(key)
        return

    def __run_gc(self, key, data):
        self.stop_timer(key)
        gc.collect()
        return

    def __fire_routed_event(self, item_stack, click_type, args):
        k = len(item_stack) - 1
        while k >= 0:
            if item_stack[k].fire_event(click_type, args):
                break
            k -= 1

        return

    def __draw_background(self, surface, dirty_rects):
        surface.set_clip(Rect(0, 0, 9999, 9999))
        if self.__background == None:
            bgd_color = self.__background_color
            for dirty_rect in dirty_rects:
                surface.fill(bgd_color, dirty_rect)

        else:
            surface_blit = surface.blit
            bgd_surface = self.__background.surface
            for dirty_rect in dirty_rects:
                surface_blit(bgd_surface, dirty_rect, dirty_rect)

        return

    def __update_over_item_callback(self, key, data):
        self.stop_timer(key)
        (x, y) = pygame.mouse.get_pos()
        self.__update_over_item(int(_div(x , engine.SCREEN_FACTOR)), int(_div(y , engine.SCREEN_FACTOR)))
        return

    def __update_over_item(self, x, y):
        item_stack = self.hit_test_stack(x, y)
        if self.target_surface == None and self.game.loading_layer != None:
            new_over_item = None
        elif self.__mouse_cursor != None and not self.__use_mouse_layer:
            new_over_item = self.__mouse_cursor
        else:
            k = len(item_stack) - 1
            new_over_item = None
            while k >= 0:
                item = item_stack[k]
                if item.has_event_handler(ItemEvent.MOUSE_ENTER) or item.has_event_handler(ItemEvent.MOUSE_LEAVE):
                    new_over_item = item
                    break
                k -= 1

        if self.__over_item != new_over_item:
            if len(self.__leftmousedown_handlers) > 0:
                over_captured_item = False
                for handler_data in self.__leftmousedown_handlers:
                    if handler_data[0] == new_over_item:
                        over_captured_item = True

                if not over_captured_item:
                    new_over_item = None
            old_over_item = self.__over_item
            self.__over_item = new_over_item
            if old_over_item != None:
                old_over_item.fire_event(ItemEvent.MOUSE_LEAVE, ItemEventArgsMouse(x, y))
            if self.__over_item != None:
                self.__over_item.fire_event(ItemEvent.MOUSE_ENTER, ItemEventArgsMouse(x, y))
        return item_stack

    def prepare(self):
        return

    def render(self, update_mouse=False):
        pos = pygame.mouse.get_pos()
        if pos != self.__mouse_real_pos or update_mouse:
            self.__mouse_real_pos = pos
            x = int(_div(pos[0] , engine.SCREEN_FACTOR))
            y = int(_div(pos[1] , engine.SCREEN_FACTOR))
            self.__update_over_item(x, y)
            if self.__mouse_cursor != None:
                self.__update_mouse_cursor_position(x, y)
        timers = self.__timers
        if len(timers) > 0:
            ticks = pygame.time.get_ticks()
            i = 0
            while i < len(timers):
                timer = timers[i]
                if timer.render_first:
                    timer.render_first = False
                else:
                    while ticks >= timer.tick:
                        timer.func(timer.key, timer.data)
                        if timer not in timers:
                            i -= 1
                            break
                        if timer.drop_ticks:
                            while ticks >= timer.tick:
                                timer.tick += timer.milliseconds

                            break
                        else:
                            timer.tick += timer.milliseconds

                i += 1

        target_surface = self.target_surface
        if target_surface == None:
            target_surface = self.game.window
        frame_delay = self.game.get_frame_delay()
        dirty_rects = []
        prerender_dirty_rects = []
        prerender = self.__prerender_to_layer != None
        for l in self.layers:
            if prerender:
                l.update(prerender_dirty_rects, frame_delay)
                prerender = self.__prerender_to_layer != l
                if len(prerender_dirty_rects) > 6:
                    self.__compact_dirty_rects(prerender_dirty_rects)
            else:
                l.update(dirty_rects, frame_delay)
                if len(prerender_dirty_rects) > 6:
                    self.__compact_dirty_rects(dirty_rects)

        if self.target_surface != None:
            loading_layer = None
        else:
            loading_layer = self.game.loading_layer
            if loading_layer != None:
                loading_layer.update(dirty_rects, frame_delay)
        if self.__mouse_layer != None:
            self.__mouse_layer.update(dirty_rects, frame_delay)
        if self.__background_dirty:
            if self.__prerender_to_layer != None:
                prerender_dirty_rects = [
                 target_surface.get_rect()]
                dirty_rects = []
            else:
                dirty_rects = [
                 target_surface.get_rect()]
            self.__background_dirty = False
        prerender = self.__prerender_to_layer != None
        if prerender:
            if self.__update_prerender_buffer:
                self.__update_prerender_buffer = False
                prerender_rects = [target_surface.get_rect()]
            else:
                prerender_rects = prerender_dirty_rects
        if self.__prerender_to_layer != None:
            self.__draw_background(self.__prerender_buffer, prerender_rects)
        else:
            self.__draw_background(target_surface, dirty_rects)
        for l in self.layers:
            if prerender:
                if l.get_visible():
                    l.draw(self.__prerender_buffer, prerender_rects)
                if self.__prerender_to_layer == l:
                    for prerender_dirty_rect in prerender_dirty_rects:
                        k = prerender_dirty_rect.collidelist(dirty_rects)
                        while k != -1:
                            prerender_dirty_rect.union_ip(dirty_rects[k])
                            del dirty_rects[k]
                            k = prerender_dirty_rect.collidelist(dirty_rects)

                        dirty_rects.append(prerender_dirty_rect)

                    if len(dirty_rects) > 0:
                        self.__draw_prerender_buffer(target_surface, dirty_rects)
                    prerender = False
            elif l.get_visible():
                l.draw(target_surface, dirty_rects)

        if loading_layer != None:
            loading_layer.draw(target_surface, dirty_rects)
        elif self.__mouse_layer != None:
            self.__mouse_layer.draw(target_surface, dirty_rects)
        if self.target_surface == None:
            if self.game.get_show_fps():
                self.game.draw_fps(dirty_rects)
            self.game.update_display(dirty_rects)
        return

    def __compact_dirty_rects(self, dirty_rects):
        while len(dirty_rects) > 6:
            dirty_rect = dirty_rects[0]
            dirty_rect.union_ip(dirty_rects[1])
            del dirty_rects[0:1]
            k = dirty_rect.collidelist(dirty_rects)
            while k != -1:
                dirty_rect.union_ip(dirty_rects[k])
                del dirty_rects[k]
                k = dirty_rect.collidelist(dirty_rects)

            dirty_rects.append(dirty_rect)

        return

    def __draw_prerender_buffer(self, target_surface, dirty_rects):
        for dirty_rect in dirty_rects:
            target_surface.set_clip(dirty_rect)
            target_surface.blit(self.__prerender_buffer, dirty_rect, dirty_rect)

        return

    def __load_background(self, image):
        if image == None:
            self.__background = None
            self.__background_color = Color('#000000')
        else:
            rect = image.get_real_rect()
            if self.target_surface == None:
                (stage_width, stage_height) = self.game.get_window_size()
            else:
                (stage_width, stage_height) = self.target_surface.get_size()
            if rect.width >= stage_width and rect.height >= stage_height:
                self.__background = image
            else:
                surface = pygame.Surface((stage_width, stage_height))
                y = 0
                while y < stage_height:
                    x = 0
                    while x < stage_width:
                        surface.blit(image.surface, (x, y), rect)
                        x += rect.width

                    y += rect.height

                self.__background = assets.Image(surface)
        return

    def __update_mouse_cursor_position(self, x, y):
        if self.__mouse_snap_to_cursor:
            pygame.mouse.set_pos(int((self.__mouse_cursor.get_left() + self.__mouse_pointer[0]) * engine.SCREEN_FACTOR), int((self.__mouse_cursor.get_top() + self.__mouse_pointer[1]) * engine.SCREEN_FACTOR))
            self.__mouse_snap_to_cursor = False
        elif self.__mouse_move_area != None:
            if callable(self.__mouse_move_area):
                (x, y) = self.__mouse_move_area(x, y)
            else:
                cursor_width = self.__mouse_cursor.get_width()
                cursor_height = self.__mouse_cursor.get_height()
                if x < self.__mouse_move_area.left:
                    x = self.__mouse_move_area.left
                elif x + cursor_width > self.__mouse_move_area.right:
                    x = self.__mouse_move_area.right - cursor_width
                if y < self.__mouse_move_area.top:
                    y = self.__mouse_move_area.top
                elif y + cursor_height > self.__mouse_move_area.bottom:
                    y = self.__mouse_move_area.bottom - cursor_height
            if x != None and y != None:
                pygame.mouse.set_pos(int(x * engine.SCREEN_FACTOR), int(y * engine.SCREEN_FACTOR))
        if x != None and y != None:
            self.__mouse_cursor.set_lefttop(x - self.__mouse_pointer[0], y - self.__mouse_pointer[1])
        return

    def handle_event(self, e):
        return 0

    def redraw(self):
        self.__background_dirty = True
        if self.__changed_handler != None:
            self.__changed_handler(self)
        self.__mouse_update = True
        return

    class TimerData:

        def __init__(self, key, milliseconds, func, data, drop_ticks, render_first):
            self.key = key
            self.tick = pygame.time.get_ticks() + milliseconds
            self.milliseconds = milliseconds
            self.func = func
            self.data = data
            self.drop_ticks = drop_ticks
            self.render_first = render_first
            return


class StageIso(Stage):

    def __init__(self, game, tags, background_image=None, target_surface=None):
        Stage.__init__(self, game, background_image, target_surface)
        self.__origin = (300, 200)
        self.__cell_width = 80
        self.__cell_height = 40
        self.__multiplier = 1
        self.__item_definitions = {}
        self.__item_images_cache = {}
        self.__item_masks_cache = {}
        self.__set_name = ''
        self.__image_suffix = ''
        self.__tags = tags
        self.__adjust_positions = None
        return

    def add_layer(self, layer, index=-1):
        Stage.add_layer(self, layer, index)
        return

    def get_rowcol(self, x, y):
        x -= self.__origin[0] * self.__multiplier
        y -= self.__origin[1] * self.__multiplier
        m = _div(float(-self.__cell_height) , self.__cell_width)
        t1 = _div(y , (2 * m))
        t2 = _div(x , 2)
        t3 = _div(self.__cell_width * self.__multiplier , 2)
        row = int(math.floor(_div((-t1 - t2) , t3)))
        col = int(math.floor(_div((-t1 + t2) , t3)))
        return (
         row, col)

    def get_xy(self, row, col):
        x = self.__origin[0] * self.__multiplier + _div(self.__cell_width , 2) * self.__multiplier * (col - row)
        y = self.__origin[1] * self.__multiplier + _div(self.__cell_height , 2) * self.__multiplier * (row + col + 1)
        return (
         int(x), int(y))

    def hit_test(self, x, y):
        return Stage.hit_test(self, x, y)

    def hit_test_stack(self, x, y, ignore_clip=False):
        return Stage.hit_test_stack(self, x, y, ignore_clip)

    def get_grid_origin(self):
        return self.__origin

    def get_grid_cell_size(self):
        return (
         self.__cell_width, self.__cell_height)

    def get_grid_multiplier(self):
        return self.__multiplier

    def get_grid_definition(self):
        return (
         self.__origin, self.__cell_width, self.__cell_height, self.__multiplier)

    def set_grid_definition(self, origin, cell_width, cell_height, multiplier):
        self.__origin = origin
        self.__cell_width = cell_width
        self.__cell_height = cell_height
        self.__multiplier = multiplier
        return

    def get_tags(self):
        return self.__tags

    def set_tags(self, tags):
        self.__tags = tags
        return

    def get_set_name(self):
        return self.__set_name

    def set_items(self, set_name, image_suffix='', item_definitions=None):
        self.__set_name = set_name
        self.__image_suffix = image_suffix
        self.__item_images_cache = {}
        self.__item_masks_cache = {}
        if item_definitions != None:
            self.__item_definitions = item_definitions
        elif set_name != '':
            file_name = self.__set_name + '.tcs'
            try:
                self.__item_definitions = {}
                data = assets.load_data(file_name)
                for fields in data:
                    if len(fields) > 0:
                        type = fields[0]
                        try:
                            center = (int(fields[1]), int(fields[2]))
                            size = (int(fields[3]), int(fields[4]))
                            l = fields[5].split('|')
                            place_holders = []
                            for place_holder in l:
                                if len(place_holder) >= 3:
                                    place_holder = place_holder.split(',')
                                    place_holders.append(IsoPlaceHolder(place_holder[0], int(place_holder[1]), int(place_holder[2])))

                            tag = fields[6].strip()
                            l = fields[7].split('|')
                            states = []
                            for state in l:
                                state = state.split(',')
                                if len(state) >= 3:
                                    if len(state) >= 4:
                                        clip = state[3].strip() == '1'
                                    else:
                                        clip = False
                                    states.append(IsoDefState(state[0], (int(state[1]), int(state[2])), clip))

                            self.__item_definitions[type] = IsoDefinition(center, size, place_holders, tag, states)
                        except Exception:
                            print(("Invalid format for item '" + type + "' in file '" + file_name + "'"))
                            raise

            except Exception:
                print(('Cannot load items data:', file_name))
                raise

        return

    def get_item_definition(self, item_type, flipped_h=False):
        try:
            definition = self.__item_definitions[item_type]
        except Exception:
            print(("Missing definition for item '" + item_type + "'."))
            raise

        return definition

    def get_item_definitions(self):
        return self.__item_definitions

    def get_item_types_with_tag(self, tag):
        item_types = []
        for (item_type, definition) in list(self.__item_definitions.items()):
            if definition.tag == tag:
                item_types.append(item_type)

        return item_types

    def load_item_image(self, type, state, flip_h=False, suffix=None):
        key = type
        if state.suffix != '':
            state_suffix = '_' + state.suffix
            key += state_suffix
        else:
            state_suffix = ''
        if suffix != None:
            key += suffix
            state_suffix += suffix
        if flip_h:
            key += '?H'
        if key in self.__item_images_cache:
            image = self.__item_images_cache[key]
        else:
            image = None
            if flip_h:
                image = self.load_item_image(type, state, False, suffix)
            if image == None:
                file_name = self.__set_name + type + self.__image_suffix + state_suffix + '.png'
                image = assets.load_image(file_name)
            else:
                file_name = key
            if flip_h:
                image = assets.Image(pygame.transform.flip(image.surface, True, False), file_name)
            self.__item_images_cache[key] = image
        return image

    def load_item_mask(self, type, state, flip_h, mask_suffix):
        key = type
        if state.suffix != '':
            suffix = '_' + state.suffix
            key += suffix
        else:
            suffix = ''
        suffix += '$' + mask_suffix
        if flip_h:
            key += '?H'
        if key in self.__item_masks_cache:
            mask = self.__item_masks_cache[key]
        else:
            mask = None
            if flip_h:
                mask = self.load_item_mask(type, state, False, mask_suffix)
            if mask == None:
                file_name = self.__set_name + type + self.__image_suffix + suffix + '.gif'
                mask = assets.load_mask(file_name)
            if flip_h:
                mask = pygame.transform.flip(mask, True, False)
            self.__item_masks_cache[key] = mask
        return mask

    def load_level(self, level_name, layer, states, prepare_item=None):
        file_name = self.__set_name + level_name + '.tcl'
        items = []
        try:
            data = assets.load_data(file_name)
            for fields in data:
                if len(fields) > 0:
                    type = fields[0]
                    if type.endswith('?H'):
                        type = type[:len(type) - 2]
                        flip_h = True
                    else:
                        flip_h = False
                    try:
                        row = float(fields[1])
                        col = float(fields[2])
                        state_suffix = fields[3].strip()
                    except Exception:
                        print(("Invalid format for item '" + type + "' in file '" + file_name + "'"))
                        raise
                    else:
                        item_state = None
                        for state in states:
                            if state.suffix == state_suffix:
                                item_state = state
                                break

                        if item_state == None:
                            raise Exception("State suffix '" + state_suffix + "' is not defined, and item '" + type + "' has this state.")
                        item = ItemCell(self, type, item_state, flip_h, row, col)
                        if prepare_item != None:
                            prepare_item(item)
                        layer.add(item)
                        items.append(item)

        except Exception:
            print(('Cannot load level items:', file_name))
            raise

        return items

    def save_level(self, level_name, layer):
        file_name = self.__set_name + level_name + '.tcl'
        try:
            data = []
            items_to_write = layer.items[:]
            i = 0
            while i < len(items_to_write):
                item = items_to_write[i]
                duplicate = False
                j = i + 1
                while j < len(items_to_write):
                    item2 = items_to_write[j]
                    item_position = item.get_position()
                    if item_position != None and item.get_type() == item2.get_type() and item_position == item2.get_position() and item.get_flip_h() == item2.get_flip_h():
                        duplicate = True
                        break
                    else:
                        j += 1

                if duplicate:
                    del items_to_write[i]
                else:
                    i += 1

            for item in items_to_write:
                fields = []
                if item.get_flip_h():
                    fields.append(item.get_type() + '?H')
                else:
                    fields.append(item.get_type())
                (row, col) = item.get_position()
                if row % 1 < 0.001:
                    row = int(row)
                fields.append(str(row))
                if col % 1 < 0.001:
                    col = int(col)
                fields.append(str(col))
                fields.append(item.get_state().suffix)
                data.append(fields)

            assets.save_data(file_name, data)
        except Exception:
            print(('Cannot save items data:', file_name))
            raise

        return

    def load_place_holders(self, layer, list):
        for item in layer.items:
            if isinstance(item, ItemCell):
                definition = item.get_definition()
                place_holders = definition.place_holders
                for i in range(len(place_holders)):
                    list.append((item, place_holders[i], i))

        return

    def find_item(self, layer, position, type):
        for item in layer.items:
            if isinstance(item, ItemCell):
                if item.get_type() == type and item.get_position() == position:
                    return item

        return


class IsoDefinition():

    def __init__(self, center, size, place_holders, tag, states):
        self.center = center
        self.size = size
        self.place_holders = place_holders
        self.tag = tag
        self.states = states
        self.__flip_h = None
        return

    def has_state(self, state):
        for def_state in self.states:
            if def_state.name == state.name:
                return True

        return False

    def flip_h(self, item):
        if self.__flip_h == None:
            flipped_place_holders = []
            for placeholder in self.place_holders:
                flipped_place_holders.append(IsoPlaceHolder(placeholder.tag, -placeholder.x, placeholder.y))

            flipped_states = []
            for state in self.states:
                flipped_states.append(IsoDefState(state.name, state.center, state.clip))

            self.__flip_h = IsoDefinition(self.center, (self.size[1], self.size[0]), flipped_place_holders, self.tag, flipped_states)
            self.__flip_h.__flip_h = self
        return self.__flip_h


class IsoDefState():

    def __init__(self, name, center, clip):
        self.name = name
        self.center = center
        self.clip = clip
        return


class IsoPlaceHolder():

    def __init__(self, tag, x, y):
        self.tag = tag
        self.x = x
        self.y = y
        return


class IsoState():

    def __init__(self, name, suffix):
        self.name = name
        self.suffix = suffix
        return


class Item():

    def __init__(self, left, top, width, height):
        self.__layer = None
        self.__left = left
        self.__top = top
        self.__width = width
        self.__height = height
        self.__alpha = 255
        self.visible = True
        self.rect = Rect(left, top, width, height)
        self.image = None
        self.draw_function = None
        self.__events = {}
        self.__rollover = None
        return

    def get_visible(self):
        return self.visible

    def set_visible(self, visible):
        if self.visible != visible:
            self.visible = visible
            self.set_dirty()
        return

    def get_left(self):
        return self.__left

    def set_left(self, value):
        if self.__left != value:
            self.__left = value
            self.set_dirty()
        return

    def get_top(self):
        return self.__top

    def set_top(self, value):
        if self.__top != value:
            self.__top = value
            self.set_dirty()
        return

    def set_lefttop(self, left, top):
        if self.__left != left or self.__top != top:
            self.__left = left
            self.__top = top
            self.set_dirty()
        return

    def get_width(self):
        return self.__width

    def set_width(self, value):
        if self.__width != value:
            self.__width = value
            self.set_dirty()
        return

    def get_height(self):
        return self.__height

    def set_height(self, value):
        if self.__height != value:
            self.__height = value
            self.set_dirty()
        return

    def get_bounds(self):
        return Rect(self.__left, self.__top, self.__width, self.__height)

    def get_size(self):
        return (
         self.__width, self.__height)

    def set_dirty(self):
        if self.__layer != None:
            self.__layer.add_dirty_item(self)
        if self.__rollover != None:
            self.__update_rollover_position()
        return

    def get_layer(self):
        return self.__layer

    def set_layer(self, layer):
        if layer == None:
            self.__layer = None
        elif self.__layer != None:
            raise Exception('The item is already part of a layer')
        else:
            self.__layer = layer
        return

    def get_stage(self):
        if self.__layer == None:
            return
        else:
            return self.__layer.get_stage()
        return

    def update(self, frame_delay):
        real_left = self.__left
        real_top = self.__top
        if self.visible:
            real_width = self.__width
            real_height = self.__height
        else:
            real_width = 0
            real_height = 0
        old_rect = self.rect
        self.rect = Rect(real_left, real_top, real_width, real_height)
        if old_rect == None:
            return self.rect
        else:
            return self.rect.union(old_rect)
        return

    def is_over(self, x, y, ignore_clip=False):
        return self.__left <= x and x < self.__left + self.__width and self.__top <= y and y < self.__top + self.__height

    def add_event_handler(self, event, handler):
        if event in self.__events:
            self.__events[event].append(handler)
        else:
            self.__events[event] = [
             handler]
        return

    def remove_event_handler(self, event, handler):
        if event in self.__events:
            if handler in self.__events[event]:
                handlers = self.__events[event]
                handlers.remove(handler)
                if len(handlers) == 0:
                    del self.__events[event]
        return

    def fire_event(self, event, args):
        if event in self.__events:
            handlers = self.__events[event]
            handled = False
            for handler in handlers:
                ret = handler(self, args)
                if ret or ret == None:
                    handled = True

            return handled
        else:
            return False
        return

    def has_event_handler(self, event):
        return event in self.__events and len(self.__events[event]) > 0

    def set_rollover(self, image, sound, x=None, y=None):
        if image == None:
            self.__rollover = None
            self.remove_event_handler(ItemEvent.MOUSE_ENTER, self.__rollover_mouse_enter)
            self.remove_event_handler(ItemEvent.MOUSE_LEAVE, self.__rollover_mouse_leave)
        else:
            item_image = ItemImage(0, 0, image)
            self.__rollover = (item_image, sound, x, y)
            self.remove_event_handler(ItemEvent.MOUSE_ENTER, self.__rollover_mouse_enter)
            self.remove_event_handler(ItemEvent.MOUSE_LEAVE, self.__rollover_mouse_leave)
            self.add_event_handler(ItemEvent.MOUSE_ENTER, self.__rollover_mouse_enter)
            self.add_event_handler(ItemEvent.MOUSE_LEAVE, self.__rollover_mouse_leave)
        return

    def show_rollover(self, play_sound):
        if self.__rollover != None:
            layer = self.get_layer()
            if layer != None:
                stage = layer.get_stage()
                if stage != None and not stage.is_timer_started((self, 'fade')):
                    item_image = self.__update_rollover_position()
                    layer.add(item_image, layer.index_of(self))
                    rollover_sound = self.__rollover[1]
                    if play_sound and rollover_sound != None:
                        stage.render()
                        rollover_sound.stop()
                        rollover_sound.play()
        return

    def hide_rollover(self):
        if self.__rollover != None:
            image = self.__rollover[0]
            layer = image.get_layer()
            if layer != None:
                layer.remove(image)
        return

    def __rollover_mouse_enter(self, item, args):
        self.show_rollover(True)
        return

    def __rollover_mouse_leave(self, item, args):
        self.hide_rollover()
        return

    def __update_rollover_position(self):
        item_image = self.__rollover[0]
        x = self.__rollover[2]
        y = self.__rollover[3]
        if x == None:
            dx = _div((self.get_width() - item_image.get_width()) , 2)
        else:
            dx = x
        if y == None:
            dy = _div((self.get_height() - item_image.get_height()) , 2)
        else:
            dy = y
        item_image.set_left(self.__left + dx)
        item_image.set_top(self.__top + dy)
        return item_image


class ItemEvent():
    CLICK = 0
    DBLCLICK = 1
    MOUSE_ENTER = 2
    MOUSE_LEAVE = 3
    MOUSE_MOVE = 4
    GOT_FOCUS = 5
    LOST_FOCUS = 6
    STATE_CHANGED = 7


class ItemEventArgs():

    def __init__(self):
        return


class ItemEventArgsMouse(ItemEventArgs):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        return


class ItemEventArgsStateChanged(ItemEventArgs):

    def __init__(self, previous_state):
        self.previous_state = previous_state
        return


class ItemImage(Item):

    def __init__(self, left, top, image, area=None, hit_over_transparent=False):
        Item.__init__(self, left, top, 0, 0)
        self.__alpha = 255
        self.__hit_over_transparent = hit_over_transparent
        self.set_image(image, area)
        return

    def get_alpha(self):
        return self.__alpha

    def set_alpha(self, alpha):
        self.__alpha = alpha
        self.surface = set_surface_alpha(self.__source_surface, alpha)
        self.set_dirty()
        return

    def is_over(self, x, y, ignore_clip=False):
        bounds = self.get_bounds()
        if bounds.collidepoint(x, y):
            if self.__hit_over_transparent:
                return True
            if ignore_clip:
                test_surface = self.__source_surface
            else:
                test_surface = self.surface
            try:
                c = test_surface.get_at((int(x - self.get_left()), int(y - self.get_top())))
            except Exception:
                return False
            else:
                if c[3] > 40:
                    return True
        return False

    def get_image(self):
        return self.__image

    def set_image(self, image, area=None):
        if hasattr(self, '_ItemImage__rollover') and self.__rollover != None and self.__rollover[1] != None:
            self.__rollover[1] = image
        elif hasattr(self, '_ItemImage__pressed') and self.__pressed != None and self.__pressed[1] != None:
            self.__pressed[1] = image
        else:
            self.__set_image_internal(image, area)
        return

    def set_clip_mask(self, image_mask, image_pos):
        if image_mask == None:
            self.__source_surface = self.__surface_noclip
            if self.surface != self.__surface_noclip:
                self.surface = self.__surface_noclip
                self.set_dirty()
        else:
            left = self.get_left()
            top = self.get_top()
            if image_pos[0] < left:
                x = 0
                area_x = left - image_pos[0]
            else:
                x = image_pos[0] - left
                area_x = 0
            if image_pos[1] < top:
                y = 0
                area_y = top - image_pos[1]
            else:
                y = image_pos[1] - top
                area_y = 0
            area_width = min(image_mask.get_width() - area_x, self.get_width())
            area_height = min(image_mask.get_height() - area_y, self.get_height())
            self.surface = self.__source_surface.copy()
            alpha_matrix = pygame.surfarray.pixels_alpha(self.surface)
            alpha_matrix_mask = pygame.surfarray.pixels_alpha(image_mask.surface)
            for i in range(area_width):
                alpha_matrix[x + i][y:y + area_height] &= alpha_matrix_mask[area_x + i][area_y:area_y + area_height]

            self.__source_surface = self.surface
            self.set_dirty()
        return

    def set_rollover_image(self, image, sound):
        if hasattr(self, '_ItemImage__rollover') and self.__rollover != None:
            old_image = self.__rollover[1]
            self.__rollover = None
            if old_image != None:
                self.set_image(old_image)
            self.remove_event_handler(ItemEvent.MOUSE_ENTER, self.__rollover_mouse_enter)
            self.remove_event_handler(ItemEvent.MOUSE_LEAVE, self.__rollover_mouse_leave)
        if image != None:
            self.__rollover = [
             image, None, sound]
            self.add_event_handler(ItemEvent.MOUSE_ENTER, self.__rollover_mouse_enter)
            self.add_event_handler(ItemEvent.MOUSE_LEAVE, self.__rollover_mouse_leave)
        return

    def set_pressed_image(self, image):
        if hasattr(self, '_ItemImage__pressed') and self.__pressed != None:
            old_image = self.__pressed[1]
            self.__pressed = None
            if old_image != None:
                self.set_image(old_image)
            self.remove_event_handler(ItemEvent.CLICK, self.__pressed_click)
        if image != None:
            self.__pressed = [
             image, None]
            self.add_event_handler(ItemEvent.CLICK, self.__pressed_click)
        return

    def __set_image_internal(self, image, area=None):
        self.__image = image
        if image == None:
            self.area = (0, 0, 0, 0)
            self.surface = pygame.Surface((0, 0), pygame.SRCALPHA, 32)
            self.__source_surface = self.surface
            self.__surface_noclip = self.surface
            self.set_width(0)
            self.set_height(0)
        else:
            self.set_width(image.get_width())
            self.set_height(image.get_height())
            self.surface = image.surface
            self.__source_surface = self.surface
            self.__surface_noclip = self.surface
            self.area = area
            if self.__alpha != 255:
                self.surface = set_surface_alpha(self.__source_surface, self.__alpha)
            self.set_dirty()
        return

    def __rollover_mouse_enter(self, item, args):
        if self.__rollover != None:
            if hasattr(self, '_ItemImage__pressed') and self.__pressed != None and self.__pressed[1] != None:
                self.__rollover[1] = self.__pressed[1]
                self.__pressed[1] = self.__rollover[0]
            else:
                current_image = self.get_image()
                self.__set_image_internal(self.__rollover[0])
                self.__rollover[1] = current_image
            rollover_sound = self.__rollover[2]
            if rollover_sound != None:
                layer = self.get_layer()
                if layer != None:
                    stage = layer.get_stage()
                    if stage != None:
                        stage.render()
                        rollover_sound.stop()
                        rollover_sound.play()
        return

    def __rollover_mouse_leave(self, item, args):
        if self.__rollover != None:
            if hasattr(self, '_ItemImage__pressed') and self.__pressed != None and self.__pressed[1] != None:
                self.__pressed[1] = self.__rollover[1]
                self.__rollover[1] = None
            else:
                old_image = self.__rollover[1]
                if old_image != None:
                    self.__rollover[1] = None
                    item.__set_image_internal(old_image)
        return

    def __pressed_click(self, item, args):
        if self.__pressed != None:
            stage = self.get_stage()
            if stage != None:
                current_image = self.get_image()
                self.__set_image_internal(self.__pressed[0])
                self.__pressed[1] = current_image
                stage.capture_leftmousedown(self, self.__pressed_mousecapture)
        return

    def __pressed_mousecapture(self, mouse_args, released):
        if released:
            if self.__pressed != None:
                old_image = self.__pressed[1]
                if old_image != None:
                    self.__pressed[1] = None
                    self.__set_image_internal(old_image)
        return


class ItemCustomDraw(Item):

    def __init__(self, left, top, width, height, draw_function, mask=None):
        Item.__init__(self, left, top, width, height)
        self.draw_function = draw_function
        self.mask = mask
        return

    def is_over(self, x, y, ignore_clip=False):
        bounds = self.get_bounds()
        if bounds.collidepoint(x, y):
            if self.mask == None:
                return True
            elif callable(self.mask):
                return self.mask(self, x, y)
            else:
                try:
                    c = self.mask.get_at((x - self.get_left(), y - self.get_top()))
                    if c[0] != 255 or c[1] != 255 or c[2] != 255:
                        return True
                except Exception:
                    return False

        return False


class ItemCell(ItemImage):

    def __init__(self, stage, type, state, flip_h=False, row=-999, col=-999):
        self.__stage = stage
        ItemImage.__init__(self, 0, 0, None)
        self.__state = state
        self.__center = None
        self.__flip_h = flip_h
        self.__type = None
        self.__definition = None
        self.set_type(type)
        self.__position = (0, 0)
        if row != -999:
            self.set_position(row, col)
        return

    def clone(self, stage):
        (row, col) = self.get_position()
        new_item = ItemCell(stage, self.__type, self.__state, self.__flip_h, -999, -999)
        new_item.__center = self.__center
        new_item.set_position(row, col)
        new_item.set_visible(self.get_visible())
        if hasattr(self, '_ItemCell__visible_in_states') and self.__visible_in_states != None:
            new_item.__visible_in_states = self.__visible_in_states[:]
        if hasattr(self, 'placeholder_items') and self.placeholder_items != None:
            new_item.placeholder_items = self.placeholder_items[:]
        return new_item

    def get_type(self):
        return self.__type

    def set_type(self, type):
        if self.__type != type:
            if self.__type == None:
                position = None
            else:
                position = self.get_position()
            self.__type = type
            self.__image = self.__stage.load_item_image(type, self.__state, self.__flip_h)
            self.set_image(self.__image, None)
            self.__definition = self.__stage.get_item_definition(type)
            if self.__definition == None:
                raise Exception("There is no definition for item '" + type + "'")
            if self.__flip_h:
                self.__definition = self.__definition.flip_h(self)
            self.__load_center()
            if position != None:
                self.set_position(position[0], position[1])
        return

    def get_state(self):
        return self.__state

    def set_state(self, state):
        if self.__state != state:
            position = self.get_position()
            previous_state = self.__state
            self.__state = state
            self.__image = self.__stage.load_item_image(self.__type, self.__state, self.__flip_h)
            self.set_image(self.__image, None)
            self.__load_center()
            self.set_position(position[0], position[1])
            if hasattr(self, 'placeholder_items'):
                for item_over in self.placeholder_items:
                    if hasattr(item_over, '_ItemCell__visible_in_states'):
                        visible_in_states = item_over.__visible_in_states
                        if visible_in_states != None:
                            if visible_in_states[0].get_type() == self.__type:
                                clip_mask = None
                                if state in visible_in_states[1]:
                                    item_over.set_visible(True)
                                    clip = False
                                    for def_state in self.__definition.states:
                                        if def_state.name == state.name:
                                            if def_state.clip:
                                                clip = True
                                            break

                                    if clip:
                                        if clip_mask == None:
                                            clip_mask = self.__stage.load_item_image(self.__type, self.__state, self.__flip_h, '$x')
                                            clip_pos = (self.get_left(), self.get_top())
                                        item_over.set_clip_mask(clip_mask, clip_pos)
                                    else:
                                        item_over.set_clip_mask(None, None)
                                else:
                                    item_over.set_visible(False)

            self.fire_event(ItemEvent.STATE_CHANGED, ItemEventArgsStateChanged(previous_state))
        return

    def get_position(self):
        return self.__position

    def set_position(self, row, col):
        (left, top) = self.__from_grid_position(row, col)
        self.set_lefttop(left, top)
        self.__position = (row, col)
        return

    def get_mask(self, mask_suffix):
        return self.__stage.load_item_mask(self.__type, self.__state, self.__flip_h, mask_suffix)

    def get_at_mask(self, x, y, mask_suffix):
        mask = self.__stage.load_item_mask(self.__type, self.__state, False, mask_suffix)
        if mask == None:
            return (255, 255, 255, 255)
        else:
            if self.__flip_h:
                mask_x = self.get_width() - (x - self.get_left())
            else:
                mask_x = x - self.get_left()
            mask_y = y - self.get_top()
            if mask_x < 0 or mask_y < 0 or mask_x >= mask.get_width() or mask_y >= mask.get_height():
                return (255, 255, 255, 255)
            else:
                return mask.get_at((mask_x, mask_y))
        return

    def get_center(self):
        return self.__center

    def set_to_place_holder(self, container_item, place_holder, below=False, only_visible_in_states=None):
        (row, col) = container_item.get_position()
        (ph_row, ph_col) = container_item.get_place_holder_rowcol(place_holder)
        drow = ph_row - row
        dcol = ph_col - col
        self.__load_center()
        (cell_width, cell_height) = self.__stage.get_grid_cell_size()
        self.__center = (self.__center[0] - place_holder.x + _div((dcol - drow) * cell_width , 2),
         self.__center[1] - place_holder.y + _div((dcol + drow) * cell_height , 2))
        self.set_position(ph_row, ph_col)
        if container_item.__flip_h:
            self.__image = self.__stage.load_item_image(self.__type, self.__state, True)
            self.set_image(self.__image, None)
            self.__flip_h = True
        if only_visible_in_states != None:
            self.__visible_in_states = (container_item, only_visible_in_states)
            self.set_visible(self.get_state() in only_visible_in_states)
        elif hasattr(self, '_ItemCell__visible_in_states'):
            self.__visible_in_states = None
        if hasattr(self, '_ItemCell__placeholder_container'):
            self.placeholder_container.unregister_placeholder_item(self)
        self.placeholder_container = container_item
        container_item.register_placeholder_item(self)
        return

    def get_place_holder_rowcol(self, place_holder):
        multiplier = self.__stage.get_grid_multiplier()
        return self.__stage.get_rowcol(self.get_left() + (self.__center[0] + place_holder.x) * multiplier, self.get_top() + (self.__center[1] + place_holder.y) * multiplier)

    def get_place_holder_xy(self, place_holder):
        multiplier = self.__stage.get_grid_multiplier()
        return (self.get_left() + (self.__center[0] + place_holder.x) * multiplier,
         self.get_top() + (self.__center[1] + place_holder.y) * multiplier)

    def get_flip_h(self):
        return self.__flip_h

    def set_flip_h(self, value):
        if self.__flip_h != value:
            position = self.get_position()
            self.__image = self.__stage.load_item_image(self.__type, self.__state, value)
            self.set_image(self.__image, None)
            self.__definition = self.__definition.flip_h(self)
            self.__flip_h = value
            self.__load_center()
            if position != None:
                self.set_position(position[0], position[1])
        return

    def get_definition(self):
        return self.__definition

    def reload_definition(self):
        type = self.__type
        self.__type = '???'
        self.set_type(type)
        return

    def collision_test(self, row, col, only_item_layer):
        layer = self.get_layer()
        if layer != None:
            if only_item_layer:
                return self.__collide_test_layer(row, col, layer)
            else:
                stage = layer.get_stage()
                if stage != None:
                    for layer in stage.layers:
                        item = self.__collide_test_layer(row, col, self.__layer)
                        if item != None:
                            return item

        return

    def register_placeholder_item(self, item):
        if not hasattr(self, 'placeholder_items'):
            self.placeholder_items = [
             item]
        else:
            self.placeholder_items.append(item)
        return

    def unregister_placeholder_item(self, item):
        if hasattr(self, 'placeholder_items'):
            self.placeholder_items.remove(item)
        return

    def __load_center(self):
        if self.__state.suffix == '':
            self.__center = self.__definition.center
        else:
            state_center = None
            for state in self.__definition.states:
                if state.name == self.__state.name:
                    state_center = state.center

            if state_center == None:
                raise Exception("State '" + self.__state.name + "' is not defined for item '" + self.__type + "'")
            else:
                self.__center = state_center
        if self.__flip_h:
            self.__center = (
             _div(self.get_width() , self.__stage.get_grid_multiplier()) - self.__center[0], self.__center[1])
        return

    def __collide_test_layer(self, row, col, layer):
        size = self.__definition.size
        for item in layer.items:
            if isinstance(item, ItemCell) and item != self:
                item_pos = item.get_position()
                if item_pos != None:
                    if item_pos[0] < row + size[0] and item_pos[1] < col + size[1]:
                        item_def = item.get_definition()
                        item_size = item_def.size
                        if item_pos[0] + item_size[0] > row and item_pos[1] + item_size[1] > col:
                            return item

        return

    def __from_grid_position(self, row, col):
        if self.__definition == None:
            return (
             row, col)
        else:
            stage = self.__stage
            (origin, cell_width, cell_height, multiplier) = stage.get_grid_definition()
            center = self.__center
            left = int((origin[0] + _div((col - row) * cell_width , 2) - center[0]) * multiplier)
            top = int((origin[1] + _div((col + row) * cell_height , 2) - center[1] + _div(cell_height , 2)) * multiplier)
            return (
             left, top)
        return

    def __to_grid_position(self, left, top):
        stage = self.__stage
        (origin, cell_width, cell_height, multiplier) = stage.get_grid_definition()
        center = self.__center
        d1 = _div((_div(left , multiplier) - origin[0] + center[0]) , (_div(cell_width , 2)))
        d2 = _div((_div(top , multiplier) - origin[1] + center[1] - _div(cell_height , 2)) , (_div(cell_height , 2)))
        col = _div((d1 + d2) , 2)
        row = col - d1
        return (
         row, col)


class ItemMask(Item):

    def __init__(self, left, top, mask):
        if isinstance(mask, pygame.Surface):
            width = mask.get_width()
            height = mask.get_height()
        elif isinstance(mask, assets.Image):
            width = mask.get_width()
            height = mask.get_height()
        else:
            width = mask[0]
            height = mask[1]
            mask = None
        Item.__init__(self, left, top, width, height)
        self.mask = mask
        self.draw_function = self.__draw_item
        return

    def is_over(self, x, y, ignore_clip=False):
        bounds = self.get_bounds()
        if bounds.collidepoint(x, y):
            if self.mask == None:
                return True
            else:
                try:
                    c = self.mask.get_at((x - self.get_left(), y - self.get_top()))
                    if c[0] != 255 or c[1] != 255 or c[2] != 255:
                        return True
                except Exception:
                    return False

        return False

    def update(self, frame_delay):
        return

    def get_at(self, x, y):
        return self.mask.get_at((x, y))

    def __draw_item(self, item, target):
        return


class ItemText(Item):
    VALID_UNICODE_CHARS = ['á', 'é', 'í', 'ó', 'ú', 'Á', 'É', 'Í', 'Ó', 'Ú', 'ñ', 'Ñ']

    def __init__(self, left, top, font, line_height, text, color=(255, 255, 255), background=None, width=-1, height=-1, h_align=1, v_align=1, additional_fonts=[]):
        self.__width = width
        self.__height = height
        self.__h_align = h_align
        self.__v_align = v_align
        self.__font = font
        self.__additional_fonts = additional_fonts
        if line_height == 0:
            self.__line_height = max(1, font.get_linesize())
        else:
            self.__line_height = line_height
        self.__color = color
        self.__background = background
        self.__alpha = 255
        self.__break_text_into = None
        self.__rollover_color = None
        self.__edit_mode = None
        self.__max_chars = -1
        Item.__init__(self, left, top, 0, 0)
        self.__text = text
        self.area = None
        self.__update_text()
        if self.__width != -1:
            self.set_width(self.__width)
        else:
            self.__dx = 0
        if self.__height != -1:
            self.set_height(self.__height)
        else:
            self.__dy = 0
        self.draw_function = self.__draw_item
        return

    def set_editable(self, editable, key_pressed=None):
        if editable:
            if self.__edit_mode == None:
                self.__edit_mode = False
                self.__edit_key_pressed = key_pressed
                self.__update_text()
        else:
            self.__edit_mode = None
        return

    def get_alpha(self):
        return self.__alpha

    def set_alpha(self, alpha):
        self.__alpha = alpha
        self.__text_surface = set_surface_alpha(self.__source_surface, alpha)
        self.set_dirty()
        return

    def get_color(self):
        return self.__color

    def set_color(self, color):
        if self.__rollover_color != None and self.__rollover_color[1] != None:
            self.__rollover_color[1] = color
        elif self.__color != color:
            self.__color = color
            self.__mark_text_to_update()
        return

    def set_rollover_color(self, rollover_color, sound):
        if self.__rollover_color != None:
            old_color = self.__rollover_color[1]
            self.__rollover_color = None
            if old_color != None:
                self.__color = old_color
                self.__mark_text_to_update()
            self.remove_event_handler(ItemEvent.MOUSE_ENTER, self.__rollover_color_mouse_enter)
            self.remove_event_handler(ItemEvent.MOUSE_LEAVE, self.__rollover_color_mouse_leave)
        if rollover_color != None:
            self.__rollover_color = [
             rollover_color, None, sound]
            self.add_event_handler(ItemEvent.MOUSE_ENTER, self.__rollover_color_mouse_enter)
            self.add_event_handler(ItemEvent.MOUSE_LEAVE, self.__rollover_color_mouse_leave)
        return

    def get_background(self):
        return self.__background

    def set_background(self, background):
        if self.__background != background:
            self.__background = background
            self.__mark_text_to_update()
        return

    def set_dimensions(self, width, height):
        self.__width = width
        self.__height = height
        if self.__width != -1:
            self.set_width(self.__width)
        else:
            self.__dx = 0
        if self.__height != -1:
            self.set_height(self.__height)
        else:
            self.__dy = 0
        self.__update_text()
        return

    def get_text(self):
        return self.__text

    def set_text(self, text):
        if self.__text != text:
            self.__text = text
            self.__update_text()
        return

    def break_text_into(self, item_text):
        self.__break_text_into = item_text
        return

    def update(self, frame_delay):
        if self.__text_surface == None:
            self.__render_text()
        return Item.update(self, frame_delay)

    def hit_test(self, x, y):
        adjust = _div(self.__font.get_linesize() , 4)
        editable = self.__edit_mode != None
        return hittest_text(self.__text, x - self.get_left() + adjust, y - self.get_top(), self.__font, self.__additional_fonts, self.__line_height, self.get_width(), self.get_height(), True, self.__h_align, editable, self.__break_text_into)

    def set_edit_on_click(self, item=None, click_callback=None):
        if item == None:
            item = self
        self.__edit_click_callback = click_callback
        item.add_event_handler(ItemEvent.CLICK, self.__begin_edit_on_click)
        return

    def set_watermark_text(self, text, color=(155, 125, 112)):
        self.__watermark_text = (
         text, color)
        return

    def set_max_chars(self, max_chars):
        self.__max_chars = max_chars
        return

    def begin_edit(self, x=1000, y=1000):
        if self.__edit_mode == None:
            raise Exception('The ItemText is not editable.')
        index = self.hit_test(x, y)
        stage = self.get_stage()
        if stage != None:
            if stage.get_focus() == self:
                stage.get_focus_data()[0] = index
                stage.get_focus_data()[1] = True
                self.__start_cursor_timer()
            else:
                stage.set_focus(self, index)
            self.__update_text()
        return

    def end_edit(self):
        stage = self.get_stage()
        if stage != None:
            if stage.get_focus() == self:
                stage.set_focus(None)
                self.__update_text()
        return

    def on_got_focus(self, set_focus_data):
        if IS_ANDROID:
            pygame.key.start_text_input()   # abre el teclado en pantalla
        self.__edit_mode = True
        self.__start_cursor_timer()
        index = set_focus_data
        return [index, True]

    def on_lost_focus(self, stage, data):
        if IS_ANDROID:
            pygame.key.stop_text_input()
        timer_key = (
         self, 'key_repeat')
        stage.stop_timer(timer_key)
        self.__edit_mode = False
        self.__update_text()
        return

    def handle_event_focused(self, event, data):
        if event.type == KEYDOWN:
            key = event.key
            str = event.unicode
            stage = self.get_stage()
            if stage != None:
                timer_key = (
                 self, 'key_repeat')
                if self.__can_repeat(str):
                    stage.start_timer(timer_key, 600, self.__handle_key_repeat, (key, str, data, True), True, False)
                if self.__handle_key(key, str, data):
                    return True
        elif event.type == KEYUP:
            timer_key = (
             self, 'key_repeat')
            stage = self.get_stage()
            if stage != None:
                stage.stop_timer(timer_key)
        return False

    def __can_repeat(self, str):
        if str != '' and ord(str) < 255 and str in ('á',
                                                                                  'é',
                                                                                  'í',
                                                                                  'ó',
                                                                                  'ú',
                                                                                  'Á',
                                                                                  'É',
                                                                                  'Í',
                                                                                  'Ó',
                                                                                  'Ú'):
            return False
        else:
            return True
        return

    def __handle_key_repeat(self, key, args):
        timer_key = (
         self, 'key_repeat')
        if args[3]:
            stage = self.get_stage()
            if stage != None:
                stage.stop_timer(timer_key)
                stage.start_timer(timer_key, 50, self.__handle_key_repeat, (args[0], args[1], args[2], False), True, False)
        self.__handle_key(args[0], args[1], args[2])
        return

    def __handle_key(self, key, str, data):
        updated = False
        handled = False
        old_cursor = data[0]
        old_text = self.__text
        if key == K_RETURN:
            self.end_edit()
            handled = True
        elif key == K_BACKSPACE:
            if data[0] > 0:
                self.__text = self.__text[:data[0] - 1] + self.__text[data[0]:]
                data[0] -= 1
                updated = True
            handled = True
        elif key == K_DELETE:
            if data[0] < len(self.__text):
                self.__text = self.__text[:data[0]] + self.__text[data[0] + 1:]
                updated = True
            handled = True
        elif key == K_RIGHT:
            if data[0] < len(self.__text):
                data[0] += 1
                updated = True
            handled = True
        elif key == K_LEFT:
            if data[0] > 0:
                data[0] -= 1
                updated = True
            handled = True
        elif key == K_HOME or key == K_UP:
            if data[0] > 0:
                data[0] = 0
                updated = True
            handled = True
        elif key == K_END or key == K_DOWN:
            if data[0] < len(self.__text):
                data[0] = len(self.__text)
                updated = True
            handled = True
        elif str != '' and (ord(str) > 31 and ord(str) < 126 or ord(str) < 255 and str in self.VALID_UNICODE_CHARS) and (len(self.__text) < self.__max_chars or self.__max_chars == -1):
            self.__text = self.__text[:data[0]] + str + self.__text[data[0]:]
            data[0] += 1
            updated = True
            handled = True
        if updated:
            data[1] = True
            if not self.__update_text():
                self.__text = old_text
                data[0] = old_cursor
                self.__update_text()
            else:
                self.__start_cursor_timer()
        if hasattr(self, '_ItemText__edit_key_pressed') and self.__edit_key_pressed != None:
            self.__edit_key_pressed(key)
        return handled

    def __start_cursor_timer(self):
        stage = self.get_stage()
        if stage != None:
            key = (
             self, 'text_cursor')
            stage.start_timer(key, 500, self.__update_cursor_timer, stage)
        return

    def __begin_edit_on_click(self, item, args):
        stage = item.get_stage()
        if stage != None:
            focused_item = stage.get_focus()
        else:
            focused_item = None
        if focused_item == self:
            self.begin_edit(args.x, args.y)
        else:
            self.begin_edit()
        if self.__edit_click_callback != None:
            self.__edit_click_callback(item, args)
        return

    def __update_text(self):
        text_fit_in_box = self.__render_text()
        self.set_dirty()
        return text_fit_in_box

    def __render_text(self):
        cursor_index = -1
        editable = False
        if self.__edit_mode != None:
            editable = True
            stage = self.get_stage()
            if stage != None:
                if self.__edit_mode:
                    focus_data = stage.get_focus_data()
                    if focus_data[1]:
                        cursor_index = focus_data[0]
        text = self.__text
        color = self.__color
        if text == '':
            if hasattr(self, '_ItemText__watermark_text'):
                (text, color) = self.__watermark_text
        (text_surface, text_fit) = render_text(text, self.__font, self.__additional_fonts, self.__line_height, self.__width, self.__height, True, color, self.__background, self.__h_align, self.__break_text_into, cursor_index, editable)
        self.__text_surface = text_surface
        self.__source_surface = text_surface
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        if self.__width == -1:
            self.set_width(text_width)
        elif self.__h_align == 1:
            self.__dx = 0
        elif self.__h_align == 2:
            self.__dx = _div((self.__width - text_width) , 2)
        elif self.__h_align == 3:
            self.__dx = self.__width - text_width
        if self.__height == -1:
            self.set_height(text_height)
        elif self.__v_align == 1:
            self.__dy = 0
        elif self.__v_align == 2:
            self.__dy = _div((self.__height - text_height) , 2)
        elif self.__v_align == 3:
            self.__dy = self.__height - text_height
        if self.__alpha != 255:
            self.__text_surface = set_surface_alpha(self.__source_surface, self.__alpha)
        return text_fit

    def __mark_text_to_update(self):
        self.__text_surface = None
        self.set_dirty()
        return

    def __draw_item(self, item, target):
        target.blit_surface(self.__text_surface, (self.get_left() + self.__dx, self.get_top() + self.__dy))
        return

    def __rollover_color_mouse_enter(self, item, args):
        if self.__rollover_color != None:
            self.__rollover_color[1] = self.__color
            self.__color = self.__rollover_color[0]
            self.__mark_text_to_update()
            rollover_sound = self.__rollover_color[2]
            if rollover_sound != None:
                layer = self.get_layer()
                if layer != None:
                    stage = layer.get_stage()
                    if stage != None:
                        stage.render()
                        rollover_sound.stop()
                        rollover_sound.play()
        return

    def __rollover_color_mouse_leave(self, item, args):
        if self.__rollover_color != None:
            old_color = self.__rollover_color[1]
            if old_color != None:
                self.__color = old_color
                self.__mark_text_to_update()
                self.__rollover_color[1] = None
        return

    def __update_cursor_timer(self, key, data):
        stage = data
        focused_item = stage.get_focus()
        if focused_item != self:
            stage.stop_timer(key)
        else:
            focus_data = stage.get_focus_data()
            focus_data[1] = not focus_data[1]
            self.__update_text()
        return


class ItemRect(Item):

    def __init__(self, left, top, width, height, font=None, line_height=0, text='', color=(0, 0, 0), background=(0, 0, 0), border=None, text_h_align=1, additional_fonts=[]):
        self.__font = font
        self.__additional_fonts = additional_fonts
        if line_height == 0 and font != None:
            self.__line_height = font.get_linesize()
        else:
            self.__line_height = line_height
        self.__color = color
        self.__background = background
        self.__border = border
        self.__text_h_align = text_h_align
        Item.__init__(self, left, top, width, height)
        self.__text = text
        self.__update_text()
        self.draw_function = self.__draw_item
        return

    def get_color(self):
        return self.__color

    def set_color(self, color):
        if self.__color != color:
            self.__color = color
            self.__mark_text_to_update()
        return

    def get_background(self):
        return self.__background

    def set_background(self, background):
        if self.__background != background:
            self.__background = background
            self.__mark_text_to_update()
        return

    def get_font(self):
        return self.__font

    def set_font(self, font):
        if self.__font != font:
            self.__font = font
            self.__update_text()
        return

    def get_text(self):
        return self.__text

    def set_text(self, text):
        if self.__text != text:
            self.__text = text
            self.__update_text()
        return

    def update(self, frame_delay):
        if self.__text_surface == None and self.__text != '':
            self.__render_text()
        return Item.update(self, frame_delay)

    def __update_text(self):
        self.__render_text()
        self.set_dirty()
        return

    def is_over(self, x, y, ignore_clip=False):
        bounds = self.get_bounds()
        if self.__background != None:
            return bounds[0] <= x and x < bounds[0] + bounds[2] and bounds[1] <= y and y < bounds[1] + bounds[3]
        else:
            return bounds[0] == x or x == bounds[0] + bounds[2] - 1 and bounds[1] == y or y == bounds[1] + bounds[3] - 1
        return

    def __render_text(self):
        width = self.get_width()
        height = self.get_height()
        if self.__text == '':
            self.__text_surface = None
            self.__text_width = width
            self.__text_height = height
            text_fit = True
        else:
            if self.__background == None or len(self.__background) >= 4 and self.__background[3] != 255:
                text_background = None
            else:
                text_background = self.__background
            (self.__text_surface, text_fit) = render_text(self.__text, self.__font, self.__additional_fonts, self.__line_height, width, height, True, self.__color, text_background, self.__text_h_align, None)
            self.__text_width = width
            self.__text_height = height
        self.set_dirty()
        return text_fit

    def __draw_item(self, item, target):
        draw_rect = item.get_bounds()
        width = draw_rect[2]
        height = draw_rect[3]
        if self.__text_width != width or self.__text_height != height:
            self.__update_text()
        if self.__background != None:
            target.fill(self.__background, draw_rect)
        if self.__text_surface != None:
            text_x = draw_rect.left + _div((draw_rect.width - self.__text_surface.get_width()) , 2)
            text_y = draw_rect.top + _div((draw_rect.height - self.__text_surface.get_height()) , 2)
            target.blit_surface(self.__text_surface, (text_x, text_y))
        if self.__border != None:
            target.draw_rect(self.__border, draw_rect)
        return

    def __mark_text_to_update(self):
        self.__text_surface = None
        self.set_dirty()
        return


class ItemObject(ItemImage):

    def __init__(self, left, top, image, test_collision, normal_deceleration=None, area=None):
        ItemImage.__init__(self, left, top, image, area)
        self.__prev_velocity = (0.0, 0.0)
        self.__normal_deceleration = normal_deceleration
        self.__test_collision = test_collision
        self.__nokey_move = None
        self.__key_moves = []
        return

    def start_move_vel(self, vel_x, vel_y, key_event=None):
        self.__start_move((0, vel_x, vel_y), key_event)
        return

    def start_move_accel(self, accel_x, accel_y, max_vel_x=9999, max_vel_y=9999, key_event=None):
        self.__start_move((1, accel_x, accel_y, max_vel_x, max_vel_y), key_event)
        return

    def start_move_dynvel(self, vel_func, key_event=None):
        self.__start_move((2, vel_func), key_event)
        return

    def stop_move(self, key_event=None):
        if key_event == None:
            self.__nokey_move = None
        else:
            k = 0
            while k < len(self.__key_moves):
                if self.__key_moves[k][0] == key_event.key:
                    del self.__key_moves[k]
                else:
                    k += 1

        self.set_dirty()
        return

    def update(self, frame_delay):
        vel_x = 0
        vel_y = 0
        n = 0
        if self.__nokey_move != None:
            (vel_x, vel_y) = self.__do_move(self.__nokey_move, frame_delay)
            n += 1
        for key_move in self.__key_moves:
            (move_vel_x, move_vel_y) = self.__do_move(key_move[1], frame_delay)
            vel_x += move_vel_x
            vel_y += move_vel_y
            n += 1

        if n == 0:
            if self.__normal_deceleration != None:
                if self.__prev_velocity[0] >= 0:
                    vel_x = max(0, self.__prev_velocity[0] + _div(float(self.__normal_deceleration[0] * frame_delay) , 1000))
                else:
                    vel_x = min(0, self.__prev_velocity[0] - _div(float(self.__normal_deceleration[0] * frame_delay) , 1000))
                if self.__prev_velocity[1] >= 0:
                    vel_y = max(0, self.__prev_velocity[1] + _div(float(self.__normal_deceleration[1] * frame_delay) , 1000))
                else:
                    vel_y = min(0, self.__prev_velocity[1] - _div(float(self.__normal_deceleration[1] * frame_delay) , 1000))
        else:
            vel_x = _div(vel_x, n)
            vel_y = _div(vel_y, n)
        new_left = self.get_left() + vel_x * frame_delay
        new_top = self.get_top() + vel_y * frame_delay
        if self.__test_collision == None or not self.__test_collision(self, new_left, new_top):
            self.set_lefttop(new_left, new_top)
        else:
            vel_x = 0
            vel_y = 0
            self.__nokey_move = None
            self.__key_moves = []
        rect = ItemImage.update(self, frame_delay)
        if vel_x != 0 or vel_y != 0 or self.__nokey_move != None or len(self.__key_moves) > 0:
            self.set_dirty()
        self.__prev_velocity = (
         vel_x, vel_y)
        return rect

    def __start_move(self, move_tuple, key_event):
        if key_event == None:
            self.__nokey_move = move_tuple
        else:
            for key_move in self.__key_moves:
                if key_move[0] == key_event.key:
                    self.__key_moves.remove(key_move)

            self.__key_moves.append((key_event.key, move_tuple))
        self.set_dirty()
        return

    def __do_move(self, move_data, frame_delay):
        if move_data[0] == 0:
            return (
             move_data[1], move_data[2])
        elif move_data[0] == 1:
            vel_x = self.__prev_velocity[0] + _div(float(move_data[1] * frame_delay) , 1000)
            vel_y = self.__prev_velocity[1] + _div(float(move_data[2] * frame_delay) , 1000)
            if move_data[1] >= 0:
                if vel_x > move_data[3]:
                    vel_x = move_data[3]
            elif vel_x < move_data[3]:
                vel_x = move_data[3]
            if move_data[2] >= 0:
                if vel_y > move_data[4]:
                    vel_y = move_data[4]
            elif vel_y < move_data[4]:
                vel_y = move_data[4]
            return (vel_x, vel_y)
        else:
            return move_data[1](frame_delay)
        return


def render_text(text, font, additional_fonts, line_height, max_width, max_height, antialias, color, background, h_align, break_text_into, cursor_index=-1, editable=False):
    if max_width == -1:
        max_line_width = sys.maxsize
    else:
        max_line_width = max_width
        if editable:
            max_line_width -= 2
    (lines, remaining_lines, break_color, break_font) = wrap_text_in_lines(text, False, color, font, line_height, additional_fonts, max_line_width, max_height, break_text_into)
    line_surfs = []
    width = 0
    if background == None or len(background) >= 4 and background[3] != 255:
        text_background = None
    else:
        text_background = background
    height = 0
    line_count = len(lines)
    for i in range(line_count):
        line = lines[i]
        part_surfs = []
        line_surfs_width = 0
        line_surfs_height = 0
        for line_part in line:
            part_font_data = line_part[1]
            if text_background == None:
                part_surf = part_font_data[0].render(line_part[2], antialias, line_part[0])
            else:
                part_surf = part_font_data[0].render(line_part[2], antialias, line_part[0], text_background)
            line_surfs_width += part_surf.get_width()
            part_surfs.append((part_surf, part_font_data))
            if i < line_count - 1:
                part_height = part_font_data[1]
            else:
                part_height = max(font.get_linesize(), part_font_data[1])
            if part_height > line_surfs_height:
                line_surfs_height = part_height

        line_surfs.append((line_surfs_width, line_surfs_height, part_surfs))
        if line_surfs_width > width:
            width = line_surfs_width
        height += line_surfs_height

    if cursor_index != -1:
        if height == 0:
            height = line_height
        cursor_text_data = wrap_text_in_lines(text, True, color, font, line_height, additional_fonts, max_line_width, max_height, break_text_into)
        draw_cursor(cursor_index, text, cursor_text_data[0], line_surfs, width, line_height, font)
        extra_width = 2
    elif editable:
        extra_width = 2
    else:
        extra_width = 0
    surface = pygame.Surface((width + extra_width, height), pygame.SRCALPHA, 32)
    if background == None:
        surface.fill((0, 0, 0, 0))
    else:
        surface.fill(background)
    line_y = 0
    for i in range(len(line_surfs)):
        if h_align == 1:
            line_x = 0
        elif h_align == 2:
            line_x = max(0, _div((width - line_surfs[i][0]) , 2))
        elif h_align == 3:
            line_x = max(0, width - line_surfs[i][0])
        parts_height = line_surfs[i][1]
        line_part_surfs = line_surfs[i][2]
        max_ascent = -1
        for part_surf_data in line_part_surfs:
            part_surf = part_surf_data[0]
            part_height = part_surf_data[1][1]
            y_adjust = part_surf_data[1][2]
            if part_height >= parts_height:
                surface.blit(part_surf, (line_x, line_y + y_adjust))
            else:
                if max_ascent == -1:
                    for part_surf_data2 in line_part_surfs:
                        ascent = part_surf_data2[1][0].get_ascent()
                        if ascent > max_ascent:
                            max_ascent = ascent
                margin = max_ascent - part_surf_data[1][0].get_ascent()
                surface.blit(part_surf, (line_x, line_y + margin + y_adjust))
            line_x += part_surf.get_width()

        line_y += parts_height

    if break_text_into != None:
        k = 0
        while k < len(remaining_lines):
            line = remaining_lines[k]
            only_spaces = True
            for c in line:
                if c != ' ' and c != '\r' and c != '\t':
                    only_spaces = False
                    break

            if only_spaces:
                k += 1
            else:
                break

        if k > 0:
            remaining_lines = remaining_lines[k:]
        remaining_text = ('\n').join(remaining_lines)
        if break_font[0] != font and break_font[1] != None:
            remaining_text = '&#f:' + break_font[1] + '!' + remaining_text
        if break_color != color:
            remaining_text = '&#c' + (',').join(map(str, break_color)) + '!' + remaining_text
        break_text_into.set_text(remaining_text)
    return (surface, len(remaining_lines) == 0)


def draw_cursor(cursor_index, text, lines, line_surfs, width, line_height, font):
    line_index = 0
    text_index = 0
    while line_index < len(lines):
        line = lines[line_index]
        part_index = 0
        while part_index < len(line):
            part = line[part_index]
            part_text = part[2]
            if cursor_index >= text_index and cursor_index < text_index + len(part_text):
                part_surf = line_surfs[line_index][2][part_index][0]
                char_index = cursor_index - text_index
                part_font = part[1][0]
                x = part_font.size(part_text[0:char_index])[0]
                draw_cursor_in_surface(part_surf, x)
                return
            else:
                text_index += len(part_text)
            part_index += 1

        line_index += 1

    line_index = len(lines) - 1
    if line_index < 0:
        new_surf = pygame.Surface((2, line_height), pygame.SRCALPHA, 32)
        draw_cursor_in_surface(new_surf, 0)
        line_part_surfs = [(new_surf, (font, line_height, 0))]
        line_surfs.append((2, line_height, line_part_surfs))
    else:
        line = lines[line_index]
        part_index = len(line) - 1
        if part_index >= 0:
            part = line[part_index]
            line_surfs_data = line_surfs[line_index]
            line_part_surfs = line_surfs_data[2]
            part_surf_data = line_part_surfs[part_index]
            part_surf = part_surf_data[0]
            (width, height) = part_surf.get_size()
            new_surf = pygame.Surface((width + 2, height), pygame.SRCALPHA, 32)
            new_surf.blit(part_surf, (0, 0))
            if len(part_surf_data) != 2:
                raise Exception('Invalid surface part data, excepted data with length 2. Fix the code below to copy all the data if the size changed.')
            line_part_surfs[part_index] = (
             new_surf, part_surf_data[1])
            draw_cursor_in_surface(new_surf, width)
    return


def draw_cursor_in_surface(surf, x):
    surf.fill((0, 0, 0), (x, 1, 2, surf.get_height() - 2))
    return


color = None   # en Python 2 era un global que venía de "from pygame.locals import *" (solo se usa para medir)


def hittest_text(text, x, y, font, additional_fonts, line_height, width, height, antialias, h_align, editable=False, break_text_into=None):
    max_line_width = width
    if editable:
        max_line_width -= 2
    result = wrap_text_in_lines(text, False, color, font, line_height, additional_fonts, max_line_width, height, break_text_into)
    lines = result[0]
    line_y = 0
    line_index = 0
    index = 0
    while line_index < len(lines) - 1 and line_y + line_height < y:
        for line_part in lines[line_index]:
            index += len(line_part[2])

        if index < len(text) and text[index] == '\n':
            index += 1
        line_y += line_height
        line_index += 1

    if line_index < len(lines):
        part_index = 0
        line = lines[line_index]
        line_x = 0
        if h_align != 1:
            line_width = 0
            for i in range(len(line)):
                part = line[i]
                part_font = part[1][0]
                part_text = part[2]
                line_width += part_font.size(part_text)[0]

            if h_align == 2:
                line_x = _div((width - line_width) , 2)
            elif h_align == 3:
                line_x = width - line_width
        found = False
        while part_index < len(line) and not found:
            part = line[part_index]
            char_index = 0
            part_font = part[1][0]
            part_text = part[2]
            char_width = 0
            while char_index < len(part_text):
                char_index += 1
                char_width = part_font.size(part_text[0:char_index])[0]
                if line_x + char_width < x:
                    index += 1
                else:
                    found = True
                    break

            line_x += char_width
            part_index += 1

        if not found and index > 0 and line_index + 1 < len(lines):
            index -= 1
    return index


def wrap_text_in_lines(text, hit_test, color, font, line_height, additional_fonts, max_line_width, max_height, break_text_into):
    lines = []
    remaining_lines = []
    current_height = [
     0]
    current_color = [color]
    current_font = [font, line_height, 0, None]
    for line in text.splitlines():
        wrap_line(line, hit_test, font, line_height, additional_fonts, lines, current_height, max_line_width, max_height, remaining_lines, color, current_color, current_font, False, break_text_into)

    return (lines, remaining_lines, current_color[0], (current_font[0], current_font[1]))


def wrap_line(line, hit_test, font, line_height, additional_fonts, lines, current_height, max_width, max_height, remaining_lines, default_color, current_color, current_font, add_ellipsis, break_text_into):
    if max_height != -1 and current_height[0] + line_height > max_height:
        remaining_lines.append(line)
    else:
        line_width = current_font[0].size(line)[0]
        if line_width <= max_width and line.find('&#') == -1:
            lines.append([(current_color[0], current_font[:], line)])
            current_height[0] += current_font[1]
        else:
            start = 0
            new_line = ''
            empty_line = True
            line_width = 0
            space_width = current_font[0].size(' ')[0]
            line_parts = []
            line_parts_height = 0
            while start < len(line):
                next_control = line.find('&#', start)
                if next_control == -1:
                    line_part = line[start:]
                    next_word = ''
                else:
                    line_part = line[start:next_control]
                    next_control_end = line.find('!', next_control)
                    if next_control_end == -1:
                        next_control_end = len(line)
                    k = line.find(' ', next_control_end + 1)
                    if k == -1:
                        next_word = line[next_control_end + 1:]
                    else:
                        next_word = line[next_control_end + 1:k]
                while next_word.startswith('&#'):
                    control_end = next_word.find('!')
                    if control_end == -1:
                        break
                    else:
                        next_word = next_word[control_end + 1:]

                if line_part != '':
                    words = line_part.split(' ')
                    i = 0
                    new_line = ''
                    for i in range(len(words)):
                        add_word = words[i]
                        add_space = True
                        while add_word != None:
                            word = add_word
                            add_word = None
                            word_width = current_font[0].size(word)[0]
                            if i == len(words) - 1:
                                kk = next_word.find('&#')
                                if kk == -1:
                                    next_word_text = next_word
                                else:
                                    next_word_text = next_word[0:kk]
                                extra_width = current_font[0].size(next_word_text)[0]
                            else:
                                extra_width = 0
                            if word_width > max_width:
                                if add_ellipsis:
                                    end_width = current_font[0].size('...')[0]
                                    if end_width > max_width:
                                        word = ''
                                        word_width = 0
                                    else:
                                        k = len(word)
                                        while k >= 0 and word_width + end_width > max_width:
                                            k -= 1
                                            word_width = current_font[0].size(word[0:k])[0]

                                        if hit_test:
                                            word = word[:k]
                                        else:
                                            word = word[:k] + '...'
                                        word_width += end_width
                                else:
                                    is_last_line = current_height[0] + current_font[1] * 2 >= max_height
                                    if not is_last_line or break_text_into != None:
                                        end_width = current_font[0].size('-')[0]
                                        if end_width > max_width:
                                            word = ''
                                            word_width = 0
                                        else:
                                            k = len(word)
                                            while k >= 0 and word_width + end_width > max_width:
                                                k -= 1
                                                word_width = current_font[0].size(word[0:k])[0]

                                            add_word = word[k:]
                                            if hit_test:
                                                word = word[:k]
                                            else:
                                                word = word[:k] + '-'
                                            word_width += end_width
                                    else:
                                        k = len(word)
                                        while k >= 0 and word_width > max_width:
                                            k -= 1
                                            word_width = current_font[0].size(word[0:k])[0]

                                        word = word[:k]
                            if empty_line and line_width + word_width + extra_width <= max_width:
                                new_line = word
                                line_width += word_width
                                empty_line = False
                            elif line_width + word_width + space_width + extra_width <= max_width:
                                new_line += ' ' + word
                                line_width += word_width + space_width
                            else:
                                if new_line != '':
                                    if word != '' and add_space:
                                        new_line += ' '
                                    line_parts.append((current_color[0], current_font[:], new_line))
                                    line_parts_height = max(line_parts_height, current_font[1])
                                if len(line_parts) > 0:
                                    lines.append(line_parts)
                                    current_height[0] += line_parts_height
                                line_parts = []
                                line_parts_height = 0
                                if word == '':
                                    new_line = ''
                                    line_width = 0
                                    empty_line = True
                                else:
                                    new_line = word
                                    line_width = word_width
                                if max_height != -1 and current_height[0] + line_height >= max_height:
                                    text = (' ').join(words[i:])
                                    if next_control != -1:
                                        text += line[next_control:]
                                    remaining_lines.append(text)
                                    return
                            add_space = False

                        i += 1

                if next_control == -1:
                    start = len(line)
                elif next_control_end >= next_control + 3:
                    c = line[next_control + 2]
                    if c == 'c' or c == 'f':
                        if new_line != '':
                            line_parts.append((current_color[0], current_font[:], new_line))
                            line_parts_height = max(line_parts_height, current_font[1])
                            new_line = ''
                            empty_line = True
                        if next_control + 3 == next_control_end:
                            if c == 'c':
                                current_color[0] = default_color
                            elif c == 'f':
                                current_font[0] = font
                                current_font[1] = line_height
                                current_font[2] = 0
                                current_font[3] = None
                        elif c == 'c':
                            rgb = line[next_control + 3:next_control_end].split(',')
                            current_color[0] = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
                        elif c == 'f':
                            font_name = line[next_control + 4:next_control_end]
                            font_selected = additional_fonts[font_name]
                            if len(font_selected) >= 3:
                                current_font[:] = [
                                 font_selected[0], font_selected[1], font_selected[2], font_name]
                            else:
                                current_font[:] = [
                                 font_selected[0], font_selected[1], 0, font_name, None]
                            if current_font[1] == 0:
                                current_font[1] = current_font[0].get_linesize()
                if next_control != -1:
                    start = next_control_end + 1

            if new_line != '':
                line_parts.append((current_color[0], current_font[:], new_line))
                line_parts_height = max(line_parts_height, current_font[1])
            if len(line_parts) > 0:
                lines.append(line_parts)
                current_height[0] += line_parts_height
    return


def set_surface_alpha(surface, alpha):
    surface = surface.copy()
    if surface.get_bitsize() < 32:
        surface.set_alpha(alpha)
    elif surface.get_width() != 0:
        alpha_matrix = pygame.surfarray.pixels_alpha(surface)
        mult_alpha = alpha_matrix * (_div(float(alpha) , 255))
        alpha_matrix[:] = mult_alpha.astype('b')
    return surface


class Layer():

    def __init__(self):
        self.items = []
        self.stage = None
        self.__visible = True
        self.__changed_handler = None
        self.custom_draw = CustomDraw()
        self.__several_rows_items = []
        self.__alpha = 255
        self.__alpha_buffer = None
        self.__alpha_blit = None
        self.__clip = None
        self.__drawn = False
        self.dirty_rects = []
        self.dirty_items = []
        self.dirty_layer = False
        return

    def contains(self, item):
        return item in self.items

    def empty(self):
        while len(self.items) > 0:
            self.remove(self.items[0])

        return

    def add(self, item, index=-1):
        layer = item.get_layer()
        if layer != None:
            layer.remove(item)
        item.set_layer(self)
        if index == -1:
            index = len(self.items)
            self.items.append(item)
        else:
            self.items.insert(index, item)
        item.set_dirty()
        if self.stage != None:
            self.stage.update_mouse()
        return

    def remove(self, item):
        if self.stage != None:
            focused_item = self.stage.get_focus()
        else:
            focused_item = None
        if item in self.items:
            if focused_item == item:
                self.stage.set_focus(None)
            self.items.remove(item)
            item.set_layer(None)
            if item.rect not in self.dirty_rects and item.rect.width != 0 and item.rect.height != 0:
                self.dirty_rects.append(item.rect)
                if self.__changed_handler != None:
                    self.__changed_handler(self.stage)
        if self.stage != None:
            self.stage.update_mouse()
        return

    def index_of(self, item):
        return self.items.index(item)

    def get_count(self):
        return len(self.items)

    def get_visible(self):
        return self.__visible

    def set_visible(self, visible):
        if self.__visible != visible:
            self.__visible = visible
            if self.stage != None:
                self.dirty_layer = True
        return

    def update(self, dirty_rects, frame_delay):
        dirty_rects_list = self.dirty_rects
        self.dirty_rects = []
        dirty_items_list = self.dirty_items
        self.dirty_items = []
        for rect in dirty_rects_list:
            k = rect.collidelist(dirty_rects)
            while k != -1:
                rect.union_ip(dirty_rects[k])
                del dirty_rects[k]
                k = rect.collidelist(dirty_rects)

            dirty_rects.append(rect)

        if self.dirty_layer:
            self.dirty_layer = False
            for item in self.items:
                dirty_rect = item.update(frame_delay)
                if self.__clip != None and dirty_rect != None:
                    dirty_rect = dirty_rect.clip(self.__clip)
                if dirty_rect != None and dirty_rect.width != 0 and dirty_rect.height != 0:
                    k = dirty_rect.collidelist(dirty_rects)
                    while k != -1:
                        dirty_rect.union_ip(dirty_rects[k])
                        del dirty_rects[k]
                        k = dirty_rect.collidelist(dirty_rects)

                    dirty_rects.append(dirty_rect)

        else:
            for item in dirty_items_list:
                dirty_rect = item.update(frame_delay)
                if self.__clip != None and dirty_rect != None:
                    dirty_rect = dirty_rect.clip(self.__clip)
                    if dirty_rect.width == 0 or dirty_rect.height == 0:
                        dirty_rect = None
                if dirty_rect != None:
                    k = dirty_rect.collidelist(dirty_rects)
                    while k != -1:
                        dirty_rect.union_ip(dirty_rects[k])
                        del dirty_rects[k]
                        k = dirty_rect.collidelist(dirty_rects)

                    dirty_rects.append(dirty_rect)

        if self.__alpha != 255:
            if len(dirty_rects_list) != 0 or len(dirty_items_list) != 0 or self.dirty_layer and self.__alpha_buffer == None:
                (self.__alpha_buffer, self.__alpha_bounds) = self.render_into_surface()
                self.__alpha_blit = set_surface_alpha(self.__alpha_buffer, self.__alpha)
        return

    def draw(self, surface, dirty_rects):
        if self.__clip != None and (self.__clip.width == 0 or self.__clip.height == 0):
            return
        if len(dirty_rects) > 0:
            surface_blit = surface.blit
            if self.__clip == None:
                set_clip = surface.set_clip
            else:
                self.__set_clip_surface = surface
                set_clip = self.__set_clip
            if self.__alpha_blit != None:
                alpha_bounds = self.__alpha_bounds
                set_clip(alpha_bounds)
                for dirty_rect in dirty_rects:
                    dirty_rect_clipped = dirty_rect.clip(alpha_bounds)
                    dirty_rect_adj = dirty_rect_clipped.move(-alpha_bounds.left, -alpha_bounds.top)
                    surface_blit(self.__alpha_blit, dirty_rect_clipped, dirty_rect_adj)

            else:
                self.custom_draw.surface = surface
                for dirty_rect in dirty_rects:
                    set_clip(dirty_rect)
                    for item in self.items:
                        rect = item.rect
                        if not rect.colliderect(dirty_rect) or not item.visible:
                            continue
                        draw_function = item.draw_function
                        if draw_function == None:
                            if item.area == None:
                                surface_blit(item.surface, rect)
                            else:
                                surface_blit(item.surface, rect, item.area)
                        else:
                            draw_function(item, self.custom_draw)

            self.__set_clip_surface = None
        if not self.__drawn:
            if len(self.items) > 0:
                self.__drawn = True
        return

    def add_dirty_item(self, item):
        if item not in self.dirty_items:
            self.dirty_items.append(item)
        if self.__changed_handler != None:
            self.__changed_handler(self.stage)
        return

    def get_alpha(self):
        return self.__alpha

    def set_alpha(self, alpha):
        if self.__alpha != alpha:
            self.__alpha = alpha
            if self.__alpha == 255:
                self.__alpha_buffer = None
                self.__alpha_blit = None
            elif self.__alpha_buffer != None:
                self.__alpha_blit = set_surface_alpha(self.__alpha_buffer, self.__alpha)
            self.set_dirty()
        return

    def get_stage(self):
        return self.stage

    def set_stage(self, stage):
        if stage == None:
            self.stage = None
            self.__changed_handler = None
        elif self.stage != None:
            raise Exception('The layer is already part of a stage')
        else:
            self.stage = stage
            self.__changed_handler = stage.get_changed_handler()
        return

    def get_bounds(self):
        layer_bounds = None
        for item in self.items:
            if item.get_visible():
                item_bounds = item.get_bounds()
                if layer_bounds == None:
                    layer_bounds = item_bounds
                else:
                    layer_bounds.union_ip(item_bounds)

        if layer_bounds == None:
            return Rect(0, 0, 0, 0)
        else:
            return layer_bounds
        return

    def set_dirty(self):
        self.dirty_layer = True
        return

    def get_clip(self):
        return self.__clip

    def set_clip(self, clip):
        if len(self.items) == 0 or not self.__drawn:
            self.dirty_layer = True
        elif clip != None and clip.height == 0 and self.__clip != None:
            clip = Rect(self.__clip.x, self.__clip.y, clip.width, 0)
        if self.__clip != clip and self.stage != None:
            (window_width, window_height) = self.stage.game.get_window_size()
            if clip == None:
                new_clip = Rect(0, 0, window_width, window_height)
            else:
                new_clip = clip
            if self.__clip == None:
                old_clip = Rect(0, 0, window_width, window_height)
            else:
                old_clip = self.__clip
            total_dirty_rect = old_clip.union(new_clip)
            if total_dirty_rect.width != 0 and total_dirty_rect.height != 0:
                if old_clip.left > total_dirty_rect.left:
                    dirty_rect = Rect(total_dirty_rect.left, total_dirty_rect.top, old_clip.left - total_dirty_rect.left, total_dirty_rect.height)
                    self.dirty_rects.append(dirty_rect)
                elif new_clip.left > total_dirty_rect.left:
                    dirty_rect = Rect(total_dirty_rect.left, total_dirty_rect.top, new_clip.left - total_dirty_rect.left, total_dirty_rect.height)
                    self.dirty_rects.append(dirty_rect)
                if old_clip.right < total_dirty_rect.right:
                    dirty_rect = Rect(old_clip.right, total_dirty_rect.top, total_dirty_rect.right - old_clip.right, total_dirty_rect.height)
                    self.dirty_rects.append(dirty_rect)
                elif new_clip.right < total_dirty_rect.right:
                    dirty_rect = Rect(new_clip.right, total_dirty_rect.top, total_dirty_rect.right - new_clip.right, total_dirty_rect.height)
                    self.dirty_rects.append(dirty_rect)
                if old_clip.top > total_dirty_rect.top:
                    dirty_rect = Rect(old_clip.left, total_dirty_rect.top, old_clip.width, old_clip.top - total_dirty_rect.top)
                    self.dirty_rects.append(dirty_rect)
                elif new_clip.top > total_dirty_rect.top:
                    dirty_rect = Rect(new_clip.left, total_dirty_rect.top, new_clip.width, new_clip.top - total_dirty_rect.top)
                    self.dirty_rects.append(dirty_rect)
                if old_clip.bottom < total_dirty_rect.bottom:
                    dirty_rect = Rect(old_clip.left, old_clip.bottom, old_clip.width, total_dirty_rect.bottom - old_clip.bottom)
                    self.dirty_rects.append(dirty_rect)
                elif new_clip.bottom < total_dirty_rect.bottom:
                    dirty_rect = Rect(new_clip.left, new_clip.bottom, new_clip.width, total_dirty_rect.bottom - new_clip.bottom)
                    self.dirty_rects.append(dirty_rect)
        self.__clip = clip
        return

    def is_inside_clip(self, x, y):
        if self.__clip == None:
            return True
        else:
            return self.__clip.collidepoint(x, y)
        return

    def render_into_surface(self):
        bounds = self.get_bounds()
        buffer = pygame.Surface(bounds.size, pygame.SRCALPHA, 32)
        surface_blit = buffer.blit
        custom_draw = CustomDrawDelta(buffer, -bounds.left, -bounds.top)
        custom_draw.surface = buffer
        for item in self.items:
            draw_function = item.draw_function
            if draw_function == None:
                if item.area == None:
                    surface_blit(item.surface, item.rect.move(-bounds.left, -bounds.top))
                else:
                    surface_blit(item.surface, item.rect.move(-bounds.left, -bounds.top), item.area)
            else:
                draw_function(item, custom_draw)

        return (
         buffer, bounds)

    def __set_clip(self, rect):
        if self.__clip != None:
            rect = rect.clip(self.__clip)
        self.__set_clip_surface.set_clip(rect)
        return

    def __add_serveral_rows_item(self, item, definition):
        (row, col) = item.get_position()
        self.__several_rows_items.append((item, row, row + definition.size[0] - 1, col))
        return

    def __remove_serveral_rows_item(self, item):
        for big_item in self.__several_rows_items:
            if big_item[0] == item:
                self.__several_rows_items.remove(big_item)

        return

    def __update_serveral_rows_item(self, item, definition):
        found = False
        (row, col) = item.get_position()
        t = (item, row, row + definition.size[0] - 1, col)
        k = 0
        l = len(self.__several_rows_items)
        while k < l:
            if self.__several_rows_items[k][0] == item:
                self.__several_rows_items[k] = t
                found = True
                break
            k += 1

        if not found:
            self.__several_rows_items.append(t)
        return


MAX_SPEED = 90

class LayerRace(Layer):

    def __init__(self, stage, vehicle):
        Layer.__init__(self)
        self.__speed = 0.0
        self.__speed_mark = 0.0
        self.__acceleration = 0
        self.__accelerating = False
        self.__distance_traveled = 0
        self.__braking = False
        self.__speed_item = None
        self.__distance_traveled_item = None
        self.__sound_acceleration = None
        self.__sound_deceleration = None
        self.__sound_braked = None
        self.__sound_max_speed = None
        self.__sound_engine_on = None
        self.__engine_channel = sounds.VirtualChannel(stage)
        self.__const_acceleration = 0
        self.__const_normal_deceleration = 0
        self.__const_break_deceleration = 0
        self.add(vehicle)
        self.car = assets.load_image('alien.gif')
        self.car_pos2 = (300, 0)
        self.car_speed2 = 10
        self.images = [assets.load_image('p2s01i005.png'), assets.load_image('p2s01i005_o.png')]
        self.positions1 = [(0, 0), (90, 0), (0, 150), (90, 150), (0, 300)]
        self.image_index1 = 0
        self.positions2 = [(500, 0), (410, 0), (500, 150), (410, 150), (500, 300)]
        self.image_index2 = 0
        self.image_step = 0
        return

    def get_speed(self):
        return self.__speed

    def get_distance_traveled(self):
        return self.__distance_traveled

    def set_engine_sounds(self, acceleration, deceleration, braked, max_speed, engine_on):
        self.__sound_acceleration = acceleration
        self.__sound_deceleration = deceleration
        self.__sound_braked = braked
        self.__sound_max_speed = max_speed
        self.__sound_engine_on = engine_on
        self.__const_acceleration = _div(MAX_SPEED , (float(acceleration.get_length()) * 1000))
        self.__const_normal_deceleration = _div(-MAX_SPEED , (float(deceleration.get_length()) * 1000))
        self.__const_break_deceleration = _div(-MAX_SPEED , (float(braked.get_length()) * 1000))
        return

    def set_speed_item(self, item):
        self.__speed_item = item
        return

    def set_distance_traveled_item(self, item):
        self.__distance_traveled_item = item
        return

    def play_engine_on(self):
        self.__engine_channel.play(self.__sound_engine_on, -1, 1000, 0)
        return

    def start_accelerate(self):
        if self.__speed < MAX_SPEED:
            self.__acceleration = self.__const_acceleration
            self.__accelerating = True
            self.__braking = False
            speed_mark = MAX_SPEED - self.__acceleration * 1000
            if self.__speed > speed_mark:
                self.__engine_channel.play(self.__sound_max_speed, -1, 500, 0)
                self.__speed_mark = MAX_SPEED
            else:
                offset = _div(float(self.__speed) , MAX_SPEED)
                self.__engine_channel.play(self.__sound_acceleration, 0, 500, offset)
                self.__speed_mark = speed_mark
        return

    def stop_accelerate(self):
        if self.__accelerating:
            self.__acceleration = self.__const_normal_deceleration
            self.__accelerating = False
            speed_mark = -self.__acceleration * 500
            if self.__speed < speed_mark:
                self.__engine_channel.play(self.__sound_engine_on, -1, 100, 0)
                self.__speed_mark = 0
            else:
                offset = 1 - _div(float(self.__speed) , MAX_SPEED)
                self.__engine_channel.play(self.__sound_deceleration, 0, 500, offset)
                self.__speed_mark = speed_mark
        return

    def start_break(self):
        if self.__speed > 0:
            self.__acceleration = self.__const_break_deceleration
            self.__accelerating = False
            self.__braking = True
            speed_mark = -self.__acceleration * 100
            if self.__speed < speed_mark:
                self.__engine_channel.play(self.__sound_engine_on, -1, 100, 0)
                self.__speed_mark = 0
            else:
                offset = 1 - _div(float(self.__speed) , MAX_SPEED)
                self.__engine_channel.play(self.__sound_braked, 0, 50, offset)
                self.__speed_mark = speed_mark
        return

    def stop_break(self):
        if self.__braking:
            self.__acceleration = self.__const_normal_deceleration
            self.__braking = False
            speed_mark = -self.__acceleration * 500
            if self.__speed < speed_mark:
                self.__engine_channel.play(self.__sound_engine_on, -1, 100, 0)
                self.__speed_mark = 0
            else:
                offset = 1 - _div(float(self.__speed) , MAX_SPEED)
                self.__engine_channel.play(self.__sound_deceleration, 0, 250, offset)
                self.__speed_mark = speed_mark
        return

    def update(self, dirty_rects, frame_delay):
        if self.__acceleration > 0:
            self.__speed += self.__acceleration * frame_delay
            if self.__speed >= MAX_SPEED:
                self.__speed = MAX_SPEED
                self.__acceleration = 0
            if self.__speed > self.__speed_mark:
                if self.__acceleration == 0:
                    cross_fade = 0
                else:
                    cross_fade = int(_div((MAX_SPEED - self.__speed) , self.__acceleration))
                self.__engine_channel.play(self.__sound_max_speed, -1, cross_fade, 0)
                self.__speed_mark = MAX_SPEED
        elif self.__acceleration < 0:
            self.__speed += self.__acceleration * frame_delay
            if self.__speed <= 0:
                self.__speed = 0
                self.__acceleration = 0
            if self.__speed < self.__speed_mark:
                if self.__acceleration == 0:
                    cross_fade = 0
                else:
                    cross_fade = int(_div(self.__speed , -self.__acceleration))
                self.__engine_channel.play(self.__sound_engine_on, -1, cross_fade, 0)
                self.__speed_mark = 0
        if self.__speed_item != None:
            self.__speed_item.set_text(str(int(self.__speed)))
        self.__distance_traveled += self.__speed * (_div(float(frame_delay) , 360))
        if self.__distance_traveled_item != None:
            self.__distance_traveled_item.set_text(str(int(self.__distance_traveled)))
        Layer.update(self, dirty_rects, frame_delay)
        if self.car_speed2 > 0:
            dirty_rects.append(Rect(self.car_pos2[0], self.car_pos2[1], self.car.get_width(), self.car.get_height() + self.car_speed2))
        else:
            dirty_rects.append(Rect(self.car_pos2[0], self.car_pos2[1] + self.car_speed2, self.car.get_width(), self.car.get_height() - self.car_speed2))
        if self.car_speed2 > 0:
            dirty_rects.append(Rect(self.car_pos2[0] - 100, self.car_pos2[1], self.car.get_width(), self.car.get_height() + self.car_speed2))
        else:
            dirty_rects.append(Rect(self.car_pos2[0] - 100, self.car_pos2[1] + self.car_speed2, self.car.get_width(), self.car.get_height() - self.car_speed2))
        if self.image_step == 0:
            for pos in self.positions1:
                dirty_rects.append(Rect(pos[0], pos[1], self.images[self.image_index1].get_width(), self.images[self.image_index1].get_height()))

        elif self.image_step == 1:
            for pos in self.positions2:
                dirty_rects.append(Rect(pos[0], pos[1], self.images[self.image_index2].get_width(), self.images[self.image_index2].get_height()))

        return

    def draw(self, surface, dirty_rects):
        if self.image_step == 0:
            for pos in self.positions1:
                surface.blit(self.images[self.image_index1].surface, (pos[0], pos[1]))

            self.image_index1 += 1
            if self.image_index1 >= len(self.images):
                self.image_index1 = 0
        elif self.image_step == 1:
            for pos in self.positions2:
                surface.blit(self.images[self.image_index2].surface, (pos[0], pos[1]))

            self.image_index2 += 1
            if self.image_index2 >= len(self.images):
                self.image_index2 = 0
        self.image_step += 1
        if self.image_step > 1:
            self.image_step = 0
        self.car_pos2 = (
         self.car_pos2[0], self.car_pos2[1] + self.car_speed2)
        surface.blit(self.car.surface, (self.car_pos2[0], self.car_pos2[1]))
        surface.blit(self.car.surface, (self.car_pos2[0] - 100, self.car_pos2[1]))
        if self.car_speed2 > 0:
            if self.car_pos2[1] > 300:
                self.car_speed2 = -self.car_speed2
        elif self.car_pos2[1] < 30:
            self.car_speed2 = -self.car_speed2
        Layer.draw(self, surface, dirty_rects)
        return


class LayerBuffered(Layer):

    def __init__(self, width, height, use_alpha=False):
        Layer.__init__(self)
        if use_alpha:
            self.__buffer = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        else:
            self.__buffer = pygame.Surface((width, height))
        return

    def update(self, dirty_rects, frame_delay):
        dirty_rects_list = self.dirty_rects
        self.dirty_rects = []
        dirty_items_list = self.dirty_items
        self.dirty_items = []
        for item in dirty_items_list:
            dirty_rect = item.update(frame_delay)
            if dirty_rect != None:
                dirty_rects_list.append(dirty_rect)

        if len(dirty_rects_list) > 0:
            buffer = self.__buffer
            buffer.set_clip(Rect(0, 0, 9999, 9999))
            for rect in dirty_rects_list:
                buffer.fill((0, 0, 0, 0), rect)

            Layer.draw(self, buffer, dirty_rects_list)
            for rect in dirty_rects_list:
                k = rect.collidelist(dirty_rects)
                while k != -1:
                    rect.union_ip(dirty_rects[k])
                    del dirty_rects[k]
                    k = rect.collidelist(dirty_rects)

                dirty_rects.append(rect)

        return

    def draw(self, surface, dirty_rects):
        surface_blit = surface.blit
        buffer = self.__buffer
        surface.set_clip(Rect(0, 0, 9999, 9999))
        for dirty_rect in dirty_rects:
            surface_blit(buffer, dirty_rect, dirty_rect)

        return


class CustomDraw():

    def __init__(self, width=0, height=0):
        if width == 0:
            self.surface = None
        else:
            self.surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        return

    def blit_surface(self, surface, pos, area=None):
        if area != None:
            self.surface.blit(surface, pos, area)
        else:
            self.surface.blit(surface, pos)
        return

    def blit_image(self, image, pos, area=None):
        if area != None:
            self.surface.blit(image.surface, pos, area)
        else:
            self.surface.blit(image.surface, pos)
        return

    def blit_stage(self, stage, pos, area=None):
        surface = stage.target_surface
        if surface == None:
            surface = stage.game.window
        if area != None:
            self.surface.blit(surface, pos, area)
        else:
            self.surface.blit(surface, pos)
        return

    def clear(self, color):
        self.surface.fill(color)
        return

    def fill(self, color, rect):
        self.surface.fill(color, rect)
        return

    def draw_line(self, color, start_pos, end_pos, width=1):
        pygame.draw.line(self.surface, color, start_pos, end_pos, width)
        return

    def draw_rect(self, color, rect, width=1):
        pygame.draw.rect(self.surface, color, rect, width)
        return


class CustomDrawDelta():

    def __init__(self, surface, dx, dy):
        self.surface = surface
        self.dx = dx
        self.dy = dy
        return

    def blit_surface(self, surface, pos, area=None):
        if area != None:
            self.surface.blit(surface, pos, area)
        else:
            self.surface.blit(surface, pos)
        return

    def blit_image(self, image, pos, area=None):
        if area != None:
            self.surface.blit(image.surface, pos, area)
        else:
            self.surface.blit(image.surface, pos)
        return

    def blit_stage(self, stage, pos, area=None):
        surface = stage.target_surface
        if surface == None:
            surface = stage.game.window
        if area != None:
            self.surface.blit(surface, pos, area)
        else:
            self.surface.blit(surface, pos)
        return

    def clear(self, color):
        self.surface.fill(color)
        return

    def fill(self, color, rect):
        self.surface.fill(color, rect)
        return

    def draw_line(self, color, start_pos, end_pos, width=1):
        pygame.draw.line(self.surface, color, (start_pos[0] + self.dx, start_pos[1] + self.dy), (
         end_pos[0] + self.dx, end_pos[1] + self.dy), width)
        return

    def draw_rect(self, color, rect, width=1):
        rect = Rect(rect[0] + self.dx, rect[1] + self.dy, rect[2], rect[3])
        pygame.draw.rect(self.surface, color, rect, width)
        return


