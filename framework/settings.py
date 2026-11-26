# Ajustes del port (engranaje arriba a la derecha): pantalla, calidad de imagen, sonido y persecución.
# Se guardan en data/settings.json dentro de la carpeta de datos del jugador.
import json, os

SCREEN_MODES = ('Original', 'Rellenar', 'Estirar')   # 4:3 con bordes / bordes difuminados / estirada

DEFAULTS = {
    'screen': 0,       # índice de SCREEN_MODES
    'smooth': False,   # filtrado suave al agrandar (menos pixelado)
    'hd': False,       # calidad HD: la imagen se duplica con un algoritmo que respeta los bordes
    'tv': False,       # efecto TV (líneas de barrido)
    'fps': False,      # mostrar FPS
    'music': 100,      # volumen de la música (%)
    'sfx': 100,        # volumen de los efectos (%)
    'ghost': False,    # persecución: los choques no frenan y el combustible no se acaba
}

_values = None


def _path():
    try:
        from . import external
        base = external.data_path
    except Exception:
        base = ''
    return os.path.join(base, 'data', 'settings.json')


def load():
    global _values
    _values = dict(DEFAULTS)
    try:
        with open(_path(), 'r') as f:
            data = json.load(f)
        for k, v in data.items():
            if k in DEFAULTS and type(v) == type(DEFAULTS[k]):
                _values[k] = v
    except Exception:
        pass
    return _values


def get(key):
    if _values is None:
        load()
    return _values[key]


def set(key, value):
    if _values is None:
        load()
    _values[key] = value
    save()


def save():
    try:
        with open(_path(), 'w') as f:
            json.dump(_values, f)
    except Exception as e:
        print('settings: no se pudo guardar', e)


def music_volume():
    return get('music') / 100.0


def sfx_volume():
    return get('sfx') / 100.0
