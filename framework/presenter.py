# Presentación en pantalla y menú de ajustes.
#
# El juego dibuja siempre en su superficie original de 600x450. Este módulo toma esa imagen y la muestra
# con el renderizador de SDL (por GPU) según los ajustes:
#   - Original: 4:3 con bordes negros.   - Rellenar: los bordes se llenan con la misma imagen difuminada
#     (cubre todo el marco sin estirar ni recortar).   - Estirar: ocupa toda la pantalla.
#   - Suavizado (filtrado lineal), Calidad HD (scale2x antes de agrandar) y Efecto TV.
# También dibuja el engranaje de ajustes (arriba a la derecha) y el menú, y mientras está abierto pausa
# el juego (el reloj del juego se detiene). Si el renderizador no está disponible queda la presentación
# de pygame de siempre (SCALED).
import os, math
import pygame
from pygame.locals import *
from . import settings

LW, LH = 600, 450
active = None


def _sdl_lib():
    import ctypes
    names = ['libSDL2.so', 'libSDL2-2.0.so.0', 'libSDL2-2.0.so', 'SDL2.dll', 'libSDL2-2.0.0.dylib']
    try:
        names.insert(0, os.path.join(os.path.dirname(pygame.__file__), 'SDL2.dll'))
    except Exception:
        pass
    for n in names:
        try:
            return ctypes.CDLL(n)
        except Exception:
            continue
    return None


