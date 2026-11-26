from framework import assets, text, animations
from framework.stage import *
from game.data import datamodel

class CharacterId:

    def __init__(self, rollover_sound=None):
        self.loaded = False
        self.rollover_mask = None
        self.name_rollover_item = None
        self.rollover_sound = rollover_sound
        return

    def set_up_id(self, layer, char_info, x, y, enable_edit=False, click_callback=None):
        self.layer = layer
        if not self.loaded:
            self.load_assets()
        backdrop = ItemImage(x, y, self.backdrop_image)
        layer.add(backdrop)
        if click_callback:
            rollover_image = assets.load_image('p0_mainmenu_rolloverID.png')
            self.rollover_mask = ItemMask(x + 29, y + 25, rollover_image.get_size())
            self.rollover_mask.set_rollover(rollover_image, self.rollover_sound)
            self.rollover_mask.add_event_handler(ItemEvent.CLICK, click_callback)
            layer.add(self.rollover_mask)
        elif enable_edit:
            name_rollover_image = assets.load_image('p0_merits_main_name_rollover.jpg')
            self.name_rollover_item = ItemImage(x + 152, y + 79, name_rollover_image)
            self.name_rollover_item.set_visible(False)
            layer.add(self.name_rollover_item)
            self.rollover_mask = ItemMask(self.name_rollover_item.get_left(), self.name_rollover_item.get_top(), name_rollover_image.get_size())
            self.rollover_mask.add_event_handler(ItemEvent.MOUSE_ENTER, self.name_enter)
            self.rollover_mask.add_event_handler(ItemEvent.MOUSE_LEAVE, self.name_leave)
            layer.add(self.rollover_mask)
        self.avatar = ItemImage(x + 42, y + 38, None)
        layer.add(self.avatar)
        box = ItemImage(x + 37, y + 33, self.box_image)
        layer.add(box)
        self.range_text = ItemText(x + 167, y + 63, self.font_11, 0, '', (148, 34,
                                                                          34), None, 130, 13, 1, 1)
        layer.add(self.range_text)
        self.name_text = ItemText(x + 167, y + 89, self.font_16, 16, '', (58, 30, 16), None, 100, 49, 1, 1)
        layer.add(self.name_text)
        self.range_item = ItemImage(x + 42, y + 125, None)
        layer.add(self.range_item)
        if enable_edit:
            self.name_text.set_max_chars(30)
            self.name_text.set_editable(True)
            self.name_text.set_edit_on_click(self.rollover_mask, self.name_click)
            self.name_text.add_event_handler(ItemEvent.GOT_FOCUS, self.name_got_focus)
            self.name_text.add_event_handler(ItemEvent.LOST_FOCUS, self.name_lost_focus)
        self.load_character(char_info)
        return

    def name_click(self, item, args):
        stage = self.layer.get_stage()
        stage.render()
        stage.click_sound.play()
        return

    def name_enter(self, item, args):
        self.update_name_rollover_visible()
        return

    def name_leave(self, item, args):
        self.update_name_rollover_visible()
        return

    def name_got_focus(self, item, args):
        self.update_name_rollover_visible()
        return

    def name_lost_focus(self, item, args):
        self.update_name_rollover_visible()
        stage = self.layer.get_stage()
        character = stage.game.datastore.user_character
        new_name = apply_name_text_casing(item.get_text())
        if character.charinfo.name != new_name:
            character.charinfo.name = new_name
            self.name_text.set_text(new_name)
            stage.game.datastore.save_characters()
            stage.game.datastore.update_score_name(character)
            stage.game.datastore.save_highscores()
        return

    def update_name_rollover_visible(self):
        stage = self.layer.get_stage()
        visible = stage.get_over_item() == self.rollover_mask or stage.get_focus() == self.name_text
        self.name_rollover_item.set_visible(visible)
        return

    def load_character(self, char_info):
        if char_info == None:
            placeholder_image = assets.load_image('p0_detective_placeholder.jpg')
            self.avatar.set_image(placeholder_image)
            self.range_text.set_text('')
            self.name_text.set_text('')
            self.range_item.set_visible(False)
            if self.rollover_mask:
                self.rollover_mask.set_visible(False)
        else:
            self.load_avatar(char_info)
            self.avatar.set_image(self.avatar_image)
            range = datamodel.get_range_name(char_info.range_level)
            self.range_text.set_text(range)
            self.range_item.set_visible(True)
            self.load_range(char_info)
            self.range_item.set_image(self.range_image)
            self.name_text.set_text(char_info.name)
            if self.rollover_mask:
                self.rollover_mask.set_visible(True)
        return

    def load_range(self, char_info):
        if char_info.range_level != self.range_image_level:
            self.range_image = assets.load_image('p0_detective_ranks_lvl' + str(char_info.range_level) + '.png')
            self.range_image_level = char_info.range_level
        return

    def load_assets(self):
        if not self.loaded:
            self.backdrop_image = assets.load_image('p0_mainmenu_id_backdrop.png')
            self.box_image = assets.load_image('p0_merits_main_id_box.png')
            self.font_11 = assets.load_font('evilgeniusbb_bld.ttf', 11)
            self.font_16 = assets.load_font('evilgeniusbb_reg.ttf', 16)
            self.avatar_name = None
            self.range_image_level = -1
            self.__loaded = True
        return

    def load_avatar(self, char_info):
        name = 'p0_detective_'
        if char_info.sex == 'M':
            name += 'male_'
        else:
            name += 'female_'
        name += '%03d' % char_info.avatar + '_id.jpg'
        if self.avatar_name != name:
            self.avatar_image = assets.load_image(name)
            self.avatar_name = name
        return


def apply_name_text_casing(name):
    start = 0
    new_name = ''
    l = len(name)
    i = 0
    while i <= l:
        if i == l:
            if start < l:
                new_name += text.to_upper(name[start]) + text.to_lower(name[start + 1:i])
        elif name[i] == ' ':
            new_name += text.to_upper(name[start]) + text.to_lower(name[start + 1:i]) + ' '
            start = i + 1
        i += 1

    return new_name


