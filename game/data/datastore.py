from framework import assets, stats
from framework.stage import *
from game.data import datamodel, serialization
from game.data.datamodel import CharacterInfo
import collections, uuid, version
BASE_REQUEST_URL = 'http://ws.trojanchicken.com/ded/uy/'
UPDATE_URL = BASE_REQUEST_URL + 'update'
STATS_URL = BASE_REQUEST_URL + 'stats'
ERRORS_URL = BASE_REQUEST_URL + 'errors'
SCORE_KEY = '@i90[pp.'
SCORE_IV = '\x00\x00\x00\x00\x00\x00\x00\x00'
VERSION = version.VERSION
ARTIGAS = 'Artigas'
CANELONES = 'Canelones'
CERRO_LARGO = 'Cerro Largo'
COLONIA = 'Colonia'
DURAZNO = 'Durazno'
FLORES = 'Flores'
FLORIDA = 'Florida'
LAVALLEJA = 'Lavalleja'
MALDONADO = 'Maldonado'
MONTEVIDEO = 'Montevideo'
PAYSANDU = 'Paysandú'
RIO_NEGRO = 'Río Negro'
RIVERA = 'Rivera'
ROCHA = 'Rocha'
SALTO = 'Salto'
SAN_JOSE = 'San José'
SORIANO = 'Soriano'
TACUAREMBO = 'Tacuarembó'
TREINTA_Y_TRES = 'Treinta y Tres'
GENERICO = 'Genérico'
INDIGENA = 'Indígena'
GAUCHO = 'Gaucho'
FOSILES = 'Fósiles'
APARICIO_SARAVIA = 'Aparicio Saravia'
FABINI = 'Fabini'
ARMAS = 'Armas'
MONEDAS = 'Monedas'
BLANES = 'Blanes'
TORRES_GARCIA = 'Torres García'
SOLARI = 'Solari'
ARTE = 'Arte'
GARDEL = 'Gardel'
EUSEBIO_GIMENEZ = 'Eusebio Giménez'
MALE = 1
FEMALE = 2
TALL = 1
SHORT = 2
BRUNETTE = 1
BLONDE = 2
REDHEAD = 3
GREY_HAIRED = 4
SCAR = 1
TATOO = 2
GLASSES = 3
MOLE = 4
SPORT = 1
PET = 2
MAMMAL = 1
BIRD = 2
REPTILE = 3
FISH = 4
HERBIVORE = 1
CARNIVORE = 2
WALK = 1
FLY = 2
SWIM = 3
AQUATIC = 1
TERRESTRIAL = 2
THIEF_CAR_COLORS = {'violet': 'violeta', 'green': 'verde', 'blue': 'azul'}

