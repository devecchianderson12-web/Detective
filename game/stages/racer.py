# Persecución (fase 3). El original era un módulo nativo (game.stages.racer.pyd, C++ con SDL y yaml-cpp)
# que tomaba la pantalla y corría su propio bucle hasta terminar. Esta es una reimplementación en Python
# con la misma interfaz -start(...)- que lee los mismos archivos data/*.yaml. Los valores sacados del
# binario (ingeniería inversa) están marcados con "RE:".
#
# RE: paso fijo de 32 ms; entradas: acelerar, frenar, izquierda, derecha (+ Esc y Enter); el tránsito se
#     genera hasta 600 adelante y se borra 900 atrás; resistencia = (-v²·drag - v·rolling)/masa; frenar
#     resta "break"; sin acelerar se suma "extra_resistance"; cambios de marcha a rpm > max+100 y
#     rpm < max-20; torque cae pasado max_rpm: (2·max - 1.2·rpm); rpm mínimo 50; la cámara sigue al
#     auto; se gana al alcanzar al ladrón y se pierde cuando se termina el tiempo (combustible).
import math, os, random
import pygame
from pygame.locals import *
import yaml
from framework import settings

DT = 0.032                       # RE: TC::tick cada 0x20 ms
SCREEN_W, SCREEN_H = 600, 450
HORIZON = 232                    # línea del horizonte (abajo del cielo de 234 px)
FOCAL = 450.0                    # distancia focal en píxeles
CAM_HEIGHT = 3.4                 # altura de la cámara en unidades del mundo
DRAW_DISTANCE = 600.0            # RE: 600 (distancia de generación del tránsito)
BEHIND_DISTANCE = 900.0          # RE: 900
IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_PRIVATE' in os.environ


def _color(value):
    value = str(value).strip()
    if len(value) < 6:
        value = value.zfill(6)
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def _load_yaml(path):
    with open(path, 'rb') as f:
        return yaml.safe_load(f.read().decode('latin-1').replace('\t', ' '))


class Assets:

    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.scaled = {}

    def image(self, path):
        if path not in self.images:
            try:
                img = pygame.image.load(path)
                if img.get_flags() & SRCALPHA or img.get_colorkey() is not None or path.endswith('.png') or path.endswith('.gif'):
                    img = img.convert_alpha()
                else:
                    img = img.convert()
            except Exception as e:
                print('racer: no se pudo cargar', path, e)
                img = pygame.Surface((1, 1), SRCALPHA)
            self.images[path] = img
        return self.images[path]

    def sound(self, spec):
        # spec puede ser "sounds/x.wav" o {sound: ..., volume: ...}
        if spec is None:
            return None
        if isinstance(spec, dict):
            path, volume = spec.get('sound'), float(spec.get('volume', 1))
        else:
            path, volume = spec, 1.0
        if not path:
            return None
        key = (path, volume)
        if key not in self.sounds:
            snd = None
            if pygame.mixer.get_init() and os.path.exists(path):
                try:
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(volume * settings.sfx_volume())
                except Exception as e:
                    print('racer: no se pudo cargar', path, e)
            self.sounds[key] = snd
        return self.sounds[key]

    def scale(self, img, w, h):
        # escalado con caché: los tamaños se redondean para reutilizar superficies entre cuadros
        w = max(1, int(w))
        h = max(1, int(h))
        if w > 1200 or h > 1200:
            return None
        qw = w if w < 64 else w - w % 2
        qh = h if h < 64 else h - h % 2
        key = (id(img), qw, qh)
        s = self.scaled.get(key)
        if s is None:
            if len(self.scaled) > 900:
                self.scaled.clear()
            s = pygame.transform.scale(img, (qw, qh))
            self.scaled[key] = s
        return s


class Animation:

    def __init__(self, assets, frames, loop=True):
        self.frames = []
        for fr in frames or []:
            tex = fr.get('texture')
            ytr = 0
            if isinstance(tex, dict):
                ytr = tex.get('y_translation', 0)
                tex = tex.get('image')
            dy = 0
            if fr.get('pixel_translation'):
                dy = fr['pixel_translation'].get('y', 0)
            self.frames.append((assets.image(tex), float(fr.get('duration', 50)) / 1000.0, ytr, dy))
        self.loop = loop
        self.t = 0.0
        self.index = 0
        self.done = False

    def reset(self):
        self.t = 0.0
        self.index = 0
        self.done = False

    def step(self, dt):
        if not self.frames or self.done:
            return
        self.t += dt
        while self.t >= self.frames[self.index][1]:
            self.t -= self.frames[self.index][1]
            self.index += 1
            if self.index >= len(self.frames):
                if self.loop:
                    self.index = 0
                else:
                    self.index = len(self.frames) - 1
                    self.done = True
                    return

    def frame(self):
        return self.frames[self.index] if self.frames else None

    def total(self):
        return sum(f[1] for f in self.frames)


class AngleSprites:
    # texturas de un auto según el ángulo con el que se lo ve (lista de {to, both|left|right})

    def __init__(self, assets, defs):
        self.levels = []
        for d in defs or []:
            entry = {'to': float(d.get('to', 90))}
            for side in ('both', 'left', 'right'):
                if side in d:
                    t = d[side]
                    entry[side] = (assets.image(t['texture']), float(t.get('width', 4)), float(t.get('height', 3)))
            self.levels.append(entry)

    def get(self, angle_deg):
        a = abs(angle_deg)
        for e in self.levels:
            if a <= e['to']:
                if 'both' in e:
                    return e['both']
                return e['left'] if angle_deg < 0 else e['right']
        e = self.levels[-1]
        if 'both' in e:
            return e['both']
        return e['left'] if angle_deg < 0 else e['right']


class Piece:

    def __init__(self, start, defn):
        self.start = start
        self.parts = []          # (z0, z1, curvatura)
        z = start
        for part in defn.get('road', []):
            if 'segment' in part:
                ln = float(part['segment'].get('length', 100))
                self.parts.append((z, z + ln, 0.0))
            else:
                c = part['corner']
                ln = float(c.get('length', 100))
                r = float(c.get('radius', 400))
                d = 1.0 if str(c.get('direction', 'right')).strip() == 'right' else -1.0
                self.parts.append((z, z + ln, d / r))
            z += ln
        self.end = z
        self.objects = defn.get('objects', []) or []


class Track:

    def __init__(self, map_def):
        self.defs = map_def.get('pieces', [])
        self.pieces = []
        self.end = 0.0
        self.width = float(map_def.get('width', 15))
        # el primer tramo siempre es una recta
        self.add_piece(self.defs[0] if self.defs else {'road': [{'segment': {'length': 200}}]})

    def add_piece(self, defn):
        p = Piece(self.end, defn)
        self.pieces.append(p)
        self.end = p.end

    def ensure(self, z):
        while self.end < z:
            self.add_piece(random.choice(self.defs))
        while len(self.pieces) > 2 and self.pieces[1].end < z - 2 * BEHIND_DISTANCE:
            self.pieces.pop(0)

    def curvature(self, z):
        for p in self.pieces:
            if p.start <= z < p.end:
                for z0, z1, c in p.parts:
                    if z0 <= z < z1:
                        return c
        return 0.0


class WorldObject:
    __slots__ = ('x', 'z', 'w', 'h', 'tex', 'body_w', 'body_x')

    def __init__(self, x, z, w, h, tex, body):
        self.x, self.z, self.w, self.h, self.tex = x, z, w, h, tex
        if body:
            self.body_w = float(body.get('w', 0))
            self.body_x = float(body.get('x', 0))
        else:
            self.body_w = 0.0
            self.body_x = 0.0


class Car:

    def __init__(self, sprites, width, z, x, speed):
        self.sprites = sprites
        self.width = width
        self.z = z
        self.x = x
        self.target_x = x
        self.speed = speed
        self.channel = None


