import sys, traceback, builtins, os
os.environ.setdefault('SDL_ANDROID_TRAP_BACK_BUTTON', '1')   # Android: "atrás" llega como tecla (Escape) y no cierra la app


def show_crash(text):
    # Si el juego falla se muestra el error en pantalla (y se guarda en crash.txt) en vez de cerrarse
    # sin aviso: así se puede sacar una captura del problema en el teléfono.
    try:
        base = os.environ.get('ANDROID_PRIVATE', '')
        with open(os.path.join(base, 'crash.txt'), 'w') as f:
            f.write(text)
    except Exception:
        pass
    try:
        import pygame
        pygame.init()
        screen = pygame.display.get_surface() or pygame.display.set_mode((600, 450), pygame.SCALED)
        font = pygame.font.Font(None, 16)
        screen.fill((20, 20, 30))
        y = 6
        lines = ['Ocurrió un error (tocá la pantalla para salir):', ''] + text.splitlines()[-34:]
        for line in lines:
            while line:
                part, line = line[:95], line[95:]
                screen.blit(font.render(part, True, (240, 240, 240)), (6, y))
                y += 12
        pygame.display.flip()
        waited = 0
        while waited < 120000:
            for e in pygame.event.get():
                if e.type in (pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    return
            pygame.time.wait(50)
            waited += 50
    except Exception:
        traceback.print_exc()


def android_absolute_paths():
    # En Android, SDL busca las rutas relativas dentro del APK (assets) y no en la carpeta de la app:
    # pygame no encontraba "sounds/..." ni "images/...". Se pasan a rutas absolutas.
    if 'ANDROID_ARGUMENT' not in os.environ and 'ANDROID_PRIVATE' not in os.environ:
        return
    import pygame

    def absolute(func):
        def wrapper(path, *args, **kwargs):
            if isinstance(path, str) and not os.path.isabs(path):
                path = os.path.abspath(path)
            return func(path, *args, **kwargs)
        return wrapper
    pygame.image.load = absolute(pygame.image.load)
    pygame.mixer.Sound = absolute(pygame.mixer.Sound)
    pygame.mixer.music.load = absolute(pygame.mixer.music.load)
    font_class = pygame.font.Font

    class Font(font_class):
        def __init__(self, path, *args, **kwargs):
            if isinstance(path, str) and not os.path.isabs(path):
                path = os.path.abspath(path)
            font_class.__init__(self, path, *args, **kwargs)
    pygame.font.Font = Font


def main():
    g = None
    android_absolute_paths()
    try:
        from framework import py2compat
        builtins._div = py2compat.div   # "/" con semántica de Python 2 (ver re/fixdiv.py)
        import framework.assets, framework.stats
        from framework import leveldesigner, stats
        from framework.engine import Game
        from game.stages import case, phase2, accessmenu, startscreen, logotc, presentation, updatemanager
        from game.data import datastore, datamodel, dictionary, statcodes
    except Exception:
        traceback.print_exc()
        show_crash(traceback.format_exc())
        return
    try:
        g = Game('División Especial de Detectives', 'cursor.png', 'p0_loading.gif')
        g.set_quit_on_escape(False)
        g.datastore = datastore.Datastore(g)
        g.update_manager = updatemanager.UpdateManager()
        g.set_design_stage(accessmenu.AccessMenuStage(g, False))
        g.set_test_stage(accessmenu.AccessMenuStage(g, True))
        g.stats.start_time_event(statcodes.PLAY)
        initial_stage = presentation.PresentationStage(g)
        g.run(initial_stage)
    except:
        print('An unexpected error occurred, and the application was closed.')
        traceback.print_exc()
        (type, value, tb) = sys.exc_info()
        stats.report_error(type, value, tb)
        if not isinstance(value, SystemExit) or value.code not in (None, 0):
            show_crash(traceback.format_exc())

    if g != None:
        g.stats.end_time_event(statcodes.PLAY)
        g.stats.save_if_pending()
    return


if __name__ == '__main__':
    main()
