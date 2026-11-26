import platform
from . import phase0, help
from framework.stage import *
from framework import animations
from game.data.datastore import THIEF_CAR_COLORS

def get_time_of_day(hour):
    if hour < 16:
        return 'noon'
    if hour < 18:
        return 'afternoon'
    return 'night'


class Phase3Content(phase0.PhaseContent):

    def __init__(self):
        return

    def initialize(self, game, stage):
        self.game = game
        self.stage = stage
        return

    def add_above_info_layers(self):
        background_layer = Layer()
        self.stage.add_layer(background_layer)
        background = ItemRect(0, 0, 600, 450)
        background_layer.add(background)
        try:
            from .racer import start
        except ImportError:
            import traceback
            traceback.print_exc()

            def start(*args, **kwargs):
                return 0

        self.start_racer = start
        animations.wait(self.stage, 10, self.prepare_chase)
        return

    def prepare_chase(self):
        self.loading_layer = self.game.add_loading_to_stage()
        if self.loading_layer != None:
            animations.cancel_blind_layer(self.stage, self.loading_layer, True)
        self.game.hide_loading()
        cp = self.game.datastore.user_character_progress
        if not cp.phase3_help:
            help_dialog = help.Help(self.stage)
            help_dialog.show_help(7, True, False, self.close_help_callback, (7, 9))
            cp.phase3_help = True
        else:
            self.start_chase()
        return

    def close_help_callback(self):
        self.start_chase()
        return

    def start_chase(self):
        screen = pygame.display.get_surface()
        sound_values = self.game.mixer_params
        print(sound_values)
        if screen.get_width() == 600:
            overlay = 0
        else:
            overlay = 1
        case = self.game.datastore.user_character_progress.case
        if case.thief_car_color:
            color = case.thief_car_color
        else:
            color = 'violet'
        result = self.start_racer(screen, overlay, 'images/' + case.thief.phase3_image, 'images/' + get_avatar_path(self.game.datastore.user_character.charinfo), get_time_of_day(case.actual_days()[1]), 'data/p3_map_' + case.last_department_lair.chase_map + '.yaml', color, sound_values[0], sound_values[1], sound_values[2])
        if isinstance(result, type(())) or isinstance(result, type([])):
            result = result[0]
        self.game.datastore.user_character_progress.case.caught_thief = result
        if self.loading_layer != None:
            self.stage.remove_layer(self.loading_layer)
        self.stage.redraw()
        self.stage.set_phase(1)
        return


def get_avatar_path(char_info):
    name = 'p0_detective_'
    if char_info.sex == 'M':
        name += 'male_'
    else:
        name += 'female_'
    name += '%03d' % char_info.avatar + '_carchase.jpg'
    return name


