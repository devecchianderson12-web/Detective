from framework import assets, text, animations
from framework.stage import *
import random

class Help:

    def __init__(self, stage, hide_up=False, include_ui_help=False):
        self.stage = stage
        self.hide_up = hide_up
        self.include_ui_help = include_ui_help
        self.ui_page_count = 4
        self.guide_page_count = 9
        self.layer = Layer()
        self.current_layer = Layer()
        self.previous_layer = Layer()
        self.button_layer = Layer()
        self.continue_sound = stage.click_sound
        self.rollover_sound = stage.rollover_sound
        self.help_sound = assets.load_sound('p0_help.ogg')
        return

    def show_help(self, page, show_nextprevious, show_empty_background, close_callback=None, page_range=None):
        self.page = page
        self.show_nextprevious = show_nextprevious
        self.close_callback = close_callback
        self.page_range = page_range
        if self.include_ui_help and page == 1:
            self.ui_help = True
        else:
            self.ui_help = False
        self.load_help_shared_data()
        self.stage.show_dialog(self.layer, self.handle_event)
        if show_empty_background:
            self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, True, [], self.blind_show_help_callback)
        else:
            self.blind_show_help_callback(self.layer, True)
        return

    def close_help(self):
        if self.hide_up:
            blind_direction = animations.BlindDirection.HIDE_UP
        else:
            blind_direction = animations.BlindDirection.HIDE_DOWN
        self.stage.blind_dialog(self.layer, blind_direction, True, [], self.blind_close_help_callback)
        return

    def blind_show_help_callback(self, layer, blind_background=False):
        self.set_up_help_dialog()
        self.set_up_help_page()
        self.stage.add_layer(self.previous_layer)
        self.stage.add_layer(self.current_layer)
        self.stage.add_layer(self.button_layer)
        self.stage.blind_dialog(self.layer, animations.BlindDirection.SHOW_DOWN, blind_background, [])
        self.stage.render()
        animations.wait(self.stage, 100, self.play_help_sound)
        return

    def play_help_sound(self):
        self.help_sound.play()
        return

    def load_help_shared_data(self):
        background_image = assets.load_image('p0_tutorial_remake_background.png')
        self.background_item = ItemImage(51, 27, background_image)
        self.font_20_bold = assets.load_font('evilgeniusbb_bld.ttf', 20)
        self.font_13 = assets.load_font('evilgeniusbb_reg.ttf', 13)
        self.font_13_bold = assets.load_font('evilgeniusbb_bld.ttf', 13)
        self.close_button_image = assets.load_image('p0_tutorial_remake_btn_close_normal.png')
        self.close_button_rollover_image = assets.load_image('p0_tutorial_remake_btn_close_rollover.png')
        if self.show_nextprevious:
            self.next_button_image = assets.load_image('p0_tutorial_remake_btn_next_normal.png')
            self.next_button_rollover_image = assets.load_image('p0_tutorial_remake_btn_next_rollover.png')
            self.previous_button_image = assets.load_image('p0_tutorial_remake_btn_prev_normal.png')
            self.previous_button_rollover_image = assets.load_image('p0_tutorial_remake_btn_prev_rollover.png')
        self.continue_sound = assets.load_sound('GUI_Click.ogg')
        return

    def set_up_help_dialog(self):
        self.layer.empty()
        self.layer.add(self.background_item)
        close_button_item = ItemImage(261, 382, self.close_button_image)
        close_button_item.set_rollover_image(self.close_button_rollover_image, self.rollover_sound)
        close_button_item.add_event_handler(ItemEvent.CLICK, self.close_button_click)
        self.button_layer.add(close_button_item)
        if self.show_nextprevious:
            self.previous_button_item = ItemImage(220, 386, self.previous_button_image)
            self.previous_button_item.set_rollover_image(self.previous_button_rollover_image, self.rollover_sound)
            self.previous_button_item.add_event_handler(ItemEvent.CLICK, self.previous_button_click)
            self.button_layer.add(self.previous_button_item)
            self.next_button_item = ItemImage(356, 386, self.next_button_image)
            self.next_button_item.set_rollover_image(self.next_button_rollover_image, self.rollover_sound)
            self.next_button_item.add_event_handler(ItemEvent.CLICK, self.next_button_click)
            self.button_layer.add(self.next_button_item)
        return

    def set_up_help_page(self):
        items = []
        for item in self.current_layer.items:
            items.append(item)

        self.previous_layer.empty()
        self.current_layer.empty()
        for item in items:
            self.previous_layer.add(item)

        if self.ui_help:
            if self.page == 1:
                example_image = assets.load_image('p0_tut_nuevo_interface_notext_001.jpg')
                example_item = ItemImage(69, 89, example_image)
                self.current_layer.add(example_item)
                message = 'DEPARTAMENTO\nACTUAL'
                text1_item = ItemText(173, 178, self.font_13, 12, message, (0, 0, 0), None, 115, 50, 1, 1, None)
                self.current_layer.add(text1_item)
                message = 'DÍA & HORA'
                text2_item = ItemText(292, 178, self.font_13, 12, message, (0, 0, 0), None, 115, 30, 3, 1, None)
                self.current_layer.add(text2_item)
                message = 'AQUÍ PUEDES VER TODA LA\nINFORMACIÓN SOBRE\n&#c150,6,3!TU DETECTIVE&#c!'
                text3_item = ItemText(219, 245, self.font_13, 12, message, (0, 0, 0), None, 176, 52, 1, 1, None)
                self.current_layer.add(text3_item)
                police_image = assets.load_image('p0_tutorial_remake_policeman_pos1.png')
                police_item = ItemImage(394, 69, police_image)
                self.current_layer.add(police_item)
            elif self.page == 2:
                example_image = assets.load_image('p0_tut_nuevo_interface_notext_002.jpg')
                example_item = ItemImage(69, 89, example_image)
                self.current_layer.add(example_item)
                message = 'AQUÍ VERÁS LOS &#c150,6,3!OBJETOS&#c! QUE\nENCUENTRES AL INVESTIGAR EL\nESCONDITE DEL LADRÓN.'
                text1_item = ItemText(193, 156, self.font_13, 12, message, (0, 0, 0), None, 195, 60, 2, 1, None)
                self.current_layer.add(text1_item)
                police_image = assets.load_image('p0_tutorial_remake_policeman_pos1.png')
                police_item = ItemImage(394, 69, police_image)
                self.current_layer.add(police_item)
            elif self.page == 3:
                example_image = assets.load_image('p0_tut_nuevo_interface_notext_003.jpg')
                example_item = ItemImage(69, 89, example_image)
                self.current_layer.add(example_item)
                message = 'CON ESTE &#c150,6,3!MAPA&#c! PUEDES\n&#c150,6,3!VIAJAR&#c! POR TODO EL PAÍS\nPARA ATRAPAR AL LADRÓN.'
                text1_item = ItemText(110, 135, self.font_13, 12, message, (0, 0, 0), None, 235, 47, 3, 1, None)
                self.current_layer.add(text1_item)
                message = 'AQUÍ PUEDES VER TODA LA\n&#c150,6,3!INFORMACIÓN&#c! SOBRE EL CASO Y\n&#c150,6,3!HACER EL IDENTIKIT&#c! DEL LADRÓN.'
                text2_item = ItemText(110, 189, self.font_13, 12, message, (0, 0, 0), None, 235, 47, 3, 1, None)
                self.current_layer.add(text2_item)
                message = 'AQUÍ PUEDES VER TODOS LOS\n&#c150,6,3!DATOS&#c! QUE HAYAS OBTENIDO\nSOBRE NUESTRO PAÍS.'
                text3_item = ItemText(110, 248, self.font_13, 12, message, (0, 0, 0), None, 235, 47, 3, 1, None)
                self.current_layer.add(text3_item)
                police_image = assets.load_image('p0_tutorial_remake_policeman_pos1.png')
                police_item = ItemImage(394, 69, police_image)
                self.current_layer.add(police_item)
            elif self.page == 4:
                example_image = assets.load_image('p0_tut_nuevo_interface_notext_004.jpg')
                example_item = ItemImage(69, 89, example_image)
                self.current_layer.add(example_item)
                message = 'PRESIONANDO LA TECLA &#c150,6,3!"X"&#c! ACCEDES AL MENÚ\nPRINCIPAL. EL PROGRESO DE TU DETECTIVE\nQUEDA GUARDADO AUTOMÁTICAMENTE.'
                text1_item = ItemText(147, 100, self.font_13, 12, message, (0, 0, 0), None, 286, 45, 3, 1, None)
                self.current_layer.add(text1_item)
                police_image = assets.load_image('p0_tutorial_remake_policeman_pos1.png')
                police_item = ItemImage(394, 69, police_image)
                self.current_layer.add(police_item)
        elif self.page == 1:
            example_image = assets.load_image('p0_tutorial_remake_d1.jpg')
            example_item = ItemImage(67, 140, example_image)
            self.current_layer.add(example_item)
            number_item = ItemText(264, 133, self.font_20_bold, 0, str(self.page), (144,
                                                                                    22,
                                                                                    22), None, 66, 25, 2, 1)
            self.current_layer.add(number_item)
            additional_fonts = {'bold': (self.font_13_bold, 16, -2)}
            if not self.include_ui_help:
                message = '&#c144,22,22!&#f:bold!Saludos Agente.&#f!&#c!\n'
            else:
                message = ''
            message += 'te haré una breve reseña de los\n' + '&#f:bold!pasos a seguir para atrapar al ladrón.&#f!'
            text1_item = ItemText(114, 84, self.font_13, 16, message, (0, 0, 0), None, 364, 50, 2, 2, additional_fonts)
            self.current_layer.add(text1_item)
            message = 'Interroga a &#c144,22,22!&#f:bold!los testigos&#f!&#c! que han visto actividades sospechosas.'
            text2_item = ItemText(171, 162, self.font_13, 16, message, (0, 0, 0), None, 243, 35, 2, 2, additional_fonts)
            self.current_layer.add(text2_item)
            police_image = assets.load_image('p0_tutorial_remake_policeman_pos1.png')
            police_item = ItemImage(394, 69, police_image)
            self.current_layer.add(police_item)
        elif self.page == 2:
            example_image = assets.load_image('p0_tutorial_remake_d4.jpg')
            example_item = ItemImage(67, 87, example_image)
            self.current_layer.add(example_item)
            number_item = ItemText(264, 80, self.font_20_bold, 0, str(self.page), (144,
                                                                                   22,
                                                                                   22), None, 66, 25, 2, 1)
            self.current_layer.add(number_item)
            additional_fonts = {'bold': (self.font_13_bold, 16, -2)}
            message = 'Usa las &#f:bold!pistas&#f! que te den los &#f:bold!testigos&#f! para\n' + '&#f:bold!armar el identikit del ladrón&#f! y enviar\n' + 'una&#f:bold! orden de arresto&#f! en su contra, sin ella\n' + '&#c144,22,22!&#f:bold!no podrás arrestarlo&#f!&#c! aunque lo atrapes.'
            text_item = ItemText(130, 96, self.font_13, 16, message, (0, 0, 0), None, 332, 92, 2, 2, additional_fonts)
            self.current_layer.add(text_item)
            police_image = assets.load_image('p0_tutorial_remake_policeman_pos1.png')
            police_item = ItemImage(394, 69, police_image)
            self.current_layer.add(police_item)
        elif self.page == 3:
            example_image = assets.load_image('p0_tutorial_remake_d5.jpg')
            example_item = ItemImage(67, 87, example_image)
            self.current_layer.add(example_item)
            number_item = ItemText(264, 80, self.font_20_bold, 0, str(self.page), (144,
                                                                                   22,
                                                                                   22), None, 66, 25, 2, 1)
            self.current_layer.add(number_item)
            additional_fonts = {'bold': (self.font_13_bold, 16, -2)}
            message = 'Recuerda que tienes un &#f:bold!tiempo límite&#f! para atrapar al ladrón.\n' + 'SI LO SOBREPASAS, &#f:bold!ESCAPARÁ&#f!.'
            text_item = ItemText(166, 112, self.font_13, 16, message, (0, 0, 0), None, 263, 50, 2, 2, additional_fonts)
            self.current_layer.add(text_item)
            police_image = assets.load_image('p0_tutorial_remake_policeman_pos2.png')
            police_item = ItemImage(394, 69, police_image)
            self.current_layer.add(police_item)
        elif self.page == 4:
            example_image = assets.load_image('p0_tutorial_remake_d2.jpg')
            example_item = ItemImage(67, 87, example_image)
            self.current_layer.add(example_item)
            number_item = ItemText(264, 80, self.font_20_bold, 0, str(self.page), (144,
                                                                                   22,
                                                                                   22), None, 66, 25, 2, 1)
            self.current_layer.add(number_item)
            additional_fonts = {'bold': (self.font_13_bold, 16, -2)}
            message = 'Usa las pistas que te den para dar con el &#f:bold!escondite&#f! del ladrón.'
            text_item = ItemText(171, 109, self.font_13, 16, message, (0, 0, 0), None, 243, 34, 2, 2, additional_fonts)
            self.current_layer.add(text_item)
            police_image = assets.load_image('p0_tutorial_remake_policeman_pos2.png')
            police_item = ItemImage(394, 69, police_image)
            self.current_layer.add(police_item)
        elif self.page == 5:
            example_image = assets.load_image('p0_tutorial_remake_d3.jpg')
            example_item = ItemImage(67, 87, example_image)
            self.current_layer.add(example_item)
            number_item = ItemText(264, 80, self.font_20_bold, 0, str(self.page), (144,
                                                                                   22,
                                                                                   22), None, 66, 25, 2, 1)
            self.current_layer.add(number_item)
            additional_fonts = {'bold': (self.font_13_bold, 16, -2)}
            message = 'Investiga el escondite para\nencontrar pistas que te indiquen su\nnuevo paradero.'
            text_item = ItemText(161, 109, self.font_13, 16, message, (0, 0, 0), None, 263, 50, 2, 2, additional_fonts)
            self.current_layer.add(text_item)
            police_image = assets.load_image('p0_tutorial_remake_policeman_pos1.png')
            police_item = ItemImage(394, 69, police_image)
            self.current_layer.add(police_item)
        elif self.page == 6:
            example_image = assets.load_image('p0_tutorial_remake_dik.jpg')
            example_item = ItemImage(67, 87, example_image)
            self.current_layer.add(example_item)
            number_item = ItemText(264, 80, self.font_20_bold, 0, str(self.page), (144,
                                                                                   22,
                                                                                   22), None, 66, 25, 2, 1)
            self.current_layer.add(number_item)
            message = '¡Persigue al ladrón &#c144,22,22!en tu coche&#c! antes de que se escape!'
            text_item = ItemText(166, 132, self.font_13_bold, 16, message, (0, 0, 0), None, 263, 50, 2, 2, None)
            self.current_layer.add(text_item)
            police_image = assets.load_image('p0_tutorial_remake_policeman_pos3.png')
            police_item = ItemImage(394, 69, police_image)
            self.current_layer.add(police_item)
        elif self.page == 7:
            example_image = assets.load_image('p3_help_d1.jpg')
            example_item = ItemImage(68, 87, example_image)
            self.current_layer.add(example_item)
            message = 'Debes atrapar al ladrón antes de que\nse acabe el combustible.'
            text1_item = ItemText(141, 101, self.font_13_bold, 14, message, (0, 0,
                                                                             0), None, 302, 38, 2, 2, None)
            self.current_layer.add(text1_item)
            additional_fonts = {'bold': (self.font_13_bold, 14, -1)}
            message = 'Para conducir el auto usa los\n&#f:bold!&#c150,6,3!siguientes controles&#c!&#f!:'
            text2_item = ItemText(141, 141, self.font_13, 14, message, (0, 0, 0), None, 302, 38, 2, 2, additional_fonts)
            self.current_layer.add(text2_item)
            police_image = assets.load_image('p0_tutorial_remake_policeman_pos1.png')
            police_item = ItemImage(394, 69, police_image)
            self.current_layer.add(police_item)
        elif self.page == 8:
            example_image = assets.load_image('p3_help_d2.jpg')
            example_item = ItemImage(68, 87, example_image)
            self.current_layer.add(example_item)
            message = '&#c150,6,3!O TAMBIÉN PUEDES UTILIZAR:&#c!'
            text_item = ItemText(141, 105, self.font_13_bold, 12, message, (0, 0, 0), None, 302, 38, 2, 2, None)
            self.current_layer.add(text_item)
            police_image = assets.load_image('p0_tutorial_remake_policeman_pos1.png')
            police_item = ItemImage(394, 69, police_image)
            self.current_layer.add(police_item)
        elif self.page == 9:
            example_image = assets.load_image('p3_help_d3.jpg')
            example_item = ItemImage(68, 87, example_image)
            self.current_layer.add(example_item)
            additional_fonts = {'bold': (self.font_13_bold, 16, -2)}
            message = 'Para atrapar al ladrón solo debes &#f:bold!adelantarlo&#f!.'
            text2_item = ItemText(141, 112, self.font_13, 16, message, (0, 0, 0), None, 302, 38, 2, 2, additional_fonts)
            self.current_layer.add(text2_item)
            police_image = assets.load_image('p0_tutorial_remake_policeman_pos1.png')
            police_item = ItemImage(394, 69, police_image)
            self.current_layer.add(police_item)
        elif self.page == 101:
            example_image = assets.load_image('p0_tutorial_remake_dik.jpg')
            example_item = ItemImage(67, 87, example_image)
            self.current_layer.add(example_item)
            additional_fonts = {'bold': (self.font_13_bold, 16, -2)}
            message = '&#c144,22,22!&#f:bold!¡MUY BIEN!&#f!&#c!\nVas por buen camino, ya tienes una &#f:bold!órden\nde arresto&#f! contra el ladrón.\n\nAhora deberás &#f:bold!seguir buscándolo&#f!\npara poder atraparlo.'
            text_item = ItemText(143, 93, self.font_13, 16, message, (0, 0, 0), None, 312, 128, 2, 2, additional_fonts)
            self.current_layer.add(text_item)
            police_image = assets.load_image('p0_tutorial_remake_policeman_pos1.png')
            police_item = ItemImage(394, 69, police_image)
            self.current_layer.add(police_item)
        elif self.page == 102:
            example_image = assets.load_image('p0_tutorial_remake_dg2.jpg')
            example_item = ItemImage(67, 87, example_image)
            self.current_layer.add(example_item)
            additional_fonts = {'bold': (self.font_13_bold, 16, -2)}
            message = '&#c144,22,22!&#f:bold!¡MUY BIEN!&#f!&#c!\nYa encontraste &#f:bold!todas las pistas&#f! que\nhay en la habitación.\n\nAhora deberás usarlas para descubrir la &#f:bold!nueva\nubicación&#f! del ladrón y &#f:bold!viajar&#f! hasta allí.'
            text_item = ItemText(130, 94, self.font_13, 16, message, (0, 0, 0), None, 340, 128, 2, 2, additional_fonts)
            self.current_layer.add(text_item)
            police_image = assets.load_image('p0_tutorial_remake_policeman_pos1.png')
            police_item = ItemImage(394, 69, police_image)
            self.current_layer.add(police_item)
        if self.show_nextprevious:
            if self.include_ui_help:
                self.previous_button_item.set_visible(self.page > 1 or not self.ui_help)
                self.next_button_item.set_visible(self.page < self.guide_page_count or self.ui_help)
            else:
                if self.page_range == None:
                    from_page = 1
                    to_page = self.guide_page_count
                else:
                    from_page = self.page_range[0]
                    to_page = self.page_range[1]
                self.previous_button_item.set_visible(self.page > from_page)
                self.next_button_item.set_visible(self.page < to_page)
        if len(self.previous_layer.items) > 0:
            animations.stop_blind_layer(self.current_layer)
            animations.stop_blind_layer(self.previous_layer)
            self.previous_layer.set_clip(None)
            area = Rect(69, 52, 455, 345)
            animations.blind_layer(self.current_layer, animations.BlindDirection.SHOW_DOWN, area, 450, None, False)
            animations.blind_layer(self.previous_layer, animations.BlindDirection.HIDE_DOWN, area, 450, None, False)
        return

    def close_button_click(self, item, args):
        self.stage.render()
        self.continue_sound.play()
        self.close_help()
        return

    def blind_close_help_callback(self, layer):
        self.stage.close_dialog(self.layer)
        if self.close_callback != None:
            self.close_callback()
        return

    def previous_button_click(self, item, args):
        self.stage.render()
        self.continue_sound.play()
        self.page -= 1
        if self.page == 0 and not self.ui_help:
            self.page = self.ui_page_count
            self.ui_help = True
        self.set_up_help_page()
        return

    def next_button_click(self, item, args):
        self.stage.render()
        self.continue_sound.play()
        self.page += 1
        if self.page > self.ui_page_count and self.ui_help:
            self.page = 1
            self.ui_help = False
        self.set_up_help_page()
        return

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.stage.render()
                self.continue_sound.play()
                self.close_help()
                return True
        return


