import sys, traceback, builtins, os
os.environ.setdefault('SDL_ANDROID_TRAP_BACK_BUTTON', '1')   # Android: "atrás" llega como tecla (Escape) y no cierra la app
from framework import py2compat
builtins._div = py2compat.div   # "/" con semántica de Python 2 (ver re/fixdiv.py)
import framework.assets, framework.stats
from framework import leveldesigner, stats
from framework.engine import Game
from game.stages import case, phase2, accessmenu, startscreen, logotc, presentation, updatemanager
from game.data import datastore, datamodel, dictionary, statcodes

def main():
    g = None
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

    if g != None:
        g.stats.end_time_event(statcodes.PLAY)
        g.stats.save_if_pending()
    return


if __name__ == '__main__':
    main()