class Blink:
    # carteles que parpadean (available/unavailable en ms, times = cantidad de veces, 0 = siempre)

    def __init__(self, assets, d, sound=None):
        self.img = assets.image(d.get('texture') or d.get('src')) if (d.get('texture') or d.get('src')) else None
        self.x = d.get('x', 0)
        self.y = d.get('y', 0)
        self.on = float(d.get('available', 250)) / 1000.0
        self.off = float(d.get('unavailable', 0)) / 1000.0
        self.times = int(d.get('times', 0))
        self.wait = float(d.get('wait', 0)) / 1000.0
        self.active = False
        self.t = 0.0
        self.sound = sound

    def start(self):
        if not self.active:
            self.active = True
            self.t = 0.0
            self.count = -1

    def stop(self):
        self.active = False

    def step(self, dt):
        if not self.active:
            return
        period = self.on + self.off
        prev = int(self.t / period) if period > 0 else 0
        self.t += dt
        n = int(self.t / period) if period > 0 else 0
        if self.sound is not None and (self.count < 0 or n != prev) and (self.times == 0 or n < self.times):
            self.sound.play()
        self.count = n
        if self.times and n >= self.times:
            self.active = False

    def visible(self):
        if not self.active:
            return False
        if self.off <= 0:
            return True
        period = self.on + self.off
        return (self.t % period) < self.on

    def draw(self, screen):
        if self.img is not None and self.visible():
            screen.blit(self.img, (self.x, self.y))


