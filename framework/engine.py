import pygame, os, platform, gc
from . import engine, stage, stats, assets, animations
from pygame.locals import *
from framework.stage import Layer, ItemImage
from .external import is_sugar
try:
    import numpy
    pygame.surfarray.use_arraytype('numpy')
except:
    pass

IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_PRIVATE' in os.environ
SCREEN_FACTOR = 1
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 450

class Game():

    def __init__(self, title, default_mouse_cursor=None, loading_image=None):
        try:
            import psyco
            psyco.full()
        except Exception as message:
            print(('Psyco couldnt be used to improve speed:', message))

        if platform.system() == 'Windows':
            self.mixer_params = (44100, -16, 2, 1024)
        elif is_sugar:
            self.mixer_params = (22050, -16, 1, 4096)
        else:
            self.mixer_params = (44100, -16, 2, 512)
        pygame.mixer.pre_init(*self.mixer_params)
        pygame.init()
        self.__empty_sound = assets.load_sound('Silence.ogg')
        # Port Android/PC: la imagen original de 600x450 la escala SDL (SCALED) a toda la pantalla
        # manteniendo la proporción; los toques llegan ya en coordenadas de 600x450.
        engine.SCREEN_FACTOR = 1
        if platform.system() == 'Windows':
            self.__set_icon('icon.gif')
        pygame.display.init()
        flags = pygame.SCALED
        if IS_ANDROID:
            flags |= pygame.FULLSCREEN
        self.display = pygame.display.set_mode((engine.SCREEN_WIDTH, engine.SCREEN_HEIGHT), flags)
        self.window = pygame.Surface((600, 450), 0, self.display)
        self.window_rect = self.window.get_rect()
        pygame.display.set_caption(title)
        self.__stage = None
        self.__design_stage = None
        self.__default_mouse_cursor = default_mouse_cursor
        self.__loading_image = loading_image
        self.loading_layer = None
        self.__show_fps = False
        self.__clock = pygame.time.Clock()
        self.__frame_delay = 0
        self.__fps_max_width = 0
        self.__quit_game = 0
        self.__font = assets.load_font('freesansbold.ttf', 13)
        self.__dimmed_background = None
        self.__development_mode = False
        self.__quit_on_escape = True
        self.__loading_start = None
        self.stats = stats.Stats()
        if default_mouse_cursor == None or IS_ANDROID:
            # en pantallas táctiles no se dibuja la flecha del mouse (los arrastres siguen mostrando el objeto)
            self.__default_mouse_cursor = None
        else:
            self.__default_mouse_cursor = assets.load_image(default_mouse_cursor)
        return

    def run(self, initial_stage):
        if not stage.STREAM_MUSIC:
            pygame.mixer.set_reserved(1)
        self.set_stage(initial_stage)
        test = _TestScript(self)
        while not self.__quit_game:
            self.__frame_delay = self.__clock.tick(40)
            test.step()
            self.__stage.notify_tick()

        return

    def quit(self):
        if self.__stage != None:
            closed_handler = self.__stage.get_closed_handler()
            if closed_handler != None:
                closed_handler(self.__stage)
        self.__quit_game = 1
        self.stats.save_if_pending()
        return

    def get_show_fps(self):
        return self.__show_fps

    def set_show_fps(self, value):
        self.__show_fps = value
        self.__stage.redraw()
        return

    def get_quit_on_escape(self):
        return self.__quit_on_escape

    def set_quit_on_escape(self, value):
        self.__quit_on_escape = value
        return

    def get_default_mouse_cursor(self):
        return self.__default_mouse_cursor

    def get_design_stage(self):
        return self.__design_stage

    def set_design_stage(self, design_stage):
        self.__design_stage = design_stage
        return

    def get_test_stage(self):
        return self.__test_stage

    def set_test_stage(self, test_stage):
        self.__test_stage = test_stage
        return

    def get_development_mode(self):
        return self.__development_mode

    def set_development_mode(self, development_mode):
        self.__development_mode = development_mode
        return

    def set_stage(self, stage, show_loading=False, loading_image=None):
        next_stage = _ChangeStageDummy(self, self.__stage, stage)
        if not show_loading:
            self.__stage = next_stage
        else:
            self.__next_stage = next_stage
            self.show_loading(self.__set_next_stage, loading_image)
        return

    def show_loading(self, callback, loading_image=None):
        self.__stage.stop_music()
        if self.loading_layer != None:
            stage = self.loading_layer.get_stage()
            if stage != None:
                animations.cancel_blind_layer(stage, self.loading_layer, False)
                stage.remove_layer(self.loading_layer)
        self.loading_layer = Layer()
        if loading_image != None:
            image = assets.load_image(loading_image)
        else:
            image = assets.load_image(self.__loading_image)
        item = ItemImage(0, 0, image)
        self.loading_layer.add(item)
        self.loading_layer.stage = self.__stage
        self.__stage.redraw_mouse()
        if self.__loading_start == None:
            self.__loading_start = pygame.time.get_ticks()
        animations.blind_layer(self.loading_layer, animations.BlindDirection.SHOW_DOWN, None, 450, callback)
        return

    def add_loading_to_stage(self):
        layer = self.loading_layer
        if layer != None:
            layer.stage = None
            self.__stage.add_layer(layer)
        self.loading_layer = None
        return layer

    def hide_loading(self, callback=None, blind=True):
        if self.loading_layer != None:
            if self.__loading_start != None:
                elapsed_time = pygame.time.get_ticks() - self.__loading_start
                min_time = 1500
                if elapsed_time < min_time:
                    pygame.time.wait(min_time - elapsed_time)
                self.__loading_start = None
            self.hide_loading_callback = callback
            if self.loading_layer.get_stage() != None:
                if blind:
                    animations.blind_layer(self.loading_layer, animations.BlindDirection.HIDE_UP, None, 450, self.__blind_hide_loading_callback)
                else:
                    self.__blind_hide_loading_callback(self.loading_layer)
        elif callback != None:
            callback(None)
        return

    def get_window_size(self):
        return self.window.get_size()

    def draw_fps(self, dirty_rects):
        text = self.__font.render('FPS: ' + str(round(self.__clock.get_fps(), 2)), True, (0,
                                                                                          0,
                                                                                          0))
        text_rect = text.get_rect()
        text_rect.topleft = (4, 2)
        if text_rect[2] + 10 > self.__fps_max_width:
            self.__fps_max_width = text_rect[2] + 10
        border_rect = Rect(0, 0, self.__fps_max_width, text_rect.height + 4)
        self.window.set_clip(border_rect)
        pygame.draw.rect(self.window, (250, 250, 250), border_rect)
        pygame.draw.rect(self.window, (20, 20, 20), border_rect, 1)
        self.window.blit(text, text_rect)
        dirty_rects.append(border_rect)
        return

    def get_frame_delay(self):
        return self.__frame_delay

    def update_display(self, dirty_rects):
        if SCREEN_FACTOR == 2:
            dirty_rects2 = []
            for r in dirty_rects:
                r = self.window_rect.clip(r)
                r2 = [x * 2 for x in r]
                s2 = pygame.transform.scale2x(self.window.subsurface(r))
                self.display.blit(s2, r2)
                dirty_rects2.append(r2)

            pygame.display.update(dirty_rects2)
        elif SCREEN_FACTOR == 1:
            self.display.blit(self.window, (0, 0))
            pygame.display.update(dirty_rects)
        else:
            dirty_rects2 = []
            for r in dirty_rects:
                r = self.window_rect.clip(r)
                r2 = [x * SCREEN_FACTOR for x in r]
                s2 = pygame.transform.scale(self.window.subsurface(r), r2[2:4])
                self.display.blit(s2, r2)
                dirty_rects2.append(r2)

            pygame.display.update(dirty_rects2)
        return

    def get_empty_sound(self):
        return self.__empty_sound

    def __set_icon(self, iconname):
        icon = pygame.Surface((32, 32))
        icon.set_colorkey((255, 0, 255))
        rawicon = pygame.image.load(iconname)
        for i in range(0, 32):
            for j in range(0, 32):
                icon.set_at((i, j), rawicon.get_at((i, j)))

        pygame.display.set_icon(icon)
        return

    def __set_next_stage(self, layer):
        self.__stage = self.__next_stage
        self.__next_stage = None
        return

    def __blind_hide_loading_callback(self, layer):
        self.__stage.render()
        self.__stage.redraw_mouse()
        self.loading_layer = None
        callback = self.hide_loading_callback
        self.hide_loading_callback = None
        if callback != None:
            callback(layer)
        return


