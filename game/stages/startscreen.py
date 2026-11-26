from framework.stage import *
from game.stages import case, mainmenu
from framework import animations
from framework.animations import BlindDirection

class StartScreenStage(Stage):

    def __init__(self, game, initial_mainmenu=False):
        Stage.__init__(self, game)
        self.start_layer = None
        self.initial_mainmenu = initial_mainmenu
        self.showing_main_menu = False
        return

    def prepare(self):
        self.font = assets.load_font('evilgeniusbb_reg.ttf', 24)
        self.music_intro = assets.load_music('p1_music_intro.ogg')
        self.music_loop = assets.load_music('p1_music_loop.ogg')
        self.click_sound = assets.load_sound('GUI_Click.ogg')
        self.rollover_sound = assets.load_sound('GUI_roll_over.ogg')
        self.render()
        self.play_music(self.music_intro, self.music_loop)
        if self.initial_mainmenu:
            self.show_mainmenu(True)
        else:
            self.show_tc_logo()
            animations.wait(self, 3606, self.show_start_screen)
        return

    def show_tc_logo(self):
        self.tc_layer = Layer()
        self.add_layer(self.tc_layer)
        logo_image = assets.load_image('p0_logomain_logo.jpg')
        logo_item = ItemImage(220, 77, logo_image)
        self.tc_layer.add(logo_item)
        copy_image = assets.load_image('p0_copyright_copy.jpg')
        copy_item = ItemImage(181, 417, copy_image)
        self.tc_layer.add(copy_item)
        ceibal_logo = assets.load_image('p0_ceibal_logo.jpg')
        ceibal_item = ItemImage(527, 7, ceibal_logo)
        self.tc_layer.add(ceibal_item)
        animations.blind_layer(self.tc_layer, BlindDirection.SHOW_DOWN, None, 450, None, False)
        return

    def show_start_screen(self):
        if not self.showing_main_menu:
            self.start_layer = Layer()
            background_image = assets.load_image('p0_presentation_back_2.jpg')
            background = ItemImage(0, 0, background_image)
            self.start_layer.add(background)
            self.start_info_item = ItemMask(0, 0, (600, 450))
            self.start_layer.add(self.start_info_item)
            animations.wait(self, 366, self.add_start_info_item)
            blink_text = assets.load_image('p0_presentation_btn_2.jpg')
            self.blink_text_image = ItemImage(166, 398, blink_text)
            self.start_layer.add(self.blink_text_image)
            self.blink_text_image.set_visible(False)
            self.add_layer(self.start_layer)
            animations.blind_layer(self.tc_layer, animations.BlindDirection.HIDE_DOWN, None, 450)
            animations.blind_layer(self.start_layer, animations.BlindDirection.SHOW_DOWN, None, 450, self.blind_set_up_start_callback)
        return

    def add_start_info_item(self):
        if not self.showing_main_menu:
            self.start_info_item.add_event_handler(ItemEvent.CLICK, self.button_click)
        return

    def blind_set_up_start_callback(self, layer):
        if not self.is_timer_started('timer_start'):
            self.start_timer('timer_start', 390, self.update_timer)
        return

    def update_timer(self, item, args):
        if self.blink_text_image.get_visible():
            self.blink_text_image.set_visible(False)
        else:
            self.blink_text_image.set_visible(True)
        return

    def button_click(self, item, args):
        self.render()
        self.click_sound.play()
        self.show_mainmenu()
        return

    def handle_event(self, e):
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE and not self.showing_main_menu:
                self.render()
                self.click_sound.play()
                self.remove_layer(self.tc_layer)
                self.show_mainmenu(True)
                return True
        return

    def show_mainmenu(self, apply_blind=True):
        if self.start_layer == None:
            self.blind_hide_start_callback(self.start_layer, apply_blind)
        else:
            animations.blind_layer(self.start_layer, animations.BlindDirection.HIDE_DOWN, None, 450, self.blind_hide_start_callback)
        return

    def blind_hide_start_callback(self, layer, apply_blind=True):
        self.showing_main_menu = True
        main = mainmenu.MainMenu(self)
        main.show_mainmenu(False, None, apply_blind)
        return


