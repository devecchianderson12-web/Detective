from framework.stage import *
from framework import assets, animations
import math, random
from . import map
car_angle = 135

class Map(Item):

    def __init__(self, stage, from_phase0, car_animation=False):
        self.stage = stage
        self.from_phase0 = from_phase0
        self.map_layer = Layer()
        self.rollover_layer = Layer()
        self.mask_layer = Layer()
        self.car_layer = Layer()
        self.font = assets.load_font('freesansbold.ttf', 13)
        self.large_font = assets.load_font('nakel___.ttf', 30)
        self.load_dialog_images()
        self.load_car_images()
        self.load_sounds()
        self.set_up(not car_animation, car_animation)
        return

    def load_dialog_images(self):
        self.background_image = assets.load_image('p0_map_back.png')
        self.close_button_image = assets.load_image('p0_button_close.png')
        self.close_button_image_rollover = assets.load_image('p0_button_close_rollover.png')
        return

    def close_map(self):
        self.stage.close_dialog(self.map_layer)
        return

    def load_car_images(self):
        self.car_stopped = [
         assets.load_image('p0_map_car_t.png'),
         assets.load_image('p0_map_car_tl.png'),
         assets.load_image('p0_map_car_l.png'),
         assets.load_image('p0_map_car_bl.png'),
         assets.load_image('p0_map_car_b.png')]
        top_running = [
         assets.load_image('p0_map_car_t_001.png'),
         assets.load_image('p0_map_car_t_002.png'),
         assets.load_image('p0_map_car_t_003.png')]
        top_left_running = [assets.load_image('p0_map_car_tl_001.png'),
         assets.load_image('p0_map_car_tl_002.png'),
         assets.load_image('p0_map_car_tl_003.png')]
        left_running = [assets.load_image('p0_map_car_l_001.png'),
         assets.load_image('p0_map_car_l_002.png'),
         assets.load_image('p0_map_car_l_003.png')]
        bottom_left_running = [assets.load_image('p0_map_car_bl_001.png'),
         assets.load_image('p0_map_car_bl_002.png'),
         assets.load_image('p0_map_car_bl_003.png')]
        bottom_running = [assets.load_image('p0_map_car_b_001.png'),
         assets.load_image('p0_map_car_b_002.png'),
         assets.load_image('p0_map_car_b_003.png')]
        self.car_running = [
         top_running, 
         top_left_running, 
         left_running, 
         bottom_left_running, 
         bottom_running]
        mark_image = assets.load_image('p0_map_dot.png')
        self.car_move_marks = animations.MoveMarks(mark_image, 20)
        return

    def load_sounds(self):
        self.rollover_sound = assets.load_sound('GUI_roll_over.ogg')
        self.click_sound = assets.load_sound('GUI_Click.ogg')
        self.engine_sound = assets.load_sound('p0_car_map.ogg')
        self.tires_sound = assets.load_sound('p3_car_tires.wav')
        return

    def set_up(self, show_close, all_actives):
        self.img_id_normal = False
        self.selected_department = None
        self.traveling_to = None
        self.map_movement_unlocked = False
        self.map_layer.empty()
        self.rollover_layer.empty()
        self.mask_layer.empty()
        self.car_layer.empty()
        self.background = ItemImage(0, 0, self.background_image, None)
        self.map_layer.add(self.background)
        self.set_map_movement_data(all_actives)
        self.set_departaments_data(all_actives)
        if show_close:
            self.set_up_close_button()
        self.set_up_department_items()
        self.set_up_department_masks()
        self.set_up_texts()
        self.set_up_active_department()
        self.set_up_car()
        return

    def set_map_movement_data(self, all_actives):
        case = self.stage.game.datastore.user_character_progress.case
        if not all_actives:
            clue_found = len(case.clues_found) > 0
            if case.last_department_visited == case.list_departments[0] and case.last_department_lair == case.list_departments[0] or not case.wrong_witness_visited and not clue_found:
                self.map_movement_unlocked = False
            else:
                self.map_movement_unlocked = True
        else:
            self.map_movement_unlocked = True
        return

    def set_departaments_data(self, all_actives):
        departments = self.stage.game.datastore.list_departments
        self.department_data = [
         MapDepartment(departments[0], 'artigas', 139, 64, (255, 0, 0), 196, 104),
         MapDepartment(departments[1], 'canelones', 224, 335, (150, 150, 150), 256, 359),
         MapDepartment(departments[2], 'cerrolargo', 286, 170, (0, 150, 255), 339, 218),
         MapDepartment(departments[3], 'colonia', 118, 308, (255, 150, 150), 161, 333),
         MapDepartment(departments[4], 'durazno', 186, 220, (255, 255, 150), 245, 262),
         MapDepartment(departments[5], 'flores', 176, 267, (255, 0, 255), 204, 296),
         MapDepartment(departments[6], 'florida', 221, 263, (150, 255, 150), 258, 312),
         MapDepartment(departments[7], 'lavalleja', 270, 278, (150, 150, 255), 306, 319),
         MapDepartment(departments[8], 'maldonado', 279, 317, (0, 150, 0), 311, 366),
         MapDepartment(departments[9], 'montevideo', 227, 368, (0, 0, 150), 238, 378),
         MapDepartment(departments[10], 'paysandu', 127, 157, (255, 150, 0), 178, 197),
         MapDepartment(departments[11], 'rionegro', 116, 214, (0, 255, 0), 172, 242),
         MapDepartment(departments[12], 'rivera', 237, 113, (0, 255, 150), 289, 162),
         MapDepartment(departments[13], 'rocha', 328, 268, (150, 0, 255), 357, 322),
         MapDepartment(departments[14], 'salto', 132, 109, (255, 255, 0), 189, 152),
         MapDepartment(departments[15], 'sanjose', 186, 312, (255, 150, 255), 210, 344),
         MapDepartment(departments[16], 'soriano', 116, 258, (0, 0, 255), 154, 291),
         MapDepartment(departments[17], 'tacuarembo', 213, 141, (0, 255, 255), 262, 197),
         MapDepartment(departments[18], 'treintaytres', 297, 237, (255, 0, 150), 346, 261)]
        if all_actives:
            for dep in self.department_data:
                dep.inactive = False

        else:
            posible_deps = []
            case = self.stage.game.datastore.user_character_progress.case
            if case.last_department_lair == case.list_departments[0] or case.last_department_lair == case.list_departments[1]:
                posible_deps = case.list_posible_departments
            for d in posible_deps:
                self.department_data[self.stage.game.datastore.list_departments.index(d)].inactive = False

            self.set_last_visited_departments()
        return

    def set_up_close_button(self):
        self.close_button = ItemImage(275, 392, self.close_button_image, None)
        self.close_button.add_event_handler(ItemEvent.CLICK, self.button_click)
        self.close_button.set_rollover_image(self.close_button_image_rollover, self.rollover_sound)
        self.map_layer.add(self.close_button)
        return

    def set_up_department_items(self):
        case = self.stage.game.datastore.user_character_progress.case
        for dep_data in self.department_data:
            if self.map_movement_unlocked:
                if dep_data.inactive and dep_data.department != case.list_departments[0]:
                    image = assets.load_image('p0_map_inactive_' + dep_data.image_name + '.png')
                    inactive_item = ItemImage(dep_data.x, dep_data.y, image)
                    self.map_layer.add(inactive_item)
                else:
                    image = assets.load_image('p0_map_' + dep_data.image_name + '_rollover.png')
                    rollover_item = ItemImage(dep_data.x, dep_data.y, image)
                    dep_data.roll_over = rollover_item
            else:
                image = assets.load_image('p0_map_inactive_' + dep_data.image_name + '.png')
                inactive_item = ItemImage(dep_data.x, dep_data.y, image)
                dep_data.inactive = True
                self.map_layer.add(inactive_item)

        return

    def set_up_department_masks(self):
        masks = assets.load_mask('p0_map_mask.gif')
        self.department_masks = ItemMask(117, 66, masks)
        self.mask_layer.add(self.department_masks)
        self.department_masks.add_event_handler(ItemEvent.CLICK, self.department_masks_click)
        self.department_masks.add_event_handler(ItemEvent.MOUSE_MOVE, self.department_masks_move)
        self.department_masks.add_event_handler(ItemEvent.MOUSE_LEAVE, self.department_masks_leave)
        return

    def set_up_texts(self):
        self.department_text = ItemText(368, 115, self.large_font, 37, '', (100, 25,
                                                                            25), None, 130, 91, 2, 2)
        self.map_layer.add(self.department_text)
        return

    def set_up_car(self):
        car_image = self.get_car_stopped_image(map.car_angle)
        (left, top) = self.get_car_pos(self.active_department, car_image)
        self.car = ItemImage(left, top, car_image)
        self.car_layer.add(self.car)
        return

    def get_car_pos(self, dep, car_image):
        left = dep.center_x - _div(car_image.get_width() , 2)
        top = dep.center_y - _div(car_image.get_height() , 2)
        return (
         left, top)

    def button_click(self, item, args):
        self.stage.render()
        self.click_sound.play()
        if item == self.close_button:
            self.close_map()
        return

    def department_masks_click(self, item, args):
        if self.traveling_to == None:
            dep_data = self.get_department(args)
            if dep_data != None:
                self.stage.render()
                self.click_sound.play()
                self.set_selected_department(None, False)
                self.go_to(dep_data.department)
                self.close_button.set_visible(False)
                from game.data.serialization import get_travel_turns
                case = self.stage.game.datastore.user_character_progress.case
                travel_turns = get_travel_turns(self.stage.game.datastore, [case.last_department_visited, case.last_department_lair])
                case.time_spend += travel_turns
                if case.wrong_witness_visited:
                    case.wrong_witness_visited = False
        return

    def department_masks_move(self, item, args):
        if self.traveling_to == None:
            dep_data = self.get_department(args)
            self.set_selected_department(dep_data, True)
        return

    def department_masks_leave(self, item, args):
        self.set_selected_department(None, False)
        return

    def get_department(self, args):
        color = self.department_masks.get_at(args.x - self.department_masks.get_left(), args.y - self.department_masks.get_top())
        for dep_data in self.department_data:
            if dep_data.mask_color[0:3] == color[0:3]:
                if dep_data.inactive:
                    return
                else:
                    return dep_data

        return

    def set_up_active_department(self):
        last_department = self.stage.game.datastore.user_character_progress.case.last_department_visited
        for data in self.department_data:
            if data.department == last_department:
                self.active_department = data
                break

        image = assets.load_image('p0_map_active_' + self.active_department.image_name + '.png')
        self.active_department_image = ItemImage(self.active_department.x, self.active_department.y, image)
        self.map_layer.add(self.active_department_image)
        self.department_text.set_text(last_department.name)
        return

    def set_selected_department(self, dep_data, play_rollover_sound):
        if self.selected_department != dep_data:
            self.rollover_layer.empty()
            self.department_text.set_text('')
            if dep_data != None:
                if dep_data != self.active_department:
                    self.department_text.set_text(dep_data.department.name)
                    if not dep_data.inactive:
                        self.rollover_layer.add(dep_data.roll_over)
                        if play_rollover_sound:
                            self.stage.render()
                            self.rollover_sound.stop()
                            self.rollover_sound.play()
            self.selected_department = dep_data
        return

    def go_to(self, department, show_rotation_animation=True):
        for data in self.department_data:
            if data.department == department:
                dep_data = data
                break

        self.traveling_to = dep_data
        if dep_data == self.active_department:
            animations.wait(self.stage, 2000, self.go_to_phase1)
        else:
            self.department_text.set_text(dep_data.department.name)
            self.show_rotation_animation = show_rotation_animation
            animations.wait(self.stage, 100, self.start_engine)
        return

    def start_engine(self):
        self.stage.render()
        self.engine_sound.play(-1)
        animations.wait(self.stage, 150, self.start_move_car)
        return

    def start_move_car(self):
        self.stage.render()
        self.engine_sound.play(-1)
        animations.remove_move_marks(self.car)
        animations.stop_image_sequence(self.car)
        (rotation_images, new_angle) = self.get_car_rotation_images()
        map.car_angle = new_angle
        if self.show_rotation_animation:
            animations.start_image_sequence(self.car, rotation_images, 15, 0, self.rotate_car_callback)
        else:
            self.move_car_to_target()
        return

    def get_car_rotation_images(self):
        (left, top) = self.get_car_pos(self.traveling_to, self.car.get_image())
        dx = left - self.car.get_left()
        dy = top - self.car.get_top()
        angle = -math.degrees(math.atan2(dy, dx))
        angle = round(_div(angle , 45)) * 45
        current_angle = map.car_angle
        diff = angle - current_angle
        if diff >= 360:
            diff -= 360
        if diff >= 0 and diff <= 180 or diff <= -180:
            increment = 45
        else:
            increment = -45
        images = []
        if angle == 180:
            angle = -180
        if current_angle == 180:
            current_angle = -180
        if angle != current_angle:
            if angle == 180:
                angle = -180
            while True:
                images.append(self.get_car_stopped_image(current_angle))
                if angle == current_angle:
                    break
                else:
                    current_angle += increment
                    if current_angle >= 180:
                        current_angle -= 360
                    elif current_angle < -180:
                        current_angle += 360

        return (
         images, current_angle)

    def get_car_running_image(self, angle, index):
        if angle == 0:
            return self.car_running[2][index].flip_h_copy()
        elif angle == 45:
            return self.car_running[1][index].flip_h_copy()
        elif angle == 90:
            return self.car_running[0][index]
        elif angle == 135:
            return self.car_running[1][index]
        elif angle == -45:
            return self.car_running[3][index].flip_h_copy()
        elif angle == -90:
            return self.car_running[4][index]
        elif angle == -135:
            return self.car_running[3][index]
        else:
            return self.car_running[2][index]
        return

    def get_car_stopped_image(self, angle):
        if angle == 0:
            return self.car_stopped[2].flip_h_copy()
        elif angle == 45:
            return self.car_stopped[1].flip_h_copy()
        elif angle == 90:
            return self.car_stopped[0]
        elif angle == 135:
            return self.car_stopped[1]
        elif angle == -45:
            return self.car_stopped[3].flip_h_copy()
        elif angle == -90:
            return self.car_stopped[4]
        elif angle == -135:
            return self.car_stopped[3]
        else:
            return self.car_stopped[2]
        return

    def rotate_car_callback(self, item):
        self.move_car_to_target()
        return

    def move_car_to_target(self):
        (left, top) = self.get_car_pos(self.traveling_to, self.car.get_image())
        dx = left - self.car.get_left()
        dy = top - self.car.get_top()
        distance = math.sqrt(dx * dx + dy * dy)
        self.start_car_on_animation()
        duration = distance * 8
        animations.start_move(self.car, left, top, duration, None, self.car_move_marks, self.move_car_callback)
        animations.wait(self.stage, duration - 150, self.play_tires_sound)
        return

    def play_tires_sound(self):
        self.engine_sound.stop()
        self.tires_sound.play()
        return

    def move_car_callback(self, item):
        case = self.stage.game.datastore.user_character_progress.case
        case.last_department_visited = self.traveling_to.department
        animations.fade_out_item(self.active_department_image, True, 250)
        self.set_up_active_department()
        animations.fade_in_item(self.active_department_image, 250)
        animations.wait(self.stage, 2000, self.go_to_phase1)
        return

    def go_to_phase1(self):
        if self.from_phase0:
            self.stage.set_phase(1, True)
        else:
            from . import phase0
            game = self.stage.game
            game.set_stage(phase0.Phase0Stage(game, 1), True, 'p0_loading_slides_001.jpg')
        return

    def add_other_layer(self):
        self.stage.add_layer(self.rollover_layer)
        self.stage.add_layer(self.car_layer)
        self.stage.add_layer(self.mask_layer)
        return

    def start_car_on_animation(self):
        images = []
        l = len(self.car_running[0])
        image_index = 0
        for i in range(l):
            images.append(self.get_car_running_image(map.car_angle, (image_index + i) % l))

        animations.start_image_sequence(self.car, images, 15, -1)
        return

    def set_last_visited_departments(self):
        case = self.stage.game.datastore.user_character_progress.case
        if case.last_department_lair == case.list_departments[0] or case.last_department_lair == case.list_departments[1]:
            last_visited = self.department_data[self.stage.game.datastore.list_departments.index(case.list_departments[0])]
            image = assets.load_image('p0_map_lkl_' + last_visited.image_name + '.png')
            last_visited_item = ItemImage(last_visited.x, last_visited.y, image)
            self.map_layer.add(last_visited_item)
        elif case.last_department_lair == case.list_departments[2]:
            visited = self.department_data[self.stage.game.datastore.list_departments.index(case.list_departments[0])]
            last_visited = self.department_data[self.stage.game.datastore.list_departments.index(case.list_departments[1])]
            visited_image = assets.load_image('p0_map_lkl_' + visited.image_name + '.png')
            last_visited_image = assets.load_image('p0_map_lkl_' + last_visited.image_name + '.png')
            visited_item = ItemImage(visited.x, visited.y, visited_image)
            last_visited_item = ItemImage(last_visited.x, last_visited.y, last_visited_image)
            self.map_layer.add(visited_item)
            self.map_layer.add(last_visited_item)
        return


class MapDepartment():

    def __init__(self, department, image_name, x, y, mask_color, center_x, center_y):
        self.department = department
        self.image_name = image_name
        self.x = x
        self.y = y
        self.mask_color = mask_color
        self.center_x = center_x
        self.center_y = center_y
        self.inactive = True
        return