class _TestScript:
    """Pruebas automáticas (DET_TEST="cuadro:click:x:y;cuadro:shot:archivo;cuadro:quit"): toques y capturas."""

    def __init__(self, game):
        self.game = game
        self.frame = 0
        self.steps = []
        for part in os.environ.get('DET_TEST', '').split(';'):
            if part:
                f = part.split(':')
                self.steps.append((int(f[0]), f[1], f[2:]))

    def step(self):
        if not self.steps:
            return
        self.frame += 1
        for f, cmd, args in list(self.steps):
            if f != self.frame:
                continue
            if cmd in ('down', 'move', 'up'):
                self._post_mouse(cmd, args)
            elif cmd == 'click':
                pos = (int(args[0]) * SCREEN_FACTOR, int(args[1]) * SCREEN_FACTOR)
                pygame.event.post(pygame.event.Event(MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(0, 0, 0)))
                pygame.event.post(pygame.event.Event(MOUSEBUTTONDOWN, pos=pos, button=1))
                pygame.event.post(pygame.event.Event(MOUSEBUTTONUP, pos=pos, button=1))
            elif cmd == 'key':
                k = getattr(pygame, 'K_' + args[0])
                pygame.event.post(pygame.event.Event(KEYDOWN, key=k, mod=0, unicode=args[1] if len(args) > 1 else ''))
                if IS_ANDROID and len(args) > 1 and args[1]:
                    pygame.event.post(pygame.event.Event(pygame.TEXTINPUT, text=args[1]))   # teclado en pantalla
                pygame.event.post(pygame.event.Event(KEYUP, key=k, mod=0))
            elif cmd == 'shot':
                pygame.image.save(self.game.display, args[0])
            elif cmd == 'quit':
                self.game.quit()
            elif cmd == 'devmenu':
                # menú de desarrollo del original (teclas 1-7 = fases y minijuegos)
                self.game.set_development_mode(True)
                self.game.set_stage(self.game.get_design_stage())
            elif cmd == 'monkey':
                self._monkey(int(args[0]), int(args[1]), int(args[2]))
        stage = self.game._Game__stage
        name = type(stage).__name__
        if name != getattr(self, '_last_stage', None):
            self._last_stage = name
            print('STAGE', self.frame, name, flush=True)

    def _monkey(self, seed, count, interval):
        # toques/arrastres al azar para buscar errores (cuadro:monkey:semilla:cantidad:intervalo)
        import random
        rnd = random.Random(seed)
        f = self.frame
        for i in range(count):
            f += interval
            x, y = rnd.randrange(600), rnd.randrange(450)
            if rnd.random() < 0.25:
                x2, y2 = rnd.randrange(600), rnd.randrange(450)
                self.steps.append((f, 'down', [x, y]))
                for k in range(1, 6):
                    self.steps.append((f + k, 'move', [x + (x2 - x) * k // 5, y + (y2 - y) * k // 5, 1]))
                self.steps.append((f + 6, 'up', [x2, y2]))
            elif rnd.random() < 0.08:
                ch = rnd.choice('abcdefghijklmnopqrstuvwxyz')
                self.steps.append((f, 'key', [ch, ch]))
            else:
                self.steps.append((f, 'click', [x, y]))
        self.steps.append((f + 60, 'quit', []))

    def _post_mouse(self, cmd, args):
        pos = (int(args[0]) * SCREEN_FACTOR, int(args[1]) * SCREEN_FACTOR)
        if cmd == 'down':
            pygame.event.post(pygame.event.Event(MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(0, 0, 0)))
            pygame.event.post(pygame.event.Event(MOUSEBUTTONDOWN, pos=pos, button=1))
        elif cmd == 'move':
            pygame.event.post(pygame.event.Event(MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(1, 0, 0)))
        else:
            pygame.event.post(pygame.event.Event(MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(1, 0, 0)))
            pygame.event.post(pygame.event.Event(MOUSEBUTTONUP, pos=pos, button=1))


class _ChangeStageDummy():

    def __init__(self, game, old_stage, new_stage):
        self.__game = game
        self.__old_stage = old_stage
        self.__new_stage = new_stage
        return

    def notify_tick(self):
        old_stage = self.__old_stage
        self.__game._Game__stage = self.__new_stage
        if old_stage != None:
            old_stage.set_focus(None)
            closed_handler = old_stage.get_closed_handler()
            if closed_handler != None:
                closed_handler(old_stage)
                del closed_handler
            old_stage.close()
        key_repeat = self.__new_stage.get_key_repeat()
        if key_repeat == None:
            pygame.key.set_repeat()
        else:
            pygame.key.set_repeat(key_repeat[0], key_repeat[1])
        pygame.event.set_grab(False)
        if old_stage != None:
            old_stage.stop_music()
            old_stage.stop_sounds()
        if self.__game.loading_layer != None:
            self.__game.loading_layer.stage = None
        del old_stage
        del self.__old_stage
        gc.collect()
        self.__new_stage.play_music()
        if not self.__new_stage.initialized:
            self.__new_stage.initialize()
            self.__new_stage.initialized = True
        if self.__game.loading_layer != None:
            self.__game.loading_layer.stage = self.__new_stage
        self.__new_stage.redraw()
        self.__new_stage.prepare()
        if self.__game.loading_layer != None:
            self.__game.hide_loading(self.__game.hide_loading_callback)
        return

    def set_focus(self, item, set_focus_data=None):
        return

    def close(self):
        return

    def stop_music(self):
        return

    def stop_sounds(self):
        return

    def get_closed_handler(self):
        return