class Presenter:

    def __init__(self, game):
        from pygame._sdl2.video import Window, Renderer, Texture
        self.Texture = Texture
        self.game = game
        self.window = Window.from_display_module()
        self.renderer = Renderer.from_window(self.window)
        self.surface = pygame.display.get_surface()
        self.sdl = _sdl_lib()
        self.tex = None
        self.tex_key = None
        self.bg_tex = None
        self.tv_tex = None
        self.gear_tex = None
        self.gear_key = None
        self.rect = pygame.Rect(0, 0, LW, LH)
        self.menu = SettingsMenu(self)
        self.paused_since = None
        self.paused_total = 0
        self._real_ticks = pygame.time.get_ticks
        self._real_get = pygame.event.get
        self._real_mouse_pos = pygame.mouse.get_pos
        self._layout()

    # ------------------------------------------------------------- instalación

    def install(self):
        global active
        active = self
        pygame.display.flip = self.present
        pygame.display.update = lambda *a, **k: self.present()
        pygame.event.get = self.get_events
        pygame.mouse.get_pos = self.mouse_pos
        pygame.time.get_ticks = self.ticks
        self.apply_audio()

    def ticks(self):
        # mientras el menú está abierto el reloj del juego no avanza (los temporizadores no corren)
        now = self._real_ticks()
        paused = self.paused_total
        if self.paused_since is not None:
            paused += now - self.paused_since
        return now - paused

    def pause(self, value):
        now = self._real_ticks()
        if value and self.paused_since is None:
            self.paused_since = now
        elif not value and self.paused_since is not None:
            self.paused_total += now - self.paused_since
            self.paused_since = None

    def is_paused(self):
        return self.menu.open

    # ------------------------------------------------------------- geometría

    def _layout(self):
        try:
            self.renderer.logical_size = (0, 0)
        except Exception:
            pass
        W, H = self.window.size
        self.W, self.H = W, H
        mode = settings.get('screen')
        if mode == 2:
            self.rect = pygame.Rect(0, 0, W, H)
        else:
            s = min(float(W) / LW, float(H) / LH)
            w, h = int(LW * s), int(LH * s)
            self.rect = pygame.Rect((W - w) // 2, (H - h) // 2, w, h)
        # engranaje: en el margen derecho si hay lugar; si no, sobre el juego en la esquina superior derecha
        margin = W - self.rect.right
        if margin >= 70:
            r = int(min(margin * 0.32, H * 0.055))
            self.gear = (self.rect.right + margin // 2, r + int(H * 0.04), r)
        else:
            r = int(min(self.rect.h * 0.035, 40))
            self.gear = (self.rect.right - r - 6, self.rect.top + r + 6, r)

    def to_logical(self, x, y):
        r = self.rect
        return (int((x - r.x) * LW / float(r.w)), int((y - r.y) * LH / float(r.h)))

    def finger(self, event):
        return self.to_logical(event.x * self.W, event.y * self.H)

    def mouse_pos(self):
        x, y = self._real_mouse_pos()
        return self.to_logical(x, y)

    # ------------------------------------------------------------- eventos

    def get_events(self, *args, **kwargs):
        events = self._real_get(*args, **kwargs)
        out = []
        for e in events:
            if e.type == VIDEORESIZE or (hasattr(pygame, 'WINDOWSIZECHANGED') and e.type == pygame.WINDOWSIZECHANGED):
                self._layout()
            if e.type in (MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP):
                wpos = e.pos
                d = dict(e.dict)
                d['pos'] = self.to_logical(*wpos)
                if 'rel' in d:
                    d['rel'] = (int(d['rel'][0] * LW / float(self.rect.w)), int(d['rel'][1] * LH / float(self.rect.h)))
                e = pygame.event.Event(e.type, d)
                if e.type == MOUSEBUTTONDOWN and getattr(e, 'button', 1) == 1 and self.gear_hit(wpos):
                    self.menu.toggle()
                    continue
            if self.menu.open:
                if e.type == QUIT:
                    out.append(e)
                else:
                    self.menu.handle(e)
                continue
            if e.type in (FINGERDOWN, FINGERMOTION, FINGERUP) and e.type == FINGERDOWN:
                if self.gear_hit((e.x * self.W, e.y * self.H)):
                    continue
            out.append(e)
        return out

    def gear_hit(self, wpos):
        gx, gy, r = self.gear
        return math.hypot(wpos[0] - gx, wpos[1] - gy) <= max(r * 1.6, 22)

    # ------------------------------------------------------------- dibujo

    def _scale_hint(self, linear):
        if self.sdl is not None:
            try:
                self.sdl.SDL_SetHintWithPriority(b'SDL_RENDER_SCALE_QUALITY', b'1' if linear else b'0', 2)
            except Exception:
                pass

    def _texture(self, attr, key_attr, key, surface, linear):
        tex = getattr(self, attr)
        if tex is not None and getattr(self, key_attr) == key:
            try:
                tex.update(surface)
                return tex
            except Exception:
                pass
        self._scale_hint(linear)
        tex = self.Texture.from_surface(self.renderer, surface)
        setattr(self, attr, tex)
        setattr(self, key_attr, key)
        return tex

    def present(self):
        if (self.W, self.H) != self.window.size:
            self._layout()
        ren = self.renderer
        try:
            ren.logical_size = (0, 0)
        except Exception:
            pass
        ren.draw_color = (0, 0, 0, 255)
        ren.clear()
        frame = self.surface
        if settings.get('screen') == 1 and (self.rect.w < self.W or self.rect.h < self.H):
            small = pygame.transform.smoothscale(frame.convert(), (48, 36))
            bg = self._texture('bg_tex', 'bg_key', 'bg', small, True)
            try:
                bg.color = (105, 105, 105)
            except Exception:
                pass
            s = max(self.W / 48.0, self.H / 36.0)
            w, h = int(48 * s) + 2, int(36 * s) + 2
            bg.draw(dstrect=((self.W - w) // 2, (self.H - h) // 2, w, h))
        hd = settings.get('hd')
        src = pygame.transform.scale2x(frame) if hd else frame
        tex = self._texture('tex', 'tex_key', (hd, settings.get('smooth'), src.get_size()), src, settings.get('smooth'))
        tex.draw(dstrect=tuple(self.rect))
        if settings.get('tv'):
            self._draw_tv()
        if self.menu.open:
            overlay = self.menu.render()
            self._scale_hint(True)
            t = self.Texture.from_surface(ren, overlay)
            t.draw(dstrect=tuple(self.rect))
        self._draw_gear()
        ren.present()

    def _draw_tv(self):
        if self.tv_tex is None:
            s = pygame.Surface((4, LH * 2), SRCALPHA)
            for y in range(0, LH * 2, 2):
                s.fill((0, 0, 0, 70), (0, y + 1, 4, 1))
            self._scale_hint(False)
            self.tv_tex = self.Texture.from_surface(self.renderer, s)
        self.tv_tex.draw(dstrect=tuple(self.rect))

    def _draw_gear(self):
        gx, gy, r = self.gear
        key = (r, self.menu.open)
        if self.gear_tex is None or self.gear_key != key:
            self._scale_hint(True)
            self.gear_tex = self.Texture.from_surface(self.renderer, gear_surface(r * 2, self.menu.open))
            self.gear_key = key
        self.gear_tex.draw(dstrect=(gx - r, gy - r, r * 2, r * 2))

    # ------------------------------------------------------------- audio

    def apply_audio(self):
        try:
            pygame.mixer.Channel(0).set_volume(settings.music_volume())
            pygame.mixer.music.set_volume(settings.music_volume())
            from . import assets
            assets.apply_sfx_volume()
        except Exception:
            pass

    def idle(self):
        # bucle mientras el menú está abierto (el juego está en pausa)
        self.get_events()
        self.present()


def gear_surface(size, highlighted=False):
    # engranaje con la estética del juego: dorado como los marcos del HUD, borde marrón oscuro
    k = 4
    S = size * k
    s = pygame.Surface((S, S), SRCALPHA)
    c = S / 2.0
    outer, inner, hole = S * 0.47, S * 0.36, S * 0.15
    teeth = 8
    pts = []
    for i in range(teeth * 4):
        a = i * math.pi * 2 / (teeth * 4)
        rr = outer if (i % 4) in (1, 2) else inner
        pts.append((c + math.cos(a) * rr, c + math.sin(a) * rr))
    dark = (70, 38, 16)
    gold = (245, 196, 72) if highlighted else (226, 170, 60)
    pygame.draw.polygon(s, dark, [(c + (x - c) * 1.08, c + (y - c) * 1.08) for x, y in pts])
    pygame.draw.polygon(s, gold, pts)
    pygame.draw.circle(s, (250, 222, 140), (int(c - S * 0.05), int(c - S * 0.05)), int(inner * 0.75))
    pygame.draw.circle(s, gold, (int(c), int(c)), int(inner * 0.72))
    pygame.draw.circle(s, dark, (int(c), int(c)), int(hole + S * 0.03))
    pygame.draw.circle(s, (120, 70, 30), (int(c), int(c)), int(hole))
    return pygame.transform.smoothscale(s, (size, size))


class SettingsMenu:
    # Menú de ajustes dibujado con piezas del juego (papel del archivo, botones de flecha y cerrar,
    # tipografía de los formularios). Se maneja con toques/clics o con el teclado.

    PAGES = ('main', 'graphics', 'sound', 'controls')
    TITLES = {'main': 'AJUSTES', 'graphics': 'GRÁFICOS', 'sound': 'SONIDO', 'controls': 'PERSECUCIÓN'}

    def __init__(self, presenter):
        self.p = presenter
        self.open = False
        self.page = 'main'
        self.sel = 0
        self.loaded = False
        self.prev_rects = {}

    def _load(self):
        if self.loaded:
            return
        self.loaded = True
        img = lambda n: pygame.image.load(os.path.join('images', n)).convert_alpha()
        self.paper = img('p0_witness_popup.png')
        self.close_img = img('p0_button_close.png')
        self.close_hover = img('p0_button_close_rollover.png')
        self.next_img = pygame.transform.smoothscale(img('p0_button_next_active.png'), (30, 30))
        self.prev_img = pygame.transform.smoothscale(img('p0_button_previous_active.png'), (30, 30))
        self.title_font = pygame.font.Font(os.path.join('fonts', 'evilgeniusbb_bld.ttf'), 30)
        self.font = pygame.font.Font(os.path.join('fonts', 'evilgeniusbb_bld.ttf'), 21)
        self.small = pygame.font.Font(os.path.join('fonts', 'evilgeniusbb_reg.ttf'), 15)

    def toggle(self):
        self.open = not self.open
        self.page = 'main'
        self.sel = 0
        self.p.pause(self.open)
        if not self.open:
            settings.save()

    # ------------------------------------------------------------- filas

    def rows(self):
        g = settings.get
        if self.page == 'main':
            return [('Gráficos', None, lambda d: self.go('graphics')),
                    ('Sonido', None, lambda d: self.go('sound')),
                    ('Persecución', None, lambda d: self.go('controls')),
                    ('Volver al juego', None, lambda d: self.toggle())]
        if self.page == 'graphics':
            return [('Pantalla', settings.SCREEN_MODES[g('screen')], lambda d: self.cycle('screen', 3, d)),
                    ('Suavizado', self.onoff('smooth'), lambda d: self.flip('smooth')),
                    ('Calidad HD', self.onoff('hd'), lambda d: self.flip('hd')),
                    ('Efecto TV', self.onoff('tv'), lambda d: self.flip('tv')),
                    ('Mostrar FPS', self.onoff('fps'), lambda d: self.flip('fps'))]
        if self.page == 'sound':
            return [('Música', '%d%%' % g('music'), lambda d: self.volume('music', d)),
                    ('Efectos', '%d%%' % g('sfx'), lambda d: self.volume('sfx', d))]
        tc = self.touch_cfg()
        return [('Opacidad', '%d%%' % round(tc['opacity'] * 100), lambda d: self.touch_set('opacity', d * 0.1, 0.15, 1.0)),
                ('Tamaño', '%d%%' % round(tc['size'] * 100), lambda d: self.touch_set('size', d * 0.1, 0.6, 1.6)),
                ('Ubicación', 'Restablecer', lambda d: self.touch_reset()),
                ('Modo fantasma', self.onoff('ghost'), lambda d: self.flip('ghost'))]

    def onoff(self, key):
        return 'Sí' if settings.get(key) else 'No'

    def go(self, page):
        self.page = page
        self.sel = 0

    def flip(self, key):
        settings.set(key, not settings.get(key))
        if key == 'fps':
            try:
                self.p.game.set_show_fps(settings.get('fps'))
            except Exception:
                pass

    def cycle(self, key, n, d):
        settings.set(key, (settings.get(key) + (d or 1)) % n)
        self.p._layout()

    def volume(self, key, d):
        v = settings.get(key) + (d or 1) * 10
        if v > 100:
            v = 0
        if v < 0:
            v = 100
        settings.set(key, v)
        self.p.apply_audio()

    # controles táctiles de la persecución (mismo archivo que usa racer.py)
    def touch_cfg(self):
        try:
            from game.stages.racer import TouchControls
            return TouchControls.load(TouchControls)
        except Exception:
            return {'opacity': 0.55, 'size': 1.0, 'pos': {}}

    def touch_set(self, key, delta, lo, hi):
        from game.stages.racer import TouchControls
        cfg = self.touch_cfg()
        v = round(cfg[key] + (delta or 0.1), 2)
        if v > hi + 1e-6:
            v = lo
        if v < lo - 1e-6:
            v = hi
        cfg[key] = v
        tc = TouchControls.__new__(TouchControls)
        tc.cfg = cfg
        TouchControls.save(tc)

    def touch_reset(self):
        import copy
        from game.stages.racer import TouchControls
        cfg = self.touch_cfg()
        cfg['pos'] = copy.deepcopy(TouchControls.DEFAULTS['pos'])
        tc = TouchControls.__new__(TouchControls)
        tc.cfg = cfg
        TouchControls.save(tc)

    # ------------------------------------------------------------- geometría del panel (600x450)

    PANEL = pygame.Rect(114, 55, 372, 340)

    def row_rect(self, i):
        return pygame.Rect(self.PANEL.left + 28, self.PANEL.top + 78 + i * 44, self.PANEL.w - 56, 38)

    def close_rect(self):
        return pygame.Rect(self.PANEL.right - 38, self.PANEL.top - 8, 46, 46)

    def handle(self, e):
        if e.type == KEYDOWN:
            n = len(self.rows())
            if e.key in (K_ESCAPE, K_AC_BACK):
                if self.page == 'main':
                    self.toggle()
                else:
                    self.go('main')
            elif e.key in (K_DOWN, K_KP2):
                self.sel = (self.sel + 1) % n
            elif e.key in (K_UP, K_KP8):
                self.sel = (self.sel - 1) % n
            elif e.key in (K_LEFT, K_KP4):
                self.activate(self.sel, -1)
            elif e.key in (K_RIGHT, K_KP6, K_RETURN, K_KP_ENTER, K_SPACE):
                self.activate(self.sel, 1)
        elif e.type == MOUSEBUTTONDOWN and getattr(e, 'button', 1) == 1:
            pos = e.pos
            if self.close_rect().inflate(10, 10).collidepoint(pos):
                if self.page == 'main':
                    self.toggle()
                else:
                    self.go('main')
                return
            for i in range(len(self.rows())):
                r = self.row_rect(i)
                if r.collidepoint(pos):
                    self.sel = i
                    prev = self.prev_rects.get(i)
                    d = -1 if prev is not None and prev.inflate(14, 14).collidepoint(pos) else 1
                    self.activate(i, d)
                    return
        elif e.type == MOUSEMOTION:
            for i in range(len(self.rows())):
                if self.row_rect(i).collidepoint(e.pos):
                    self.sel = i

    def activate(self, i, d):
        rows = self.rows()
        if 0 <= i < len(rows):
            rows[i][2](d)

    def render(self):
        self._load()
        s = pygame.Surface((LW, LH), SRCALPHA)
        s.fill((0, 0, 0, 120))
        P = self.PANEL
        s.blit(self.paper, P.topleft)
        title = self.TITLES[self.page]
        self._outlined(s, title, self.title_font, (205, 40, 20), (70, 15, 5), (P.centerx, P.top + 32))
        self.prev_rects = {}
        for i, (label, value, _) in enumerate(self.rows()):
            r = self.row_rect(i)
            if i == self.sel:
                hl = pygame.Surface(r.size, SRCALPHA)
                pygame.draw.rect(hl, (230, 190, 120, 110), hl.get_rect(), border_radius=6)
                s.blit(hl, r.topleft)
            if value is None:
                t = self.font.render(label.upper(), True, (60, 35, 20))
                s.blit(t, (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))
                if label != 'Volver al juego':
                    s.blit(self.next_img, (r.right - 34, r.centery - 15))
            else:
                t = self.font.render(label.upper() + ':', True, (165, 25, 15))
                s.blit(t, (r.left + 6, r.centery - t.get_height() // 2))
                v = self.font.render(value.upper(), True, (40, 25, 15))
                vx = r.right - 34 - v.get_width() - 6
                s.blit(v, (vx, r.centery - v.get_height() // 2))
                s.blit(self.prev_img, (vx - 36, r.centery - 15))
                self.prev_rects[i] = pygame.Rect(vx - 36, r.centery - 15, 30, 30)
                s.blit(self.next_img, (r.right - 34, r.centery - 15))
        c = self.close_rect()
        s.blit(self.close_img, c.topleft)
        if self.page == 'controls':
            hint = self.small.render('Los controles se mueven desde el engranaje de la persecución', True, (90, 70, 55))
            s.blit(hint, (P.centerx - hint.get_width() // 2, P.bottom - 34))
        return s

    def _outlined(self, s, text, font, color, outline, center):
        base = font.render(text, True, color)
        x, y = center[0] - base.get_width() // 2, center[1] - base.get_height() // 2
        for dx in (-2, 0, 2):
            for dy in (-2, 0, 2):
                if dx or dy:
                    s.blit(font.render(text, True, outline), (x + dx, y + dy))
        s.blit(base, (x, y))


def install(game):
    """Activa la presentación propia; si falla queda la de pygame (SCALED)."""
    if os.environ.get('SDL_VIDEODRIVER') == 'dummy' and not os.environ.get('DET_PRESENTER'):
        return None
    try:
        p = Presenter(game)
        p.install()
        p.present()
        return p
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('presenter: se usa la presentación de pygame', e)
        return None
