from framework.stage import *
from game.stages import startscreen
from framework import animations, web, stats
from game.data.datastore import UPDATE_URL, ERRORS_URL, STATS_URL, VERSION
from framework import external

def send_error_cb(result):
    if not result.error:
        stats.delete_error_data()
    return


class PresentationStage(Stage):

    def __init__(self, game):
        Stage.__init__(self, game)
        return

    def initialize(self):
        data = {'current': VERSION}
        error_data = stats.get_error_data(10000)
        web.query(UPDATE_URL, data, callback=self.game.update_manager.web_cb)
        web.send_data(STATS_URL, {'current': VERSION, 'stats': (self.game.stats.get_data())}, compressed=True)
        if error_data:
            web.send_data(ERRORS_URL, {'current': ('%.2f' % VERSION), 'error': (error_data.decode('utf-8', 'replace'))}, encoding='json', callback=send_error_cb, compressed=True)
            del error_data
        self.actual_screen = 0
        self.actual_item = 0
        self.actual_layer = None
        self.next_item_wait = None
        self.caution_screen_shown = not external.other_activities_running()
        self.font_13 = assets.load_font('evilgeniusbb_reg.ttf', 13)
        self.font_14 = assets.load_font('evilgeniusbb_reg.ttf', 14)
        self.font_13_bold = assets.load_font('evilgeniusbb_bld.ttf', 13)
        self.music_intro = assets.load_music('p2_music_intro.ogg')
        self.music_loop = assets.load_music('p2_music_loop.ogg')
        self.rollover_sound = assets.load_sound('GUI_roll_over.ogg')
        self.continue_sound = assets.load_sound('GUI_Click.ogg')
        return

    def prepare(self):
        if self.caution_screen_shown:
            self.start_presentation()
        else:
            layer = Layer()
            self.add_layer(layer)
            image = assets.load_image('p0_gamewarning_backslide.png')
            layer.add(ItemImage(132, 111, image))
            text = ItemText(163, 183, self.font_14, 13, 'Se recomienda cerrar todas las aplicaciones para el correcto funcionamiento del juego.', (153,
                                                                                                                                                   0,
                                                                                                                                                   0), None, 268, 56, 2, 2)
            layer.add(text)
            button = ItemImage(245, 265, assets.load_image('p0_gamewarning_btn_continuar_normal.png'))
            button.set_rollover_image(assets.load_image('p0_gamewarning_btn_continuar_rollover.png'), self.rollover_sound)
            button.add_event_handler(ItemEvent.CLICK, self.start_presentation)
            layer.add(button)
            self.caution_screen_shown = True
        return

    def start_presentation(self, *args, **kwargs):
        self.render()
        self.play_music(self.music_intro, self.music_loop)
        self.set_up_escape_button()
        self.show_next_screen()
        return

    def show_next_screen(self):
        if self.actual_screen != 5:
            self.empty_layers()
            self.continue_button_layer = None
            self.continue_visible = False
            self.layer = Layer()
            self.add_layer(self.layer)
            self.set_up_background()
            self.add_layer(self.escape_layer)
        else:
            self.empty_layers([self.layer, self.escape_layer])
            self.layer.remove(self.screen_mask)
            index = self.layers.index(self.layer)
            self.layer = Layer()
            self.set_up_background()
            self.add_layer(self.layer, index + 1)
            self.continue_button_layer = None
            self.continue_visible = False
        animations.blind_layer(self.layer, animations.BlindDirection.SHOW_DOWN, None, 450, self.blind_show_screen_callback, False)
        return

    def blind_show_screen_callback(self, layer):
        self.add_fast_click_mask()
        self.show_next_item()
        return

    def add_fast_click_mask(self):
        self.screen_mask = ItemMask(0, 0, (600, 450))
        self.screen_mask.add_event_handler(ItemEvent.CLICK, self.screen_click)
        self.layer.add(self.screen_mask)
        return

    def screen_click(self, item, args):
        if not self.continue_button_layer and self.actual_layer != None and self.actual_layer.get_stage() == None:
            if self.next_item_wait != None:
                animations.cancel_wait(self, self.next_item_wait)
            self.add_next_item_with_blind()
        return

    def set_up_background(self):
        if self.actual_screen == 0:
            newspaper_image = assets.load_image('p0_intro_s1_background.jpg')
            newspaper_item_image = ItemImage(0, 0, newspaper_image, None)
            self.layer.add(newspaper_item_image)
        elif self.actual_screen == 1:
            newspaper_image = assets.load_image('p0_intro_s2_background.jpg')
            newspaper_item_image = ItemImage(0, 0, newspaper_image, None)
            self.layer.add(newspaper_item_image)
        elif self.actual_screen == 2:
            newspaper_image = assets.load_image('p0_intro_s3_background.jpg')
            newspaper_item_image = ItemImage(0, 0, newspaper_image, None)
            self.layer.add(newspaper_item_image)
        elif self.actual_screen == 3:
            newspaper_image = assets.load_image('p0_intro_s4_background.jpg')
            newspaper_item_image = ItemImage(0, 0, newspaper_image, None)
            self.layer.add(newspaper_item_image)
        elif self.actual_screen == 4:
            newspaper_image = assets.load_image('p0_intro_s5_background.jpg')
            newspaper_item_image = ItemImage(0, 0, newspaper_image, None)
            self.layer.add(newspaper_item_image)
        elif self.actual_screen == 5:
            while len(self.layer.items) > 1:
                self.layer.remove(self.layer.items[1])

            (window_width, window_height) = self.game.get_window_size()
            background_surface = pygame.Surface((window_width / 2, window_height / 2), pygame.SRCALPHA, 32)
            background_surface.fill((0, 0, 0, 180))
            background_image = assets.Image(background_surface)
            background_item = ItemImage(0, 0, background_image)
            self.layer.add(background_item)
            background_item = ItemImage(window_width / 2, 0, background_image)
            self.layer.add(background_item)
            background_item = ItemImage(0, window_height / 2, background_image)
            self.layer.add(background_item)
            background_item = ItemImage(window_width / 2, window_height / 2, background_image)
            self.layer.add(background_item)
        return

    def set_up_escape_button(self):
        self.escape_layer = Layer()
        button_image = assets.load_image('p0_escape_intro_btn_normal.png')
        rollover_image = assets.load_image('p0_escape_intro_btn_rollover.png')
        button_item = ItemImage(545, 26, button_image)
        button_item.set_rollover_image(rollover_image, self.rollover_sound)
        button_item.add_event_handler(ItemEvent.CLICK, self.escape_button_click)
        button_item.add_event_handler(ItemEvent.MOUSE_ENTER, self.escape_button_enter)
        button_item.add_event_handler(ItemEvent.MOUSE_LEAVE, self.escape_button_leave)
        self.escape_layer.add(button_item)
        button_text_image = assets.load_image('p0_escape_intro_txt.png')
        self.escape_text_item = ItemImage(433, 24, button_text_image)
        self.escape_text_item.set_visible(False)
        self.escape_layer.add(self.escape_text_item)
        return

    def escape_button_click(self, item, args):
        self.render()
        self.continue_sound.play()
        self.skip_presentation()
        return

    def escape_button_enter(self, item, args):
        self.escape_text_item.set_visible(True)
        return

    def escape_button_leave(self, item, args):
        self.escape_text_item.set_visible(False)
        return

    def show_continue_button(self):
        if not self.continue_visible:
            self.actual_layer = Layer()
            continue_image = assets.load_image('p0_endings_btn_continue_normal.png')
            continue_rollover_image = assets.load_image('p0_endings_btn_continue_rollover.png')
            continue_button = ItemImage(233, 403, continue_image)
            continue_button.set_rollover_image(continue_rollover_image, self.rollover_sound)
            continue_button.add_event_handler(ItemEvent.CLICK, self.continue_button_click)
            self.actual_layer.add(continue_button)
            self.continue_visible = True
            self.next_item_wait = animations.wait(self, 2000, self.add_next_item_with_blind)
        return

    def show_next_item(self):
        if self.actual_screen == 0:
            if self.actual_item == 0:
                image = assets.load_image('p0_intro_s1_dialogue.png')
                left = 317
                top = 327
                self.show_image(left, top, image, 1000)
            else:
                self.show_continue_button()
        elif self.actual_screen == 1:
            if self.actual_item == 0:
                image = assets.load_image('p0_intro_s2_dialogue1.png')
                left = 49
                top = 38
                self.show_image(left, top, image, 1000)
            elif self.actual_item == 1:
                image = assets.load_image('p0_intro_s2_dialogue2.png')
                left = 352
                top = 281
                self.show_image(left, top, image, 5500)
            else:
                self.show_continue_button()
        elif self.actual_screen == 2:
            if self.actual_item == 0:
                image = assets.load_image('p0_intro_s3_dialogue1.png')
                left = 5
                top = 24
                self.show_image(left, top, image, 1000)
            elif self.actual_item == 1:
                image = assets.load_image('p0_intro_s3_dialogue2.png')
                left = 308
                top = 146
                self.show_image(left, top, image, 5000)
            elif self.actual_item == 2:
                image = assets.load_image('p0_intro_s3_dialogue3.png')
                left = 6
                top = 317
                self.show_image(left, top, image, 5000)
            else:
                self.show_continue_button()
        elif self.actual_screen == 3:
            if self.actual_item == 0:
                image = assets.load_image('p0_intro_s4_dialogue1.png')
                left = 31
                top = 29
                self.show_image(left, top, image, 2000)
            elif self.actual_item == 1:
                image = assets.load_image('p0_intro_s4_dialogue2.png')
                left = 328
                top = 184
                self.show_image(left, top, image, 5000)
            else:
                self.show_continue_button()
        elif self.actual_screen == 4:
            if self.actual_item == 0:
                image = assets.load_image('p0_intro_s5_dialogue1.png')
                left = 3
                top = 53
                self.show_image(left, top, image, 1000)
            else:
                self.show_continue_button()
        elif self.actual_screen == 5:
            if self.actual_item == 0:
                image = assets.load_image('p0_intro_s6_dialogue1.png')
                left = 149
                top = 150
                self.show_image(left, top, image, 250)
            else:
                self.show_continue_button()
        return

    def show_image(self, left, top, image, milliseconds):
        self.actual_layer = Layer()
        box_image = ItemImage(left, top, image)
        self.actual_layer.add(box_image)
        self.next_item_wait = animations.wait(self, milliseconds, self.add_next_item_with_blind)
        return

    def show_text(self, left, top, milliseconds, text, font, color, width=-1, height=-1):
        self.actual_layer = Layer()
        item = ItemText(left, top, font, 0, text, color, width=width, height=height, h_align=2, v_align=2)
        self.actual_layer.add(item)
        self.next_item_wait = animations.wait(self, milliseconds, self.add_next_item_with_blind)
        return

    def add_next_item_with_blind(self):
        self.next_item_wait = None
        if self.actual_screen == 0:
            if self.actual_item < 1:
                self.actual_item += 1
            else:
                self.actual_item = 0
                self.actual_screen = 1
        elif self.actual_screen == 1:
            if self.actual_item < 2:
                self.actual_item += 1
            else:
                self.actual_item = 0
                self.actual_screen = 2
        elif self.actual_screen == 2:
            if self.actual_item < 3:
                self.actual_item += 1
            else:
                self.actual_item = 0
                self.actual_screen = 3
        elif self.actual_screen == 3:
            if self.actual_item < 2:
                self.actual_item += 1
            else:
                self.actual_item = 0
                self.actual_screen = 4
        elif self.actual_screen == 4:
            if self.actual_item < 1:
                self.actual_item += 1
            else:
                self.actual_item = 0
                self.actual_screen = 5
        elif self.actual_screen == 5:
            if self.actual_item < 1:
                self.actual_item = 1
            else:
                self.actual_item = 0
                self.actual_screen = 6
        self.add_layer(self.actual_layer)
        if self.escape_layer.get_stage() != None:
            self.remove_layer(self.escape_layer)
        self.add_layer(self.escape_layer)
        animations.blind_layer(self.actual_layer, animations.BlindDirection.SHOW_DOWN, self.actual_layer.get_bounds(), 450, None, False)
        if self.actual_item != 0:
            self.show_next_item()
        return

    def continue_button_click(self, item, args):
        self.render()
        self.continue_sound.play()
        if self.actual_screen == 6:
            initial_stage = startscreen.StartScreenStage(self.game)
            self.game.set_stage(initial_stage)
        else:
            self.show_next_screen()
        return

    def handle_event(self, e):
        if e.type == KEYDOWN:
            if e.key == K_SPACE or e.key == K_ESCAPE:
                self.render()
                self.continue_sound.play()
                pygame.time.wait(int(self.continue_sound.get_length() * 1000))
                self.skip_presentation()
                return True
        return

    def skip_presentation(self):
        initial_stage = startscreen.StartScreenStage(self.game)
        self.game.set_stage(initial_stage)
        return


