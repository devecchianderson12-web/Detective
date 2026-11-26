from . import stage, assets
from .stage import ItemImage
import math, pygame, sys
from . import animations
WAIT_ORDINAL = 1
try:
    scale_function = pygame.transform.smoothscale
except AttributeError:
    scale_function = pygame.transform.scale

def fade_in_item(item, duration=500, callback=None, to_alpha=255):
    stage = __get_item_stage(item)
    key = (
     item, 'fade')
    milliseconds = 20
    if item.get_alpha() == 255:
        item.set_alpha(0)
    stage.stop_timer(key)
    data = [
     pygame.time.get_ticks(), None, duration, to_alpha, callback, stage]
    stage.start_timer(key, milliseconds, __timer_fade_in_item, data, True, True)
    return key


def fade_out_item(item, remove, duration=500, callback=None):
    stage = __get_item_stage(item)
    key = (
     item, 'fade')
    milliseconds = 20
    stage.stop_timer(key)
    item.hide_rollover()
    data = [
     pygame.time.get_ticks(), None, duration, remove, callback, stage]
    stage.start_timer(key, milliseconds, __timer_fade_out_item, data, True, True)
    return key


def cancel_item_fade(key):
    stage = __get_item_stage(key[0])
    stage.stop_timer(key)
    return


def fade_in_layer(layer, duration=500, callback=None):
    stage = __get_layer_stage(layer)
    if layer.get_alpha() == 255:
        layer.set_alpha(0)
    key = (layer, 'fade')
    milliseconds = 20
    stage.stop_timer(key)
    data = [
     pygame.time.get_ticks(), None, duration, callback, stage]
    stage.start_timer(key, milliseconds, __timer_fade_in_layer, data, True, True)
    return


def fade_out_layer(layer, duration=500, callback=None):
    stage = __get_layer_stage(layer)
    key = (
     layer, 'fade')
    milliseconds = 20
    stage.stop_timer(key)
    data = [
     pygame.time.get_ticks(), None, duration, callback, stage]
    stage.start_timer(key, milliseconds, __timer_fade_out_layer, data, True, True)
    return


def start_image_sequence(item_image, images, fps, loops=0, callback=None):
    stage = __get_item_stage(item_image)
    key = (
     item_image, 'image_sequence')
    stage.stop_timer(key)
    milliseconds = _div(1000 , fps)
    stage.start_timer(key, milliseconds, __timer_image_sequence, [0, images, loops, callback, stage])
    return


def stop_image_sequence(item_image):
    stage = __get_item_stage(item_image)
    item_data = stage.stop_timer((item_image, 'image_sequence'))
    if item_data == None:
        return 0
    else:
        return item_data[0]
    return


def start_move(item, left, top, duration, acceleration=None, move_marks=None, callback=None):
    stage = __get_item_stage(item)
    key = (
     item, 'move')
    milliseconds = 20
    stage.stop_timer(key)
    item_left = item.get_left()
    item_top = item.get_top()
    if move_marks == None:
        move_marks_data = None
    else:
        angle = math.atan2(top - item_top, left - item_left)
        dx_per_mark = math.cos(angle) * move_marks.separation
        dy_per_mark = math.sin(angle) * move_marks.separation
        if abs(dx_per_mark) < 1 and abs(dy_per_mark) < 1:
            move_marks_data = None
        else:
            mark_image_dx = _div(item.get_width() , 2) - _div(move_marks.mark_image.get_width() , 2)
            mark_image_dy = _div(item.get_height() , 2) - _div(move_marks.mark_image.get_height() , 2)
            move_marks_data = [item_left - dx_per_mark, item_top - dy_per_mark, dx_per_mark, dy_per_mark, mark_image_dx, mark_image_dy]
    data = [0, duration, item_left, item_top, left, top, acceleration, move_marks, 
     move_marks_data, callback, stage]
    stage.start_timer(key, milliseconds, __timer_move, data, True, True)
    return


def remove_move_marks(item):
    layer = item.get_layer()
    if layer != None:
        items_to_remove = []
        for i in layer.items:
            if isinstance(i, ItemImage):
                if hasattr(i, 'move_mark_item'):
                    if i.move_mark_item == item:
                        items_to_remove.append(i)

        for i in items_to_remove:
            layer.remove(i)

    return


def stop_move(item):
    stage = __get_item_stage(item)
    stage.stop_timer((item, 'move'))
    return


