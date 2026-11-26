from framework import assets, animations
from framework.stage import *
import random
from .minigame import Minigame
from game.data import statcodes

class MinigameBricklayer(Minigame):

    def __init__(self, stage, phase1content, witness):
        Minigame.__init__(self, stage, phase1content, witness, statcodes.MG_BRICKLAYER, statcodes.MG_BRICKLAYER_SOLVED, statcodes.MG_BRICKLAYER_NOTSOLVED, 'bricklayer')
        self.witness_minigame_box_image = assets.load_image('p1_minigame_flux_bricklayer_dialogue1.png')
        self.right_sound = assets.load_sound('p1_minigame_right.ogg')
        self.drag_sound = assets.load_sound('p1_minigame_bricklayer_drag.ogg')
        self.fade_sound = assets.load_sound('fade.ogg')
        self.showing_missing_piece = False
        self.move_duration = self.drag_sound.get_length() * 1000 * 0.75
        bricklayer_image = assets.load_image('p1_minigame_bricklayer.png')
        self.witness_item = ItemImage(428, 66, bricklayer_image, None)
        self.puzzle_pieces = []
        self.max_help_stages = 4
        self.minigame_solved = False
        self.start_time = None
        self.pause_start_time = None
        self.pause_total_time = 0
        self.title = 'ALBAÑIL'
        self.question_intro = 'El Albañil se encuentra muy ocupado\nen este momento, quizás si lo ayudas\npuedas interrogarlo luego.'
        self.question = '¿Te ofreces a ayudarlo?'
        self.request_text = 'El dueño de casa me pidió que colocara\nun mural en la pared y me lo dio separado\nen piezas de cerámica.'
        self.request_question_text = '¿Me ayudas a ordenar las piezas\npara formar la imagen?'
        self.thanks_text = '¡Muchas gracias! El dueño de casa va a quedar muy satisfecho.'
        self.picture = self.select_picture()
        return

    def get_music(self):
        return self.phase1content.music_minigame_1

    def blind_show_minigame_callback(self, layer):
        if not self.stage.game.datastore.user_character_progress.minigame_bricklayer_help_seen:
            self.stop_minigame(False)
            self.show_help_dialog()
            self.stage.game.datastore.user_character_progress.minigame_bricklayer_help_seen = True
        else:
            self.start_minigame()
        return

    def load_help_data(self):
        if self.help_stage == 1:
            background_image = assets.load_image('p1_minigame_bricklayer_help_d1.jpg')
            back_left = 126
            back_top = 146
            upper_help_text = 'En la pantalla veremos las piezas del mural desordenadas.'
            upper_text_left = 157
            upper_text_top = 94
            upper_text_width = 288
            upper_text_height = 67
            self.help_previous_button.set_visible(False)
        elif self.help_stage == 2:
            background_image = assets.load_image('p1_minigame_bricklayer_help_d2.jpg')
            back_left = 125
            back_top = 143
            upper_help_text = 'Haciendo clic sobre una pieza, ésta se moverá hasta el espacio vacío.'
            upper_text_left = 163
            upper_text_top = 94
            upper_text_width = 275
            upper_text_height = 49
        elif self.help_stage == 3:
            background_image = assets.load_image('p1_minigame_bricklayer_help_d3.jpg')
            back_left = 125
            back_top = 143
            upper_help_text = 'Si hay más piezas entre ella y el espacio vacío se moverán todas.'
            upper_text_left = 156
            upper_text_top = 94
            upper_text_width = 288
            upper_text_height = 56
        elif self.help_stage == 4:
            background_image = assets.load_image('p1_minigame_bricklayer_help_d4.jpg')
            back_left = 125
            back_top = 143
            upper_help_text = 'Una vez que la imagen esté formada se dará por concluída la tarea.'
            upper_text_left = 157
            upper_text_top = 94
            upper_text_width = 288
            upper_text_height = 56
        background_help_image_item = ItemImage(0, 0, None, None)
        background_help_image_item.set_image(background_image)
        background_help_image_item.set_lefttop(back_left, back_top)
        self.help_current_layer.add(background_help_image_item)
        self.upper_help_text_item = ItemText(upper_text_left, upper_text_top, self.font_14, 16, upper_help_text, (183,
                                                                                                                  35,
                                                                                                                  35), None, upper_text_width, upper_text_height, 2)
        self.help_current_layer.add(self.upper_help_text_item)
        return

    def start_minigame(self):
        self.play_music()
        self.start_play_stats_event()
        if self.start_time == None:
            self.start_time = pygame.time.get_ticks()
        else:
            self.pause_total_time += pygame.time.get_ticks() - self.pause_start_time
            self.pause_start_time = None
        return

    def stop_minigame(self, solved):
        self.end_play_stats_event(solved)
        self.pause_start_time = pygame.time.get_ticks()
        return

    def set_up_minigame(self):
        photo_number = self.picture.number
        location = self.picture.location
        department = self.picture.department
        character_progress = self.stage.game.datastore.user_character_progress
        minigame_level = character_progress.range.minigame_level
        if minigame_level == 1:
            rows = 3
            cols = 3
            self.maximum_time = 15
            self.maximum_time_score = 150
        elif minigame_level == 2:
            rows = 3
            cols = 3
            self.maximum_time = 30
            self.maximum_time_score = 200
        else:
            rows = 3
            cols = 3
            self.maximum_time = 150
            self.maximum_time_score = 120
        self.set_up_game_background_items()
        self.set_up_puzzle(photo_number, rows, cols, minigame_level)
        self.set_up_frame(location, department)
        self.set_up_buttons()
        self.set_up_photo(photo_number)
        self.set_up_witness()
        return

    def close_click(self, item, args):
        if not self.escape_key_event():
            self.stop_minigame(False)
            self.phase1content.minigame_solved(False)
            self.close_minigame()
        return

    def set_up_buttons(self):
        close_image = assets.load_image('p1_minigames_btn_close_normal.png')
        rollover_image = assets.load_image('p1_minigames_btn_close_active.png')
        close_item = ItemImage(258, 43, close_image)
        close_item.set_rollover_image(rollover_image, self.rollover_sound)
        close_item.add_event_handler(ItemEvent.CLICK, self.close_click)
        self.layer.add(close_item)
        help_image = assets.load_image('p1_minigames_btn_help_normal.png')
        rollover_image = assets.load_image('p1_minigames_btn_help_active.png')
        help_item = ItemImage(293, 44, help_image)
        help_item.set_rollover_image(rollover_image, self.rollover_sound)
        help_item.add_event_handler(ItemEvent.CLICK, self.help_click)
        self.layer.add(help_item)
        return

    def set_up_game_background_items(self):
        background_image = assets.load_image('p1_minigame_bricklayer_background.png')
        background_item = ItemImage(89, 62, background_image)
        self.layer.add(background_item)
        return

    def set_up_frame(self, location, department):
        frame_image = assets.load_image('p1_minigame_bricklayer_frame.png')
        frame_item = ItemImage(89, 62, frame_image)
        self.layer.add(frame_item)
        location_text = ItemText(180, 360, self.font_13_bld, 0, location, (75, 47,
                                                                           7), None, 229, 20, 2)
        self.layer.add(location_text)
        font_10_bld = assets.load_font('evilgeniusbb_bld.ttf', 10)
        department_text = ItemText(180, 376, font_10_bld, 0, '- ' + department + ' -', (100,
                                                                                        66,
                                                                                        12), None, 229, 16, 2)
        self.layer.add(department_text)
        return

    def set_up_photo(self, photo_number):
        photo_image = assets.load_image('p1_minigame_bricklayer_photo_00' + str(photo_number) + '.png')
        photo_item = ItemImage(0, 157, photo_image)
        self.layer.add(photo_item)
        return

    def set_up_puzzle(self, photo_number, rows, cols, minigame_level):
        self.puzzle_image = assets.load_image('p1_minigame_bricklayer_postal_00' + str(photo_number) + '.jpg')
        self.tile_image = None
        self.tile_image = assets.load_image('p1_minigame_bricklayer_tile' + str(rows) + 'x' + str(cols) + '.png')
        self.rows = rows
        self.cols = cols
        self.minigame_level = minigame_level
        for piece in self.puzzle_pieces:
            self.layer.remove(piece)

        self.grid = [[None for i in range(self.cols)] for j in range(self.rows)]
        self.piece_width = self.puzzle_image.get_width() / self.cols
        self.piece_height = self.puzzle_image.get_height() / self.rows
        for i in range(self.rows):
            for j in range(self.cols):
                if i != self.rows - 1 or j != self.cols - 1:
                    piece = ItemImage(0, 0, self.create_piece_image(i, j))
                    piece.add_event_handler(ItemEvent.CLICK, self.piece_click)
                    piece.row = i
                    piece.col = j
                    self.puzzle_pieces.append(piece)
                    self.layer.add(piece)

        self.shuffle()
        for i in range(self.rows):
            for j in range(self.cols):
                self.set_piece_pos(i, j)

        return

    def shuffle(self):
        rows = self.rows
        cols = self.cols
        n = cols * rows - 1
        if self.minigame_level == 1:
            method = 1
            movements = 6
            from_row = 1
            from_col = 0
            min_parity = 6
            max_parity = 10
        elif self.minigame_level == 2:
            method = 1
            from_row = 0
            from_col = 0
            movements = 8
            min_parity = 6
            max_parity = 12
        else:
            method = 2
            min_parity = 10
            max_parity = 999
            from_row = 0
            from_col = 0
        while True:
            if method == 1:
                list = self.perform_random_movements(rows, cols, movements, from_row, from_col)
            else:
                list = self.generate_random_positions(n)
            parity = self.calculate_parity(list, n)
            if parity % 2 == 0 and parity >= min_parity and parity <= max_parity:
                break

        for piece in self.puzzle_pieces:
            piece_pos = piece.row * cols + piece.col
            index = list.index(piece_pos)
            new_row = index / cols
            new_col = index % cols
            self.grid[new_row][new_col] = piece

        self.from_row = from_row
        self.from_col = from_col
        return

    def perform_random_movements(self, rows, cols, movements, from_row, from_col):
        matrix = [list(range(i * cols, (i + 1) * cols)) for i in range(rows)]
        col = cols - 1
        row = rows - 1
        previous_oposite_direction = 1
        for i in range(movements):
            valid_direction = False
            while not valid_direction:
                direction = random.randint(0, 3)
                if direction == previous_oposite_direction:
                    direction = (direction + 1) % 4
                if direction == 0:
                    if row > from_row:
                        new_col = col
                        new_row = row - 1
                        valid_direction = True
                        previous_oposite_direction = 1
                elif direction == 1:
                    if row + 1 < rows:
                        new_col = col
                        new_row = row + 1
                        valid_direction = True
                        previous_oposite_direction = 0
                elif direction == 2:
                    if col > from_col:
                        new_col = col - 1
                        new_row = row
                        valid_direction = True
                        previous_oposite_direction = 3
                elif col + 1 < cols:
                    new_col = col + 1
                    new_row = row
                    valid_direction = True
                    previous_oposite_direction = 2

            temp = matrix[row][col]
            matrix[row][col] = matrix[new_row][new_col]
            matrix[new_row][new_col] = temp
            row = new_row
            col = new_col

        list = []
        for row in range(rows):
            for col in range(cols):
                list.append(matrix[row][col])

        return list

    def generate_random_positions(self, n):
        list = []
        numbers = list(range(0, n))
        for i in range(n):
            i = random.choice(numbers)
            numbers.remove(i)
            list.append(i)

        return list

    def calculate_parity(self, list, n):
        parity = 0
        parity_list = list[:]
        for i in range(n):
            for j in range(0, len(parity_list)):
                if parity_list[j] == i:
                    del parity_list[j]
                    break
                else:
                    parity += 1

        return parity

    def set_piece_pos(self, row, col, animated=False):
        piece = self.grid[row][col]
        if piece != None:
            piece.current_row = row
            piece.current_col = col
            new_left = 114 + col * piece.get_width()
            new_top = 87 + row * piece.get_height()
            if animated:
                animations.start_move(piece, new_left, new_top, self.move_duration)
                animations.wait_locked(self.stage, self.move_duration, None)
            else:
                piece.set_left(new_left)
                piece.set_top(new_top)
        return

    def piece_click(self, item, args):
        if not self.minigame_solved:
            row = item.current_row
            col = item.current_col
            if row < self.from_row or col < self.from_col:
                moved = False
            else:
                empty_row = -1
                empty_col = -1
                for r in range(self.rows):
                    for c in range(self.cols):
                        if self.grid[r][c] == None:
                            empty_row = r
                            empty_col = c
                            break

                    if empty_row != -1:
                        break

                moved = False
                if row == empty_row:
                    if col < empty_col:
                        c = empty_col - 1
                        while c >= col:
                            self.move_to(self.grid[row][c], row, c + 1)
                            moved = True
                            c -= 1

                    elif col > empty_col:
                        c = empty_col + 1
                        while c <= col:
                            self.move_to(self.grid[row][c], row, c - 1)
                            moved = True
                            c += 1

                elif col == empty_col:
                    if row < empty_row:
                        r = empty_row - 1
                        while r >= row:
                            self.move_to(self.grid[r][col], r + 1, col)
                            moved = True
                            r -= 1

                    elif row > empty_row:
                        r = empty_row + 1
                        while r <= row:
                            self.move_to(self.grid[r][col], r - 1, col)
                            moved = True
                            r += 1

            self.stage.render()
            if moved:
                self.drag_sound.play()
            else:
                self.stage.click_sound.play()
        return

    def move_to(self, piece, to_row, to_col):
        if to_row >= 0:
            if to_row < self.rows and to_col >= 0 and to_col < self.cols and self.grid[to_row][to_col] == None:
                from_row = piece.current_row
                from_col = piece.current_col
                self.grid[from_row][from_col] = None
                self.grid[to_row][to_col] = piece
                self.set_piece_pos(to_row, to_col, True)
                self.check_minigame_solved()
                return True
        return False

    def check_minigame_solved(self):
        solved = True
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.grid[row][col]
                if piece != None:
                    if piece.current_row != piece.row or piece.current_col != piece.col:
                        solved = False
                        break
                if not solved:
                    break

        if solved:
            self.minigame_solved = True
            self.stop_minigame(True)
            self.stage.render()
            self.right_sound.play()
            animations.wait_locked(self.stage, 500, self.show_missing_piece)
        return

    def show_missing_piece(self):
        self.showing_missing_piece = True
        piece = ItemImage(0, 0, self.create_piece_image(self.rows - 1, self.cols - 1))
        piece.row = self.rows - 1
        piece.col = self.cols - 1
        self.layer.add(piece)
        self.grid[piece.row][piece.col] = piece
        self.set_piece_pos(piece.row, piece.col)
        animations.fade_in_item(piece, 500)
        animations.wait_locked(self.stage, 1500, self.show_missing_piece_callback)
        self.stage.render()
        self.fade_sound.play()
        return

    def escape_key_event(self):
        if self.showing_missing_piece:
            self.continue_sound.play()
            self.minigame_solved_callback()
            return True
        return

    def show_missing_piece_callback(self):
        button_normal_image = assets.load_image('p0_endings_btn_continue_normal.png')
        button_rollover_image = assets.load_image('p0_endings_btn_continue_rollover.png')
        button = ItemImage(216, 404, button_normal_image)
        button.set_rollover_image(button_rollover_image, self.rollover_sound)
        button.add_event_handler(ItemEvent.CLICK, self.continue_click)
        self.layer.add(button)
        return

    def continue_click(self, item, args):
        self.showing_missing_piece = False
        self.minigame_solved_callback()
        self.continue_sound.play()
        return

    def create_piece_image(self, row, col):
        surf = pygame.Surface((self.piece_width, self.piece_height), pygame.SRCALPHA, 32)
        surf.blit(self.puzzle_image.surface, (0, 0), Rect(col * self.piece_width, row * self.piece_height, self.piece_width, self.piece_height))
        if self.tile_image != None:
            surf.blit(self.tile_image.surface, (0, 0))
        return assets.Image(surf)

    def calculate_solved_score(self):
        if self.pause_start_time != None:
            self.pause_total_time += pygame.time.get_ticks() - self.pause_start_time
            self.pause_start_time = None
        elapsed_time = (pygame.time.get_ticks() - self.start_time - self.pause_total_time) / 1000
        if elapsed_time <= self.maximum_time:
            time_score = self.maximum_time_score * (self.maximum_time - elapsed_time) / self.maximum_time
        else:
            time_score = 0
        return [100,
         time_score]

    def select_picture(self):
        pictures_seen = self.stage.game.datastore.user_character_progress.bricklayer_pictures_seen
        selected_picture = None
        random.seed()
        while selected_picture == None:
            pictures = [
             Picture('Piedra Pintada', 'Artigas', 1),
             Picture('Cerro Batoví', 'Tacuarembó', 2),
             Picture('Faro de Cabo Polonio', 'Rocha', 3),
             Picture('Monumento al Ahogado', 'Maldonado', 4),
             Picture('Real de San Carlos', 'Colonia', 5)]
            for number in pictures_seen:
                for picture in pictures:
                    if picture.number == number:
                        pictures.remove(picture)
                        break

            if len(pictures) == 0:
                del pictures_seen[0:len(pictures_seen) / 2]
            else:
                selected_picture = random.choice(pictures)
                pictures_seen.append(selected_picture.number)

        return selected_picture

    def create_character_happy_item(self):
        bricklayer_happy_image = assets.load_image('p1_minigame_bricklayer_happy.png')
        return ItemImage(433, 66, bricklayer_happy_image, None)


class Picture():

    def __init__(self, location, department, number):
        self.location = location
        self.department = department
        self.number = number
        return


