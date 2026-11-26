from framework import assets, engine, animations, leveldesigner
from framework.assets import *
from framework.stage import *
from game.data import serialization
from . import phase0, phase2, phase3, minigamegardener, help, mainmenu

class AccessMenuStage(Stage):

    def __init__(self, game, test):
        Stage.__init__(self, game)
        self.__test = test
        return

    def initialize(self):
        self.add_content_layers()
        self.options_layer = Layer()
        self.add_layer(self.options_layer)
        font = assets.load_font('freesansbold.ttf', 20)
        if not self.__test:
            options = 'I - Set items (Phase 2)\n' + 'G - Set items (Minigame - Gardener)\n' + 'L - Level Designer (Phase 2)\n' + '\n' + '0 - Main menu\n' + '1 - Phase 1\n' + '2 - Phase 2\n' + '3 - Phase 3\n' + '4 - Minigame - Shoptender\n' + '5 - Minigame - Gardener\n' + '6 - Minigame - Librarian\n' + '7 - Minigame - Bricklayer\n' + 'H - Ayuda\n' + '\n' + 'Q - Quit'
        else:
            options = '3 - Phase 3\n' + '4 - Minigame - Shoptender\n' + '5 - Minigame - Gardener\n' + '6 - Minigame - Librarian\n' + '7 - Minigame - Bricklayer\n' + '\n' + 'Q - Quit'
        menu = ItemText(100, 50, font, 0, options)
        self.options_layer.add(menu)
        small_font = assets.load_font('freesansbold.ttf', 15)
        if self.__test:
            info = ItemText(100, 400, small_font, 0, '[Press SHIFT+0 in any stage to return to this menu]')
        else:
            info = ItemText(100, 400, small_font, 0, '[Press F10 in any stage to return to this menu]')
        self.options_layer.add(info)
        self.load_character()
        return

    def load_character(self):
        datastore = self.game.datastore
        if datastore.user_character == None:
            active_character = None
            for c in datastore.characters:
                if c.active:
                    active_character = c
                    break

            if active_character != None:
                datastore.load_character(active_character)
            else:
                active_character = datastore.create_character('Hans Sarasa', 'M', 1, 'Montevideo')
                datastore.load_character(active_character)
                case_generator = serialization.CaseGenerator(datastore)
                datastore.user_character_progress.set_case(case_generator.new_case())
                datastore.user_character_progress.case.last_department_visited = datastore.user_character_progress.case.list_departments[0]
                datastore.save_character('nc', False)
        return

    def add_content_layers(self):
        return

    def handle_event(self, e):
        if e.type == KEYDOWN:
            if e.key == K_i and not self.__test:
                self.game.set_stage(leveldesigner.SetItemsStage(self.game, phase2.GRID_ORIGIN, phase2.GRID_CELL_WIDTH, phase2.GRID_CELL_HEIGHT, phase2.GRID_SIZE, phase2.ITEM_TAGS, phase2.PLACE_HOLDER_TAGS, phase2.ITEM_STATES, 'p2'))
            elif e.key == K_l and not self.__test:
                self.game.set_stage(leveldesigner.LevelDesignerStage(self.game, phase2.GRID_ORIGIN, phase2.GRID_CELL_WIDTH, phase2.GRID_CELL_HEIGHT, phase2.GRID_SIZE, phase2.ITEM_TAGS, phase2.PLACE_HOLDER_TAGS, phase2.ITEM_STATES, 'p2'))
            elif e.key == K_g and not self.__test:
                self.game.set_stage(leveldesigner.SetItemsStage(self.game, minigamegardener.GRID_ORIGIN, minigamegardener.GRID_CELL_WIDTH, minigamegardener.GRID_CELL_HEIGHT, minigamegardener.GRID_SIZE, minigamegardener.ITEM_TAGS, minigamegardener.PLACE_HOLDER_TAGS, minigamegardener.ITEM_STATES, 'p1g'))
            elif e.key == K_0 and not self.__test:
                self.click_sound = assets.load_sound('GUI_Click.ogg')
                self.rollover_sound = assets.load_sound('GUI_roll_over.ogg')
                main = mainmenu.MainMenu(self)
                main.show_mainmenu(False)
            elif e.key == K_1 and not self.__test:
                self.game.set_stage(phase0.Phase0Stage(self.game, 1, False))
            elif e.key == K_2 and not self.__test:
                self.game.set_stage(phase0.Phase0Stage(self.game, 2, False))
            elif e.key == K_3:
                case = self.game.datastore.user_character_progress.case
                case.arrest_order_thief = case.thief
                last_dep = case.list_departments[len(case.list_departments) - 1]
                case.last_department_lair = last_dep
                case.last_department_visited = last_dep
                self.game.set_stage(phase0.Phase0Stage(self.game, 3, False))
            elif e.key == K_4:
                case = self.game.datastore.user_character_progress.case
                case.last_department_visited = case.list_departments[0]
                stage = phase0.Phase0Stage(self.game, 1, False)
                stage.start_minigame('Almacenera')
                self.game.set_stage(stage)
            elif e.key == K_5:
                case = self.game.datastore.user_character_progress.case
                case.last_department_visited = case.list_departments[0]
                stage = phase0.Phase0Stage(self.game, 1, False)
                stage.start_minigame('Jardinero')
                self.game.set_stage(stage)
            elif e.key == K_6:
                case = self.game.datastore.user_character_progress.case
                case.last_department_visited = case.list_departments[0]
                stage = phase0.Phase0Stage(self.game, 1, False)
                stage.start_minigame('Bibliotecario')
                self.game.set_stage(stage)
            elif e.key == K_7:
                case = self.game.datastore.user_character_progress.case
                case.last_department_visited = case.list_departments[0]
                stage = phase0.Phase0Stage(self.game, 1, False)
                stage.start_minigame('Albañil')
                self.game.set_stage(stage)
            elif e.key == K_h and not self.__test:
                self.click_sound = assets.load_sound('GUI_Click.ogg')
                self.rollover_sound = assets.load_sound('GUI_roll_over.ogg')
                help_dialog = help.Help(self)
                help_dialog.show_help(1, True, False)
            elif e.key == K_q:
                self.game.quit()
        return