def start_resize(item_image, image, from_size, to_size, duration, origin_type=1, callback=None):
    stage = __get_item_stage(item_image)
    key = (
     item_image, 'resize')
    milliseconds = 20
    stage.stop_timer(key)
    resized_image = assets.Image(scale_function(image.surface, (int(from_size[0]), int(from_size[1]))))
    item_image.set_image(resized_image)
    if origin_type == 1:
        orgin_pos = (
         item_image.get_left() + _div(item_image.get_width() , 2), item_image.get_top() + _div(item_image.get_height() , 2))
    else:
        orgin_pos = None
    data = [
     0, image, duration, origin_type, orgin_pos, from_size, to_size, 
     callback, stage]
    stage.start_timer(key, milliseconds, __timer_resize, data, True, True)
    return


def stop_resize(item_image):
    stage = __get_item_stage(item_image)
    stage.stop_timer((item_image, 'resize'))
    return


def wait(stage, milliseconds, callback):
    key = (
     'wait', animations.WAIT_ORDINAL)
    stage.start_timer(key, milliseconds, __timer_wait, (stage, callback))
    animations.WAIT_ORDINAL += 1
    if animations.WAIT_ORDINAL == 99999:
        animations.WAIT_ORDINAL = 1
    return key


def wait_locked(stage, milliseconds, callback, data=None):
    stage.lock_ui()
    key = ('wait_locked', animations.WAIT_ORDINAL)
    stage.start_timer(key, milliseconds, __timer_wait_locked, (stage, callback, data))
    animations.WAIT_ORDINAL += 1
    if animations.WAIT_ORDINAL == 99999:
        animations.WAIT_ORDINAL = 1
    return key


def cancel_wait(stage, key):
    stage.stop_timer(key)
    return


def stop_blind_layer(layer):
    stage = __get_layer_stage(layer)
    key = (
     layer, 'blind')
    data = stage.stop_timer(key)
    if data != None:
        if data[9]:
            stage.unlock_ui()
        direction = data[1]
        if direction == BlindDirection.SHOW_UP or direction == BlindDirection.SHOW_DOWN:
            layer.set_clip(None)
        elif direction == BlindDirection.HIDE_UP or direction == BlindDirection.HIDE_DOWN:
            clip = pygame.Rect(0, data[5], data[3], data[6])
            layer.set_clip(clip)
    return


def blind_layer(layer, direction, area, duration=450, callback=None, lock_ui=True):
    stage = __get_layer_stage(layer)
    key = (
     layer, 'blind')
    milliseconds = 20
    data = stage.stop_timer(key)
    (window_width, window_height) = stage.game.get_window_size()
    dy_factor = _div(float(window_height) , duration)
    if data != None and data[9]:
        stage.unlock_ui()
    if data != None and data[1] == direction and data[0] != None:
        data[7] = callback
    else:
        if direction == BlindDirection.SHOW_UP or direction == BlindDirection.SHOW_DOWN:
            if direction == BlindDirection.SHOW_DOWN:
                if area == None:
                    current_top = 0
                else:
                    current_top = area.top
            elif area == None:
                current_top = window_height
            else:
                current_top = area.top + area.height
            current_height = 0
            layer.set_clip(pygame.Rect(0, current_top, window_width, 0))
        elif direction == BlindDirection.HIDE_UP or direction == BlindDirection.HIDE_DOWN:
            hidden = False
            if not layer.get_visible():
                hidden = True
            else:
                clip = layer.get_clip()
                if clip != None and (clip.width == 0 or clip.height == 0):
                    hidden = True
            if hidden:
                if callback != None:
                    callback(layer)
                return
            else:
                if area == None:
                    current_top = 0
                    current_height = window_height
                else:
                    current_top = area.top
                    current_height = area.height
                layer.set_clip(None)
        data = [
         0, direction, dy_factor, window_width, window_height, 
         current_top, current_height, callback, stage, lock_ui]
    if lock_ui:
        stage.lock_ui()
    stage.start_timer(key, milliseconds, __timer_blind_layer, data, True, True)
    return


def cancel_blind_layer(stage, layer, show):
    key = (
     layer, 'blind')
    data = stage.stop_timer(key)
    if data != None:
        lock_ui = data[9]
        if lock_ui:
            stage.unlock_ui()
    if show:
        layer.set_clip(None)
    else:
        layer.set_clip(pygame.Rect(0, 0, 0, 0))
    return


def is_applying_blind(stage, layer):
    key = (
     layer, 'blind')
    return stage.is_timer_started(key)


class BlindDirection:
    SHOW_UP = 0
    SHOW_DOWN = 1
    HIDE_UP = 2
    HIDE_DOWN = 3


class MoveMarks:

    def __init__(self, mark_image, separation):
        self.mark_image = mark_image
        self.separation = separation
        return


