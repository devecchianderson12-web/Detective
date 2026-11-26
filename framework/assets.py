import pygame, os, codecs, zlib
from . import engine, external
from pygame.locals import *
SOUND_VOLUME = 1
if not os.path.exists(os.path.join(external.data_path, 'data')):
    os.mkdir(os.path.join(external.data_path, 'data'))

def load_data(file_name, field_sep=';', throw_exception=True, compressed=True, from_dynamic_path=False):
    base_path = ''
    if from_dynamic_path:
        base_path = external.data_path
    full_name = os.path.join(base_path, 'data', file_name)
    try:
        file = open(full_name, 'rb')
        raw = file.read()
        if compressed:
            raw = zlib.decompress(raw[4:])
        lines = raw.decode('latin-1').split('\n')
        if not compressed:
            lines = [l.rstrip('\r') for l in lines]
        if lines and lines[-1] == '':
            lines = lines[:-1]
        data = [line.split(field_sep) for line in lines]
        file.close()
    except Exception as message:
        if throw_exception:
            print(('Cannot load data file:', full_name))
            raise SystemExit(message)
        else:
            return []

    return data


def save_data(file_name, data, field_sep=';', compress=True):
    full_name = os.path.join(external.data_path, 'data', file_name)
    if compress:
        content = '\n'.join([field_sep.join([l.strip() for l in line]) for line in data])
        raw = b'DAT!' + zlib.compress(content.encode('latin-1', 'replace'))
    else:
        content = '\r\n'.join([field_sep.join(line) for line in data])
        raw = content.encode('latin-1', 'replace')
    # si el archivo está bloqueado un instante (antivirus, otra escritura) se reintenta; una partida que no
    # se pudo guardar no debe cerrar el juego
    import time
    for attempt in range(5):
        try:
            with open(full_name, 'wb') as file:
                file.write(raw)
            return
        except OSError as message:
            error = message
            time.sleep(0.05 * (attempt + 1))
    print(('Cannot save data file:', full_name, error))


def load_sound(file_name):
    full_name = os.path.join('sounds', file_name)
    try:
        sound = pygame.mixer.Sound(full_name)
    except pygame.error as message:
        print(('Cannot load sound:', full_name))
        raise SystemExit(message)

    return CustomSound(sound)


def load_music(file_name):
    return load_sound(file_name)


def load_image(file_name):
    surface = load_surface(file_name)
    return Image(surface, file_name)


def load_image_alpha(file_name_rgb, file_name_alpha):
    surface = load_surface_alpha(file_name_rgb, file_name_alpha)
    return Image(surface, file_name)


def load_surface(file_name):
    full_name = os.path.join('images', file_name)
    try:
        image = pygame.image.load(full_name)
    except pygame.error as message:
        print(('Cannot load image:', full_name))
        raise SystemExit(message)

    if image.get_bitsize() == 32:
        image = image.convert_alpha()
    else:
        image = image.convert()
    return image


def load_surface_alpha(file_name_rgb, file_name_alpha):
    full_name = os.path.join('images', file_name_rgb)
    try:
        image_rgb = pygame.image.load(full_name)
    except pygame.error as message:
        print(('Cannot load image:', full_name))
        raise SystemExit(message)

    if file_name_alpha == None:
        image = image_rgb.convert_alpha()
    else:
        full_name = os.path.join('images', file_name_alpha)
        try:
            image_alpha = pygame.image.load(full_name)
        except pygame.error as message:
            print(('Cannot load image:', full_name))
            raise SystemExit(message)

    image = image_rgb.convert_alpha()
    alpha = pygame.surfarray.pixels_alpha(image)
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            alpha[x][y] = image_alpha.get_at((x, y))[0]

    return image


def load_mask(file_name):
    full_name = os.path.join('images', file_name)
    try:
        image = pygame.image.load(full_name)
    except pygame.error as message:
        print(('Cannot load image:', full_name))
        raise SystemExit(message)

    return image


def load_font(file_name, size):
    full_name = os.path.join('fonts', file_name)
    return pygame.font.Font(full_name, size)


class CustomSound(object):

    def __init__(self, sound):
        self.sound = sound
        return

    def play(self, loops=0, maxtime=0):
        channel = self.sound.play(loops, maxtime)
        if channel != None:
            channel.set_volume(SOUND_VOLUME)
        return

    def stop(self):
        self.sound.stop()
        return

    def get_length(self):
        return self.sound.get_length()

    def fade_out(self):
        self.sound.fade_out()
        return

    def set_volume(self, value):
        self.sound.set_volume(value)
        return

    def get_volume(self):
        return self.sound.get_volume()

    def get_num_channel(self):
        return self.sound.get_num_channel()

    def get_buffer(self):
        return self.sound.get_buffer()


class Image(object):

    def __init__(self, surface, file_name=''):
        self.surface = surface
        self.__file_name = file_name
        return

    def get_file_name(self):
        return self.__file_name

    def get_width(self):
        return self.surface.get_width()

    def get_height(self):
        return self.surface.get_height()

    def get_size(self):
        return (
         self.get_width(), self.get_height())

    def get_at(self, x, y):
        return self.surface.get_at(x, y)

    def flip_h(self):
        self.surface = pygame.transform.flip(self.surface, True, False)
        return

    def flip_h_copy(self):
        return Image(pygame.transform.flip(self.surface, True, False), self.__file_name)

    def flip_v(self):
        self.surface = pygame.transform.flip(self.surface, False, True)
        return

    def flip_v_copy(self):
        return Image(pygame.transform.flip(self.surface, False, True), self.__file_name)

    def flip_hv(self):
        self.surface = pygame.transform.flip(self.surface, True, True)
        return

    def flip_hv_copy(self):
        return Image(pygame.transform.flip(self.surface, True, True), self.__file_name)

    def get_real_rect(self):
        return self.surface.get_rect()

    def blit_over(self, target_surface, pos, area=None):
        if area != None:
            target_surface.blit(self.surface, pos, area)
        else:
            target_surface.blit(self.surface, pos)
        return