class TouchControls:
    # Controles táctiles de la persecución: puntas de flecha izquierda/derecha y dos pedales (el largo
    # acelera, el corto frena), blancos translúcidos con orificios grises. Multitáctil. Con el botón de
    # ajustes (engranaje arriba al centro) se cambia la opacidad, el tamaño y la ubicación de cada control;
    # la configuración se guarda en data/racer_controls.json. En PC también funcionan con el mouse.

    DEFAULTS = {'opacity': 0.55, 'size': 1.0,
                'pos': {'left': [56, 318], 'right': [150, 318], 'brake': [432, 404], 'accel': [542, 366]}}
    BASE = {'left': (78, 84), 'right': (78, 84), 'brake': (112, 70), 'accel': (66, 148)}
    LABELS = {'left': 'Izquierda', 'right': 'Derecha', 'brake': 'Freno', 'accel': 'Acelerador'}
    GEAR = (300, 33, 15)

    def __init__(self):
        self.fingers = {}
        self.mouse = None
        self.settings_open = False
        self.moving = False
        self.drag = None
        self.slider_drag = None
        self.cfg = self.load()
        self.font = None
        self.small = None
        try:
            self.font = pygame.font.Font('fonts/evilgeniusbb_bld.ttf', 22)
            self.small = pygame.font.Font('fonts/evilgeniusbb_bld.ttf', 17)
        except Exception:
            self.font = pygame.font.Font(None, 26)
            self.small = pygame.font.Font(None, 20)
        self.rebuild()

    # ---------------------------------------------------------------- configuración

    @staticmethod
    def path():
        try:
            from framework import external
            base = external.data_path
        except Exception:
            base = ''
        return os.path.join(base, 'data', 'racer_controls.json')

    def load(self):
        import json, copy
        cfg = copy.deepcopy(self.DEFAULTS)
        try:
            with open(self.path(), 'r') as f:
                data = json.load(f)
            cfg['opacity'] = max(0.15, min(1.0, float(data.get('opacity', cfg['opacity']))))
            cfg['size'] = max(0.6, min(1.6, float(data.get('size', cfg['size']))))
            for k, v in data.get('pos', {}).items():
                if k in cfg['pos']:
                    cfg['pos'][k] = [float(v[0]), float(v[1])]
        except Exception:
            pass
        return cfg

    def save(self):
        import json
        try:
            with open(self.path(), 'w') as f:
                json.dump(self.cfg, f)
        except Exception as e:
            print('racer: no se pudo guardar la configuración de controles', e)

    def reset(self):
        import copy
        self.cfg = copy.deepcopy(self.DEFAULTS)
        self.rebuild()
        self.save()

    # ---------------------------------------------------------------- dibujo de los controles

    def rebuild(self):
        self.surfaces = {}
        for name in self.BASE:
            self.surfaces[name] = (self._paint(name, False), self._paint(name, True))

    def rect(self, name):
        w, h = self.BASE[name]
        k = self.cfg['size']
        cx, cy = self.cfg['pos'][name]
        return pygame.Rect(int(cx - w * k / 2), int(cy - h * k / 2), int(w * k), int(h * k))

    def _paint(self, name, pressed):
        w, h = self.BASE[name]
        k = self.cfg['size']
        w, h = int(w * k), int(h * k)
        s = pygame.Surface((w, h), SRCALPHA)
        a = int(255 * self.cfg['opacity'])
        white = (255, 255, 255, min(255, a + (60 if pressed else 0)))
        edge = (205, 205, 210, min(255, a + 70))
        hole = (110, 110, 115, min(255, a + 60))
        if name in ('accel', 'brake'):
            r = int(min(w, h) * 0.22)
            body = pygame.Rect(0, 0, w, h)
            if pressed:
                body = body.inflate(-int(w * 0.06), -int(h * 0.06))
            pygame.draw.rect(s, white, body, border_radius=r)
            pygame.draw.rect(s, edge, body, max(2, int(3 * k)), border_radius=r)
            # orificios: pedal largo en filas alternadas de 2 y 3, pedal corto en 4 filas de 8 alternadas
            if name == 'accel':
                rows, cols = 7, 3
            else:
                rows, cols = 4, 8
            hr = max(2, int(min(body.w / (cols * 2.6), body.h / (rows * 2.6))))
            for i in range(rows):
                n = cols if (i % 2 == (0 if name == 'brake' else 1)) else cols - 1
                y = body.top + body.h * (i + 0.75) / (rows + 0.5)
                for j in range(n):
                    x = body.left + body.w * (j + 1 + (0.5 if n < cols else 0)) / (cols + 1)
                    pygame.draw.circle(s, hole, (int(x), int(y)), hr)
        else:
            # punta de flecha (chevron) mirando hacia afuera
            d = -1 if name == 'left' else 1
            cx, cy = w / 2.0, h / 2.0
            tip = (cx + d * w * 0.42, cy)
            back_top = (cx - d * w * 0.34, cy - h * 0.46)
            back_bot = (cx - d * w * 0.34, cy + h * 0.46)
            notch = (cx - d * w * 0.06, cy)
            pts = [tip, back_top, notch, back_bot]
            if pressed:
                pts = [(cx + (px - cx) * 0.9, cy + (py - cy) * 0.9) for px, py in pts]
            pygame.draw.polygon(s, white, pts)
            pygame.draw.polygon(s, edge, pts, max(2, int(3 * k)))
        return s

    def draw(self, screen):
        p = self.pressed()
        for name in self.BASE:
            r = self.rect(name)
            screen.blit(self.surfaces[name][1 if name in p else 0], r.topleft)
            if self.moving:
                pygame.draw.rect(screen, (255, 230, 120), r.inflate(6, 6), 2, border_radius=8)
        self.draw_gear(screen)
        if self.settings_open:
            self.draw_settings(screen)

    def draw_gear(self, screen):
        gx, gy, gr = self.GEAR
        a = 170 if not self.settings_open else 255
        s = pygame.Surface((gr * 2 + 4, gr * 2 + 4), SRCALPHA)
        c = gr + 2
        for i in range(8):
            ang = i * math.pi / 4
            pygame.draw.circle(s, (255, 255, 255, a), (int(c + math.cos(ang) * gr * 0.82), int(c + math.sin(ang) * gr * 0.82)), max(2, gr // 4))
        pygame.draw.circle(s, (255, 255, 255, a), (c, c), int(gr * 0.72))
        pygame.draw.circle(s, (90, 90, 95, a), (c, c), int(gr * 0.72), 2)
        pygame.draw.circle(s, (110, 110, 115, a), (c, c), int(gr * 0.32))
        screen.blit(s, (gx - c, gy - c))

    # ---------------------------------------------------------------- panel de ajustes

    PANEL = pygame.Rect(150, 120, 300, 230)

    def _slider_rect(self, i):
        return pygame.Rect(self.PANEL.left + 30, self.PANEL.top + 70 + i * 52, self.PANEL.w - 60, 8)

    def _buttons(self):
        p = self.PANEL
        return {'move': pygame.Rect(p.left + 20, p.bottom - 52, 120, 34),
                'reset': pygame.Rect(p.right - 140, p.bottom - 52, 120, 34),
                'close': pygame.Rect(p.right - 34, p.top + 8, 26, 26)}

    def _button(self, screen, r, text, active=False):
        s = pygame.Surface(r.size, SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 235 if active else 200), s.get_rect(), border_radius=12)
        pygame.draw.rect(s, (150, 150, 155, 255), s.get_rect(), 2, border_radius=12)
        screen.blit(s, r.topleft)
        t = self.small.render(text, True, (60, 60, 65))
        screen.blit(t, (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))

    def draw_settings(self, screen):
        if self.moving:
            t = self.font.render('Arrastrá los controles', True, (255, 255, 255))
            bg = pygame.Surface((t.get_width() + 30, 34), SRCALPHA)
            pygame.draw.rect(bg, (20, 20, 25, 170), bg.get_rect(), border_radius=14)
            screen.blit(bg, (300 - bg.get_width() // 2, 150))
            screen.blit(t, (300 - t.get_width() // 2, 155))
            self._button(screen, self.done_rect(), 'Listo', True)
            return
        p = self.PANEL
        dim = pygame.Surface(screen.get_size(), SRCALPHA)
        dim.fill((0, 0, 0, 90))
        screen.blit(dim, (0, 0))
        bg = pygame.Surface(p.size, SRCALPHA)
        pygame.draw.rect(bg, (25, 25, 30, 215), bg.get_rect(), border_radius=18)
        pygame.draw.rect(bg, (255, 255, 255, 120), bg.get_rect(), 2, border_radius=18)
        screen.blit(bg, p.topleft)
        t = self.font.render('Controles', True, (255, 255, 255))
        screen.blit(t, (p.centerx - t.get_width() // 2, p.top + 12))
        values = [('Opacidad', (self.cfg['opacity'] - 0.15) / 0.85, '%d%%' % round(self.cfg['opacity'] * 100)),
                  ('Tamaño', (self.cfg['size'] - 0.6) / 1.0, '%d%%' % round(self.cfg['size'] * 100))]
        for i, (label, frac, txt) in enumerate(values):
            r = self._slider_rect(i)
            screen.blit(self.small.render(label, True, (230, 230, 230)), (r.left, r.top - 22))
            vt = self.small.render(txt, True, (230, 230, 230))
            screen.blit(vt, (r.right - vt.get_width(), r.top - 22))
            pygame.draw.rect(screen, (90, 90, 95), r, border_radius=4)
            pygame.draw.rect(screen, (235, 235, 235), (r.left, r.top, int(r.w * frac), r.h), border_radius=4)
            pygame.draw.circle(screen, (255, 255, 255), (r.left + int(r.w * frac), r.centery), 11)
            pygame.draw.circle(screen, (130, 130, 135), (r.left + int(r.w * frac), r.centery), 11, 2)
        b = self._buttons()
        self._button(screen, b['move'], 'Mover')
        self._button(screen, b['reset'], 'Restablecer')
        cr = b['close']
        pygame.draw.circle(screen, (255, 255, 255), cr.center, 13)
        pygame.draw.line(screen, (90, 90, 95), (cr.centerx - 5, cr.centery - 5), (cr.centerx + 5, cr.centery + 5), 3)
        pygame.draw.line(screen, (90, 90, 95), (cr.centerx + 5, cr.centery - 5), (cr.centerx - 5, cr.centery + 5), 3)

    def done_rect(self):
        return pygame.Rect(240, 195, 120, 36)

    def gear_hit(self, pos):
        gx, gy, gr = self.GEAR
        return math.hypot(pos[0] - gx, pos[1] - gy) <= gr + 10

    def _set_slider(self, i, x):
        r = self._slider_rect(i)
        frac = max(0.0, min(1.0, float(x - r.left) / r.w))
        if i == 0:
            self.cfg['opacity'] = round(0.15 + frac * 0.85, 2)
        else:
            self.cfg['size'] = round(0.6 + frac * 1.0, 2)
        self.rebuild()

    def handle_ui(self, event):
        """Eventos del botón de ajustes y del panel. Devuelve True si el evento se usó."""
        if event.type not in (MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP):
            return self.settings_open
        pos = event.pos
        if event.type == MOUSEBUTTONDOWN and getattr(event, 'button', 1) == 1:
            if not self.settings_open:
                if self.gear_hit(pos):
                    self.settings_open = True
                    self.fingers.clear()
                    self.mouse = None
                    return True
                return False
            if self.moving:
                if self.done_rect().collidepoint(pos):
                    self.moving = False
                    self.save()
                    return True
                for name in self.BASE:
                    r = self.rect(name)
                    if r.inflate(16, 16).collidepoint(pos):
                        cx, cy = self.cfg['pos'][name]
                        self.drag = (name, cx - pos[0], cy - pos[1])
                        break
                return True
            b = self._buttons()
            if b['close'].inflate(14, 14).collidepoint(pos) or self.gear_hit(pos):
                self.settings_open = False
                self.save()
            elif b['move'].collidepoint(pos):
                self.moving = True
            elif b['reset'].collidepoint(pos):
                self.reset()
            else:
                for i in range(2):
                    if self._slider_rect(i).inflate(30, 34).collidepoint(pos):
                        self.slider_drag = i
                        self._set_slider(i, pos[0])
            return True
        if event.type == MOUSEMOTION and self.settings_open:
            if self.drag is not None:
                name, dx, dy = self.drag
                w, h = self.rect(name).size
                x = max(w / 2, min(SCREEN_W - w / 2, pos[0] + dx))
                y = max(60 + h / 2, min(SCREEN_H - h / 2, pos[1] + dy))
                self.cfg['pos'][name] = [x, y]
            elif self.slider_drag is not None:
                self._set_slider(self.slider_drag, pos[0])
            return True
        if event.type == MOUSEBUTTONUP and self.settings_open:
            self.drag = None
            if self.slider_drag is not None:
                self.slider_drag = None
                self.save()
            return True
        return self.settings_open

    # ---------------------------------------------------------------- manejo

    def _hit(self, pos):
        best = None
        for name in self.BASE:
            r = self.rect(name).inflate(24, 24)
            if r.collidepoint(pos):
                d = math.hypot(pos[0] - r.centerx, pos[1] - r.centery)
                if best is None or d < best[1]:
                    best = (name, d)
        return best[0] if best else None

    @staticmethod
    def finger_pos(event):
        from framework import presenter
        if presenter.active is not None:
            return presenter.active.finger(event)
        # coordenadas normalizadas de la ventana -> coordenadas lógicas (pygame.SCALED con bandas)
        try:
            ww, wh = pygame.display.get_window_size()
        except Exception:
            ww, wh = SCREEN_W, SCREEN_H
        scale = min(float(ww) / SCREEN_W, float(wh) / SCREEN_H)
        ox = (ww - SCREEN_W * scale) / 2.0
        oy = (wh - SCREEN_H * scale) / 2.0
        return ((event.x * ww - ox) / scale, (event.y * wh - oy) / scale)

    def handle(self, event):
        if self.settings_open:
            return False
        if event.type == FINGERDOWN or event.type == FINGERMOTION:
            self.fingers[event.finger_id] = self._hit(self.finger_pos(event))
            return True
        if event.type == FINGERUP:
            self.fingers.pop(event.finger_id, None)
            return True
        if getattr(event, 'touch', False):
            return False   # eventos de mouse simulados por los toques: ya se procesaron como dedos
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.mouse = self._hit(event.pos)
        elif event.type == MOUSEMOTION and self.mouse is not None:
            self.mouse = self._hit(event.pos)
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            self.mouse = None
        return False

    def pressed(self):
        if self.settings_open:
            return set()
        p = set(v for v in self.fingers.values() if v)
        if self.mouse:
            p.add(self.mouse)
        return p


class Racer:

    def __init__(self, screen, thief_image, avatar_image, time_of_day, map_file, color):
        self.screen = screen
        self.view = pygame.Surface((SCREEN_W, SCREEN_H)).convert() if screen.get_size() != (SCREEN_W, SCREEN_H) else screen
        self.assets = A = Assets()
        self.car_def = _load_yaml('data/car.yaml')
        self.gui = _load_yaml('data/gui.yaml')
        self.map = _load_yaml(map_file)
        self.thief_def = _load_yaml('data/thief.yaml')
        self.traffic_def = _load_yaml('data/traffic.yaml')
        cam = _load_yaml('data/camera.yaml') or {}
        self.z_near = float(cam.get('z_near', 7))
        self.touch = TouchControls()
        self.show_touch = IS_ANDROID or bool(os.environ.get('DET_TOUCH'))

        # cielo
        sky = self.map.get('sky', {})
        self.sky_color = _color(sky.get('color', '232442'))
        bgs = sky.get('backgrounds', {})
        bg = bgs.get(time_of_day) or bgs.get('noon') or {}
        self.sky_bg = A.image(bg['texture']) if bg else None
        self.sky_bg_speed = float(bg.get('speed', 120)) if bg else 0
        self.sky_layers = [(A.image(l['texture']), float(l.get('speed', 200))) for l in sky.get('layers', []) or []]
        self.sky_offset = 0.0

        # terreno
        terr = self.map.get('terrain', [{}])[0]
        tt = terr.get('texture', {})
        self.floor = A.image(tt.get('image'))
        self.floor_w_units = float(tt.get('w', 86))
        self.floor_h_units = float(tt.get('h', 10))
        self.left_fill = _color(terr.get('left_fill', '5f9e43'))
        self.right_fill = _color(terr.get('right_fill', '5f9e43'))
        self.materials = {'left': [], 'right': []}
        for side in ('left', 'right'):
            for m in (terr.get('materials', {}) or {}).get(side, []) or []:
                self.materials[side].append({
                    'from': float(m.get('from', 8)), 'to': float(m.get('to', 50)),
                    'anim': Animation(A, m.get('animation')),
                    'sound': A.sound(m.get('sound_effect')),
                    'rolling': float(m.get('rolling_resistance', 300))})
        self.mat_side = None
        self.mat_def = None

        # filas del piso: z de cada fila de pantalla (piso plano)
        self.rows = []
        for y in range(HORIZON + 1, SCREEN_H):
            z = CAM_HEIGHT * FOCAL / (y - HORIZON)
            self.rows.append((y, z))

        self.track = Track(self.map)
        self.lanes = [float(l) for l in self.map.get('lanes', [3.5, -3.5])]
        self.time_limit = float(self.map.get('time', 180000)) / 1000.0
        self.exit_time = float(self.map.get('exit_time', 3000)) / 1000.0

        # objetos fijos y aleatorios
        self.fixed_objects = self.map.get('objects', []) or []
        self.random_groups = self.map.get('random_objects', {}) or {}
        self.objects = []
        self.generated_to = 0.0
        self.random_next = {'left': 0.0, 'right': 0.0}
        self.piece_objects_done = set()

        # auto del jugador
        cd = self.car_def
        self.gears = [float(g) for g in cd['acceleration']['gears']]
        self.power = float(cd['acceleration'].get('power', 14))
        self.drag = float(cd.get('drag', 0.9))
        self.rolling = float(cd.get('rolling_resistance', 85))
        self.mass = float(cd.get('mass', 2000))
        self.brake = float(cd.get('break', 150))
        self.extra_res = float(cd.get('extra_resistance', 30))
        self.max_rpm = float(cd.get('max_rpm', 300))
        self.restitution = float(cd.get('restitution', 0.5))
        self.car_width = float(cd.get('width', 3))
        self.car_length = float(cd.get('length', 8))
        corn = cd.get('cornering', {})
        self.corner_slow = float(corn.get('slow', 0.55))
        self.corner_fast = float(corn.get('fast', 0.48))
        self.corner_speed = float(corn.get('speed', 4.5))
        self.max_wheels_speed = float(cd.get('max_wheels_speed', 100))
        self.min_material_speed = float(cd.get('min_material_effect_speed', 20))
        self.sprites = []
        for sp in cd.get('sprites', []):
            entry = {'to': float(sp.get('to', 1)), 'mt': float(sp.get('material_translation', 0))}
            for side in ('both', 'left', 'right'):
                if side in sp:
                    s = sp[side]
                    entry[side] = {
                        'car': (A.image(s['car']['image']), s['car'].get('y_translation', 0)),
                        'wheels': Animation(A, s.get('wheels')),
                        'siren': (s.get('siren', {}).get('x', 0), s.get('siren', {}).get('y', -139))}
            self.sprites.append(entry)
        fin = cd.get('finishing', {})
        self.fin_close = float(fin.get('close_distance', 3.5))
        self.fin_decel = float(fin.get('deacceleration', 100))
        hc = cd.get('hard_crash', {})
        self.crash_duration = float(hc.get('duration', 1))
        self.crash_anim = {'left': Animation(A, hc.get('left', {}).get('animation'), False),
                           'right': Animation(A, hc.get('right', {}).get('animation'), False)}
        ct = cd.get('caught_thief', {})
        self.catch_anim = {'left': Animation(A, ct.get('left', {}).get('animation'), False),
                           'right': Animation(A, ct.get('right', {}).get('animation'), False)}
        self.smoke = Animation(A, cd.get('smoke', {}).get('animation'), False)
        self.smoke.done = True
        sir = cd.get('siren', {})
        self.siren_anim = Animation(A, sir.get('animation'))
        self.siren_distance = float(sir.get('start_distance', 150))
        snd = cd.get('sounds', {})
        self.snd_engine = A.sound(snd.get('engine'))
        self.snd_brake = A.sound(snd.get('break'))
        self.snd_light_crash = A.sound(snd.get('light_crash'))
        self.snd_hard_crash = A.sound(snd.get('hard_crash'))
        self.snd_siren = A.sound(snd.get('siren'))

        # ladrón
        td = self.thief_def
        tex = td.get('textures', {})
        self.thief_sprites = AngleSprites(A, tex.get(color) or tex.get('violet'))
        self.thief_speed = float(td.get('speed', 145))
        self.thief_side_speed = float(td.get('sideways_speed', 7))
        self.thief_arrow = Animation(A, td.get('arrow', {}).get('animation'))
        self.thief_arrow_y = float(td.get('arrow', {}).get('y', 3))
        self.thief = Car(self.thief_sprites, float(td.get('width', 2)), 120.0, self.lanes[0], 0.0)

        # tránsito
        tr = self.traffic_def
        self.traffic_defs = []
        for c in tr.get('cars', []):
            self.traffic_defs.append((AngleSprites(A, c.get('textures')), float(c.get('width', 2)), A.sound(c.get('engine'))))
        self.traffic_min_speed = float(tr.get('min_speed', 90))
        self.traffic_min_dist = float(tr.get('min_distance', 90))
        self.traffic_max_dist = float(tr.get('max_distance', 400))
        self.traffic = []
        self.traffic_next_z = 250.0

        # interfaz
        g = self.gui
        self.statics = [(A.image(s['texture']), (s['pos']['x'], s['pos']['y']), float(s.get('z', 0))) for s in g.get('statics', [])]
        fb = g.get('fuel_bar', {})
        self.fuel = (_color(fb.get('color', 'FAEA00')), fb['pos']['x'], fb['pos']['y'], fb.get('w', 101), fb.get('h', 7), A.image(fb['end']) if fb.get('end') else None)
        db = g.get('distance_bar', {})
        self.dist_filler = A.image(db['filler'])
        self.dist_pos = (db['pos']['x'], db['pos']['y'])
        self.dist_max = float(db.get('max_distance', 500))
        dend = db.get('end', {})
        self.dist_end = (A.image(dend['texture']), dend.get('diff_x', -8), dend.get('pos', {}).get('y', 21)) if dend else None
        mo = g.get('mileometer', {})
        self.speed_ratio = float(mo.get('speed_ratio', 0.7))
        self.digits = [A.image(n) for n in mo.get('numbers', [])]
        self.digit_pos = [(p['x'], p['y']) for p in mo.get('pos', [])]
        ed = g.get('exit_dialog', {})
        self.exit_bg = (A.image(ed['background']['src']), (ed['background']['pos']['x'], ed['background']['pos']['y']))
        # en YAML 1.1 las claves yes/no se leen como booleanos
        ey = ed.get('yes', ed.get(True))
        en = ed.get('no', ed.get(False))
        self.exit_yes = (A.image(ey['src']), (ey['pos']['x'], ey['pos']['y']))
        self.exit_no = (A.image(en['src']), (en['pos']['x'], en['pos']['y']))
        self.warn_sound = A.sound(g.get('low_fuel_sound'))
        self.sign_low_fuel = Blink(A, g.get('low_fuel_warning', {}), self.warn_sound)
        self.sign_no_fuel = Blink(A, g.get('no_fuel_sign', {}))
        self.sign_win = Blink(A, g.get('win_sign', {}))
        self.sign_thief = Blink(A, g.get('thief_near_sign', {}), self.warn_sound)
        self.fuel_warning_time = float(g.get('fuel_warning_time', 18))
        self.thief_warning_distance = float(g.get('thief_warning_distance', 150))
        ta = g.get('thief_avatar', {})
        self.thief_avatar = (A.image(thief_image), (ta.get('pos', {}).get('x', 498), ta.get('pos', {}).get('y', 11)))
        pa = g.get('player_avatar', {})
        self.player_avatar = (A.image(avatar_image), (pa.get('pos', {}).get('x', 16), pa.get('pos', {}).get('y', 14)))

        # música
        mus = self.map.get('music', {})
        self.music = mus
        self.music_state = None

        # estado
        self.z = 0.0
        self.x = self.lanes[0]
        self.speed = 0.0
        self.gear = 0
        self.steer = 0.0
        self.road_tan = 0.0
        self.car_tan = 0.0
        self.time = 0.0
        self.state = 0              # 0 carrera, 1 atrapando, 2 sin combustible, 3 cartel final, 4 salir
        self.won = False
        self.end_t = 0.0
        self.crash_t = 0.0
        self.crash_side = 'left'
        self.crash_vx = 0.0
        self.siren_on = False
        self.thief_warned = False
        self.exit_dialog = False
        self.exit_choice = 1        # 0 sí, 1 no
        self.prev_keys = set()
        self.channels = {}
        self.generate_objects(DRAW_DISTANCE + 100)

    # ---------------------------------------------------------------- sonido

    def loop_sound(self, key, snd, volume=None):
        if snd is None:
            return
        ch = self.channels.get(key)
        if ch is None or not ch.get_busy() or ch.get_sound() is not snd:
            ch = snd.play(-1)
            self.channels[key] = ch
        if ch is not None and volume is not None:
            ch.set_volume(max(0.0, min(1.0, volume)))

    def stop_sound(self, key):
        ch = self.channels.pop(key, None)
        if ch is not None:
            ch.stop()

    def play_music(self, name, loops=0, start=0.0):
        spec = self.music.get(name)
        if not spec or not pygame.mixer.get_init():
            return False
        path = spec.get('sound')
        if not path or not os.path.exists(path):
            return False
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(float(spec.get('volume', 1)) * settings.music_volume())
            pygame.mixer.music.play(loops, start)
            self.music_state = name
            return True
        except Exception as e:
            print('racer: música', path, e)
            return False

    def update_music(self):
        if not pygame.mixer.get_init():
            return
        if self.music_state in ('start', 'loop', None) and self.state in (0, 1, 2):
            if not pygame.mixer.music.get_busy():
                if self.music_state == 'loop':
                    self.play_music('loop', 0, float(self.music.get('loop', {}).get('loop_start', 0)))
                else:
                    self.play_music('loop', 0)

    # ---------------------------------------------------------------- mundo

    def generate_objects(self, upto):
        while self.generated_to < upto:
            z0 = self.generated_to
            z1 = z0 + 100.0
            self.track.ensure(z1 + 300)
            for o in self.fixed_objects:
                f, t, dz = float(o.get('from', 0)), float(o.get('to', 1e9)), float(o.get('dz', 50))
                k = math.ceil(max(z0, f) / dz) * dz
                while k < min(z1, t):
                    self.objects.append(WorldObject(float(o['x']), k, float(o['w']), float(o['h']), self.assets.image(o['texture']), o.get('body')))
                    k += dz
            for p in self.track.pieces:
                key = id(p)
                if key in self.piece_objects_done or p.start > z1:
                    continue
                self.piece_objects_done.add(key)
                for o in p.objects:
                    f, t, dz = float(o.get('from', 0)), float(o.get('to', 0)), float(o.get('dz', 50))
                    k = f
                    while k <= t:
                        self.objects.append(WorldObject(float(o['x']), p.start + k, float(o['w']), float(o['h']), self.assets.image(o['texture']), o.get('body')))
                        k += dz
            for side in ('left', 'right'):
                groups = self.random_groups.get(side) or []
                while groups and self.random_next[side] < z1:
                    grp = random.choice(groups)
                    base = self.random_next[side]
                    ln = float(grp.get('length', 250))
                    for o in grp.get('objects', []):
                        dz = float(o.get('dz', 50))
                        k = dz * 0.5
                        while k < ln:
                            self.objects.append(WorldObject(float(o['x']), base + k, float(o['w']), float(o['h']), self.assets.image(o['texture']), o.get('body')))
                            k += dz
                    self.random_next[side] = base + ln
            self.generated_to = z1
        cut = self.z - 50
        if len(self.objects) > 600 or (self.objects and self.objects[0].z < cut - 200):
            self.objects = [o for o in self.objects if o.z >= cut]

    def spawn_traffic(self):
        # RE: se generan autos hasta 600 adelante con separación aleatoria; se borran 900 atrás
        while self.traffic_next_z < self.z + DRAW_DISTANCE:
            sprites, width, snd = random.choice(self.traffic_defs)
            speed = self.traffic_min_speed + random.random() * max(0.0, self.thief_speed * 0.8 - self.traffic_min_speed)
            lane = random.choice(self.lanes)
            if abs(self.traffic_next_z - self.thief.z) < 40 and abs(lane - self.thief.x) < 3:
                lane = -lane
            car = Car(sprites, width, self.traffic_next_z, lane, speed)
            car.sound = snd
            self.traffic.append(car)
            self.traffic_next_z += self.traffic_min_dist + random.random() * (self.traffic_max_dist - self.traffic_min_dist)
        self.traffic = [c for c in self.traffic if self.z - c.z < 60 and c.z - self.z < BEHIND_DISTANCE]

    # ---------------------------------------------------------------- física

    def material_at(self, x):
        side = 'left' if x < 0 else 'right'
        ax = abs(x)
        for m in self.materials[side]:
            if m['from'] <= ax < m['to']:
                return side, m
        return side, None

    def engine_accel(self):
        g = self.gears[self.gear]
        rpm = max(50.0, self.speed * g)                       # RE: rpm mínimo 50
        if rpm > self.max_rpm + 100 and self.gear < len(self.gears) - 1:
            self.gear += 1                                    # RE: sube de marcha
            self.smoke.reset()
        elif self.gear > 0 and self.gears[self.gear - 1] * self.speed < self.max_rpm - 20:
            self.gear -= 1                                    # RE: baja de marcha
        g = self.gears[self.gear]
        rpm = max(50.0, self.speed * g)
        if rpm <= self.max_rpm:
            torque = rpm
        else:
            torque = max(0.0, 2 * self.max_rpm - rpm * 1.2)   # RE: (2·max - 1.2·rpm)
        return torque * self.power / 100.0

    def update(self, keys):
        dt = DT
        self.time += dt
        accel_key = 'accel' in keys and self.state == 0
        brake_key = 'brake' in keys and self.state == 0
        steer_in = 0
        if self.state == 0 and self.crash_t <= 0:
            if 'left' in keys:
                steer_in -= 1
            if 'right' in keys:
                steer_in += 1

        side, mat = self.material_at(self.x)
        rolling = mat['rolling'] if mat else self.rolling
        resistance = (-self.speed * self.speed * self.drag - rolling * self.speed) / self.mass   # RE
        if self.state == 1:
            a = -self.fin_decel if self.speed > self.thief.speed * 0.5 else resistance
        elif self.state in (2, 3):
            a = resistance - self.extra_res
        elif self.crash_t > 0:
            a = resistance - self.extra_res
        elif brake_key:
            a = -self.brake                                   # RE: freno
        elif accel_key:
            a = self.engine_accel() + resistance
        else:
            a = resistance - self.extra_res                   # RE: extra_resistance al soltar
        if accel_key:
            self.loop_sound('engine', self.snd_engine)
        if brake_key and self.speed > 15:
            self.loop_sound('brake', self.snd_brake)
        else:
            self.stop_sound('brake')
        self.speed = max(0.0, self.speed + a * dt)
        if self.snd_engine is not None and 'engine' in self.channels:
            ch = self.channels['engine']
            if ch:
                ch.set_volume(0.35 + 0.65 * min(1.0, self.speed / 180.0))

        # dirección (RE: handle_cornering: el volante vuelve a 0 a la misma velocidad)
        rate = self.corner_speed
        if steer_in:
            self.steer = max(-1.0, min(1.0, self.steer + steer_in * rate * dt))
        elif self.steer:
            d = rate * dt
            self.steer = 0.0 if abs(self.steer) <= d else self.steer - math.copysign(d, self.steer)
        # RE: PlayerCar::cornering_displacement = atan(v·dt·slow)·(fast·volante)
        lateral = math.atan(self.speed * dt * self.corner_slow) * self.corner_fast * self.steer
        dz = self.speed * dt
        # RE: el auto sigue la tangente del camino con retraso (0.25·anterior + 0.75·actual): en las curvas
        # se abre un poco hacia afuera
        curv = self.track.curvature(self.z)
        self.road_tan += curv * dz
        self.car_tan = 0.25 * self.car_tan + 0.75 * self.road_tan
        lateral += (self.car_tan - self.road_tan) * dz
        if self.crash_t > 0:
            self.crash_t -= dt
            lateral += self.crash_vx * dt
        new_x = self.x + lateral
        limit = self.track.width
        new_x = max(-limit, min(limit, new_x))

        # choques con objetos
        if self.state == 0 and self.crash_t <= 0:
            for o in self.objects:
                if o.body_w <= 0 or o.z < self.z or o.z > self.z + dz + 1.0:
                    continue
                ox = o.x + o.body_x
                if abs(new_x - ox) < (o.body_w + self.car_width) * 0.5:
                    self.hard_crash(1.0 if new_x > ox else -1.0)
                    new_x = self.x
                    break
        # choques con el tránsito (RE: rebote con restitución)
        for c in self.traffic:
            if c.z - self.z < self.car_length * 0.6 and c.z - self.z > -1 and abs(new_x - c.x) < (c.width + self.car_width) * 0.5:
                if self.speed > c.speed and not settings.get('ghost'):
                    self.speed = max(0.0, self.speed - (1 + self.restitution) * (self.speed - c.speed))
                    if self.snd_light_crash:
                        self.snd_light_crash.play()
                    self.steer = 0.0
                    c.z = self.z + self.car_length * 0.6 + 0.5
                    dz = 0.0
        self.x = new_x
        self.z += dz
        self.sky_offset += curv * self.speed * dt * 0.6

        # material: animaciones y sonido
        if mat and self.speed > 1:
            for m in self.materials[side]:
                m['anim'].step(dt)
            if mat['sound'] is not None:
                self.loop_sound('material', mat['sound'])
        else:
            self.stop_sound('material')
        self.mat_side = side if (mat and self.speed > 1) else None
        self.mat_def = mat

        # ladrón
        t = self.thief
        if self.state in (0, 2):
            t.speed = min(self.thief_speed, t.speed + 60 * dt)
        elif self.state == 1:
            t.speed = max(0.0, t.speed - self.fin_decel * dt)
        else:
            t.speed = max(0.0, t.speed - 40 * dt)
        ahead = [c for c in self.traffic if 0 < c.z - t.z < 70 and abs(c.x - t.target_x) < 3]
        if ahead and self.state in (0, 2):
            # esquiva por el otro carril sólo si está libre; si no, se queda detrás del auto
            for lane in self.lanes:
                if abs(lane - t.target_x) > 1 and not any(-12 < c.z - t.z < 70 and abs(c.x - lane) < 3 for c in self.traffic):
                    t.target_x = lane
                    break
            else:
                near = min(ahead, key=lambda c: c.z)
                if near.z - t.z < 25:
                    t.speed = min(t.speed, near.speed)
        if t.x != t.target_x:
            d = self.thief_side_speed * dt
            t.x = t.target_x if abs(t.target_x - t.x) <= d else t.x + math.copysign(d, t.target_x - t.x)
        t.z += t.speed * dt
        for c in self.traffic:
            c.z += c.speed * dt

        dist = t.z - self.z
        if self.state == 0:
            # RE: se alcanza al ladrón
            if dist < self.car_length * 0.5 + self.fin_close and abs(t.x - self.x) < (t.width + self.car_width) * 0.5 + 1.5:
                self.state = 1
                self.won = True
                self.catch_side = 'right' if self.x > t.x else 'left'
                self.catch_anim[self.catch_side].reset()
                self.speed = min(self.speed, t.speed + 5)
                self.sign_win.start()
                self.stop_sound('material')
                if self.snd_brake:
                    self.snd_brake.play()
            elif dist < 0:
                t.z = self.z + 1.0
            elif self.time >= self.time_limit and not settings.get('ghost'):
                self.state = 2                                  # RE: sin combustible
                self.won = False
                self.sign_no_fuel.start()
                self.stop_sound('engine')
            if self.state == 0 and not settings.get("ghost") and self.time_limit - self.time < self.fuel_warning_time:
                if not getattr(self, 'fuel_warned', False):
                    self.fuel_warned = True
                    self.sign_low_fuel.start()
            if self.state == 0 and dist < self.thief_warning_distance and not self.thief_warned:
                self.thief_warned = True
                self.sign_thief.start()
        if self.state == 1:
            self.catch_anim[self.catch_side].step(dt)
            self.z = min(self.z, t.z - 2.0)
            self.x += (t.x - self.x) * min(1.0, dt * 3)
            if self.speed <= 1 and t.speed <= 1:
                self.state = 3
                self.end_t = 0.0
        if self.state == 2 and self.speed <= 0.5:
            self.state = 3
            self.end_t = 0.0
        if self.state == 3 and self.end_t == 0.0:
            self.stop_sound('engine')
            self.stop_sound('siren')
            pygame.mixer.music.stop()
            self.play_music('win' if self.won else 'lose')
            self.music_state = 'end'
        if self.state == 3:
            self.end_t += dt
            if self.end_t > self.exit_time:
                self.state = 4

        # sirena
        if dist < self.siren_distance and self.state in (0, 1):
            self.siren_on = True
        if self.siren_on:
            self.siren_anim.step(dt)
            if self.state in (0, 1):
                self.loop_sound('siren', self.snd_siren)
            else:
                self.stop_sound('siren')
        for s in (self.sign_low_fuel, self.sign_no_fuel, self.sign_win, self.sign_thief):
            s.step(dt)
        self.smoke.step(dt)
        self.thief_arrow.step(dt)
        for sp in self.sprites:
            for side in ('both', 'left', 'right'):
                if side in sp:
                    sp[side]['wheels'].step(dt * min(1.0, self.speed / self.max_wheels_speed) if self.speed > 0.5 else 0)
        if self.crash_t > 0:
            self.crash_anim[self.crash_side].step(dt)

        self.generate_objects(self.z + DRAW_DISTANCE + 100)
        self.spawn_traffic()
        self.update_music()

    def hard_crash(self, direction):
        if settings.get('ghost'):
            return      # modo fantasma: los choques no hacen nada
        # RE: start_hard_crash: el auto gira y pierde velocidad
        self.crash_t = self.crash_duration
        self.crash_side = 'left' if direction < 0 else 'right'
        self.crash_anim[self.crash_side].reset()
        self.crash_vx = direction * min(8.0, self.speed * 0.08)
        self.speed = min(self.speed, max(0.0, self.speed * 0.35))
        self.steer = 0.0
        if self.snd_hard_crash:
            self.snd_hard_crash.play()

    # ---------------------------------------------------------------- dibujo

    def road_offsets(self):
        # desplazamiento lateral del centro del camino para cada fila (integra la curvatura)
        cam_z = self.z - self.z_near
        zs = [z for (_, z) in self.rows]   # de cerca (abajo) a lejos (arriba) en orden inverso
        offs = {}
        x = 0.0
        dx = 0.0
        prev = 0.0
        for z in sorted(zs):
            step = z - prev
            c = self.track.curvature(cam_z + z)
            dx += c * step
            x += dx * step
            offs[z] = x
            prev = z
        self.road_dx_far = dx
        return offs

    def offset_at(self, dist):
        # desplazamiento lateral del camino a una distancia arbitraria de la cámara
        cam_z = self.z - self.z_near
        x = dx = 0.0
        z = 0.0
        step = 10.0
        while z < dist:
            s = min(step, dist - z)
            c = self.track.curvature(cam_z + z)
            dx += c * s
            x += dx * s
            z += s
        return x

    def project(self, wx, wz, offset):
        d = wz - (self.z - self.z_near)
        if d < 1.0:
            return None
        sx = SCREEN_W * 0.5 + (wx + offset - self.x) * FOCAL / d
        sy = HORIZON + CAM_HEIGHT * FOCAL / d
        return sx, sy, FOCAL / d

    def draw(self):
        scr = self.view
        A = self.assets
        # cielo
        scr.fill(self.sky_color, (0, 0, SCREEN_W, HORIZON + 1))
        if self.sky_bg is not None:
            w = self.sky_bg.get_width()
            ox = int(-self.sky_offset * self.sky_bg_speed) % w
            y = HORIZON + 1 - self.sky_bg.get_height()
            scr.blit(self.sky_bg, (ox - w, y))
            scr.blit(self.sky_bg, (ox, y))
        for img, speed in self.sky_layers:
            w = img.get_width()
            ox = int(-self.sky_offset * speed) % w
            y = HORIZON + 1 - img.get_height()
            scr.blit(img, (ox - w, y))
            scr.blit(img, (ox, y))

        # piso (RE: draw_road_line, una fila de textura por línea de pantalla)
        offs = self.road_offsets()
        cam_z = self.z - self.z_near
        tex = self.floor
        tw, th = tex.get_size()
        half_units = self.floor_w_units * 0.5
        px_per_unit = tw / self.floor_w_units
        for y, z in self.rows:
            off = offs[z]
            units_per_px = z / FOCAL
            # x del mundo en el borde izquierdo y derecho de la pantalla, relativo al centro del camino
            wl = self.x - off + (0 - SCREEN_W * 0.5) * units_per_px
            wr = wl + SCREEN_W * units_per_px
            v = int(((cam_z + z) % self.floor_h_units) / self.floor_h_units * th)
            v = th - 1 - v
            # recorte de la textura dentro de [-half, half]
            tl = max(wl, -half_units)
            tr = min(wr, half_units)
            if wl < -half_units:
                xe = int((-half_units - wl) / units_per_px) + 1
                scr.fill(self.left_fill, (0, y, min(SCREEN_W, xe), 1))
            if wr > half_units:
                xs = int((half_units - wl) / units_per_px)
                if xs < SCREEN_W:
                    scr.fill(self.right_fill, (max(0, xs), y, SCREEN_W - max(0, xs), 1))
            if tr > tl:
                u0 = int((tl + half_units) * px_per_unit)
                u1 = int(math.ceil((tr + half_units) * px_per_unit))
                u1 = min(tw, max(u0 + 1, u1))
                sx0 = int((tl - wl) / units_per_px)
                sx1 = int(math.ceil((tr - wl) / units_per_px))
                width = max(1, sx1 - sx0)
                row = tex.subsurface((u0, v, u1 - u0, 1))
                scr.blit(pygame.transform.scale(row, (width, 1)), (sx0, y))

        # objetos, tránsito y ladrón (de lejos a cerca)
        items = []
        far = cam_z + DRAW_DISTANCE
        for o in self.objects:
            if cam_z + 1.5 < o.z < far:
                items.append((o.z, 0, o))
        for c in self.traffic:
            if cam_z + 1.5 < c.z < far:
                items.append((c.z, 1, c))
        if cam_z + 1.5 < self.thief.z < far + 400:
            items.append((self.thief.z, 2, self.thief))
        items.sort(key=lambda it: -it[0])
        cache = {}

        def off_for(z):
            d = z - cam_z
            k = int(d / 4)
            if k not in cache:
                cache[k] = self.offset_at(k * 4.0)
            return cache[k]

        for z, kind, ob in items:
            off = off_for(z)
            p = self.project(ob.x, z, off)
            if p is None:
                continue
            sx, sy, sc = p
            if kind == 0:
                w, h, img = ob.w * sc, ob.h * sc, ob.tex
            else:
                ang = math.degrees(math.atan2(ob.x + off - self.x, z - cam_z))
                img, wu, hu = ob.sprites.get(ang)
                w, h = wu * sc, hu * sc
            if sx + w * 0.5 < 0 or sx - w * 0.5 > SCREEN_W or h < 1:
                continue
            s = A.scale(img, w, h)
            if s is not None:
                scr.blit(s, (int(sx - s.get_width() * 0.5), int(sy - s.get_height())))
            if kind == 2 and self.state == 0 and z - self.z < self.thief_warning_distance * 2:
                fr = self.thief_arrow.frame()
                if fr:
                    ay = HORIZON + CAM_HEIGHT * FOCAL / (z - cam_z) - (hu + self.thief_arrow_y) * sc
                    k = min(1.0, sc / 15.0)
                    a_img = A.scale(fr[0], fr[0].get_width() * k, fr[0].get_height() * k)
                    if a_img is not None:
                        scr.blit(a_img, (int(sx - a_img.get_width() * 0.5), int(ay - a_img.get_height() + fr[3] * k)))

        self.draw_player(scr)

        # interfaz (RE: statics ordenados por z, el más chico más cerca)
        for img, pos, z in sorted(self.statics, key=lambda s: -s[2]):
            if z >= 5:
                scr.blit(img, pos)
        av, pos = self.player_avatar
        scr.blit(av, pos)
        av, pos = self.thief_avatar
        scr.blit(av, pos)
        for img, pos, z in sorted(self.statics, key=lambda s: -s[2]):
            if z < 5:
                scr.blit(img, pos)
        color, fx, fy, fw, fh, fend = self.fuel
        frac = 1.0 if settings.get("ghost") else max(0.0, 1.0 - self.time / self.time_limit)
        bw = int(fw * frac)
        if bw > 0:
            scr.fill(color, (fx, fy, bw, fh))
        if fend is not None and bw > 0:
            scr.blit(fend, (fx + bw - fend.get_width() // 2, fy))
        dist = max(0.0, self.thief.z - self.z)
        dfrac = min(1.0, dist / self.dist_max)
        dw = int(self.dist_filler.get_width() * dfrac)
        if dw > 0:
            scr.blit(self.dist_filler, self.dist_pos, (0, 0, dw, self.dist_filler.get_height()))
        if self.dist_end:
            img, dx, dy = self.dist_end
            scr.blit(img, (self.dist_pos[0] + dw + dx, dy))
        shown = int(self.speed * self.speed_ratio)
        digits = str(shown)
        for i, pos in enumerate(self.digit_pos):
            if i < len(digits) and self.digits:
                d = int(digits[-1 - i])
                scr.blit(self.digits[d], pos)
        for s in (self.sign_thief, self.sign_low_fuel, self.sign_no_fuel, self.sign_win):
            s.draw(scr)
        if self.show_touch and self.state == 0 and not self.exit_dialog:
            self.touch.draw(scr)
        if self.exit_dialog:
            img, pos = self.exit_bg
            scr.blit(img, pos)
            img, pos = self.exit_yes if self.exit_choice == 0 else self.exit_no
            scr.blit(img, pos)
        if self.view is not self.screen:
            pygame.transform.scale(self.view, self.screen.get_size(), self.screen)

    def draw_player(self, scr):
        bottom = SCREEN_H
        if self.state == 1 and self.catch_anim[self.catch_side].frames:
            fr = self.catch_anim[self.catch_side].frame()
            img = fr[0]
            scr.blit(img, (SCREEN_W // 2 - img.get_width() // 2, bottom - img.get_height() + fr[2]))
            return
        if self.crash_t > 0 and self.crash_anim[self.crash_side].frames:
            fr = self.crash_anim[self.crash_side].frame()
            img = fr[0]
            scr.blit(img, (SCREEN_W // 2 - img.get_width() // 2, bottom - img.get_height() + fr[2]))
            return
        a = abs(self.steer)
        entry = self.sprites[-1]
        for sp in self.sprites:
            if a <= sp['to']:
                entry = sp
                break
        if 'both' in entry:
            s = entry['both']
        else:
            s = entry['left'] if self.steer < 0 else entry['right']
        # RE: PlayerSprite: centrado abajo, sin escala, desplazado y_translation
        img, ytr = s['car']
        x = SCREEN_W // 2 - img.get_width() // 2
        y = bottom - img.get_height() + ytr
        if not self.smoke.done:
            fr = self.smoke.frame()
            if fr:
                scr.blit(fr[0], (SCREEN_W // 2 - fr[0].get_width() // 2, bottom - fr[0].get_height() + 5))
        if self.mat_side and self.speed > self.min_material_speed * 0.25 and self.mat_def:
            fr = self.mat_def['anim'].frame()
            if fr:
                fx = SCREEN_W // 2 - fr[0].get_width() // 2 + (-60 if self.mat_side == 'left' else 60)
                scr.blit(fr[0], (fx, bottom - fr[0].get_height() + int(entry['mt'])))
        scr.blit(img, (x, y))
        wf = s['wheels'].frame()
        if wf:
            wimg = wf[0]
            scr.blit(wimg, (SCREEN_W // 2 - wimg.get_width() // 2, bottom - wimg.get_height() + wf[2]))
        if self.siren_on:
            fr = self.siren_anim.frame()
            if fr:
                sx, sy = s['siren']
                scr.blit(fr[0], (SCREEN_W // 2 + sx, bottom + sy))

    # ---------------------------------------------------------------- bucle

    def keys_pressed(self):
        k = pygame.key.get_pressed()
        p = set()
        # RE: UP/KP9/a acelera, DOWN/KP3/z frena, LEFT/KP4/KP7 izquierda, RIGHT/KP6/KP1 derecha
        if k[K_UP] or k[K_KP9] or k[K_a] or k[K_PAGEUP] or k[K_KP8]:
            p.add('accel')
        if k[K_DOWN] or k[K_KP3] or k[K_z] or k[K_PAGEDOWN] or k[K_KP2]:
            p.add('brake')
        if k[K_LEFT] or k[K_KP4] or k[K_KP7] or k[K_HOME]:
            p.add('left')
        if k[K_RIGHT] or k[K_KP6] or k[K_KP1] or k[K_END]:
            p.add('right')
        if getattr(self, 'autopilot', False):
            # sólo pruebas: acelera y sigue el carril del ladrón esquivando el tránsito
            p.add('accel')
            target = self.thief.x
            for c in self.traffic:
                if 0 < c.z - self.z < 90 and abs(c.x - target) < 3:
                    target = -c.x
            if self.x < target - 1.2 + 0.4 * (self.steer > 0):
                p.add('right')
            elif self.x > target + 1.2 - 0.4 * (self.steer < 0):
                p.add('left')
        p |= self.touch.pressed()
        return p

    def dialog_hit(self, pos):
        for i, (img, p) in enumerate((self.exit_yes, self.exit_no)):
            if pygame.Rect(p, img.get_size()).inflate(20, 20).collidepoint(pos):
                return i
        return None

    def run(self):
        clock = pygame.time.Clock()
        if not self.play_music('start'):
            self.play_music('loop')
        last = pygame.time.get_ticks()
        test = os.environ.get('DET_RACER_TEST')
        frame = 0
        while self.state != 4:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.state = 4
                    self.won = False
                    pygame.event.post(pygame.event.Event(QUIT))
                    break
                if self.show_touch and self.state == 0 and not self.exit_dialog and self.touch.handle_ui(event):
                    continue
                if not self.exit_dialog:
                    self.touch.handle(event)
                if event.type == KEYDOWN:
                    if event.key in (K_ESCAPE, K_AC_BACK) and self.touch.settings_open:
                        self.touch.settings_open = False
                        self.touch.moving = False
                        self.touch.save()
                    elif event.key in (K_ESCAPE, K_AC_BACK) and self.state == 0:
                        self.exit_dialog = not self.exit_dialog
                        self.exit_choice = 1
                    elif self.exit_dialog and event.key in (K_LEFT, K_RIGHT, K_KP4, K_KP6):
                        self.exit_choice = 1 - self.exit_choice
                    elif self.exit_dialog and event.key in (K_RETURN, K_KP_ENTER, K_SPACE):
                        self.confirm_exit()
                elif self.exit_dialog and event.type in (MOUSEBUTTONDOWN, FINGERDOWN):
                    pos = TouchControls.finger_pos(event) if event.type == FINGERDOWN else event.pos
                    hit = self.dialog_hit(pos)
                    if hit is not None:
                        self.exit_choice = hit
                        self.confirm_exit()
                elif event.type == WINDOWFOCUSLOST if hasattr(pygame, 'WINDOWFOCUSLOST') else False:
                    if self.state == 0:
                        self.exit_dialog = True
            now = pygame.time.get_ticks()
            if now - last > 2000:      # RE: si pasaron más de 2 s se descarta el atraso
                last = now
            if not self.exit_dialog and not self.touch.settings_open:
                while now - last >= 32:
                    last += 32
                    self.update(self.keys_pressed())
            else:
                last = now
            self.draw()
            pygame.display.flip()
            clock.tick(60)
            if test:
                frame += 1
                self.test_step(test, frame)
        for key in list(self.channels):
            self.stop_sound(key)
        pygame.mixer.music.stop()
        return 1 if self.won else 0

    def confirm_exit(self):
        if self.exit_choice == 0:
            self.won = False
            self.state = 4
        self.exit_dialog = False

    def test_step(self, spec, frame):
        # DET_RACER_TEST="cuadro:accion[:arg];..." acciones: accel, brake, left, right, release, shot:archivo, quit, win
        for part in spec.split(';'):
            f = part.split(':')
            if not f[0] or int(f[0]) != frame:
                continue
            cmd = f[1]
            if cmd == 'shot':
                pygame.image.save(self.view, f[2])
            elif cmd == 'quit':
                self.state = 4
            elif cmd == 'win':
                self.thief.z = self.z + 5
                self.thief.x = self.x
            elif cmd in ('down', 'move', 'up'):
                et = {'down': MOUSEBUTTONDOWN, 'move': MOUSEMOTION, 'up': MOUSEBUTTONUP}[cmd]
                pygame.event.post(pygame.event.Event(et, pos=(int(f[2]), int(f[3])), button=1, buttons=(1, 0, 0), rel=(0, 0)))
            elif cmd == 'auto':
                self.autopilot = True
            elif cmd == 'log':
                print('t=%.1f z=%.0f v=%.0f x=%.1f gear=%d thief=%.0f estado=%d' % (self.time, self.z, self.speed, self.x, self.gear, self.thief.z - self.z, self.state))
            elif cmd == 'release':
                self.touch.mouse = None
            else:
                self.touch.mouse = cmd


def start(screen, overlay, thief_image, avatar_image, time_of_day, map_file, color, *mixer_params):
    racer = Racer(screen, thief_image, avatar_image, time_of_day, map_file, color)
    return racer.run()