class Datastore:

    def __init__(self, game):
        self.wrong_witness_visited = False
        self.set_up_data(game)
        return

    def load_CrimeLocations(self):
        full_name = 'test2.txt'
        file = open(full_name, 'r')
        line = file.readline()
        data = []
        my_line = ''
        i = 0
        while line != '':
            i += 1
            line = line.rstrip('\n').rstrip('\r')
            fields = line.split(',')
            crime_location = fields[0]
            fields2 = fields[1].split('(')
            l = len(fields2[0])
            department = fields2[0][1:][:l - 1]
            l = len(fields2[1])
            crime_location_type = fields2[1][:l - 1]
            my_line = 'cl' + str(i) + " = CrimeLocation('" + crime_location + "', '" + department + "', " + crime_location_type + ', None)'
            my_line2 = 'list_crime_locations.append(' + 'cl' + str(i) + ')'
            print(my_line)
            print(crime_location)
            print(department)
            print(crime_location_type)
            data.append(my_line)
            data.append(my_line2)
            line = file.readline()

        file.close()
        file = open('test_nuevo2.txt', 'w')
        for d in data:
            file.write(d + '\n')

        file.close
        return

    def build_note_list_departments(self, departments_pos):
        line = '['
        for d in departments_pos:
            line += 'self.list_departments[' + d + '], '

        line = line[:-2]
        line += ']'
        return line

    def load_rivers(self):
        full_name = 'test.txt'
        file = open(full_name, 'r')
        line = file.readline()
        data = []
        data.append('list_rivers = []')
        data.append('')
        (river, list_deps, length, basin, desc) = ('', '', '', '', '')
        river_count = 0
        while line != '':
            if line != '\n':
                line = line.rstrip('\n').rstrip('\r')
                fields = line.split('|')
                if len(fields) == 2:
                    river = fields[0]
                    list_deps = self.build_note_list_departments(fields[1].split(','))
                    pos = 1
                    desc2 = None
                elif pos == 1:
                    length = fields[0]
                    pos = 2
                elif pos == 2:
                    basin = fields[0]
                    pos = 3
                elif pos == 3:
                    desc = fields[0]
                    pos = 4
                elif pos == 4:
                    desc2 = fields[0]
            else:
                river_count += 1
                if not desc2:
                    my_line = 'r' + str(river_count) + ' = datamodel.RiverNote("' + river + '", ' + list_deps + ', "' + length + '", "' + basin + '", "' + desc + '", None)'
                else:
                    my_line = 'r' + str(river_count) + ' = datamodel.RiverNote("' + river + '", ' + list_deps + ', "' + length + '", "' + basin + '", "' + desc + '", "' + desc2 + '")'
                data.append(my_line)
                data.append('list_rivers.append(r' + str(river_count) + ')')
                my_line = ''
            line = file.readline()

        file.close()
        file = open('test_nuevo.txt', 'w')
        data.append('')
        data.append('return list_rivers')
        for d in data:
            file.write(d + '\n')

        file.close
        return

    def load_lagoons(self):
        full_name = 'test.txt'
        file = open(full_name, 'r')
        line = file.readline()
        data = []
        data.append('list_lagoons = []')
        data.append('')
        (lagoon, list_deps, surface, desc) = ('', '', '', '')
        lagoon_count = 0
        while line != '':
            if line != '\n':
                line = line.rstrip('\n').rstrip('\r')
                fields = line.split('|')
                if len(fields) == 2:
                    lagoon = fields[0]
                    list_deps = self.build_note_list_departments(fields[1].split(','))
                    pos = 1
                    desc2 = None
                elif pos == 1:
                    surface = fields[0]
                    pos = 2
                elif pos == 2:
                    desc = fields[0]
                    pos = 3
                elif pos == 3:
                    desc2 = fields[0]
            else:
                lagoon_count += 1
                if not desc2:
                    my_line = 'r' + str(lagoon_count) + ' = datamodel.LagoonNote("' + lagoon + '", ' + list_deps + ', "' + surface + '", "' + desc + '", None)'
                else:
                    my_line = 'r' + str(lagoon_count) + ' = datamodel.LagoonNote("' + lagoon + '", ' + list_deps + ', "' + surface + '", "' + desc + '", "' + desc2 + '")'
                data.append(my_line)
                data.append('list_lagoons.append(l' + str(lagoon_count) + ')')
                my_line = ''
            line = file.readline()

        file.close()
        file = open('test_nuevo.txt', 'w')
        data.append('')
        data.append('return list_lagoons')
        for d in data:
            file.write(d + '\n')

        file.close
        return

    def load_hills(self):
        full_name = 'test.txt'
        file = open(full_name, 'r')
        line = file.readline()
        data = []
        data.append('list_hills = []')
        data.append('')
        (hill, dep, height, desc) = ('', '', '', '')
        hill_count = 0
        while line != '':
            if line != '\n':
                line = line.rstrip('\n').rstrip('\r')
                fields = line.split('|')
                if len(fields) == 3:
                    hill = fields[0]
                    article = fields[1]
                    dep = fields[2]
                    pos = 1
                    desc2 = None
                elif pos == 1:
                    height = fields[0]
                    pos = 2
                elif pos == 2:
                    desc = fields[0]
                    pos = 3
                elif pos == 3:
                    desc2 = fields[0]
            else:
                hill_count += 1
                if not desc2:
                    my_line = 'h' + str(hill_count) + ' = datamodel.HillNote("' + hill + '", ' + article + '", ' + dep + ', "' + height + '", "' + desc + '", None)'
                else:
                    my_line = 'h' + str(hill_count) + ' = datamodel.HillNote("' + hill + '", ' + article + '", ' + dep + ', "' + height + '", "' + desc + '", "' + desc2 + '")'
                data.append(my_line)
                data.append('list_hills.append(h' + str(hill_count) + ')')
                my_line = ''
            line = file.readline()

        file.close()
        file = open('test_nuevo.txt', 'w')
        data.append('')
        data.append('return list_hills')
        for d in data:
            file.write(d + '\n')

        file.close
        return

    def load_history_facts(self):
        full_name = 'test.txt'
        file = open(full_name, 'r')
        line = file.readline()
        data = []
        data.append('list_history_facts = []')
        data.append('')
        (history_fact, sentence_start, article, list_deps, date, desc) = ('', '', '',
                                                                          '', '',
                                                                          '')
        history_fact_count = 0
        pos = 1
        desc2 = None
        while line != '':
            if line != '\n':
                line = line.rstrip('\n').rstrip('\r')
                fields = line.split('|')
                if pos == 1:
                    sentence_start = fields[0]
                    pos = 2
                    desc2 = None
                elif pos == 2:
                    article = fields[0]
                    pos = 3
                elif pos == 3:
                    history_fact = fields[0]
                    list_deps = self.build_note_list_departments(fields[1].split(','))
                    pos = 4
                elif pos == 4:
                    date = fields[0]
                    pos = 5
                elif pos == 5:
                    desc = fields[0]
                    pos = 6
                elif pos == 6:
                    desc2 = fields[0]
            else:
                history_fact_count += 1
                if not desc2:
                    my_line = 'hf' + str(history_fact_count) + ' = datamodel.HistoryFactNote("' + sentence_start + '", "' + article + '", "' + history_fact + '", ' + list_deps + ', "' + date + '", "' + desc + '", None)'
                else:
                    my_line = 'hf' + str(history_fact_count) + ' = datamodel.HistoryFactNote("' + sentence_start + '", "' + article + '", "' + history_fact + '", ' + list_deps + ', "' + date + '", "' + desc + '", "' + desc2 + '")'
                data.append(my_line)
                data.append('list_history_facts.append(hf' + str(history_fact_count) + ')')
                my_line = ''
                pos = 1
            line = file.readline()

        file.close()
        file = open('test_nuevo.txt', 'w')
        data.append('')
        data.append('return list_history_facts')
        for d in data:
            file.write(d + '\n')

        file.close
        return

    def load_locations(self):
        full_name = 'test.txt'
        file = open(full_name, 'r')
        line = file.readline()
        data = []
        data.append('list_locations = []')
        data.append('')
        (location, dep, loc_type, sentence_start, population, desc) = ('', '', '',
                                                                       '', '', '')
        location_count = 0
        while line != '':
            if line != '\n':
                line = line.rstrip('\n').rstrip('\r')
                fields = line.split('|')
                if len(fields) == 2:
                    location = fields[0]
                    dep = fields[1]
                    pos = 1
                elif pos == 1:
                    loc_type = fields[0]
                    pos = 2
                elif pos == 2:
                    if loc_type == 'Ciudad':
                        sentence_start = 'visitar la ciudad de'
                    elif loc_type == 'Pueblo':
                        sentence_start = 'visitar el pueblo de'
                    elif loc_type == 'Balneario':
                        sentence_start = 'visitar el balneario'
                    elif loc_type == 'Población':
                        sentence_start = 'visitar la población de'
                    elif loc_type == 'Centro poblado':
                        sentence_start = 'visitar el centro poblado de'
                    elif loc_type == 'Villa':
                        sentence_start = 'visitar villa'
                    elif loc_type == 'Fraccionamiento':
                        sentence_start = 'visitar el fraccionamiento de'
                    population = fields[0]
                    pos = 3
                elif pos == 3:
                    desc = fields[0]
            else:
                location_count += 1
                my_line = 'loc' + str(location_count) + ' = datamodel.LocationNote("' + location + '", ' + dep + ', "' + loc_type + '", "' + sentence_start + '", "' + population + '", "' + desc + '")'
                data.append(my_line)
                data.append('list_locations.append(loc' + str(location_count) + ')')
                my_line = ''
            line = file.readline()

        file.close()
        file = open('test_nuevo.txt', 'w')
        data.append('')
        data.append('return list_locations')
        for d in data:
            file.write(d + '\n')

        file.close
        return

    def load_writers(self):
        full_name = 'test.txt'
        file = open(full_name, 'r')
        line = file.readline()
        data = []
        data.append('list_writers = []')
        data.append('')
        (writer, dep, dates, desc) = ('', '', '', '')
        writer_count = 0
        while line != '':
            if line != '\n':
                line = line.rstrip('\n').rstrip('\r')
                fields = line.split('|')
                if len(fields) == 3:
                    writer = fields[0]
                    sex = fields[1]
                    dep = fields[2]
                    pos = 1
                elif pos == 1:
                    dates = fields[0]
                    pos = 2
                elif pos == 2:
                    desc = fields[0]
            else:
                writer_count += 1
                my_line = 'wr' + str(writer_count) + ' = datamodel.WriterNote("' + writer + '", ' + sex + '", ' + dep + ', "' + dates + '", "' + desc + '")'
                data.append(my_line)
                data.append('list_writers.append(wr' + str(writer_count) + ')')
                my_line = ''
            line = file.readline()

        file.close()
        file = open('test_nuevo.txt', 'w')
        data.append('')
        data.append('return list_writers')
        for d in data:
            file.write(d + '\n')

        file.close
        return

    def set_up_data(self, game):
        self.game = game
        self.list_departments = self.set_up_departments()
        self.list_animals = self.set_up_animals()
        self.list_sports = self.set_up_sports()
        self.list_stolen_objects = self.set_up_stolen_objects()
        self.list_crime_locations = self.set_up_crime_locations()
        self.list_thieves = self.set_up_thieves()
        self.list_lair_sets = self.set_up_lair_sets()
        self.list_witnesses = self.set_up_witness()
        self.list_statements = self.set_up_statements()
        self.list_identikit_statements = self.set_up_identikit_statements()
        self.list_janitor_statements = self.set_up_janitor_statements()
        self.list_clue_types = self.set_up_clue_types()
        self.list_clues = self.set_up_clues()
        self.list_rivers = self.set_up_rivers()
        self.list_lagoons = self.set_up_lagoons()
        self.list_hills = self.set_up_hills()
        self.list_history_facts = self.set_up_history_facts()
        self.list_locations = self.set_up_locations()
        self.list_writers = self.set_up_writers()
        self.notes_type_index = {'HISTORY_FACT': (self.list_history_facts), 'RIVER': (self.list_rivers), 
           'LAGOON': (self.list_lagoons), 
           'HILL': (self.list_hills), 
           'LOCATION': (self.list_locations), 
           'WRITER': (self.list_writers)}
        self.department_type_index = collections.defaultdict((lambda : collections.defaultdict(list)))
        for note in self.list_history_facts + self.list_rivers + self.list_lagoons + self.list_hills + self.list_locations + self.list_writers:
            for department in note.get_departments():
                self.department_type_index[department.name][note.type].append(note)

        self.load_characters()
        self.user_character = None
        self.highscores = None
        return

    def show_clue_messages(self):
        messages = []
        longest_message = ''
        for dep_clues in list(self.department_type_index.values()):
            for (note_type, note_items) in list(dep_clues.items()):
                for note_item in note_items:
                    for clue in self.list_clues:
                        clue_type = self.get_clue_type(note_type)
                        if clue_type in clue.list_types:
                            stageclue = datamodel.StageClue(clue, note_item)
                            message = stageclue.build_item_message()
                            if len(message) > len(longest_message):
                                longest_message = message
                            messages.append((clue.id, note_type, message))

        messages.sort()
        messages.append(['Mensaje más largo: ' + longest_message])
        messages.append([])
        dep_messages = []
        for dep_clues in list(self.department_type_index.values()):
            for (note_type, note_items) in list(dep_clues.items()):
                for note_item in note_items:
                    stageclue = datamodel.StageClue(clue, note_item)
                    message = stageclue.build_right_department_message(self.list_departments[0])
                    dep_messages.append((clue.id, note_type, message))

        dep_messages.sort()
        messages += dep_messages
        messages.append([])
        location_messages = []
        for dep_clues in list(self.department_type_index.values()):
            for (note_type, note_items) in list(dep_clues.items()):
                for note_item in note_items:
                    if hasattr(note_item, 'description'):
                        data = [
                         note_item.type, note_item.name, note_item.description]
                        description = note_item.description
                    elif note_item.description2 != None:
                        data = [
                         note_item.type, note_item.name, note_item.description1, note_item.description2]
                        description = note_item.description1 + ' ' + note_item.description2
                    else:
                        data = [
                         note_item.type, note_item.name, note_item.description1]
                        description = note_item.description1
                    data.append('|')
                    valid_department = False
                    if hasattr(note_item, 'department'):
                        depnames = note_item.department.name
                        data.append(depnames)
                        if note_item.department.name in description:
                            valid_department = True
                    else:
                        depnames = ''
                        for dep in note_item.list_departments:
                            data.append(dep.name)
                            if dep.name in description:
                                valid_department = True
                            if depnames == '':
                                depnames = dep.name
                            else:
                                depnames += ', ' + dep.name

                    if not valid_department:
                        raise Exception('Invalid department associated (' + depnames + ') with clue:\n' + str(data))
                    location_messages.append(data)

        location_messages.sort()
        messages += location_messages
        assets.save_data('clues.txt', messages, ';', False)
        print('Clue messages saved!')
        return

    def load_characters(self):
        data = assets.load_data('characters.dat', ';', False, from_dynamic_path=True)
        self.characters = []
        self.max_char_id = 0
        active_character = None
        if len(data) > 0:
            for character in data:
                if len(character) >= 2:
                    try:
                        character_info = datamodel.CharacterInfo(character[0] == '1', int(character[1]), self.decode_name(character[2]), int(character[3]), character[4], character[5], int(character[6]))
                        self.characters.append(character_info)
                        if character_info.active:
                            active_character = character_info
                        if character_info.id > self.max_char_id:
                            self.max_char_id = character_info.id + 1
                    except Exception:
                        print('Error reading characters')
                        (type, value, tb) = sys.exc_info()
                        stats.report_error(type, value, tb)

        return active_character

    def save_characters(self):
        characters_data = []
        for character in self.characters:
            if character.active:
                active_str = '1'
            else:
                active_str = '0'
            characters_data.append((active_str, str(character.id), self.encode_name(character.name), str(character.avatar), character.sex, character.location, str(character.range_level)))

        assets.save_data('characters.dat', characters_data)
        return

    def encode_name(self, s):
        return s.replace('$', '$s').replace(';', '$d')

    def decode_name(self, s):
        return s.replace('$d', ';').replace('$s', '$')

    def create_character(self, name, is_male, avatar, location, set_active=True):
        if is_male:
            sex = 'M'
        else:
            sex = 'F'
        id = self.max_char_id + 1
        self.max_char_id = id
        charinfo = datamodel.CharacterInfo(set_active, id, name, avatar, sex, location, 0)
        if set_active:
            for character in self.characters:
                character.active = False

        self.characters.append(charinfo)
        serialization.delete_character(charinfo.id)
        self.save_characters()
        return charinfo

    def load_character(self, charinfo):
        (self.user_character, self.user_character_progress, self.user_character_stage) = serialization.open_character(self, charinfo)
        return

    def delete_character(self, charinfo):
        self.characters.remove(charinfo)
        self.save_characters()
        serialization.delete_character(charinfo.id)
        return

    def save_character(self, stage, check_save_in_development):
        serialization.save_character(self, self.user_character, self.user_character_progress, self.game, stage, check_save_in_development)
        self.game.stats.save_if_pending()
        return

    def get_highscores(self):
        if self.highscores == None:
            self.load_highscores()
        return self.highscores

    def load_highscores(self):
        self.highscores = {}
        self.highscores_pending_save = False
        data = assets.load_data('highscores.dat', ';', False, from_dynamic_path=True)
        if data != None:
            for line in data:
                try:
                    category = line[0]
                    characters = []
                    k = 1
                    while k < len(line):
                        name = self.decode_name(line[k])
                        c_uuid = uuid.UUID(line[k + 1])
                        score = int(line[k + 2])
                        character = datamodel.HighscoreCharacter(name, c_uuid, score)
                        characters.append(character)
                        k += 3

                    self.highscores[category] = characters
                except Exception:
                    print('Error reading highscores')
                    (type, value, tb) = sys.exc_info()
                    stats.report_error(type, value, tb)

        return

    def get_highscore_data(self):
        highscores = self.get_highscores()
        data = []
        for (category, characters) in list(highscores.items()):
            line = [
             category]
            for c in characters:
                line.append(self.encode_name(c.name))
                line.append(str(c.uuid))
                line.append(str(c.score))

            data.append(line)

        return data

    def save_highscores(self):
        if self.highscores != None and self.highscores_pending_save:
            data = self.get_highscore_data()
            assets.save_data('highscores.dat', data)
            self.highscores_pending_save = False
        return

    def add_score(self, category, character, score):
        if self.highscores == None:
            self.highscores = {}
        highscore_character = datamodel.HighscoreCharacter(character.charinfo.name, character.uuid, score)
        if category not in self.highscores:
            self.highscores[category] = [highscore_character]
            self.highscores_pending_save = True
        else:
            k = 0
            characters = self.highscores[category]
            update_score = True
            for i in range(len(characters)):
                if characters[i].uuid == character.uuid:
                    if characters[i].score >= score:
                        update_score = False
                    else:
                        del characters[i]
                    break

            if update_score:
                k = 0
                while k < len(characters):
                    if characters[k].score < score:
                        break
                    else:
                        k += 1

                characters.insert(k, highscore_character)
                if len(characters) > 10:
                    del characters[10:]
                self.highscores_pending_save = True
        return

    def update_score_name(self, character):
        if self.highscores != None:
            for (category, characters) in list(self.highscores.items()):
                for c in characters:
                    if c.uuid == character.uuid:
                        c.name = character.charinfo.name
                        self.highscores_pending_save = True

        return

    def set_up_departments(self):
        list_departments = []
        cities = [
         datamodel.CityPin(152, 204, False, 'Baltasar Brum', 2, 0, (125, 200)), datamodel.CityPin(133, 113, False, 'Tomás Gomensoro', 3, 1, (100, 109)), datamodel.CityPin(90, 74, False, 'Bella Unión', 2, 0, (58, 69)), datamodel.CityPin(359, 106, True, 'Artigas', 1, 0, (348, 107))]
        d1 = datamodel.Department(ARTIGAS, 'artigas', (32, 27), (22, 10), cities, 'medalla1', 'field')
        list_departments.append(d1)
        cities = [
         datamodel.CityPin(89, 131, False, 'Santa Lucía', 2, 0, (68, 134)), datamodel.CityPin(136, 158, False, 'Canelones', 1, 0, (121, 162)), datamodel.CityPin(155, 243, False, 'Las Piedras', 2, 0, (134, 253)), datamodel.CityPin(257, 248, True, 'Pando', 1, 0, (240, 255))]
        d2 = datamodel.Department(CANELONES, 'canelones', (60, 26), (36, 54), cities, 'medalla2', 'beach')
        list_departments.append(d2)
        cities = [
         datamodel.CityPin(227, 199, False, 'Fraile Muerto', 2, 0, (207, 207)), datamodel.CityPin(321, 72, True, 'Isidoro Noblía', 3, 1, (292, 72)), datamodel.CityPin(311, 168, True, 'Melo', 1, 0, (293, 175)), datamodel.CityPin(464, 224, True, 'Río Branco', 2, 0, (431, 229))]
        d3 = datamodel.Department(CERRO_LARGO, 'cerrolargo', (84, 15), (46, 28), cities, 'medalla3', 'field')
        list_departments.append(d3)
        cities = [
         datamodel.CityPin(68, 106, False, 'Carmelo', 1, 0, (49, 118)), datamodel.CityPin(226, 294, False, 'Colonia del Sacramento', 3, 2, (207, 296)), datamodel.CityPin(359, 282, True, 'Juan Lacaze', 2, 0, (331, 291)), datamodel.CityPin(376, 77, True, 'Florencio Sánchez', 3, 1, (354, 61))]
        d4 = datamodel.Department(COLONIA, 'colonia', (35, 33), (18, 49), cities, 'medalla4', 'beach')
        list_departments.append(d4)
        cities = [
         datamodel.CityPin(158, 279, False, 'Durazno', 1, 0, (152, 280)), datamodel.CityPin(291, 234, True, 'Carmen', 1, 0, (272, 245)), datamodel.CityPin(364, 258, True, 'Sarandí del Yí', 2, 0, (348, 272)), datamodel.CityPin(382, 144, True, 'Blanquillo', 2, 0, (352, 142))]
        d5 = datamodel.Department(DURAZNO, 'durazno', (27, 19), (31, 34), cities, 'medalla5', 'field')
        list_departments.append(d5)
        cities = [
         datamodel.CityPin(199, 17, False, 'Andresito', 1, 0, (188, 22)), datamodel.CityPin(225, 301, False, 'Ismael Cortinas', 3, 1, (200, 308)), datamodel.CityPin(330, 134, True, 'Juan José Castro', 3, 2, (301, 129)), datamodel.CityPin(280, 148, True, 'Trinidad', 1, 0, (263, 156))]
        d6 = datamodel.Department(FLORES, 'flores', (140, 12), (27, 42), cities, 'medalla6', 'field')
        list_departments.append(d6)
        cities = [
         datamodel.CityPin(167, 143, False, 'Sarandí Grande', 2, 0, (139, 147)), datamodel.CityPin(193, 240, False, 'Florida', 1, 0, (176, 242)), datamodel.CityPin(321, 226, True, 'Casupá', 1, 0, (301, 244)), datamodel.CityPin(335, 155, True, 'Cerro Colorado', 3, 1, (309, 170))]
        d7 = datamodel.Department(FLORIDA, 'florida', (132, 0), (34, 43), cities, 'medalla7', 'field')
        list_departments.append(d7)
        cities = [
         datamodel.CityPin(232, 34, False, 'José Batlle y Ordóñez', 3, 2, (203, 30)), datamodel.CityPin(215, 257, False, 'Minas', 1, 0, (195, 272)), datamodel.CityPin(155, 310, False, 'Solís de Mataojo', 3, 2, (135, 306)), datamodel.CityPin(348, 33, True, 'José Pedro Varela', 3, 2, (326, 25))]
        d8 = datamodel.Department(LAVALLEJA, 'lavalleja', (134, 9), (43, 44), cities, 'medalla8', 'field')
        list_departments.append(d8)
        cities = [
         datamodel.CityPin(177, 290, False, 'Piriápolis', 1, 0, (159, 307)), datamodel.CityPin(232, 305, False, 'Maldonado', 1, 0, (229, 304)), datamodel.CityPin(278, 272, True, 'San Carlos', 2, 0, (247, 270)), datamodel.CityPin(288, 92, True, 'Aiguá', 1, 0, (285, 89))]
        d9 = datamodel.Department(MALDONADO, 'maldonado', (123, 11), (45, 51), cities, 'medalla9', 'beach')
        list_departments.append(d9)
        cities = [
         datamodel.CityPin(307, 282, False, 'Centro', 1, 0, (299, 285), 'el'), datamodel.CityPin(220, 240, False, 'Villa del Cerro', 3, 2, (199, 238), 'la'), datamodel.CityPin(377, 177, True, 'Jardines del Hipódromo', 3, 2, (348, 177)), datamodel.CityPin(453, 254, True, 'Carrasco', 2, 0, (422, 261))]
        d10 = datamodel.Department(MONTEVIDEO, 'montevideo', (36, 12), (35, 58), cities, 'medalla10', 'beach')
        list_departments.append(d10)
        cities = [
         datamodel.CityPin(199, 252, False, 'Piedras Coloradas', 3, 1, (175, 260)), datamodel.CityPin(133, 147, False, 'Quebracho', 1, 0, (121, 152)), datamodel.CityPin(96, 249, False, 'Paysandú', 1, 0, (81, 258)), datamodel.CityPin(291, 235, True, 'Guichón', 1, 0, (270, 262))]
        d11 = datamodel.Department(PAYSANDU, 'paysandu', (76, 27), (19, 24), cities, 'medalla11', 'field')
        list_departments.append(d11)
        cities = [
         datamodel.CityPin(218, 127, False, 'Young', 1, 0, (220, 127)), datamodel.CityPin(127, 111, False, 'San Javier', 1, 0, (105, 120)), datamodel.CityPin(135, 196, False, 'Nuevo Berlín', 2, 0, (112, 205)), datamodel.CityPin(81, 247, False, 'Fray Bentos', 2, 0, (56, 248))]
        d12 = datamodel.Department(RIO_NEGRO, 'rionegro', (66, 35), (18, 34), cities, 'medalla12', 'field')
        list_departments.append(d12)
        cities = [
         datamodel.CityPin(140, 93, False, 'Tranqueras', 2, 0, (121, 95)), datamodel.CityPin(211, 184, False, 'Minas de Corrales', 3, 2, (188, 186)), datamodel.CityPin(187, 27, False, 'Rivera', 1, 0, (187, 27)), datamodel.CityPin(384, 239, True, 'Vichadero', 1, 0, (372, 250))]
        d13 = datamodel.Department(RIVERA, 'rivera', (66, 12), (39, 17), cities, 'medalla13', 'field')
        list_departments.append(d13)
        cities = [
         datamodel.CityPin(232, 100, False, 'Lascano', 1, 0, (222, 110)), datamodel.CityPin(212, 258, False, 'Rocha', 1, 0, (198, 271)), datamodel.CityPin(304, 206, True, 'Castillos', 1, 0, (281, 215)), datamodel.CityPin(360, 109, True, 'Chuy', 1, 0, (347, 116))]
        d14 = datamodel.Department(ROCHA, 'rocha', (183, 14), (53, 43), cities, 'medalla14', 'beach')
        list_departments.append(d14)
        cities = [
         datamodel.CityPin(104, 39, False, 'Belén', 1, 0, (98, 46)), datamodel.CityPin(109, 114, False, 'Constitución', 2, 0, (71, 119)), datamodel.CityPin(80, 194, False, 'Salto', 1, 0, (67, 206)), datamodel.CityPin(300, 110, True, 'Pueblo Lavalleja', 3, 1, (262, 110))]
        d15 = datamodel.Department(SALTO, 'salto', (57, 36), (21, 17), cities, 'medalla15', 'field')
        list_departments.append(d15)
        cities = [
         datamodel.CityPin(185, 189, False, 'Ecilda Paullier', 2, 0, (149, 184)), datamodel.CityPin(273, 162, True, 'San José de Mayo', 3, 2, (246, 165)), datamodel.CityPin(302, 268, True, 'Libertad', 1, 0, (287, 276)), datamodel.CityPin(374, 312, True, 'Ciudad del Plata', 3, 1, (349, 314))]
        d16 = datamodel.Department(SAN_JOSE, 'sanjose', (157, 8), (30, 49), cities, 'medalla16', 'field')
        list_departments.append(d16)
        cities = [
         datamodel.CityPin(148, 182, False, 'Dolores', 1, 0, (138, 192)), datamodel.CityPin(190, 91, False, 'Mercedes', 1, 0, (175, 95)), datamodel.CityPin(328, 228, True, 'José Enrique Rodó', 3, 2, (299, 231)), datamodel.CityPin(374, 285, True, 'Cardona', 1, 0, (359, 291))]
        d17 = datamodel.Department(SORIANO, 'soriano', (86, 14), (18, 41), cities, 'medalla17', 'field')
        list_departments.append(d17)
        cities = [
         datamodel.CityPin(149, 306, False, 'Paso de los Toros', 3, 2, (123, 311)), datamodel.CityPin(243, 114, False, 'Tacuarembó', 2, 0, (214, 108)), datamodel.CityPin(334, 131, True, 'Ansina', 1, 0, (312, 135)), datamodel.CityPin(262, 248, True, 'San Gregorio de Polanco', 3, 2, (234, 253))]
        d18 = datamodel.Department(TACUAREMBO, 'tacuarembo', (132, 16), (33, 22), cities, 'medalla18', 'field')
        list_departments.append(d18)
        cities = [
         datamodel.CityPin(77, 116, False, 'Santa Clara de Olimar', 3, 2, (55, 110)), datamodel.CityPin(227, 220, False, 'Treinta y Tres', 2, 0, (203, 225)), datamodel.CityPin(348, 124, True, 'Vergara', 1, 0, (337, 131)), datamodel.CityPin(375, 207, True, 'Gral. Enrique Martínez', 3, 2, (360, 209))]
        d19 = datamodel.Department(TREINTA_Y_TRES, 'treintaytres', (29, 56), (47, 36), cities, 'medalla19', 'field')
        list_departments.append(d19)
        return list_departments

    def set_up_crime_locations(self):
        list_crime_locations = []
        cl1 = datamodel.CrimeLocation('el', 'Museo Departamental', self.list_departments[0], GENERICO, None)
        list_crime_locations.append(cl1)
        cl2 = datamodel.CrimeLocation('el', 'Museo Histórico Departamental "Juan Spikerman"', self.list_departments[1], GENERICO, None)
        list_crime_locations.append(cl2)
        cl3 = datamodel.CrimeLocation('el', 'Museo Arqueológico "Prof. Antonio Taddei"', self.list_departments[1], INDIGENA, FOSILES)
        list_crime_locations.append(cl3)
        cl4 = datamodel.CrimeLocation('el', 'Museo General Aparicio Saravia', self.list_departments[2], APARICIO_SARAVIA, None)
        list_crime_locations.append(cl4)
        cl5 = datamodel.CrimeLocation('el', 'Museo Histórico Regional', self.list_departments[2], GENERICO, None)
        list_crime_locations.append(cl5)
        cl6 = datamodel.CrimeLocation('el', 'Museo Municipal', self.list_departments[3], GENERICO, None)
        list_crime_locations.append(cl6)
        cl7 = datamodel.CrimeLocation('el', 'Museo del Indígena', self.list_departments[3], INDIGENA, None)
        list_crime_locations.append(cl7)
        cl8 = datamodel.CrimeLocation('el', 'Museo Paleontológico y Arqueológico', self.list_departments[3], INDIGENA, FOSILES)
        list_crime_locations.append(cl8)
        cl9 = datamodel.CrimeLocation('el', 'Museo del Gaucho', self.list_departments[4], GAUCHO, None)
        list_crime_locations.append(cl9)
        cl10 = datamodel.CrimeLocation('el', 'Museo Departamental', self.list_departments[5], FOSILES, None)
        list_crime_locations.append(cl10)
        cl11 = datamodel.CrimeLocation('el', 'Museo Cau Rusiñol', self.list_departments[5], ARTE, None)
        list_crime_locations.append(cl11)
        cl12 = datamodel.CrimeLocation('el', 'Museo Histórico Municipal', self.list_departments[6], GENERICO, None)
        list_crime_locations.append(cl12)
        cl13 = datamodel.CrimeLocation('el', 'Museo Municipal del Gaucho', self.list_departments[7], GAUCHO, None)
        list_crime_locations.append(cl13)
        cl14 = datamodel.CrimeLocation('el', 'Museo Eduardo Fabini', self.list_departments[7], FABINI, None)
        list_crime_locations.append(cl14)
        cl15 = datamodel.CrimeLocation('la', 'Casa de la cultura', self.list_departments[7], GENERICO, None)
        list_crime_locations.append(cl15)
        cl16 = datamodel.CrimeLocation('el', 'Museo Didáctico Artiguista', self.list_departments[8], ARMAS, None)
        list_crime_locations.append(cl16)
        cl17 = datamodel.CrimeLocation('el', 'Museo Regional "Francisco Mazzoni"', self.list_departments[8], GENERICO, None)
        list_crime_locations.append(cl17)
        cl18 = datamodel.CrimeLocation('el', 'Museo del Gaucho y de la Moneda', self.list_departments[9], GAUCHO, MONEDAS)
        list_crime_locations.append(cl18)
        cl19 = datamodel.CrimeLocation('el', 'Museo Nacional de Artes Visuales', self.list_departments[9], ARTE, None)
        list_crime_locations.append(cl19)
        cl20 = datamodel.CrimeLocation('el', 'Museo Municipal de Bellas Artes "Juan Manuel Blanes"', self.list_departments[9], BLANES, None)
        list_crime_locations.append(cl20)
        cl21 = datamodel.CrimeLocation('el', 'Museo Torres García', self.list_departments[9], TORRES_GARCIA, None)
        list_crime_locations.append(cl21)
        cl22 = datamodel.CrimeLocation('el', 'Museo Municipal Precolombino y Colonial', self.list_departments[9], INDIGENA, ARMAS)
        list_crime_locations.append(cl22)
        cl23 = datamodel.CrimeLocation('el', 'Museo de Artes Plásticas', self.list_departments[10], ARTE, None)
        list_crime_locations.append(cl23)
        cl24 = datamodel.CrimeLocation('el', 'Museo Histórico Municipal', self.list_departments[10], GENERICO, None)
        list_crime_locations.append(cl24)
        cl25 = datamodel.CrimeLocation('el', 'Museo "Luis A. Solari"', self.list_departments[11], SOLARI, None)
        list_crime_locations.append(cl25)
        cl26 = datamodel.CrimeLocation('el', 'Museo Municipal de Historia y Arqueología', self.list_departments[12], GENERICO, None)
        list_crime_locations.append(cl26)
        cl27 = datamodel.CrimeLocation('el', 'Museo Municipal de Artes Plásticas', self.list_departments[12], ARTE, None)
        list_crime_locations.append(cl27)
        cl28 = datamodel.CrimeLocation('el', 'Museo Regional', self.list_departments[13], MONEDAS, GENERICO)
        list_crime_locations.append(cl28)
        cl29 = datamodel.CrimeLocation('el', 'Museo de la Fortaleza de Santa Teresa', self.list_departments[13], ARMAS, None)
        list_crime_locations.append(cl29)
        cl30 = datamodel.CrimeLocation('el', 'Museo del Fuerte San Miguel', self.list_departments[13], ARMAS, None)
        list_crime_locations.append(cl30)
        cl31 = datamodel.CrimeLocation('el', 'Museo Histórico Municipal', self.list_departments[14], GENERICO, None)
        list_crime_locations.append(cl31)
        cl32 = datamodel.CrimeLocation('el', 'Museo del Hombre y la Tecnología', self.list_departments[14], GENERICO, None)
        list_crime_locations.append(cl32)
        cl33 = datamodel.CrimeLocation('el', 'Museo Departamental', self.list_departments[15], GENERICO, None)
        list_crime_locations.append(cl33)
        cl34 = datamodel.CrimeLocation('el', 'Museo de Bellas Artes', self.list_departments[15], ARTE, None)
        list_crime_locations.append(cl34)
        cl35 = datamodel.CrimeLocation('el', 'Museo Santo Domingo', self.list_departments[16], FOSILES, INDIGENA)
        list_crime_locations.append(cl35)
        cl36 = datamodel.CrimeLocation('la', 'Biblioteca-Museo "Eusebio Giménez"', self.list_departments[16], EUSEBIO_GIMENEZ, None)
        list_crime_locations.append(cl36)
        cl37 = datamodel.CrimeLocation('el', 'Museo Carlos Gardel', self.list_departments[17], GARDEL, None)
        list_crime_locations.append(cl37)
        cl38 = datamodel.CrimeLocation('el', 'Museo del Indio y del Gaucho "Washington Escobar"', self.list_departments[17], INDIGENA, GAUCHO)
        list_crime_locations.append(cl38)
        cl39 = datamodel.CrimeLocation('el', 'Museo Abierto de Artes Visuales', self.list_departments[17], ARTE, None)
        list_crime_locations.append(cl39)
        cl40 = datamodel.CrimeLocation('el', 'Museo Histórico', self.list_departments[18], GENERICO, None)
        list_crime_locations.append(cl40)
        cl41 = datamodel.CrimeLocation('el', 'Museo Municipal de Bellas Artes "Agustín Araujo"', self.list_departments[18], ARTE, None)
        list_crime_locations.append(cl41)
        return list_crime_locations

    def set_up_rivers(self):
        list_rivers = []
        r1 = datamodel.RiverNote('Río Arapey', [self.list_departments[14]], '240 km', '11.410 km2', 'Atraviesa todo el departamento de Salto y desemboca en el río Uruguay.', None)
        list_rivers.append(r1)
        r2 = datamodel.RiverNote('Río Cebollatí', [self.list_departments[7], self.list_departments[13], self.list_departments[18]], '240 km', '14.085 km2', 'Corre de SO a NO', 'Sirve de límite entre los departamentos de Rocha con Lavalleja y Treinta y Tres.')
        list_rivers.append(r2)
        r3 = datamodel.RiverNote('Río Cuareim', [self.list_departments[0]], '230 km', '13.390 km2', 'Nace en Brasil y bordea el departamento de Artigas hasta que  desemboca en el río Uruguay.', None)
        list_rivers.append(r3)
        r4 = datamodel.RiverNote('Río Daymán', [self.list_departments[14], self.list_departments[10]], '150 km', '3.183 km2', 'Sirve de límite entre los departamentos de Salto y Paysandú. Desemboca en el río Uruguay, cerca de allí se encuentran las termas del mismo nombre.', None)
        list_rivers.append(r4)
        r5 = datamodel.RiverNote('Río Olimar', [self.list_departments[18]], '155 km', '5.320 km2', 'Nace en el departamento de Treinta y Tres y lo atraviesa de O a E para luego desembocar en el río Cebollatí.', None)
        list_rivers.append(r5)
        r6 = datamodel.RiverNote('Río Queguay', [self.list_departments[10]], '280 km', '7.866 km2', 'Nace en el departamento de Paysandú y desemboca en el río Uruguay.', None)
        list_rivers.append(r6)
        r7 = datamodel.RiverNote('Río Rosario', [self.list_departments[3]], '90 km', '1.745 km2', 'Nace en el departamento de Colonia y lo atraviesa de N a S para luego desembocar en el Río de la Plata.', None)
        list_rivers.append(r7)
        r8 = datamodel.RiverNote('Río San José', [self.list_departments[5], self.list_departments[15]], '130 km', '3.543 km2', 'Nace en el departamento de Flores atraviesa el departamento de San José de NO a SE y desemboca en el río Santa Lucía.', None)
        list_rivers.append(r8)
        r9 = datamodel.RiverNote('Río San Juan', [self.list_departments[3]], '80 km', '1.500 km2', 'Nace en el departamento de Colonia, corre de NE a SO y desemboca en el Río de la Plata.', None)
        list_rivers.append(r9)
        r10 = datamodel.RiverNote('Río San Luis', [self.list_departments[13]], '45 km', '2.360 km2', 'Nace en el departamento de Rocha y desemboca en la laguna Merín.', None)
        list_rivers.append(r10)
        r11 = datamodel.RiverNote('Río San Salvador', [self.list_departments[16]], '135 km', '3.000 km2', 'Nace en el departamento de Soriano y desemboca en el río Uruguay.', None)
        list_rivers.append(r11)
        r12 = datamodel.RiverNote('Río Santa Lucía', [self.list_departments[7], self.list_departments[6], self.list_departments[1], self.list_departments[15]], '230 km', '13.500 km2', 'Nace en el departamento de Lavalleja, corre de E a O y es el límite de los departamentos de Florida y Canelones; al S, entre los departamentos de Canelones y San José; desemboca en un pequeño delta, en el Río de la Plata.', None)
        list_rivers.append(r12)
        r13 = datamodel.RiverNote('Río Tacuarembó', [self.list_departments[12], self.list_departments[17]], '250 km', '14.000 km2', 'Nace en el departamento de Rivera y corre de N a S, atraviesa el departamento de Tacuarembó y desemboca en el río Negro.', None)
        list_rivers.append(r13)
        r14 = datamodel.RiverNote('Río Tacuarí', [self.list_departments[2], self.list_departments[18]], '195 km', '3.600 km2', 'Nace en el departamento de Cerro Largo, recorre el territorio de NO a SE hasta el límite con Treinta y Tres donde desemboca en la laguna Merín.', None)
        list_rivers.append(r14)
        r15 = datamodel.RiverNote('Río Yaguarón', [self.list_departments[2]], '225 km', '3.000 km2', 'Nace al S del Brasil y es uno de los límites entre este país y el nuestro. Desemboca en la laguna Merín luego de bordear el departamento de Cerro Largo.', None)
        list_rivers.append(r15)
        r16 = datamodel.RiverNote('Río Yí', [self.list_departments[18], self.list_departments[4], self.list_departments[6], self.list_departments[5]], '225 km', '12.600 km2', 'Nace en el límite entre Treinta y Tres, Florida y Durazno. Es el límite entre Florida y Durazno, y entre este último y Flores, hasta desembocar en el Río Negro.', None)
        list_rivers.append(r16)
        return list_rivers

    def set_up_lagoons(self):
        list_lagoons = []
        l1 = datamodel.LagoonNote('Laguna de Castillos', [self.list_departments[13]], '100 km2', 'Ubicada en el departamento de Rocha.', 'Se comunica con el océano Atlántico a través del arroyo Valizas.')
        list_lagoons.append(l1)
        l2 = datamodel.LagoonNote('Laguna de Rocha', [self.list_departments[13]], '72 km2', 'Ubicada en el departamento de Rocha, cerca de la ciudad de La Paloma.', None)
        list_lagoons.append(l2)
        l3 = datamodel.LagoonNote('Laguna del Sauce', [self.list_departments[8]], '70 km2', 'Ubicada en el departamento de Maldonado.', 'Se conecta con el Río de la Plata a través del arroyo El Potrero.')
        list_lagoons.append(l3)
        l4 = datamodel.LagoonNote('Laguna Garzón', [self.list_departments[8], self.list_departments[13]], '35 km2', 'Es el límite entre los departamentos de Maldonado y Rocha. Vierte sus aguas en el Océano Atlántico.', None)
        list_lagoons.append(l4)
        l5 = datamodel.LagoonNote('Laguna José Ignacio', [self.list_departments[8]], '35 km2', 'Ubicada en el departamento de Maldonado. Desemboca sobre el océano Atlántico.', None)
        list_lagoons.append(l5)
        l6 = datamodel.LagoonNote('Laguna Merín', [self.list_departments[13], self.list_departments[18], self.list_departments[2]], '3.750 km2', 'Ubicada en el límite E de los departamentos de Rocha, Treinta y Tres y Cerro Largo.', 'Está unida a la Laguna de los Patos, perteneciente a Brasil, a través del río San Gonzalo.')
        list_lagoons.append(l6)
        l7 = datamodel.LagoonNote('Laguna Negra', [self.list_departments[13]], '180 km2', 'Ubicada en el departamento de Rocha.', 'Es también conocida como Laguna de los Difuntos.')
        list_lagoons.append(l7)
        return list_lagoons

    def set_up_hills(self):
        list_hills = []
        h1 = datamodel.HillNote('Cerro Tupambaé', 'el', self.list_departments[2], '470 metros', 'Se encuentra en la Sierra de las Ruinas, departamento de Cerro Largo.', None)
        list_hills.append(h1)
        h2 = datamodel.HillNote('Cerros de Ojosmín', 'los', self.list_departments[5], '209 metros', 'Se encuentran en la Cuchilla Grande, al O del departamento de Flores.', None)
        list_hills.append(h2)
        h3 = datamodel.HillNote('Cerro Arequita', 'el', self.list_departments[7], '305 metros', 'Ubicado en las cercanías de la ciudad de Minas, departamento de Lavalleja, junto a él corre el río Santa Lucía.', None)
        list_hills.append(h3)
        h4 = datamodel.HillNote('Cerro Artigas', 'el', self.list_departments[7], '215 metros', 'Ubicado en la ciudad de Minas, departamento de Lavalleja.', 'En su cima hay una escultura dedicada a nuestro prócer José Artigas.')
        list_hills.append(h4)
        h5 = datamodel.HillNote('Cerro del Verdún', 'el', self.list_departments[7], '325 metros', 'Ubicado en las cercanías de la ciudad de Minas, departamento de Lavalleja.', 'El 19 de abril miles de peregrinos llegan al santuario de la Virgen del Verdún que se encuentra en su cima.')
        list_hills.append(h5)
        h6 = datamodel.HillNote('Cerro Penitente', 'el', self.list_departments[7], '357 metros', 'Ubicado en las cercanías de la ciudad de Minas, departamento de Lavalleja.', 'Aquí nace el arroyo que forma la cascada llamada Salto del Penitente, que tiene 60 metros de altura.')
        list_hills.append(h6)
        h7 = datamodel.HillNote('Cerro Baltasar', 'el', self.list_departments[8], '329 metros', 'Ubicado en el departamento de Maldonado. Es un cerro de piedra desnuda que parece haber sido tallado con un cincel.', None)
        list_hills.append(h7)
        h8 = datamodel.HillNote('Cerro Catedral', 'el', self.list_departments[8], '513 metros', 'Ubicado en Aiguá, departamento de Maldonado, su nombre se debe a su gran tamaño.', 'Es el cerro más alto del país.')
        list_hills.append(h8)
        h9 = datamodel.HillNote('Cerro de los Burros', 'el', self.list_departments[8], '171 metros', 'También conocido como Cerro de la Virgen. Se encuentra frente a playa Hermosa, departamento de Maldonado.', 'Está cubierto por una vegetación abundante y es todo un desafío encontrar el camino hacia la cima.')
        list_hills.append(h9)
        h10 = datamodel.HillNote('Cerro del Toro', 'el', self.list_departments[8], '195 metros', 'Ubicado en Piriápolis, departamento de Maldonado.', 'En su ladera se encuentra la famosa Fuente del Toro que Francisco Piria hizo traer especialmente de París. Es la escultura de un toro de tamaño natural y por su boca brota una chorro de agua mineral.')
        list_hills.append(h10)
        h11 = datamodel.HillNote('Cerro Pan de Azúcar', 'el', self.list_departments[8], '389 metros', 'Ubicado en el departamento de Maldonado.', 'En su cumbre hay una cruz de 35 metros de altura, a la que se puede subir para disfrutar del panorama. A sus pies se encuentra la reserva de fauna autóctona.')
        list_hills.append(h11)
        h12 = datamodel.HillNote('Cerro San Antonio', 'el', self.list_departments[8], '130 metros', 'También llamado Cerro del Inglés. Se encuentra en Piriápolis, departamento de Maldonado.', 'Se puede acceder a la cima en un sistema de aerosillas. Allí se encuentra el templo de San Antonio, cuya imagen tallada en terracota fue traída desde Milán.')
        list_hills.append(h12)
        h13 = datamodel.HillNote('Cerro de las Ánimas', 'el', self.list_departments[8], '501 metros', 'Situado en la Sierra de las Ánimas, que a su vez forma parte de la Cuchilla Grande, departamento de Maldonado.', 'Es el segundo cerro más alto del país.')
        list_hills.append(h13)
        h14 = datamodel.HillNote('Cerro de Montevideo', 'el', self.list_departments[9], '134 metros', 'Situado en la ciudad de Montevideo.', 'Tiene un faro que funciona con el mecanismo original, de principios de siglo.')
        list_hills.append(h14)
        h15 = datamodel.HillNote('Cerro Bonito', 'el', self.list_departments[12], '351 metros', 'Ubicado en el valle del Lunarejo, departamento de Rivera.', None)
        list_hills.append(h15)
        h16 = datamodel.HillNote('Cerro de los Chivos', 'el', self.list_departments[12], '284 metros', 'Ubicado en el departamento de Rivera.', 'Pertenece al grupo de cerros chatos denominado Tres Cerros del Cuñapirú.')
        list_hills.append(h16)
        h17 = datamodel.HillNote('Cerro del Medio', 'el', self.list_departments[12], '221 metros', 'Ubicado en el departamento de Rivera.', 'Pertenece al grupo de cerros chatos llamado Tres Cerros del Cuñapirú.')
        list_hills.append(h17)
        h18 = datamodel.HillNote('Cerro Lunarejo', 'el', self.list_departments[12], '332 metros', 'Ubicado entre las localidades de Tranqueras y Masoller, departamento de Rivera, en el valle del arroyo del mismo nombre.', 'Se encuentra cubierto por una vegetación abundante.')
        list_hills.append(h18)
        h19 = datamodel.HillNote('Cerro Miriñaque', 'el', self.list_departments[12], '282 metros', 'Ubicado en el departamento de Rivera.', 'Pertenece al grupo de cerros chatos llamado Tres Cerros de Cuñapirú.')
        list_hills.append(h19)
        h20 = datamodel.HillNote('Cerro Batoví', 'el', self.list_departments[17], '224 metros', 'Ubicado a 25 kilómetros de la ciudad de Tacuarembó, capital del departamento.', 'Su nombre en guaraní significa "seno de virgen" y es el emblema del departamento.')
        list_hills.append(h20)
        h21 = datamodel.HillNote('Cerro Cementerio', 'el', self.list_departments[17], '255 metros', 'Ubicado en las proximidades del Valle Edén, departamento de Tacuarembó.', 'Se trata de un enorme peñasco que tiene un gran valor arqueológico por contar con un cementerio indígena, con sus tumbas, veredas y escalones.')
        list_hills.append(h21)
        return list_hills

    def set_up_history_facts(self):
        list_history_facts = []
        hf1 = datamodel.HistoryFactNote('tuvo lugar', 'el', 'Grito de Asencio', [self.list_departments[16]], '27 de febrero de 1811', 'Tuvo lugar cerca del arroyo Asencio, actual departamento de Soriano.', 'Desde allí, un grupo de revolucionarios orientales condujeron las primeras acciones de la Revolución oriental.')
        list_history_facts.append(hf1)
        hf2 = datamodel.HistoryFactNote('tuvo lugar', 'el', 'Desembarco de los 33 Orientales', [self.list_departments[16]], '19 de abril de 1825', 'Tuvo lugar en la playa de la Agraciada, departamento de Soriano.', 'Desde allí comenzó la Cruzada Libertadora.')
        list_history_facts.append(hf2)
        hf3 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Declaratoria de la independencia', [self.list_departments[6]], '18 de julio de 1825', 'Tuvo lugar en el paraje conocido como Piedra Alta, en las cercanías de la ciudad de Florida.', 'En este acto se declaró la independencia de la Provincia Oriental con respecto al Brasil, se estableció su pabellón y se dictaminó su unión a las Provincias Unidas del Río de la Plata.')
        list_history_facts.append(hf3)
        hf4 = datamodel.HistoryFactNote('comenzó', 'el', 'Éxodo del Pueblo Oriental', [self.list_departments[15]], '23 de octubre de 1811', 'Se denomina éxodo del Pueblo Oriental a la emigración colectiva de casi la totalidad de las poblaciones criollas de la Banda Oriental. Siguieron a José G. Artigas cuando se retiró, al levantarse el Sitio de Montevideo.', 'Partieron desde las cercanías del arroyo San José.')
        list_history_facts.append(hf4)
        hf5 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Jura de la Constitución', [self.list_departments[9]], '18 de julio de 1830', 'Fue la primera Constitución uruguaya y estaba basada en las Constituciones de Francia, Estados Unidos, Argentina, Brasil, Chile y España.', 'El acto se desarrolló en el edificio del Cabildo, frente a la Plaza Matriz de Montevideo')
        list_history_facts.append(hf5)
        hf6 = datamodel.HistoryFactNote('se redactaron', 'Las', 'Instrucciones del Año XIII', [self.list_departments[9]], '13 de abril de 1813', 'Son las Instrucciones que llevaron los representantes de la Provincia Oriental, aprobadas en el Congreso de Tres Cruces, a la Asamblea Constituyente en Buenos Aires. En ellas se establecieron las normas que regirían a la Provincia una vez conquistada la independencia.', 'La redacción se llevó a cabo en la quinta de Manuel Sainz de Cavia, en Montevideo, en la actual intersección de las calles avenida Italia y Morales.')
        list_history_facts.append(hf6)
        hf7 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Batalla de Arbolito', [self.list_departments[2]], '28 de febrero de 1897', 'Fue un enfrentamiento entre el ejército colorado, al mando del general Justino Muniz, y las fuerzas revolucionarias blancas, al mando de Aparicio Saravia.', 'Tuvo lugar en la cuchilla de Arbolito, en el departamento de Cerro Largo.')
        list_history_facts.append(hf7)
        hf8 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Batalla de Arroyo Grande', [self.list_departments[16], self.list_departments[5]], '6 de diciembre de 1842', 'Fue uno de los enfrentamientos que se produjeron durante la Guerra Grande, entre el ejército de la Confederación, al mando del general Manuel Oribe, y las fuerzas del Gobierno de Montevideo, al mando del general Fructuoso Rivera.', 'Tuvo lugar en los márgenes de dicho arroyo, afluente del río Negro, que conforma el límite de los Departamentos de Soriano y Flores.')
        list_history_facts.append(hf8)
        hf9 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Batalla de Cagancha', [self.list_departments[15]], '29 de diciembre de 1839', 'Fue uno de los enfrentamientos que se produjeron durante la Guerra Grande, entre el ejército de la Confederación, al mando del general Pascual Echagüe, y las fuerzas del Gobierno de Montevideo, al mando del general Fructuoso Rivera.', 'Tuvo lugar cerca del arroyo de Cagancha, en el Departamento de San José.')
        list_history_facts.append(hf9)
        hf10 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Batalla de Cardal', [self.list_departments[9]], '20 de enero de 1807', 'Enfrentamiento entre las fuerzas defensoras de la ciudad de Montevideo y los soldados de la Armada inglesa, durante las Invasiones inglesas.', None)
        list_history_facts.append(hf10)
        hf11 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Batalla de Carpintería', [self.list_departments[4]], '19 de setiembre de 1836', 'Enfrentamiento entre el ejército del Gobierno, al mando de general Manuel Oribe, y las fuerzas revolucionarias, dirigidas por el general Fructuoso Rivera. En esta batalla nacieron las divisas blanca y colorada.', 'Tuvo lugar en las cercanías del arroyo Carpintería, en el Departamento de Durazno.')
        list_history_facts.append(hf11)
        hf12 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Batalla de Cerrito', [self.list_departments[9]], '31 de diciembre de 1812', 'Combate entre las fuerzas revolucionarias que sitiaban Montevideo, bajo las órdenes del general José Rondeau, y las tropas españolas al mando del mariscal Vigodet.', None)
        list_history_facts.append(hf12)
        hf13 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Batalla de Guayabo', [self.list_departments[14]], '10 de enero de 1815', 'Enfrentamiento entre el ejército de Buenos Aires, al mando del coronel Manuel Dorrego, y las fuerzas revolucionarias orientales, comandadas por el general Fructuoso Rivera.', 'Tuvo lugar en las cercanías del arroyo del mismo nombre, en el SE del departamento de Salto')
        list_history_facts.append(hf13)
        hf14 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Batalla de India Muerta', [self.list_departments[13]], '27 de marzo de 1845', 'Librada durante la Guerra Grande, entre el ejército sitiador de Montevideo, al mando del general Manuel Oribe, y las fuerzas del ejército de la Defensa, al mando del general Fructuoso Rivera.', 'Tuvo lugar en las costas del arroyo del mismo nombre, situado en el departamento de Rocha.')
        list_history_facts.append(hf14)
        hf15 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Batalla de Las Piedras', [self.list_departments[1]], '18 de mayo de 1811', 'Enfrentamiento entre las tropas españolas y las fuerzas revolucionarias al mando del general José Gervasio Artigas.', 'Tuvo lugar en las cercanías de lo que hoy es la ciudad de Las Piedras, en el departatmento de Canelones')
        list_history_facts.append(hf15)
        hf16 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Batalla de Palmar', [self.list_departments[11]], '15 de junio de 1838', 'Librada entre las tropas del ejército del Gobierno de la República, al mando del general Manuel Oribe, y las fuerzas revolucionarias, dirigidas por el general Fructuoso Rivera.', 'Tuvo lugar al norte del departamento de Río Negro, en una región así denominada por la abundancia de altas palmeras.')
        list_history_facts.append(hf16)
        hf17 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Batalla de Rincón', [self.list_departments[11]], '24 de diciembre de 1825', 'Enfrentamiento entre el ejército imperial brasileño, al mando de los coroneles Mena Barreto y Jardim, y las tropas de la Cruzada Libertadora, comandadas por el general Fructuoso Rivera.', 'Tuvo lugar en un área conocida como "Rincón de Haedo", encerrada por la confluencia de los ríos Uruguay y Negro, en el actual departamento de Río Negro.')
        list_history_facts.append(hf17)
        hf18 = datamodel.HistoryFactNote('tuvo lugar', 'la', 'Batalla de Sarandí', [self.list_departments[6]], '12 de octubre de 1825', 'Librada entre las tropas brasileñas y las tropas de la Cruzada Libertadora al mando de los generales Juan Antonio Lavalleja, Manuel Oribe y Fructuoso Rivera.', 'Tuvo lugar en las costas del Arroyo Sarandí, afluente del río Yi, en el Departamento de Florida.')
        list_history_facts.append(hf18)
        return list_history_facts

    def set_up_locations(self):
        list_locations = []
        loc1 = datamodel.LocationNote('Baltasar Brum', self.list_departments[0], 'Pueblo', 'visitar el pueblo de', '2.472 hab.', 'Pueblo situado en el SO del departamento de Artigas.')
        list_locations.append(loc1)
        loc2 = datamodel.LocationNote('Bella Unión', self.list_departments[0], 'Ciudad', 'visitar la ciudad de', '13.187 hab.', 'Ciudad situada en el NO del departamento de Artigas.')
        list_locations.append(loc2)
        loc3 = datamodel.LocationNote('Las Piedras', self.list_departments[0], 'Centro poblado', 'visitar el centro poblado de', '2.164 hab.', 'Centro poblado situado en el NO del departamento de Artigas.', 'centro poblado')
        list_locations.append(loc3)
        loc4 = datamodel.LocationNote('Pintadito', self.list_departments[0], 'Centro poblado', 'visitar el centro poblado de', '1.487 hab.', 'Centro poblado situado en el NE del departamento de Artigas.')
        list_locations.append(loc4)
        loc5 = datamodel.LocationNote('Tomás Gomensoro', self.list_departments[0], 'Pueblo', 'visitar el pueblo de', '2.818 hab.', 'Pueblo situado en el NO del departamento de Artigas.')
        list_locations.append(loc5)
        loc6 = datamodel.LocationNote('Aguas Corrientes', self.list_departments[1], 'Pueblo', 'visitar el pueblo de', '1.095 hab.', 'Pueblo situado en el O del departamento de Canelones.')
        list_locations.append(loc6)
        loc7 = datamodel.LocationNote('Atlántida', self.list_departments[1], 'Ciudad', 'visitar la ciudad de', '4.580 hab.', 'Ciudad situada en el S del departamento de Canelones.')
        list_locations.append(loc7)
        loc8 = datamodel.LocationNote('Los Cerrillos', self.list_departments[1], 'Villa', 'visitar villa', '2.080 hab.', 'Villa situada en el O del departamento de Canelones.')
        list_locations.append(loc8)
        loc9 = datamodel.LocationNote('Ciudad de la Costa', self.list_departments[1], 'Ciudad', 'visitar la ciudad de', '66.402 hab.', 'Ciudad situada en el SO del departamento de Canelones, integrada por las localidades de San José de Carrasco, Barra de Carrasco, Parque Carrasco, Solymar, Lomas de Solymar, Colinas de Solymar, El Pinar, Lagomar, Shangrilá y El Bosque.')
        list_locations.append(loc9)
        loc10 = datamodel.LocationNote('Colonia Nicolich', self.list_departments[1], 'Centro poblado', 'visitar el centro poblado de', '8,811 hab.', 'Centro poblado situado en el SO del departamento de Canelones.')
        list_locations.append(loc10)
        loc11 = datamodel.LocationNote('Empalme Olmos', self.list_departments[1], 'Pueblo', 'visitar el pueblo de', '3.978 hab.', 'Pueblo situado en el S del departamento de Canelones.')
        list_locations.append(loc11)
        loc12 = datamodel.LocationNote('Joaquín Suárez', self.list_departments[1], 'Ciudad', 'visitar la ciudad de', '6.124 hab.', 'Ciudad situada en el SO del departamento de Canelones.')
        list_locations.append(loc12)
        loc13 = datamodel.LocationNote('La Paz', self.list_departments[1], 'Ciudad', 'visitar la ciudad de', '19.832 hab.', 'Ciudad situada en el SO del departamento de Canelones.')
        list_locations.append(loc13)
        loc14 = datamodel.LocationNote('Las Piedras', self.list_departments[1], 'Ciudad', 'visitar la ciudad de', '69.222 hab.', 'Ciudad situada en el SO del departamento de Canelones.', 'ciudad')
        list_locations.append(loc14)
        loc15 = datamodel.LocationNote('Migues', self.list_departments[1], 'Villa', 'visitar villa', '2.180 hab.', 'Villa situada en el E del departamento de Canelones.')
        list_locations.append(loc15)
        loc16 = datamodel.LocationNote('Montes', self.list_departments[1], 'Pueblo', 'visitar el pueblo de', '1.713 hab.', 'Pueblo situado en el E del departamento de Canelones.')
        list_locations.append(loc16)
        loc17 = datamodel.LocationNote('Pando', self.list_departments[1], 'Ciudad', 'visitar la ciudad de', '24.004 hab.', 'Ciudad situada en el SO del departamento de Canelones.')
        list_locations.append(loc17)
        loc18 = datamodel.LocationNote('Parque del Plata', self.list_departments[1], 'Ciudad', 'visitar la ciudad de', '5.900 hab.', 'Ciudad situada en el S del departamento de Canelones.')
        list_locations.append(loc18)
        loc19 = datamodel.LocationNote('Paso de Carrasco', self.list_departments[1], 'Pueblo', 'visitar el pueblo de', '15.028 hab.', 'Pueblo situado en el SO del departamento de Canelones.')
        list_locations.append(loc19)
        loc20 = datamodel.LocationNote('Progreso', self.list_departments[1], 'Ciudad', 'visitar la ciudad de', '15.775 hab.', 'Ciudad situada en el SO del departamento de Canelones.')
        list_locations.append(loc20)
        loc21 = datamodel.LocationNote('Salinas', self.list_departments[1], 'Ciudad', 'visitar la ciudad de', '6.574 hab.', 'Ciudad situada en el S del departamento de Canelones.')
        list_locations.append(loc21)
        loc22 = datamodel.LocationNote('San Antonio', self.list_departments[1], 'Pueblo', 'visitar el pueblo de', '1.434 hab.', 'Pueblo situado en el N del departamento de Canelones.')
        list_locations.append(loc22)
        loc23 = datamodel.LocationNote('San Bautista', self.list_departments[1], 'Pueblo', 'visitar el pueblo de', '1.880 hab.', 'Pueblo situado en el centro del departamento de Canelones.')
        list_locations.append(loc23)
        loc24 = datamodel.LocationNote('San Jacinto', self.list_departments[1], 'Villa', 'visitar villa', '3.909 hab.', 'Villa situada en el centro del departamento de Canelones.')
        list_locations.append(loc24)
        loc25 = datamodel.LocationNote('San Ramón', self.list_departments[1], 'Ciudad', 'visitar la ciudad de', '6.992 hab.', 'Ciudad situada en el N del departamento de Canelones.')
        list_locations.append(loc25)
        loc26 = datamodel.LocationNote('Santa Lucía', self.list_departments[1], 'Ciudad', 'visitar la ciudad de', '16.475 hab.', 'Ciudad situada en el NO del departamento de Canelones.')
        list_locations.append(loc26)
        loc27 = datamodel.LocationNote('Santa Rosa', self.list_departments[1], 'Población', 'visitar la población de', '3.660 hab.', 'Población situada en el centro del departamento de Canelones.')
        list_locations.append(loc27)
        loc28 = datamodel.LocationNote('Sauce', self.list_departments[1], 'Población', 'visitar la población de', '5.797 hab.', 'Población situada en el SO del departamento de Canelones.')
        list_locations.append(loc28)
        loc29 = datamodel.LocationNote('Soca', self.list_departments[1], 'Ciudad', 'visitar la ciudad de', '1.742 hab.', 'Ciudad situada en el SE del departamento de Canelones.')
        list_locations.append(loc29)
        loc30 = datamodel.LocationNote('Tala', self.list_departments[1], 'Población', 'visitar la población de', '4.939 hab.', 'Población situada en el NE del departamento de Canelones.')
        list_locations.append(loc30)
        loc31 = datamodel.LocationNote('Toledo', self.list_departments[1], 'Localidad', 'visitar la población de', '4.028 hab.', 'Localidad situada en el SO del departamento de Canelones.')
        list_locations.append(loc31)
        loc32 = datamodel.LocationNote('Aceguá', self.list_departments[2], 'Pueblo', 'visitar el pueblo de', '1.493 hab.', 'Pueblo situado en el N del departamento de Cerro Largo.')
        list_locations.append(loc32)
        loc33 = datamodel.LocationNote('Fraile Muerto', self.list_departments[2], 'Villa', 'visitar villa', '3.229 hab.', 'Villa situada en el centro del departamento de Cerro Largo.')
        list_locations.append(loc33)
        loc34 = datamodel.LocationNote('Isidoro Noblía', self.list_departments[2], 'Pueblo', 'visitar el pueblo de', '2.462 hab.', 'Pueblo situado en el NE del departamento de Cerro Largo.')
        list_locations.append(loc34)
        loc35 = datamodel.LocationNote('Melo', self.list_departments[2], 'Ciudad', 'visitar la ciudad de', '50.578 hab.', 'Ciudad situada en el centro del departamento de Cerro Largo, es su capital.')
        list_locations.append(loc35)
        loc36 = datamodel.LocationNote('Río Branco', self.list_departments[2], 'Ciudad', 'visitar la ciudad de', '13.456 hab.', 'Ciudad situada en el SE del departamento de Cerro Largo.')
        list_locations.append(loc36)
        loc37 = datamodel.LocationNote('Carmelo', self.list_departments[3], 'Ciudad', 'visitar la ciudad de', '16.866 hab.', 'Ciudad ubicada en el O del departamento de Colonia.')
        list_locations.append(loc37)
        loc38 = datamodel.LocationNote('Colonia del Sacramento', self.list_departments[3], 'Ciudad', 'visitar la ciudad de', '21.714 hab.', 'Ciudad ubicada en el SO del departamento de Colonia.')
        list_locations.append(loc38)
        loc39 = datamodel.LocationNote('Colonia Valdense', self.list_departments[3], 'Ciudad', 'visitar la ciudad de', '3.087 hab.', 'Ciudad situada en el SE del departamento de Colonia.')
        list_locations.append(loc39)
        loc40 = datamodel.LocationNote('Florencio Sánchez', self.list_departments[3], 'Villa', 'visitar villa', '3.526 hab.', 'Villa situada en el NE del departamento de Colonia.', 'localidad')
        list_locations.append(loc40)
        loc41 = datamodel.LocationNote('Juan Lacaze', self.list_departments[3], 'Ciudad', 'visitar la ciudad de', '13.196 hab.', 'Ciudad situada en el S del departamento de Colonia.')
        list_locations.append(loc41)
        loc42 = datamodel.LocationNote('Nueva Helvecia', self.list_departments[3], 'Ciudad', 'visitar la ciudad de', '10.002 hab.', 'Ciudad situada en el SE del departamento de Colonia.')
        list_locations.append(loc42)
        loc43 = datamodel.LocationNote('Nueva Palmira', self.list_departments[3], 'Ciudad', 'visitar la ciudad de', '9.230 hab.', 'Ciudad situada en el NO del departamento de Colonia.')
        list_locations.append(loc43)
        loc44 = datamodel.LocationNote('Ombúes de Lavalle', self.list_departments[3], 'Villa', 'visitar villa', '3.451 hab.', 'Villa situada en el N del departamento de Colonia.')
        list_locations.append(loc44)
        loc45 = datamodel.LocationNote('Rosario', self.list_departments[3], 'Ciudad', 'visitar la ciudad de', '9.311 hab.', 'Ciudad situada en el SE del departamento de Colonia.')
        list_locations.append(loc45)
        loc46 = datamodel.LocationNote('Tarariras', self.list_departments[3], 'Ciudad', 'visitar la ciudad de', '6.070 hab.', 'Ciudad situada en el SO del departamento de Colonia.')
        list_locations.append(loc46)
        loc47 = datamodel.LocationNote('Blanquillo', self.list_departments[4], 'Pueblo', 'visitar el pueblo de', '1.162 hab.', 'Pueblo situado en el NE del departamento de Durazno.')
        list_locations.append(loc47)
        loc48 = datamodel.LocationNote('Carlos Reyles', self.list_departments[4], 'Población', 'visitar la población de', '1.039 hab.', 'Población situada en el centro del departamento de Durazno.')
        list_locations.append(loc48)
        loc49 = datamodel.LocationNote('Carmen', self.list_departments[4], 'Villa', 'visitar villa', '2.661 hab.', 'Villa situada en el centro del departamento de Durazno.')
        list_locations.append(loc49)
        loc50 = datamodel.LocationNote('La Paloma', self.list_departments[4], 'Centro poblado', 'visitar el centro poblado de', '1.547 hab.', 'Centro poblado ubicado en el NE del departamento de Durazno.', 'centro poblado')
        list_locations.append(loc50)
        loc51 = datamodel.LocationNote('Santa Bernardina', self.list_departments[4], 'Población', 'visitar la población de', '1.333 hab.', 'Población ubicada en el SO del departamento de Durazno.')
        list_locations.append(loc51)
        loc52 = datamodel.LocationNote('Sarandí del Yi', self.list_departments[4], 'Ciudad', 'visitar la ciudad de', '7.289 hab.', 'Ciudad situada en el SO del departamento de Durazno.')
        list_locations.append(loc52)
        loc53 = datamodel.LocationNote('Ismael Cortinas', self.list_departments[5], 'Población', 'visitar la población de', '1.069 hab.', 'Población situada en el SO del departamento de Flores.', 'localidad')
        list_locations.append(loc53)
        loc54 = datamodel.LocationNote('Trinidad', self.list_departments[5], 'Ciudad', 'visitar la ciudad de', '20.982 hab.', 'Ciudad situada en el centro del departamento Flores, es su capital')
        list_locations.append(loc54)
        loc55 = datamodel.LocationNote('Andresito', self.list_departments[5], 'Pueblo', 'visitar el pueblo de', '271 hab.', 'Pueblo situado en el N del departamento de Flores.')
        list_locations.append(loc55)
        loc56 = datamodel.LocationNote('La Casilla', self.list_departments[5], 'Caserío', 'visitar el pueblo de', '181 hab.', 'Caserío situado en el centro del departamento de Flores.')
        list_locations.append(loc56)
        loc57 = datamodel.LocationNote('Cardal', self.list_departments[6], 'Pueblo', 'visitar el pueblo de', '1.290 hab.', 'Pueblo situado en el SO del departamento de Florida.')
        list_locations.append(loc57)
        loc58 = datamodel.LocationNote('Casupá', self.list_departments[6], 'Villa', 'visitar villa', '2.668 hab.', 'Villa situada en el SE del departamento de Florida.')
        list_locations.append(loc58)
        loc59 = datamodel.LocationNote('Cerro Colorado', self.list_departments[6], 'Pueblo', 'visitar el pueblo de', '1.336 hab.', 'Pueblo situado en el SE del departamento de Florida.')
        list_locations.append(loc59)
        loc60 = datamodel.LocationNote('Fray Marcos', self.list_departments[6], 'Villa', 'visitar villa', '2.509 hab.', 'Villa situada en el SE del departamento de Florida.')
        list_locations.append(loc60)
        loc61 = datamodel.LocationNote('Nico Pérez', self.list_departments[6], 'Pueblo', 'visitar el pueblo de', '1.049 hab.', 'Pueblo situado en el NE del departamento de Florida.')
        list_locations.append(loc61)
        loc62 = datamodel.LocationNote('Sarandí Grande', self.list_departments[6], 'Ciudad', 'visitar la ciudad de', '6.362 hab.', 'Ciudad situada en el NO del departamento de Florida.')
        list_locations.append(loc62)
        loc63 = datamodel.LocationNote('Veinticinco de Agosto', self.list_departments[6], 'Villa', 'visitar villa', '1.794 hab.', 'Villa situada en el SO del departamento de Florida.')
        list_locations.append(loc63)
        loc64 = datamodel.LocationNote('Veinticinco de Mayo', self.list_departments[6], 'Villa', 'visitar villa', '1.845 hab.', 'Villa situada en el SO del departamento de Florida.')
        list_locations.append(loc64)
        loc65 = datamodel.LocationNote('José Batlle y Ordóñez', self.list_departments[7], 'Pueblo', 'visitar el pueblo de', '2.424 hab.', 'Pueblo situado en el NO del departamento de Lavalleja.')
        list_locations.append(loc65)
        loc66 = datamodel.LocationNote('José Pedro Varela', self.list_departments[7], 'Ciudad', 'visitar la ciudad de', '5.332 hab.', 'Ciudad situada en el NO del departamento de Lavalleja.')
        list_locations.append(loc66)
        loc67 = datamodel.LocationNote('Mariscala', self.list_departments[7], 'Pueblo', 'visitar el pueblo de', '1.674 hab.', 'Pueblo situado en el SE del departamento de Lavalleja.')
        list_locations.append(loc67)
        loc68 = datamodel.LocationNote('Minas', self.list_departments[7], 'Ciudad', 'visitar la ciudad de', '37.925 hab.', 'Ciudad situada en el SO del departamento de Lavalleja, es su capital.')
        list_locations.append(loc68)
        loc69 = datamodel.LocationNote('Solís de Mataojo', self.list_departments[7], 'Villa', 'visitar villa', '2.676 hab.', 'Villa situada en el SO del departamento de Lavalleja.')
        list_locations.append(loc69)
        loc70 = datamodel.LocationNote('Aiguá', self.list_departments[8], 'Ciudad', 'visitar la ciudad de', '2.676 hab.', 'Ciudad situada en el S del departamento de Maldonado.')
        list_locations.append(loc70)
        loc71 = datamodel.LocationNote('Cerro Pelado', self.list_departments[8], 'Población', 'visitar la población de', '6.385 hab.', 'Población situada en el E del departamento de Maldonado.')
        list_locations.append(loc71)
        loc72 = datamodel.LocationNote('Pan de Azúcar', self.list_departments[8], 'Ciudad', 'visitar la ciudad de', '7.098 hab.', 'Ciudad situada en el SO del departamento de Maldonado.')
        list_locations.append(loc72)
        loc73 = datamodel.LocationNote('Pinares - Las Delicias', self.list_departments[8], 'Balneario', 'visitar el balneario', '8.524 hab.', 'Balneario situado en S del departamento de Maldonado.')
        list_locations.append(loc73)
        loc74 = datamodel.LocationNote('Piriápolis', self.list_departments[8], 'Ciudad', 'visitar la ciudad de', '7.899 hab.', 'Ciudad situada en el SO del departamento de Maldonado.')
        list_locations.append(loc74)
        loc75 = datamodel.LocationNote('Punta del Este', self.list_departments[8], 'Ciudad', 'visitar la ciudad de', '7.298 hab.', 'Ciudad situada en el S del departamento de Maldonado.')
        list_locations.append(loc75)
        loc76 = datamodel.LocationNote('San Carlos', self.list_departments[8], 'Ciudad', 'visitar la ciudad de', '24.771 hab.', 'Ciudad situada en el S del departamento de Maldonado.')
        list_locations.append(loc76)
        loc77 = datamodel.LocationNote('San Rafael - El Placer', self.list_departments[8], 'Balneario', 'visitar el balneario', '1.994 hab.', 'Balneario situado en el S del departamento de Maldonado.')
        list_locations.append(loc77)
        loc78 = datamodel.LocationNote('Tambores', self.list_departments[10], 'Población', 'visitar la población de', '1.180 hab.', 'Población situada en el E del departamento de Paysandú.')
        list_locations.append(loc78)
        loc79 = datamodel.LocationNote('Guichón', self.list_departments[10], 'Ciudad', 'visitar la ciudad de', '5.025 hab.', 'Ciudad situada en el S del departamento de Paysandú.')
        list_locations.append(loc79)
        loc80 = datamodel.LocationNote('Nuevo Paysandú', self.list_departments[10], 'Centro poblado', 'visitar el centro poblado de', '7.468 hab.', 'Centro poblado situado en el O del departamento de Paysandú.')
        list_locations.append(loc80)
        loc81 = datamodel.LocationNote('Piedras Coloradas', self.list_departments[10], 'Centro poblado ', 'visitar el centro poblado de', '1.113 hab.', 'Centro poblado situado en el SO del departamento de Paysandú.')
        list_locations.append(loc81)
        loc82 = datamodel.LocationNote('Quebracho', self.list_departments[10], 'Villa', 'visitar villa', '2.813 hab.', 'Villa situada en el NO del departamento de Paysandú.')
        list_locations.append(loc82)
        loc83 = datamodel.LocationNote('San Félix', self.list_departments[10], 'Centro poblado', 'visitar el centro poblado de', '1.149 hab.', 'Centro poblado situado en el SO del departamento de Paysandú.')
        list_locations.append(loc83)
        loc84 = datamodel.LocationNote('Fray Bentos', self.list_departments[11], 'Ciudad', 'visitar la ciudad de', '23.122 hab.', 'Ciudad situada en el SO del departamento de Río Negro, es su capital.')
        list_locations.append(loc84)
        loc85 = datamodel.LocationNote('Nuevo Berlín', self.list_departments[11], 'Pueblo', 'visitar el pueblo de', '2.438 hab.', 'Pueblo situado en el NO del departamento de Río Negro.')
        list_locations.append(loc85)
        loc86 = datamodel.LocationNote('San Javier', self.list_departments[11], 'Villa', 'visitar villa', '1.680 hab.', 'Villa situada en el NO del departamento de Río Negro.')
        list_locations.append(loc86)
        loc87 = datamodel.LocationNote('Young', self.list_departments[11], 'Ciudad', 'visitar la ciudad de', '15.759 hab.', 'Ciudad situada en el centro del departamento de Río Negro.')
        list_locations.append(loc87)
        loc88 = datamodel.LocationNote('Mandubí', self.list_departments[12], 'Fraccionamiento', 'visitar el fraccionamiento de', '5.157 hab.', 'Fraccionamiento situado en el NE del departamento de Rivera.')
        list_locations.append(loc88)
        loc89 = datamodel.LocationNote('Minas de Corrales', self.list_departments[12], 'Pueblo', 'visitar el pueblo de', '3.444 hab.', 'Pueblo situado en el O del departamento de Rivera.')
        list_locations.append(loc89)
        loc90 = datamodel.LocationNote('Santa Teresa', self.list_departments[12], 'Centro poblado', 'visitar el centro poblado de', '2.171 hab.', 'Centro poblado situado en el NE del departamento de Rivera.')
        list_locations.append(loc90)
        loc91 = datamodel.LocationNote('Tranqueras', self.list_departments[12], 'Ciudad', 'visitar la ciudad de', '7.284 hab.', 'Ciudad situada en el NO del departamento de Rivera.')
        list_locations.append(loc91)
        loc92 = datamodel.LocationNote('Vichadero', self.list_departments[12], 'Villa', 'visitar villa', '4.074 hab.', 'Villa situada en el SE del departamento de Rivera.')
        list_locations.append(loc92)
        loc93 = datamodel.LocationNote('Castillos', self.list_departments[13], 'Ciudad', 'visitar la ciudad de', '7.649 hab.', 'Ciudad situada en el SE del departamento de Rocha.')
        list_locations.append(loc93)
        loc94 = datamodel.LocationNote('Cebollatí', self.list_departments[13], 'Pueblo', 'visitar el pueblo de', '1.606 hab.', 'Pueblo situado en el N del departamento de Rocha.')
        list_locations.append(loc94)
        loc95 = datamodel.LocationNote('Chuy', self.list_departments[13], 'Ciudad', 'visitar la ciudad de', '10.401 hab.', 'Ciudad situada en el E del departamento de Rocha.')
        list_locations.append(loc95)
        loc96 = datamodel.LocationNote('Dieciocho de Julio', self.list_departments[13], 'Villa', 'visitar villa', '1.191 hab.', 'Villa situada en el E del departamento de Rocha.')
        list_locations.append(loc96)
        loc97 = datamodel.LocationNote('La Aguada - Costa Azul', self.list_departments[13], 'Pueblo', 'visitar el pueblo de', '1.103 hab.', 'Pueblo situado en el S del departamento de Rocha.')
        list_locations.append(loc97)
        loc98 = datamodel.LocationNote('La Paloma', self.list_departments[13], 'Ciudad', 'visitar la ciudad de', '3.202 hab.', 'Ciudad situada en el S del departamento de Rocha.', 'ciudad')
        list_locations.append(loc98)
        loc99 = datamodel.LocationNote('Lascano', self.list_departments[13], 'Ciudad', 'visitar la ciudad de', '6.994 hab.', 'Ciudad situada en el NO del departamento de Rocha.')
        list_locations.append(loc99)
        loc100 = datamodel.LocationNote('Velázquez', self.list_departments[13], 'Población', 'visitar la población de', '1.084 hab.', 'Población situada en el O del departamento de Rocha.')
        list_locations.append(loc100)
        loc101 = datamodel.LocationNote('Belén', self.list_departments[14], 'Pueblo', 'visitar el pueblo de', '2.030 hab.', 'Pueblo situado en el NO del departamento de Salto.')
        list_locations.append(loc101)
        loc102 = datamodel.LocationNote('Constitución', self.list_departments[14], 'Pueblo', 'visitar el pueblo de', '2.844 hab.', 'Pueblo situado en el O del departamento de Salto.')
        list_locations.append(loc102)
        loc103 = datamodel.LocationNote('Pueblo Lavalleja', self.list_departments[14], 'Centro poblado', 'visitar el centro poblado de', '1049 hab.', 'Centro poblado situado en el  N del departamento de Salto.')
        list_locations.append(loc103)
        loc104 = datamodel.LocationNote('Ciudad del Plata', self.list_departments[15], 'Ciudad', 'visitar la ciudad de', '26.582 hab.', 'Ciudad situada en el SE del departamento de San José.')
        list_locations.append(loc104)
        loc105 = datamodel.LocationNote('Ecilda Paullier', self.list_departments[15], 'Villa', 'visitar villa', '2.351 hab.', 'Villa situada en el SO del departamento de San José')
        list_locations.append(loc105)
        loc106 = datamodel.LocationNote('Libertad', self.list_departments[15], 'Ciudad', 'visitar la ciudad de', '9.196 hab.', 'Ciudad situada en el SE del departamento de San José.')
        list_locations.append(loc106)
        loc107 = datamodel.LocationNote('Puntas de Valdez', self.list_departments[15], 'Centro poblado', 'visitar el centro poblado de', '1.267 hab.', 'Centro poblado situado en el S del departamento de San José.')
        list_locations.append(loc107)
        loc108 = datamodel.LocationNote('Rafael Perazza', self.list_departments[15], 'Población', 'visitar la población de', '1.235 hab.', 'Población situada en el S del departamento de San José.')
        list_locations.append(loc108)
        loc109 = datamodel.LocationNote('Rodríguez', self.list_departments[15], 'Villa', 'visitar villa', '2.561 hab.', 'Villa situada en el E del departamento de San José.')
        list_locations.append(loc109)
        loc110 = datamodel.LocationNote('Cardona', self.list_departments[16], 'Ciudad', 'visitar la ciudad de', '4.689 hab.', 'Ciudad situada en el SE del departamento de Soriano.')
        list_locations.append(loc110)
        loc111 = datamodel.LocationNote('Chacras de Dolores', self.list_departments[16], 'Población', 'visitar la población de', '3.251 hab.', 'Población situada en el O del departamento de Soriano.')
        list_locations.append(loc111)
        loc112 = datamodel.LocationNote('Dolores', self.list_departments[16], 'Ciudad', 'visitar la ciudad de', '15.753 hab.', 'Ciudad situada en el O del departamento de Soriano.')
        list_locations.append(loc112)
        loc113 = datamodel.LocationNote('José Enrique Rodó', self.list_departments[16], 'Villa', 'visitar villa', '2.113 hab.', 'Villa situada en el S del departamento de Soriano.', 'localidad')
        list_locations.append(loc113)
        loc114 = datamodel.LocationNote('Mercedes', self.list_departments[16], 'Ciudad', 'visitar la ciudad de', '42.032 hab.', 'Ciudad situada en el NO del departamento de Soriano, es su capital.')
        list_locations.append(loc114)
        loc115 = datamodel.LocationNote('Palmitas', self.list_departments[16], 'Pueblo', 'visitar el pueblo de', '1.954 hab.', 'Pueblo situado en el centro del departamento de Soriano.')
        list_locations.append(loc115)
        loc116 = datamodel.LocationNote('Santa Catalina', self.list_departments[16], 'Pueblo', 'visitar el pueblo de', '1.053 hab.', 'Pueblo situado en el S del departamento de Soriano.')
        list_locations.append(loc116)
        loc117 = datamodel.LocationNote('Ansina', self.list_departments[17], 'Villa', 'visitar villa', '2.790 hab.', 'Villa situada en el NE del departamento de Tacuarembó.')
        list_locations.append(loc117)
        loc118 = datamodel.LocationNote('Curtina', self.list_departments[17], 'Pueblo', 'visitar el pueblo de', '1.029 hab.', 'Pueblo situado en el O del departamento de Tacuarembó.')
        list_locations.append(loc118)
        loc119 = datamodel.LocationNote('Paso de los Toros', self.list_departments[17], 'Ciudad', 'visitar la ciudad de', '13.231 hab.', 'Ciudad situada en el SO del departamento de Tacuarembó.')
        list_locations.append(loc119)
        loc120 = datamodel.LocationNote('San Gregorio de Polanco', self.list_departments[17], 'Villa', 'visitar villa', '3.673 hab.', 'Villa situada en el S del departamento de Tacuarembó.')
        list_locations.append(loc120)
        loc121 = datamodel.LocationNote('Villa Sara', self.list_departments[18], 'Centro poblado', 'visitar el centro poblado de', '1.056 hab.', 'Centro poblado situado en el S del departamento de Treinta y Tres.')
        list_locations.append(loc121)
        loc122 = datamodel.LocationNote('Gral. Enrique Martínez', self.list_departments[18], 'Pueblo', 'visitar el pueblo de', '1.513 hab.', 'Pueblo situado en el SE del departamento de Treinta y Tres.')
        list_locations.append(loc122)
        loc123 = datamodel.LocationNote('Santa Clara de Olimar', self.list_departments[18], 'Villa', 'visitar villa', '2.305 hab.', 'Villa situada en el NO del departamento de Treinta y Tres.')
        list_locations.append(loc123)
        loc124 = datamodel.LocationNote('Vergara', self.list_departments[18], 'Ciudad', 'visitar la ciudad de', '3.986 hab.', 'Ciudad situada en el E del departamento de Treinta y Tres.')
        list_locations.append(loc124)
        return list_locations

    def set_up_writers(self):
        list_writers = []
        wr1 = datamodel.WriterNote('Eliseo Salvador Porta', 'M', self.list_departments[0], '(1912 - 1972)', 'Narrador, poeta y ensayista nacido en Tomás Gomensoro, departamento de Artigas.')
        list_writers.append(wr1)
        wr2 = datamodel.WriterNote('Alba Roballo', 'F', self.list_departments[0], '(1908 - 1996)', 'Poetisa nacida en Isla Cabello (actual Baltasar Brum), departamento de Artigas.')
        list_writers.append(wr2)
        wr3 = datamodel.WriterNote('Américo Celestino del Cioppo', 'M', self.list_departments[1], '(1904 - 1996)', 'Poeta y hombre de teatro nacido en la ciudad de Canelones.')
        list_writers.append(wr3)
        wr4 = datamodel.WriterNote('Marcelo Pareja', 'M', self.list_departments[1], '(1954)', 'Poeta nacido en Las Piedras, departamento de Canelones.')
        list_writers.append(wr4)
        wr5 = datamodel.WriterNote('Milton Stelardo', 'M', self.list_departments[1], '(1918 - 2001)', 'Narrador nacido en la ciudad de Canelones.')
        list_writers.append(wr5)
        wr6 = datamodel.WriterNote('Javier de Viana', 'M', self.list_departments[1], '(1868 - 1926)', 'Narrador, cronista y dramaturgo nacido en la ciudad de Canelones.')
        list_writers.append(wr6)
        wr7 = datamodel.WriterNote('Gley Eyherabide', 'M', self.list_departments[2], '(1934)', 'Narrador nacido en Melo, departamento de Cerro Largo.')
        list_writers.append(wr7)
        wr8 = datamodel.WriterNote('Juana de Ibarbourou', 'F', self.list_departments[2], '(1892 - 1979)', 'Poetisa y narradora nacida en Melo, departamento de Cerro Largo.')
        list_writers.append(wr8)
        wr9 = datamodel.WriterNote('José Monegal', 'M', self.list_departments[2], '(1892 - 1968)', 'Narrador y biógrafo nacido en Melo, departamento de Cerro Largo.')
        list_writers.append(wr9)
        wr10 = datamodel.WriterNote('Emilio Oribe', 'M', self.list_departments[2], '(1893 - 1975)', 'Poeta y ensayista nacido en Melo, departamento de Cerro Largo.')
        list_writers.append(wr10)
        wr11 = datamodel.WriterNote('Justino Zavala Muníz', 'M', self.list_departments[2], '(1898 - 1968)', 'Narrador, dramaturgo e historiador nacido en Melo, departamento de Cerro Largo.')
        list_writers.append(wr11)
        wr12 = datamodel.WriterNote('Carlos Martínez Moreno', 'M', self.list_departments[3], '(1917 - 1986)', 'Narrador, crítico teatral y literario nacido en la ciudad de Colonia del Sacramento.')
        list_writers.append(wr12)
        wr13 = datamodel.WriterNote('Roberto Bula Píriz', 'M', self.list_departments[4], '(1919 - ?)', 'Poeta y ensayista nacido en Sarandí del Yí, departamento de Durazno.')
        list_writers.append(wr13)
        wr14 = datamodel.WriterNote('Generoso Medina', 'M', self.list_departments[4], '(1922 - 1974)', 'Poeta y crítico nacido en la ciudad de Durazno.')
        list_writers.append(wr14)
        wr15 = datamodel.WriterNote('Omar Moreira', 'M', self.list_departments[4], '(1932)', 'Narrador nacido en Puntas del Cordobés, departamento de Durazno.')
        list_writers.append(wr15)
        wr16 = datamodel.WriterNote('Elías Regules', 'M', self.list_departments[4], '(1861 - 1929)', 'Poeta nacido en Sarandí del Yi, departamento de Durazno.')
        list_writers.append(wr16)
        wr17 = datamodel.WriterNote('Mario Arregui', 'M', self.list_departments[5], '(1917 - 1985)', 'Narrador y biógrafo nacido en Trinidad, departamento de Flores.')
        list_writers.append(wr17)
        wr18 = datamodel.WriterNote('Juan Cunha', 'M', self.list_departments[6], '(1910 - 1985)', 'Poeta nacido en Sauce de Illescas, departamento de Florida.')
        list_writers.append(wr18)
        wr19 = datamodel.WriterNote('Mario Delgado Aparaín', 'M', self.list_departments[6], '(1949)', 'Narrador nacido en la ciudad de Florida.')
        list_writers.append(wr19)
        wr20 = datamodel.WriterNote('Víctor Dotti', 'M', self.list_departments[6], '(1907 - 1955)', 'Narrador nacido en Molles del Pescado, departamento de Florida.')
        list_writers.append(wr20)
        wr21 = datamodel.WriterNote('Juan Mario Magallanes', 'M', self.list_departments[6], '(1893 - 1950)', 'Poeta y narrador nacido en la ciudad de Florida.')
        list_writers.append(wr21)
        wr22 = datamodel.WriterNote('Omar Prego Gadea', 'M', self.list_departments[6], '(1927)', 'Narrador y ensayista nacido en la ciudad de Florida.')
        list_writers.append(wr22)
        wr23 = datamodel.WriterNote('Manuel Benavente', 'M', self.list_departments[7], '(1893 - 1950)', 'Poeta y ensayista nacido en Minas, departamento de Lavalleja.')
        list_writers.append(wr23)
        wr24 = datamodel.WriterNote('Guillermo Cuadri', 'M', self.list_departments[7], '(1884 - 1953)', 'Poeta y prosista nacido en Minas, departamento de Lavalleja.')
        list_writers.append(wr24)
        wr25 = datamodel.WriterNote('Santiago Dossetti', 'M', self.list_departments[7], '(1902 - 1981)', 'Narrador nacido en Gutierrez, departamento de Lavalleja.')
        list_writers.append(wr25)
        wr26 = datamodel.WriterNote('Milton Fornaro', 'M', self.list_departments[7], '(1947)', 'Narrador nacido en Minas, departamento de Lavalleja.')
        list_writers.append(wr26)
        wr27 = datamodel.WriterNote('Rubén Loza Aguerrebere', 'M', self.list_departments[7], '(1945)', 'Narrador nacido en Minas, departamento de Lavalleja.')
        list_writers.append(wr27)
        wr28 = datamodel.WriterNote('Juan José Morosoli', 'M', self.list_departments[7], '(1899 - 1957)', 'Narrador, poeta y ensayista nacido en Minas, departamento de Lavalleja.')
        list_writers.append(wr28)
        wr29 = datamodel.WriterNote('Ariel Muniz', 'M', self.list_departments[7], '(1942)', 'Narrador nacido en Minas, departamento de Lavalleja.')
        list_writers.append(wr29)
        wr30 = datamodel.WriterNote('Blanca Luz Brum', 'F', self.list_departments[8], '(1905 - 1985)', 'Poetisa y narradora nacida en Pan de Azúcar, departamento de Maldonado.')
        list_writers.append(wr30)
        wr31 = datamodel.WriterNote('Alvaro Figueredo', 'M', self.list_departments[8], '(1907 - 1966)', 'Poeta nacido en Pan de Azúcar, departamento de Maldonado.')
        list_writers.append(wr31)
        wr32 = datamodel.WriterNote('Juan Fagetti', 'M', self.list_departments[10], '(1888 - 1954)', 'Poeta nacido en la ciudad de Paysandú.')
        list_writers.append(wr32)
        wr33 = datamodel.WriterNote('Luisa Luisi', 'F', self.list_departments[10], '(1883 - 1940)', 'Poetisa y ensayista nacida en la ciudad de Paysandú.')
        list_writers.append(wr33)
        wr34 = datamodel.WriterNote('Domingo Luis Bordoli Castelli', 'M', self.list_departments[11], '(1919 - 1982)', 'Crítico y narrador nacido en Fray Bentos, departamento de Río Negro.')
        list_writers.append(wr34)
        wr35 = datamodel.WriterNote('Sarandy Cabrera', 'M', self.list_departments[12], '(1923 - 2005)', 'Poeta nacido en la ciudad de Rivera.')
        list_writers.append(wr35)
        wr36 = datamodel.WriterNote('Ofelia Machado Bonet', 'F', self.list_departments[12], '(1908 - 1987)', 'Poetisa, novelista y ensayista nacida en la ciudad de Rivera.')
        list_writers.append(wr36)
        wr37 = datamodel.WriterNote('Gladys Castelvecchi', 'F', self.list_departments[13], '(1922 - 2008)', 'Poetisa nacida en la ciudad de Rocha.')
        list_writers.append(wr37)
        wr38 = datamodel.WriterNote('Eduardo Dieste', 'M', self.list_departments[13], '(1882 - 1954)', 'Ensayista, narrador y autor teatral nacido en la ciudad de Rocha.')
        list_writers.append(wr38)
        wr39 = datamodel.WriterNote('Elías Uriarte', 'M', self.list_departments[13], '(1945)', 'Poeta nacido en la ciudad de Rocha.')
        list_writers.append(wr39)
        wr40 = datamodel.WriterNote('Enrique Amorim', 'M', self.list_departments[14], '(1900 - 1960)', 'Narrador, poeta, dramaturgo y libretista cinematográfico nacido en la ciudad de Salto.')
        list_writers.append(wr40)
        wr41 = datamodel.WriterNote('Horacio Quiroga', 'M', self.list_departments[14], '(1878 - 1937)', 'Narrador nacido en la ciudad de Salto.')
        list_writers.append(wr41)
        wr42 = datamodel.WriterNote('Francisco Espínola', 'M', self.list_departments[15], '(1901 - 1973)', 'Narrador, ensayista y dramaturgo nacido en la ciudad de San José de Mayo.')
        list_writers.append(wr42)
        wr43 = datamodel.WriterNote('Ismael Cortinas', 'M', self.list_departments[15], '(1884 - 1940)', 'Narrador y dramaturgo nacido en la ciudad de San José de Mayo.')
        list_writers.append(wr43)
        wr44 = datamodel.WriterNote('Ricardo Paseyro', 'M', self.list_departments[16], '(1926)', 'Poeta y crítico nacido en Mercedes, departamento de Soriano.')
        list_writers.append(wr44)
        wr45 = datamodel.WriterNote('Washington Benavides', 'M', self.list_departments[17], '(1930)', 'Poeta nacido en la ciudad de Tacuarembó.')
        list_writers.append(wr45)
        wr46 = datamodel.WriterNote('Mario Benedetti', 'M', self.list_departments[17], '(1920-2009)', 'Narrador, poeta, dramaturgo y periodista nacido en Paso de los Toros, departamento de Tacuarembó.')
        list_writers.append(wr46)
        wr47 = datamodel.WriterNote('Victor Cunha', 'M', self.list_departments[17], '(1951)', 'Poeta nacido en la ciudad de Tacuarembó.')
        list_writers.append(wr47)
        wr48 = datamodel.WriterNote('Julio Da Rosa', 'M', self.list_departments[18], '(1920)', 'Narrador nacido en Costas de Porongos, departamento de Treinta y Tres.')
        list_writers.append(wr48)
        wr49 = datamodel.WriterNote('Serafín J. García', 'M', self.list_departments[18], '(1908 - 1985)', 'Poeta y narrador nacido en Cañada Grande, departamento de Treinta y Tres.')
        list_writers.append(wr49)
        wr51 = datamodel.WriterNote('Luis Hierro Gambardella', 'M', self.list_departments[18], '(1915 - 1991)', 'Poeta, narrador y crítico literario nacido en la ciudad de Treinta y Tres.')
        list_writers.append(wr51)
        wr52 = datamodel.WriterNote('Pedro Leandro Ipuche', 'M', self.list_departments[18], '(1889 - 1976)', 'Poeta, narrador y ensayista nacido en la ciudad de Treinta y Tres.')
        list_writers.append(wr52)
        wr53 = datamodel.WriterNote('Lucio Muniz', 'M', self.list_departments[18], '(1939)', 'Poeta nacido en la ciudad de Treinta y Tres.')
        list_writers.append(wr53)
        wr54 = datamodel.WriterNote('Delmira Agustini', 'F', self.list_departments[9], '(1886 - 1914)', 'Poetisa nacida en la ciudad de Montevideo.')
        list_writers.append(wr54)
        wr55 = datamodel.WriterNote('Eduardo Galeano', 'M', self.list_departments[9], '(1940)', 'Narrador y periodista nacido en la ciudad de Montevideo.')
        list_writers.append(wr55)
        wr56 = datamodel.WriterNote('Juan Carlos Onetti', 'M', self.list_departments[9], '(1909 - 1994)', 'Narrador y periodista nacido en la ciudad de Montevideo.')
        list_writers.append(wr56)
        wr57 = datamodel.WriterNote('José Enrique Rodó', 'M', self.list_departments[9], '(1871 -1917)', 'Ensayista y crítico literario nacido en la ciudad de Montevideo.')
        list_writers.append(wr57)
        wr58 = datamodel.WriterNote('Florencio Sánchez', 'M', self.list_departments[9], '(1875 - 1910)', 'Dramaturgo nacido en la ciudad de Montevideo.')
        list_writers.append(wr58)
        return list_writers

    def set_up_clue_types(self):
        list_clue_types = []
        ct1 = datamodel.ClueType('RIVER')
        list_clue_types.append(ct1)
        ct2 = datamodel.ClueType('LAGOON')
        list_clue_types.append(ct2)
        ct3 = datamodel.ClueType('HILL')
        list_clue_types.append(ct3)
        ct4 = datamodel.ClueType('LOCATION')
        list_clue_types.append(ct4)
        ct5 = datamodel.ClueType('HISTORY_FACT')
        list_clue_types.append(ct5)
        ct6 = datamodel.ClueType('WRITER')
        list_clue_types.append(ct6)
        ct7 = datamodel.ClueType('MUSICIAN')
        list_clue_types.append(ct7)
        return list_clue_types

    def set_up_clues(self):
        list_clues = []
        river_type = self.get_clue_type('RIVER')
        lagoon_type = self.get_clue_type('LAGOON')
        hill_type = self.get_clue_type('HILL')
        location_type = self.get_clue_type('LOCATION')
        history_fact_type = self.get_clue_type('HISTORY_FACT')
        writer_type = self.get_clue_type('WRITER')
        cd = datamodel.Clue('i509', [river_type, lagoon_type, location_type, hill_type])
        list_clues.append(cd)
        cd = datamodel.Clue('i511', [river_type, lagoon_type, location_type, hill_type, writer_type, history_fact_type])
        list_clues.append(cd)
        cd = datamodel.Clue('i510', [river_type, lagoon_type, location_type, hill_type, writer_type, history_fact_type])
        list_clues.append(cd)
        cd = datamodel.Clue('i523', [hill_type, lagoon_type, river_type, history_fact_type, location_type, 
         writer_type])
        list_clues.append(cd)
        cd = datamodel.Clue('i526', [hill_type, lagoon_type, river_type, history_fact_type, location_type, 
         writer_type])
        list_clues.append(cd)
        cd = datamodel.Clue('i527', [hill_type, lagoon_type, river_type, location_type])
        list_clues.append(cd)
        cd = datamodel.Clue('i528', [hill_type, lagoon_type, river_type, history_fact_type, location_type, 
         writer_type])
        list_clues.append(cd)
        return list_clues

    def get_clue_type(self, type):
        for c in self.list_clue_types:
            if c.type == type:
                return c

        raise Exception('Clue not found: ' + type)
        return

    def set_up_stolen_objects(self):
        list_stolen_objects = []
        so1 = datamodel.StolenObject('de', 'un antiguo sable', 'el sable', GENERICO)
        list_stolen_objects.append(so1)
        so2 = datamodel.StolenObject('de', 'un trabuco naranjero', 'el trabuco naranjero', GENERICO)
        list_stolen_objects.append(so2)
        so3 = datamodel.StolenObject('de', 'un antiguo fusil', 'el fusil', GENERICO)
        list_stolen_objects.append(so3)
        so4 = datamodel.StolenObject('de', 'una valiosa pintura', 'la pintura', GENERICO)
        list_stolen_objects.append(so4)
        so5 = datamodel.StolenObject('de', 'unas fotos antiguas', 'las fotos', GENERICO)
        list_stolen_objects.append(so5)
        so6 = datamodel.StolenObject('de', 'una punta de flecha indígena', 'la punta de flecha', INDIGENA)
        list_stolen_objects.append(so6)
        so7 = datamodel.StolenObject('de', 'una vasija de cerámica indígena', 'la vasija', INDIGENA)
        list_stolen_objects.append(so7)
        so8 = datamodel.StolenObject('de', 'unas herramientas indígenas', 'las herramientas', INDIGENA)
        list_stolen_objects.append(so8)
        so9 = datamodel.StolenObject('de', 'unas boleadoras indígenas', 'las boleadoras', INDIGENA)
        list_stolen_objects.append(so9)
        so10 = datamodel.StolenObject('de', 'un arco indígena', 'el arco', INDIGENA)
        list_stolen_objects.append(so10)
        so11 = datamodel.StolenObject('de', 'un antiguo facón', 'el facón', GAUCHO)
        list_stolen_objects.append(so11)
        so12 = datamodel.StolenObject('de', 'una silla de montar', 'la silla de montar', GAUCHO)
        list_stolen_objects.append(so12)
        so13 = datamodel.StolenObject('de', 'unas espuelas', 'las espuelas', GAUCHO)
        list_stolen_objects.append(so13)
        so14 = datamodel.StolenObject('de', 'unas boleadoras', 'las boleadoras', GAUCHO)
        list_stolen_objects.append(so14)
        so15 = datamodel.StolenObject('de', 'una antigua vestimenta gauchesca', 'la vestimenta', GAUCHO)
        list_stolen_objects.append(so15)
        so16 = datamodel.StolenObject('de', 'unos restos fosilizados de dinosaurio', 'los restos fosilizados', FOSILES)
        list_stolen_objects.append(so16)
        so17 = datamodel.StolenObject('de', 'unos importantes restos fósiles', 'los restos fósiles', FOSILES)
        list_stolen_objects.append(so17)
        so18 = datamodel.StolenObject('de', 'un uniforme que perteneció al General Aparicio Saravia', 'el uniforme', APARICIO_SARAVIA)
        list_stolen_objects.append(so18)
        so19 = datamodel.StolenObject('de', 'unas botas que pertenecieron al General Aparicio Saravia', 'las botas', APARICIO_SARAVIA)
        list_stolen_objects.append(so19)
        so20 = datamodel.StolenObject('de', 'unas espuelas que pertenecieron al General Aparicio Saravia', 'las espuelas', APARICIO_SARAVIA)
        list_stolen_objects.append(so20)
        so21 = datamodel.StolenObject('de', 'un sable que perteneció al General Aparicio Saravia', 'el sable', APARICIO_SARAVIA)
        list_stolen_objects.append(so21)
        so22 = datamodel.StolenObject('de', 'un violín que perteneció al músico Eduardo Fabini', 'el violín', FABINI)
        list_stolen_objects.append(so22)
        so23 = datamodel.StolenObject('de', 'las partituras originales de la obra "Campo" del compositor Eduardo Fabini', 'las partituras', FABINI)
        list_stolen_objects.append(so23)
        so24 = datamodel.StolenObject('de', 'las partituras originales de la obra "La Isla de los Ceibos" del compositor Eduardo Fabini', 'las partituras', FABINI)
        list_stolen_objects.append(so24)
        so25 = datamodel.StolenObject('de', 'las partituras originales de la obra "La Patria Vieja" del compositor Eduardo Fabini', 'las partituras', FABINI)
        list_stolen_objects.append(so25)
        so26 = datamodel.StolenObject('de', 'un antiguo sable', 'el sable', ARMAS)
        list_stolen_objects.append(so26)
        so27 = datamodel.StolenObject('de', 'un antiguo uniforme militar', 'el uniforme', ARMAS)
        list_stolen_objects.append(so27)
        so28 = datamodel.StolenObject('de', 'un antiguo fusil', 'el fusil', ARMAS)
        list_stolen_objects.append(so28)
        so29 = datamodel.StolenObject('de', 'un trabuco naranjero', 'el trabuco naranjero', ARMAS)
        list_stolen_objects.append(so29)
        so30 = datamodel.StolenObject('de', 'una colección de monedas muy antiguas', 'la colección de monedas', MONEDAS)
        list_stolen_objects.append(so30)
        so31 = datamodel.StolenObject('del', 'cuadro "El Juramento de los Treinta y Tres Orientales" del pintor Juan Manuel Blanes', 'el cuadro', BLANES)
        list_stolen_objects.append(so31)
        so32 = datamodel.StolenObject('del', 'cuadro "Asesinato del General Venancio Flores" del pintor Juan Manuel Blanes', 'el cuadro', BLANES)
        list_stolen_objects.append(so32)
        so33 = datamodel.StolenObject('del', 'cuadro "La Cautiva" del pintor Juan Manuel Blanes', 'el cuadro', BLANES)
        list_stolen_objects.append(so33)
        so34 = datamodel.StolenObject('del', 'cuadro "Demonio, Mundo y Carne" del pintor Juan Manuel Blanes', 'el cuadro', BLANES)
        list_stolen_objects.append(so34)
        so35 = datamodel.StolenObject('del', 'cuadro "Nueva York" del pintor Joaquín Torres García', 'el cuadro', TORRES_GARCIA)
        list_stolen_objects.append(so35)
        so36 = datamodel.StolenObject('del', 'cuadro "Suburbio" del pintor Joaquín Torres García', 'el cuadro', TORRES_GARCIA)
        list_stolen_objects.append(so36)
        so37 = datamodel.StolenObject('del', 'cuadro "Composición simétrica universal" del pintor Joaquín Torres García', 'el cuadro', TORRES_GARCIA)
        list_stolen_objects.append(so37)
        so38 = datamodel.StolenObject('del', 'cuadro "Arte Universal" del pintor Joaquín Torres García', 'el cuadro', TORRES_GARCIA)
        list_stolen_objects.append(so38)
        so39 = datamodel.StolenObject('del', 'cuadro "Extraña Máscara" del pintor Luis Alberto Solari', 'el cuadro', SOLARI)
        list_stolen_objects.append(so39)
        so40 = datamodel.StolenObject('del', 'cuadro "Un día y una história" del pintor Luis Alberto Solari', 'el cuadro', SOLARI)
        list_stolen_objects.append(so40)
        so41 = datamodel.StolenObject('del', 'cuadro "Carroza para un carnaval" del pintor Luis Alberto Solari', 'el cuadro', SOLARI)
        list_stolen_objects.append(so41)
        so42 = datamodel.StolenObject('del', 'cuadro "El arca de Noé" del pintor Luis Alberto Solari', 'el cuadro', SOLARI)
        list_stolen_objects.append(so42)
        so43 = datamodel.StolenObject('de', 'un valioso cuadro', 'el cuadro', ARTE)
        list_stolen_objects.append(so43)
        so44 = datamodel.StolenObject('de', 'una valiosa escultura', 'la escultura', ARTE)
        list_stolen_objects.append(so44)
        so45 = datamodel.StolenObject('de', 'un pasaporte que demuestra la nacionalidad uruguaya del cantante Carlos Gardel', 'el pasaporte', GARDEL)
        list_stolen_objects.append(so45)
        so46 = datamodel.StolenObject('de', 'una foto original del cantante Carlos Gardel', 'la foto', GARDEL)
        list_stolen_objects.append(so46)
        so47 = datamodel.StolenObject('de', 'algunos recortes de periódico de la década del 30', 'los recortes de periódico', GARDEL)
        list_stolen_objects.append(so47)
        so48 = datamodel.StolenObject('de', 'un libro muy antiguo', 'el libro', EUSEBIO_GIMENEZ)
        list_stolen_objects.append(so48)
        so49 = datamodel.StolenObject('del', 'cuadro "Romana" del pintor Carlos Federico Sáez', 'el cuadro', EUSEBIO_GIMENEZ)
        list_stolen_objects.append(so49)
        so50 = datamodel.StolenObject('del', 'cuadro "Chocaro" del pintor Carlos Federico Sáez', 'el cuadro', EUSEBIO_GIMENEZ)
        list_stolen_objects.append(so50)
        so51 = datamodel.StolenObject('del', 'cuadro "Río Tiber" del pintor Carlos Federico Sáez', 'el cuadro', EUSEBIO_GIMENEZ)
        list_stolen_objects.append(so51)
        return list_stolen_objects

    def set_up_witness(self):
        list_witnesses = []
        w1 = datamodel.Witness('Jardinero', 'p1_witness_gardener.png')
        list_witnesses.append(w1)
        w2 = datamodel.Witness('Almacenera', 'p1_witness_shoptender.png')
        list_witnesses.append(w2)
        w3 = datamodel.Witness('Bibliotecario', 'p1_witness_librarian.png')
        list_witnesses.append(w3)
        w4 = datamodel.Witness('Albañil', 'p1_witness_bricklayer.png')
        list_witnesses.append(w4)
        return list_witnesses

    def set_up_statements(self):
        list_statements = []
        st1 = datamodel.Statement('No vi a nadie sospechoso por aquí.')
        list_statements.append(st1)
        st2 = datamodel.Statement('Un hombre sospechoso\npasó por aquí.')
        list_statements.append(st2)
        st3 = datamodel.Statement('Una mujer sospechosa\npasó por aquí.')
        list_statements.append(st3)
        return list_statements

    def set_up_identikit_statements(self):
        list_statements = []
        is1 = datamodel.IdentikitStatement('Era bastante &#c144,22,22!&#f:bold!alto&#f!&#c!.', MALE, TALL, -1, -1)
        list_statements.append(is1)
        is2 = datamodel.IdentikitStatement('Era bastante &#c144,22,22!&#f:bold!alta&#f!&#c!.', FEMALE, TALL, -1, -1)
        list_statements.append(is2)
        is3 = datamodel.IdentikitStatement('Era bastante &#c144,22,22!&#f:bold!bajo&#f!&#c!.', MALE, SHORT, -1, -1)
        list_statements.append(is3)
        is4 = datamodel.IdentikitStatement('Era bastante &#c144,22,22!&#f:bold!baja&#f!&#c!.', FEMALE, SHORT, -1, -1)
        list_statements.append(is4)
        is5 = datamodel.IdentikitStatement('Era &#c144,22,22!&#f:bold!rubio&#f!&#c!.', MALE, -1, BLONDE, -1)
        list_statements.append(is5)
        is6 = datamodel.IdentikitStatement('Era &#c144,22,22!&#f:bold!rubia&#f!&#c!.', FEMALE, -1, BLONDE, -1)
        list_statements.append(is6)
        is7 = datamodel.IdentikitStatement('Era &#c144,22,22!&#f:bold!morocho&#f!&#c!.', MALE, -1, BRUNETTE, -1)
        list_statements.append(is7)
        is8 = datamodel.IdentikitStatement('Era &#c144,22,22!&#f:bold!morocha&#f!&#c!.', FEMALE, -1, BRUNETTE, -1)
        list_statements.append(is8)
        is9 = datamodel.IdentikitStatement('Era &#c144,22,22!&#f:bold!pelirrojo&#f!&#c!.', MALE, -1, REDHEAD, -1)
        list_statements.append(is9)
        is10 = datamodel.IdentikitStatement('Era &#c144,22,22!&#f:bold!pelirroja&#f!&#c!.', FEMALE, -1, REDHEAD, -1)
        list_statements.append(is10)
        is11 = datamodel.IdentikitStatement('Era &#c144,22,22!&#f:bold!canoso&#f!&#c!.', MALE, -1, GREY_HAIRED, -1)
        list_statements.append(is11)
        is12 = datamodel.IdentikitStatement('Era &#c144,22,22!&#f:bold!canosa&#f!&#c!.', FEMALE, -1, GREY_HAIRED, -1)
        list_statements.append(is12)
        is13 = datamodel.IdentikitStatement('Tenía un &#c144,22,22!&#f:bold!tatuaje&#f!&#c!.', -1, -1, -1, TATOO)
        list_statements.append(is13)
        is14 = datamodel.IdentikitStatement('Tenía una fea &#c144,22,22!&#f:bold!cicatríz&#f!&#c!.', -1, -1, -1, SCAR)
        list_statements.append(is14)
        is15 = datamodel.IdentikitStatement('Usaba &#c144,22,22!&#f:bold!lentes&#f!&#c!.', -1, -1, -1, GLASSES)
        list_statements.append(is15)
        is16 = datamodel.IdentikitStatement('Tenía un &#c144,22,22!&#f:bold!lunar&#f!&#c!.', -1, -1, -1, MOLE)
        list_statements.append(is16)
        return list_statements

    def set_up_janitor_statements(self):
        list_statements = []
        s2 = datamodel.JanitorStatement('Me preguntó por algún club que tuviese una &#c144,22,22!&#f:bold!piscina&#f!&#c! para practicar su &#c144,22,22!&#f:bold!deporte&#f!&#c! favorito.', 1, -1, AQUATIC, -1, -1)
        list_statements.append(s2)
        s3 = datamodel.JanitorStatement('Me comentó que pensaba ir a la zapatería a comprarse un &#c144,22,22!&#f:bold!calzado&#f!&#c! adecuado para practicar su &#c144,22,22!&#f:bold!deporte&#f!&#c! favorito.', 1, -1, TERRESTRIAL, -1, -1)
        list_statements.append(s3)
        s4 = datamodel.JanitorStatement('Dijo que estaba aburrido porque para practicar el &#c144,22,22!&#f:bold!deporte&#f!&#c! que le gusta necesita un &#c144,22,22!&#f:bold!equipo&#f!&#c!.', 1, 1, -1, True, -1)
        list_statements.append(s4)
        s5 = datamodel.JanitorStatement('Dijo que estaba aburrida porque para practicar el &#c144,22,22!&#f:bold!deporte&#f!&#c! que le gusta necesita un &#c144,22,22!&#f:bold!equipo&#f!&#c!.', 1, 2, -1, True, -1)
        list_statements.append(s5)
        s6 = datamodel.JanitorStatement('Me comentó que pensaba ir a practicar su deporte preferido, cuando me ofrecí a jugar con él me dijo que &#c144,22,22!&#f:bold!no era un deporte de equipo&#f!&#c!.', 1, 1, -1, False, -1)
        list_statements.append(s6)
        s7 = datamodel.JanitorStatement('Me comentó que pensaba ir a practicar su deporte preferido, cuando me ofrecí a jugar con ella me dijo que &#c144,22,22!&#f:bold!no era un deporte de equipo&#f!&#c!.', 1, 2, -1, False, -1)
        list_statements.append(s7)
        s8 = datamodel.JanitorStatement('Preguntó por una casa de deportes porque necesitaba comprar una &#c144,22,22!&#f:bold!pelota&#f!&#c! para practicar su &#c144,22,22!&#f:bold!deporte&#f!&#c! favorito.', 1, -1, -1, -1, True)
        list_statements.append(s8)
        s9 = datamodel.JanitorStatement('Preguntó por una casa de deportes, le ofrecí una pelota, pero me dijo que &#c144,22,22!&#f:bold!no se necesita una pelota&#f!&#c! para practicar el &#c144,22,22!&#f:bold!deporte&#f!&#c! que le gusta.', 1, -1, -1, -1, False)
        list_statements.append(s9)
        s10 = datamodel.JanitorStatement('Me comentó que pensaba ir a buscar alimento para su &#c144,22,22!&#f:bold!mascota&#f!&#c! en algún comercio donde vendieran el tipo de &#c144,22,22!&#f:bold!carne&#f!&#c! que le gusta.', 2, -1, -1, CARNIVORE, -1)
        list_statements.append(s10)
        s11 = datamodel.JanitorStatement('Me comentó que pensaba ir a la &#c144,22,22!&#f:bold!verdulería&#f!&#c! a buscar alimento para su &#c144,22,22!&#f:bold!mascota&#f!&#c!.', 2, -1, -1, HERBIVORE, -1)
        list_statements.append(s11)
        s12 = datamodel.JanitorStatement('Me comentó que como su &#c144,22,22!&#f:bold!mascota&#f!&#c! tenía que &#c144,22,22!&#f:bold!amamantar&#f!&#c! a sus crías tenía que alimentarla mejor.', 2, -1, MAMMAL, -1, -1)
        list_statements.append(s12)
        s13 = datamodel.JanitorStatement('Le pregunté si tenía &#c144,22,22!&#f:bold!mascota&#f!&#c!, me dijo que si, pero que no la saca a pasear porque solo puede &#c144,22,22!&#f:bold!respirar bajo el agua&#f!&#c!.', 2, -1, FISH, -1, -1)
        list_statements.append(s13)
        s14 = datamodel.JanitorStatement('Estaba enojado porque su &#c144,22,22!&#f:bold!mascota&#f!&#c! había llenado la casa de &#c144,22,22!&#f:bold!plumas&#f!&#c!.', 2, 1, BIRD, -1, -1)
        list_statements.append(s14)
        s15 = datamodel.JanitorStatement('Estaba enojada porque su &#c144,22,22!&#f:bold!mascota&#f!&#c! había llenado la casa de &#c144,22,22!&#f:bold!plumas&#f!&#c!.', 2, 2, BIRD, -1, -1)
        list_statements.append(s15)
        s16 = datamodel.JanitorStatement('Me comentó que no es agradable acariciar a su &#c144,22,22!&#f:bold!mascota&#f!&#c! porque tiene la &#c144,22,22!&#f:bold!piel fría y escamosa&#f!&#c!.', 2, -1, REPTILE, -1, -1)
        list_statements.append(s16)
        s17 = datamodel.JanitorStatement('Me dijo que pensaba comprar una jaula nueva para su &#c144,22,22!&#f:bold!mascota&#f!&#c! porque la que tenía se había roto y tenía miedo de que se &#c144,22,22!&#f:bold!volara&#f!&#c!.', 2, -1, -1, -1, FLY)
        list_statements.append(s17)
        s18 = datamodel.JanitorStatement('Me comentó que pensaba llevar a su &#c144,22,22!&#f:bold!mascota&#f!&#c! al parque para que &#c144,22,22!&#f:bold!caminara&#f!&#c! un poco por el césped.', 2, -1, -1, -1, WALK)
        list_statements.append(s18)
        s19 = datamodel.JanitorStatement('Me dijo que pensaba comprar un estanque del tamaño adecuado para que su &#c144,22,22!&#f:bold!mascota&#f!&#c! &#c144,22,22!&#f:bold!nadara&#f!&#c! cómodamente.', 2, -1, -1, -1, SWIM)
        list_statements.append(s19)
        s20 = datamodel.JanitorStatement('Me pidió algunos &#c144,22,22!&#f:bold!alimentos&#f!&#c! para llevarle a su &#c144,22,22!&#f:bold!mascota&#f!&#c!.', -1, -1, -1, HERBIVORE, -1)
        list_statements.append(s20)
        return list_statements

    def set_up_thieves(self):
        list_thieves = []
        t1 = datamodel.Thief(MALE, SHORT, REDHEAD, GLASSES, self.list_animals[13], self.list_sports[5], 'Tomás Prestado', '"El usurero"', '32 años', 'Trabajaba anteriormente en una casa de empeño que usaba como plataforma para traficar objetos robados.\nSus amigos se quejan de que nunca devuelve las cosas.', 'p0_thief_small_tomas.png', 'p0_thief_big_tomas_1.jpg', 'p0_thief_big_tomas_2.jpg', 'p0_thief_big_tomas_3.jpg')
        list_thieves.append(t1)
        t2 = datamodel.Thief(FEMALE, TALL, BRUNETTE, MOLE, self.list_animals[7], self.list_sports[3], 'Helga Roben', '"La novicia"', '35 años', 'Originaria de Austria.\nDe joven fue novicia, pero la excomulgaron por robar el dinero de los diezmos.\nFue expulsada de su país por bailar en las colinas, lo que ocasionaba terribles avalanchas.', 'p0_thief_small_helga.png', 'p0_thief_big_helga_1.jpg', 'p0_thief_big_helga_2.jpg', 'p0_thief_big_helga_3.jpg')
        list_thieves.append(t2)
        t3 = datamodel.Thief(MALE, TALL, BRUNETTE, TATOO, self.list_animals[10], self.list_sports[6], 'Ruffo Nepomuceno Ruffiani', '"Angelito de mamá"', '30 años', 'Boxeador retirado con un récord de 112 peleas disputadas, 111 ganadas por knock-out. Una vez alguien hizo una broma con su segundo nombre, solo una vez.', 'p0_thief_small_ruffo.png', 'p0_thief_big_ruffo_1.jpg', 'p0_thief_big_ruffo_2.jpg', 'p0_thief_big_ruffo_3.jpg')
        list_thieves.append(t3)
        t4 = datamodel.Thief(FEMALE, SHORT, GREY_HAIRED, GLASSES, self.list_animals[4], self.list_sports[7], 'Teresa Terra Piña', '"La abuela"', 'Edad desconocida', 'Miembro fundador de CULT.\nSe rumorea que mantiene una relación amorosa con Timoteo T. Sacco.\nSe interesa especialmente en objetos de valor histórico porque le recuerdan su infancia.', 'p0_thief_small_teresa.png', 'p0_thief_big_teresa_1.jpg', 'p0_thief_big_teresa_2.jpg', 'p0_thief_big_teresa_3.jpg')
        list_thieves.append(t4)
        t5 = datamodel.Thief(MALE, TALL, BRUNETTE, SCAR, self.list_animals[5], self.list_sports[0], 'Giacomo Ladri', '"El padrino"', '51 años', 'Inmigrante italiano.\nEra dueño de una cadena de pizzerías y traficaba armas dentro de las cajas.\nAceptó formar parte de CULT porque le hicieron una oferta que no podía rechazar.', 'p0_thief_small_giacommo.png', 'p0_thief_big_giacommo_1.jpg', 'p0_thief_big_giacommo_2.jpg', 'p0_thief_big_giacommo_3.jpg')
        list_thieves.append(t5)
        t6 = datamodel.Thief(MALE, SHORT, REDHEAD, TATOO, self.list_animals[12], self.list_sports[3], 'Steal McCrook', '"El Duende"', '23 años', 'Procede de Irlanda.\nAfirma tener mucha suerte, que utiliza para jugar al "roba montón" por dinero en establecimientos ilegales.\nHay quienes sostienen que guarda su botín al final del arcoiris.', 'p0_thief_small_steal.png', 'p0_thief_big_steal_1.jpg', 'p0_thief_big_steal_2.jpg', 'p0_thief_big_steal_3.jpg')
        list_thieves.append(t6)
        t7 = datamodel.Thief(MALE, TALL, BLONDE, SCAR, self.list_animals[6], self.list_sports[2], 'Sven Hurtensson', '"El Vikingo"', '48 años', 'Delincuente de origen nórdico.\nEn sus viajes de saqueo y pillaje terminó quedandose en nuestro país.\nSe enoja mucho cuando la gente habla mal de ABBA.', 'p0_thief_small_sven.png', 'p0_thief_big_sven_1.jpg', 'p0_thief_big_sven_2.jpg', 'p0_thief_big_sven_3.jpg')
        list_thieves.append(t7)
        t8 = datamodel.Thief(MALE, TALL, BLONDE, TATOO, self.list_animals[14], self.list_sports[4], 'Roberto Robani', '"El Robin Hood integral"', '37 años', 'Procede de una familia de alto poder adquisitivo, su vinculación al mundo del hampa se produce unicamente por aburrimiento.\nSe hace llamar "El Robin Hood integral", ya que roba tanto a ricos como a pobres sin hacer distinción.', 'p0_thief_small_roberto.png', 'p0_thief_big_roberto_1.jpg', 'p0_thief_big_roberto_2.jpg', 'p0_thief_big_roberto_3.jpg')
        list_thieves.append(t8)
        t9 = datamodel.Thief(MALE, SHORT, GREY_HAIRED, SCAR, self.list_animals[8], self.list_sports[7], 'Timoteo T. Sacco', '"El Abuelo"', 'Edad desconocida', 'Miembro fundador de CULT.\nSe rumorea que mantiene una relación amorosa con Teresa Terra Piña.\nTiene como pasatiempo sentarse en las plazas a robarle migas de pan a las palomas.', 'p0_thief_small_timoteo.png', 'p0_thief_big_timoteo_1.jpg', 'p0_thief_big_timoteo_2.jpg', 'p0_thief_big_timoteo_3.jpg')
        list_thieves.append(t9)
        t10 = datamodel.Thief(MALE, SHORT, GREY_HAIRED, TATOO, self.list_animals[11], self.list_sports[1], 'Langostino Róbalo', '"El Pescador"', '68 años', 'Pescador muy experimentado, su técnica preferida para pescar es robando con mosca.\nLo han pescado robando varias veces.\nOdia los juegos de palabras.\nCarece de sentido del olfato.', 'p0_thief_small_langostino.png', 'p0_thief_big_langostino_1.jpg', 'p0_thief_big_langostino_2.jpg', 'p0_thief_big_langostino_3.jpg')
        list_thieves.append(t10)
        t11 = datamodel.Thief(FEMALE, TALL, BLONDE, MOLE, self.list_animals[9], self.list_sports[4], 'Helena Del Hurto', '"La Actríz"', 'Edad desconocida', 'En su época fue una afamada actriz.\nEn la última obra en la que participó su actuación fue tan buena que se robó el espectáculo, de ahí en adelante se dedicó a la delincuecia.', 'p0_thief_small_grace.png', 'p0_thief_big_grace_1.jpg', 'p0_thief_big_grace_2.jpg', 'p0_thief_big_grace_3.jpg')
        list_thieves.append(t11)
        t12 = datamodel.Thief(FEMALE, TALL, BLONDE, GLASSES, self.list_animals[2], self.list_sports[2], 'Vanessa Cuore', '"La Enfermera"', '32 años', 'Ex funcionaria de la salud.\nSe decía que por su belleza le robaba los corazones a sus pacientes.\nFue despedida injustamente por un malentendido, el director del hospital entendió esa frase literalmente.', 'p0_thief_small_vanessa.png', 'p0_thief_big_vanessa_1.jpg', 'p0_thief_big_vanessa_2.jpg', 'p0_thief_big_vanessa_3.jpg')
        list_thieves.append(t12)
        t13 = datamodel.Thief(FEMALE, SHORT, GREY_HAIRED, MOLE, self.list_animals[3], self.list_sports[1], 'Estela Bolsa Olavida', '"La vasca"', '76 años', 'Descendente de vascos.\nSe aprovecha de su aspecto de ancianita indefensa para asaltar a los jóvenes a los que les pide ayuda para cruzar la calle.\nUtiliza el dinero que obtiene para organizar partidas de rummy canasta con sus amigas.', 'p0_thief_small_estela.png', 'p0_thief_big_estela_1.jpg', 'p0_thief_big_estela_2.jpg', 'p0_thief_big_estela_3.jpg')
        list_thieves.append(t13)
        t14 = datamodel.Thief(FEMALE, SHORT, REDHEAD, SCAR, self.list_animals[15], self.list_sports[5], 'Andrea A. Salto', '"Naranjita"', '21 años', 'Adicta a las naranjas, tiene una cicatriz en el rostro que se hizo pelando una.\nDesde muy temprana edad, robaba en los puestos de fruta de su barrio aprovechando su color de pelo, que se camuflaba perfectamente con su amada fruta.', 'p0_thief_small_andrea.png', 'p0_thief_big_andrea_1.jpg', 'p0_thief_big_andrea_2.jpg', 'p0_thief_big_andrea_3.jpg')
        list_thieves.append(t14)
        t15 = datamodel.Thief(FEMALE, SHORT, REDHEAD, MOLE, self.list_animals[1], self.list_sports[6], 'Ana T. Birlo', '"La huerfanita"', '21 años', 'Vivió en un orfanato los primeros años de su vida, luego fue adoptada por un magnate.\nA causa de un trauma psicológico solo puede comunicarse con la gente a través del canto y el baile.\nSiempre deja para mañana lo que puede hacer hoy.', 'p0_thief_small_ana.png', 'p0_thief_big_ana_1.jpg', 'p0_thief_big_ana_2.jpg', 'p0_thief_big_ana_3.jpg')
        list_thieves.append(t15)
        t16 = datamodel.Thief(FEMALE, TALL, BRUNETTE, GLASSES, self.list_animals[0], self.list_sports[0], 'Roberta A. Ribas Lasmanos', '"La pianista"', '43 años', 'Excelente pianista.\nSu obra preferida es El arte de la fuga de Johann Sebastian Bach.\nFue detenida por intentar traficar armas guardándolas dentro de su piano en una gira mundial.\nQuedó en evidencia cuando se dispararon en medio de un concierto.', 'p0_thief_small_roberta.png', 'p0_thief_big_roberta_1.jpg', 'p0_thief_big_roberta_2.jpg', 'p0_thief_big_roberta_3.jpg')
        list_thieves.append(t16)
        return list_thieves

    def set_up_lair_sets(self):
        list_sets = [
         [
          1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6],
         [
          7, 7], [8, 8], [9, 9], [10, 10], [11, 11], [12, 12],
         [
          13, 13], [14, 14], [13, 15]]
        return list_sets

    def set_up_animals(self):
        list_animals = []
        a1 = datamodel.Animal('gato', MAMMAL, CARNIVORE, WALK)
        list_animals.append(a1)
        a2 = datamodel.Animal('perro', MAMMAL, CARNIVORE, WALK)
        list_animals.append(a2)
        a3 = datamodel.Animal('conejo', MAMMAL, HERBIVORE, WALK)
        list_animals.append(a3)
        a4 = datamodel.Animal('loro', BIRD, HERBIVORE, FLY)
        list_animals.append(a4)
        a5 = datamodel.Animal('canario', BIRD, HERBIVORE, FLY)
        list_animals.append(a5)
        a6 = datamodel.Animal('águila', BIRD, CARNIVORE, FLY)
        list_animals.append(a6)
        a7 = datamodel.Animal('pingüino', BIRD, CARNIVORE, SWIM)
        list_animals.append(a7)
        a8 = datamodel.Animal('tortuga de tierra', REPTILE, HERBIVORE, WALK)
        list_animals.append(a8)
        a9 = datamodel.Animal('tortuga de río', REPTILE, CARNIVORE, SWIM)
        list_animals.append(a9)
        a10 = datamodel.Animal('iguana', REPTILE, HERBIVORE, WALK)
        list_animals.append(a10)
        a11 = datamodel.Animal('cocodrilo', REPTILE, CARNIVORE, SWIM)
        list_animals.append(a11)
        a12 = datamodel.Animal('tiburón', FISH, CARNIVORE, SWIM)
        list_animals.append(a12)
        a13 = datamodel.Animal('piraña', FISH, CARNIVORE, SWIM)
        list_animals.append(a13)
        a14 = datamodel.Animal('caballito de mar', FISH, CARNIVORE, SWIM)
        list_animals.append(a14)
        a15 = datamodel.Animal('delfín', MAMMAL, CARNIVORE, SWIM)
        list_animals.append(a15)
        a16 = datamodel.Animal('murciélago de la fruta', MAMMAL, HERBIVORE, FLY)
        list_animals.append(a16)
        return list_animals

    def set_up_sports(self):
        list_sports = []
        s1 = datamodel.Sport('waterpolo', AQUATIC, True, True)
        list_sports.append(s1)
        s2 = datamodel.Sport('natación', AQUATIC, False, False)
        list_sports.append(s2)
        s3 = datamodel.Sport('nado sincronizado', AQUATIC, True, False)
        list_sports.append(s3)
        s4 = datamodel.Sport('fútbol', TERRESTRIAL, True, True)
        list_sports.append(s4)
        s5 = datamodel.Sport('golf', TERRESTRIAL, False, True)
        list_sports.append(s5)
        s6 = datamodel.Sport('carrera con postas', TERRESTRIAL, True, False)
        list_sports.append(s6)
        s7 = datamodel.Sport('carrera', TERRESTRIAL, False, False)
        list_sports.append(s7)
        s8 = datamodel.Sport('caminata', TERRESTRIAL, False, False)
        list_sports.append(s8)
        return list_sports

    def generate_departments_bordering_matrix(self):
        matrix = []
        matrix.append([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1])
        matrix.append([1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1])
        matrix.append([1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 2])
        matrix.append([1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1])
        matrix.append([1, 1, 2, 1, 1, 2, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 2, 2])
        matrix.append([1, 1, 1, 2, 2, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 2, 2, 1, 1])
        matrix.append([1, 2, 1, 1, 2, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2])
        matrix.append([1, 2, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2])
        matrix.append([1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1])
        matrix.append([1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1])
        matrix.append([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1])
        matrix.append([1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 2, 1])
        matrix.append([2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1])
        matrix.append([1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2])
        matrix.append([2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 2, 1])
        matrix.append([1, 2, 1, 2, 1, 2, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1])
        matrix.append([1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1])
        matrix.append([1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 2, 2, 1, 2, 1, 1, 1, 1])
        matrix.append([1, 1, 2, 1, 2, 1, 2, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1])
        return matrix

    def generate_departments_proximity_matrix(self):
        matrix = []
        matrix.append([1, 2, 3, 2, 3, 4, 4, 5, 5, 2, 6, 3, 7, 5, 7, 2, 3, 7, 4])
        matrix.append([2, 1, 3, 8, 8, 7, 8, 8, 7, 8, 6, 6, 4, 7, 4, 8, 7, 6, 6])
        matrix.append([3, 3, 1, 4, 3, 4, 6, 6, 6, 3, 3, 2, 6, 6, 3, 3, 2, 7, 8])
        matrix.append([2, 8, 4, 1, 7, 7, 7, 6, 6, 7, 6, 7, 4, 3, 3, 8, 7, 3, 3])
        matrix.append([3, 8, 3, 7, 1, 8, 8, 6, 6, 7, 7, 7, 6, 3, 6, 8, 7, 7, 3])
        matrix.append([4, 7, 4, 7, 8, 1, 8, 6, 6, 7, 7, 7, 3, 3, 6, 8, 8, 7, 3])
        matrix.append([4, 8, 6, 7, 8, 8, 1, 7, 7, 8, 6, 6, 3, 6, 3, 8, 6, 6, 3])
        matrix.append([5, 8, 6, 6, 6, 6, 7, 1, 8, 8, 4, 3, 2, 8, 2, 7, 3, 4, 7])
        matrix.append([5, 7, 6, 6, 6, 6, 7, 8, 1, 8, 4, 3, 2, 8, 2, 7, 3, 4, 7])
        matrix.append([2, 8, 3, 7, 7, 7, 8, 8, 8, 1, 3, 6, 4, 7, 4, 8, 6, 3, 6])
        matrix.append([6, 6, 3, 6, 7, 7, 6, 4, 4, 3, 1, 8, 6, 2, 8, 6, 8, 7, 2])
        matrix.append([3, 6, 2, 7, 7, 7, 6, 3, 3, 6, 8, 1, 4, 4, 7, 7, 8, 6, 4])
        matrix.append([7, 4, 6, 4, 6, 3, 3, 2, 2, 4, 6, 4, 1, 4, 6, 4, 4, 8, 3])
        matrix.append([5, 7, 6, 3, 3, 3, 6, 8, 8, 7, 2, 4, 4, 1, 5, 6, 4, 4, 7])
        matrix.append([7, 4, 3, 3, 6, 6, 3, 2, 2, 4, 8, 7, 6, 5, 1, 3, 7, 7, 4])
        matrix.append([2, 8, 3, 8, 8, 8, 8, 7, 7, 8, 6, 7, 4, 6, 3, 1, 7, 3, 6])
        matrix.append([3, 7, 2, 7, 7, 8, 6, 3, 3, 6, 8, 8, 4, 4, 7, 7, 1, 6, 4])
        matrix.append([7, 6, 7, 3, 7, 7, 6, 4, 4, 3, 7, 6, 8, 4, 7, 3, 6, 1, 6])
        matrix.append([4, 6, 8, 3, 3, 3, 6, 7, 7, 6, 2, 4, 3, 7, 4, 6, 4, 6, 1])
        return matrix