def __get_item_stage(item):
    layer = item.get_layer()
    if layer == None:
        raise Exception('The item must be part of a layer')
    stage = layer.get_stage()
    if stage == None:
        raise Exception("The item's layer must be part of a stage")
    return stage


def __get_layer_stage(layer):
    stage = layer.get_stage()
    if stage == None:
        raise Exception('The layer must be part of a stage')
    return stage


def __timer_fade_in_item(key, data):
    item = key[0]
    now = pygame.time.get_ticks()
    if data[1] == None:
        elapsed_time = min(0, now - data[0])
    else:
        elapsed_time = now - data[1]
    data[1] = now
    to_alpha = data[3]
    increment = to_alpha * (_div(float(elapsed_time) , data[2]))
    alpha = item.get_alpha()
    alpha += increment
    if alpha < to_alpha:
        item.set_alpha(alpha)
    else:
        item.set_alpha(to_alpha)
        stage = data[5]
        stage.stop_timer(key)
        callback = data[4]
        if callback != None:
            callback(item)
    return


def __timer_fade_out_item(key, data):
    item = key[0]
    now = pygame.time.get_ticks()
    if data[1] == None:
        elapsed_time = min(0, now - data[0])
    else:
        elapsed_time = now - data[1]
    data[1] = now
    decrement = 255 * (_div(float(elapsed_time) , data[2]))
    alpha = item.get_alpha()
    alpha -= decrement
    if alpha >= 0:
        item.set_alpha(alpha)
    else:
        item.set_alpha(0)
        layer = item.get_layer()
        if data[3] and layer != None:
            layer.remove(item)
        stage = data[5]
        stage.stop_timer(key)
        callback = data[4]
        if callback != None:
            callback(item)
    return


def __timer_fade_in_layer(key, data):
    layer = key[0]
    now = pygame.time.get_ticks()
    if data[1] == None:
        elapsed_time = min(0, now - data[0])
    else:
        elapsed_time = now - data[1]
    data[1] = now
    increment = 255 * (_div(float(elapsed_time) , data[2]))
    alpha = layer.get_alpha()
    alpha += increment
    if alpha < 255:
        layer.set_alpha(alpha)
    else:
        layer.set_alpha(255)
        stage = data[4]
        stage.stop_timer(key)
        callback = data[3]
        if callback != None:
            callback(layer)
    return


def __timer_fade_out_layer(key, data):
    layer = key[0]
    now = pygame.time.get_ticks()
    if data[1] == None:
        elapsed_time = min(0, now - data[0])
    else:
        elapsed_time = now - data[1]
    data[1] = now
    decrement = 255 * (_div(float(elapsed_time) , data[2]))
    alpha = layer.get_alpha()
    alpha -= decrement
    if alpha >= 0:
        layer.set_alpha(alpha)
    else:
        layer.set_alpha(0)
        stage = data[4]
        stage.stop_timer(key)
        callback = data[3]
        if callback != None:
            callback(layer)
    return


def __timer_image_sequence(key, data):
    item = key[0]
    images = data[1]
    if len(images) > 0:
        item.set_image(images[data[0]])
    data[0] += 1
    if data[0] >= len(images):
        data[0] = 0
        if data[2] != -1:
            data[2] -= 1
            if data[2] < 0:
                stage = data[4]
                stage.stop_timer(key)
                callback = data[3]
                if callback != None:
                    callback(item)
    return


def __timer_move(key, data):
    item = key[0]
    now = pygame.time.get_ticks()
    if data[0] == None:
        elapsed_time = 0
        data[0] = now
    else:
        elapsed_time = now - data[0]
    duration = data[1]
    left_from = data[2]
    top_from = data[3]
    left_to = data[4]
    top_to = data[5]
    acceleration = data[6]
    percentage = min(1, _div(float(elapsed_time) , duration))
    if acceleration == None:
        dx = (left_to - left_from) * percentage
        dy = (top_to - top_from) * percentage
    else:
        (maxvel_t, maxvel_dist, tension) = acceleration
        if percentage <= maxvel_t:
            factor = math.cos(_div(_div(percentage , maxvel_t) * math.pi , 2) - math.pi) + 1
            factor = math.pow(factor, tension) * maxvel_dist
        else:
            factor = math.cos(_div(_div((percentage - maxvel_t) , (1 - maxvel_t)) * math.pi , 2) - _div(math.pi , 2)) + 1 - 1
            factor = math.pow(factor, tension) * (1 - maxvel_dist) + maxvel_dist
        dx = (left_to - left_from) * factor
        dy = (top_to - top_from) * factor
    new_left = left_from + dx
    new_top = top_from + dy
    item.set_left(new_left)
    item.set_top(new_top)
    move_marks = data[7]
    if move_marks != None:
        marks_data = data[8]
        last_mark_left = marks_data[0]
        last_mark_top = marks_data[1]
        dx_per_mark = marks_data[2]
        dy_per_mark = marks_data[3]
        while dx_per_mark > 0 and last_mark_left + dx_per_mark < new_left or dx_per_mark < 0 and last_mark_left + dx_per_mark > new_left and (dy_per_mark > 0 and last_mark_top + dy_per_mark < new_top or dy_per_mark < 0 and last_mark_top + dy_per_mark > new_top):
            mark_x = last_mark_left + dx_per_mark
            mark_y = last_mark_top + dy_per_mark
            mark = ItemImage(mark_x + marks_data[4], mark_y + marks_data[5], move_marks.mark_image)
            mark.move_mark_item = item
            layer = item.get_layer()
            if layer != None:
                index = layer.items.index(item)
                layer.add(mark, index)
            last_mark_left = mark_x
            last_mark_top = mark_y
            marks_data[0] = last_mark_left
            marks_data[1] = last_mark_top

    if percentage >= 1:
        stage = data[10]
        stage.stop_timer(key)
        callback = data[9]
        if callback != None:
            callback(item)
    return


def __timer_resize(key, data):
    item_image = key[0]
    now = pygame.time.get_ticks()
    if data[0] == None:
        elapsed_time = 0
        data[0] = now
    else:
        elapsed_time = now - data[0]
    image = data[1]
    duration = data[2]
    origin_type = data[3]
    origin_pos = data[4]
    from_size = data[5]
    to_size = data[6]
    percentage = min(1, _div(float(elapsed_time) , duration))
    new_size = (int(from_size[0] + (to_size[0] - from_size[0]) * percentage), int(from_size[1] + (to_size[1] - from_size[1]) * percentage))
    if origin_type == 1:
        new_left = origin_pos[0] - _div(new_size[0] , 2)
        new_top = origin_pos[1] - _div(new_size[1] , 2)
    else:
        new_left = item_image.get_left()
        new_top = item_image.get_top()
    resized_image = assets.Image(scale_function(image.surface, new_size))
    item_image.set_image(resized_image)
    item_image.set_image(resized_image)
    item_image.set_left(new_left)
    item_image.set_top(new_top)
    if percentage >= 1:
        stage = data[8]
        stage.stop_timer(key)
        callback = data[7]
        if callback != None:
            callback(item_image)
    return


def __timer_wait(key, data):
    stage = data[0]
    callback = data[1]
    stage.stop_timer(key)
    callback()
    return


def __timer_wait_locked(key, data):
    stage = data[0]
    callback = data[1]
    callback_data = data[2]
    stage.stop_timer(key)
    stage.unlock_ui()
    if callback != None:
        if callback_data == None:
            callback()
        else:
            callback(callback_data)
    return


def __timer_blind_layer(key, data):
    layer = key[0]
    now = pygame.time.get_ticks()
    if data[0] == None:
        elapsed_time = 0
    else:
        elapsed_time = now - data[0]
    data[0] = now
    dy_factor = data[2]
    dy = elapsed_time * dy_factor
    end_of_blind = False
    direction = data[1]
    if direction == BlindDirection.SHOW_UP:
        show = True
        if data[6] >= data[4]:
            end_of_blind = True
        elif data[6] + dy >= data[4]:
            data[5] = 0
            data[6] = data[4]
        else:
            data[5] -= dy
            data[6] += dy
    elif direction == BlindDirection.SHOW_DOWN:
        show = True
        if data[6] >= data[4]:
            end_of_blind = True
        elif data[6] + dy >= data[4]:
            data[6] = data[4]
        else:
            data[6] += dy
    elif direction == BlindDirection.HIDE_UP:
        show = False
        if data[6] <= 0:
            end_of_blind = True
        elif data[6] - dy <= 0:
            data[6] = 0
            end_of_blind = True
        else:
            data[6] -= dy
    elif direction == BlindDirection.HIDE_DOWN:
        show = False
        if data[6] <= 0:
            end_of_blind = True
        elif data[6] - dy <= 0:
            data[5] = 0
            data[6] = 0
            end_of_blind = True
        else:
            data[5] += dy
            data[6] -= dy
    if end_of_blind and show:
        layer.set_clip(None)
    else:
        clip = pygame.Rect(0, data[5], data[3], data[6])
        layer.set_clip(clip)
    if end_of_blind:
        stage = data[8]
        lock_ui = data[9]
        stage.stop_timer(key)
        stage.update_mouse()
        if lock_ui:
            stage.unlock_ui()
        callback = data[7]
        if callback != None:
            stage.render()
            callback(layer)
    return


