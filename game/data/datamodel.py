from framework import assets, text

class StolenObject:

    def __init__(self, prep, desc1, desc2, type):
        self.type_location = type
        self.preposition = prep
        self.description1 = desc1
        self.description2 = desc2
        return


class CrimeLocation:

    def __init__(self, prep, name, dep, loc1, loc2=None):
        self.preposition = prep
        self.name = name
        self.department = dep
        self.type_locations = []
        self.add_type_location(loc1)
        if loc2 != None:
            self.add_type_location(loc2)
        return

    def add_type_location(self, loc):
        self.type_locations.append(loc)
        return


class CityPin:

    def __init__(self, x, y, flipped, name, tag_size, tag_separation, tag_pos, article=''):
        self.x = x
        self.y = y
        self.flipped = flipped
        self.name = name
        self.tag_size = tag_size
        self.tag_separation = tag_separation
        self.tag_pos = tag_pos
        self.article = article
        return


class Department:

    def __init__(self, name, image, image_pos, locator_pos, city_pins, img_medal, map):
        self.name = name
        self.image = image
        self.chase_map = map
        self.locator_pos = locator_pos
        self.image_pos = image_pos
        self.id_img_medal = img_medal
        self.city_pins = city_pins
        return


class ClueType:

    def __init__(self, type):
        self.type = type
        return


class Clue:

    def __init__(self, id, types):
        self.id = id
        self.list_types = types
        return


class StageClue:

    def __init__(self, clue, note_item):
        self.clue = clue
        self.note_item = note_item
        return

    def build_item_message(self):
        if self.clue.id == 'i509' or self.clue.id == 'i529':
            if self.note_item.type == 'HILL':
                if self.note_item.article == 'el':
                    article = 'del'
                else:
                    article = 'de ' + self.note_item.article
                if self.note_item.article == 'los':
                    visiting = 'visitarlos'
                else:
                    visiting = 'visitarlo'
                message = 'Una postal ' + article + ' ' + self.note_item.name + '. Seguramente el ladrón piensa ' + visiting + '.'
            elif self.note_item.type == 'LAGOON':
                message = 'Una postal de la ' + self.note_item.name + '. Seguramente el ladrón piensa visitarla.'
            elif self.note_item.type == 'RIVER':
                message = 'Una postal del ' + self.note_item.name + '. Seguramente el ladrón piensa visitarlo.'
            elif self.note_item.type == 'LOCATION':
                message = 'Una postal de la localidad de ' + self.note_item.name + '. Seguramente el ladrón piensa visitarla.'
            else:
                raise Exception('Unknown item type ' + self.note_item.type + ' for clue ' + self.clue.id)
        elif self.clue.id == 'i510' or self.clue.id == 'i511':
            if self.note_item.type == 'HILL':
                message = 'Una nota. Al parecer el ladrón piensa visitar ' + self.note_item.article + ' ' + self.note_item.name + '.'
            elif self.note_item.type == 'LAGOON':
                message = 'Una nota. Al parecer el ladrón piensa visitar la ' + self.note_item.name + '.'
            elif self.note_item.type == 'RIVER':
                message = 'Una nota. Al parecer el ladrón piensa visitar el ' + self.note_item.name + '.'
            elif self.note_item.type == 'LOCATION':
                message = 'Una nota. Al parecer el ladrón piensa visitar la localidad de ' + self.note_item.name + '.'
            elif self.note_item.type == 'HISTORY_FACT':
                message = 'Una nota. Al parecer el ladrón piensa visitar el sitio donde ' + self.note_item.sentence_start + ' ' + self.note_item.article + ' ' + self.note_item.name + '.'
            elif self.note_item.type == 'WRITER':
                message = 'Una nota. Al parecer el ladrón piensa visitar el lugar de nacimiento de ' + self.note_item.name + '.'
            else:
                raise Exception('Unknown item type ' + self.note_item.type + ' for clue ' + self.clue.id)
        elif self.clue.id == 'i523':
            if self.note_item.type == 'HILL':
                if self.note_item.article == 'los':
                    marked = 'marcados'
                    visiting = 'visitarlos'
                else:
                    marked = 'marcado'
                    visiting = 'visitarlo'
                message = 'Un libro de geografía que tiene ' + marked + ' ' + self.note_item.article + ' ' + self.note_item.name + '. Seguramente el ladrón piensa ' + visiting + '.'
            elif self.note_item.type == 'LAGOON':
                message = 'Un libro de geografía que tiene marcada la ' + self.note_item.name + '. Seguramente el ladrón piensa visitarla.'
            elif self.note_item.type == 'RIVER':
                message = 'Un libro de geografía que tiene marcado el ' + self.note_item.name + '. Seguramente el ladrón piensa visitarlo.'
            elif self.note_item.type == 'HISTORY_FACT':
                message = 'Un libro de historia sobre ' + self.note_item.article + ' ' + self.note_item.name + '. Seguramente el ladrón piensa visitar el sitio donde ' + self.note_item.sentence_start + '.'
            elif self.note_item.type == 'LOCATION':
                message = 'Un libro de geografía que tiene marcada la localidad de ' + self.note_item.name + '. Seguramente el ladrón piensa visitarla.'
            elif self.note_item.type == 'WRITER':
                message = 'Un libro de ' + self.note_item.name + '. Seguramente el ladrón piensa visitar su lugar de nacimiento.'
            else:
                raise Exception('Unknown item type ' + self.note_item.type + ' for clue ' + self.clue.id)
        elif self.clue.id == 'i526':
            if self.note_item.type == 'HILL':
                if self.note_item.article == 'los':
                    visiting = 'visitarlos'
                else:
                    visiting = 'visitarlo'
                message = 'Un CD con el título "' + self.note_item.name + '". Seguramente el ladrón piensa ' + visiting + '.'
            elif self.note_item.type == 'LAGOON':
                message = 'Un CD con el título "' + self.note_item.name + '". Seguramente el ladrón piensa visitarla.'
            elif self.note_item.type == 'RIVER':
                message = 'Un CD con el título "' + self.note_item.name + '". Seguramente el ladrón piensa visitarlo.'
            elif self.note_item.type == 'HISTORY_FACT':
                message = 'Un CD con el título "' + self.note_item.name + '". Seguramente el ladrón piensa visitar el sitio donde ' + self.note_item.sentence_start + '.'
            elif self.note_item.type == 'LOCATION':
                message = 'Un CD con el título "' + self.note_item.name + ' y sus habitantes". Seguramente el ladrón piensa visitar esa localidad.'
            elif self.note_item.type == 'WRITER':
                message = 'Un CD con el título "Vida y obra de ' + self.note_item.name + '". Seguramente el ladrón piensa visitar su lugar de nacimiento.'
            else:
                raise Exception('Unknown item type ' + self.note_item.type + ' for clue ' + self.clue.id)
        elif self.clue.id == 'i527':
            if self.note_item.type == 'HILL':
                if self.note_item.article == 'los':
                    visiting = 'visitarlos'
                else:
                    visiting = 'visitarlo'
                message = 'Un mapa que tiene marcado ' + self.note_item.article + ' ' + self.note_item.name + '. Seguramente el ladrón piensa ' + visiting + '.'
            elif self.note_item.type == 'LAGOON':
                message = 'Un mapa que tiene marcada la ' + self.note_item.name + '. Seguramente el ladrón piensa visitarla.'
            elif self.note_item.type == 'RIVER':
                message = 'Un mapa que tiene marcado el ' + self.note_item.name + '. Seguramente el ladrón piensa visitarlo.'
            elif self.note_item.type == 'LOCATION':
                message = 'Un mapa que tiene marcada la localidad de ' + self.note_item.name + '. Seguramente el ladrón piensa visitarla.'
            else:
                raise Exception('Unknown item type ' + self.note_item.type + ' for clue ' + self.clue.id)
        elif self.clue.id == 'i528':
            if self.note_item.type == 'HILL':
                message = 'Un papel arrugado. Por lo que dice, el ladrón piensa visitar ' + self.note_item.article + ' ' + self.note_item.name + '.'
            elif self.note_item.type == 'LAGOON':
                message = 'Un papel arrugado. Por lo que dice, el ladrón piensa visitar la ' + self.note_item.name + '.'
            elif self.note_item.type == 'RIVER':
                message = 'Un papel arrugado. Por lo que dice, el ladrón piensa visitar el ' + self.note_item.name + '.'
            elif self.note_item.type == 'HISTORY_FACT':
                message = 'Por lo que dice, el ladrón piensa visitar el sitio donde ' + self.note_item.sentence_start + ' ' + self.note_item.article + ' ' + self.note_item.name + '.'
            elif self.note_item.type == 'LOCATION':
                message = 'Un papel arrugado. Por lo que dice, el ladrón piensa visitar la localidad de ' + self.note_item.name + '.'
            elif self.note_item.type == 'WRITER':
                message = 'Un papel arrugado. Por lo que dice, el ladrón piensa visitar el lugar de nacimiento de ' + self.note_item.name + '.'
            else:
                raise Exception('Unknown item type ' + self.note_item.type + ' for clue ' + self.clue.id)
        else:
            message = 'Esto no parece ser una pista interesante...'
        return message

    def build_right_department_message(self, dep):
        if self.note_item.type == 'HILL':
            article = self.note_item.article
            if article == 'los':
                verb = 'están ubicados'
            else:
                verb = 'está ubicado'
            article = article[0].upper() + article[1:]
            message = article + ' &#c144,22,22!' + self.note_item.name + '&#c! ' + verb + ' en el departamento de &#c144,22,22!' + dep.name + '&#c!.'
        elif self.note_item.type == 'LAGOON':
            if len(self.note_item.list_departments) > 1:
                message = 'La &#c144,22,22!' + self.note_item.name + ' limita con el departamento de &#c144,22,22!' + dep.name + '&#c!.'
            else:
                message = 'La &#c144,22,22!' + self.note_item.name + '&#c! está ubicada en el departamento de &#c144,22,22!' + dep.name + '&#c!.'
        elif self.note_item.type == 'RIVER':
            if len(self.note_item.list_departments) > 1:
                message = 'El &#c144,22,22!' + self.note_item.name + '&#c! pasa por el departamento de &#c144,22,22!' + dep.name + '&#c!.'
            else:
                message = 'El &#c144,22,22!' + self.note_item.name + '&#c! está ubicado en el departamento de &#c144,22,22!' + dep.name + '&#c!.'
        elif self.note_item.type == 'LOCATION':
            message = 'La localidad de &#c144,22,22!' + self.note_item.name + '&#c! está situada en el departamento de &#c144,22,22!' + dep.name + '&#c!.'
        elif self.note_item.type == 'HISTORY_FACT':
            article = self.note_item.article
            article = article[0].upper() + article[1:]
            message = article + ' &#c144,22,22!' + self.note_item.name + '&#c! ' + self.note_item.sentence_start + ' en el departamento de &#c144,22,22!' + dep.name + '&#c!.'
        elif self.note_item.type == 'WRITER':
            if self.note_item.sex == 'M':
                subject = 'El escritor '
            else:
                subject = 'La escritora '
            message = subject + '&#c144,22,22!' + self.note_item.name + '&#c! nació en el departamento de &#c144,22,22!' + dep.name + '&#c!.'
        else:
            message = ''
        return message


class Notes:

    def __init__(self, items):
        self.items = items
        return


class NoteItem:

    def __init__(self, name, type, distinction=None):
        self.name = name
        self.type = type
        self.distinction = distinction
        return

    def get_full_name(self):
        if self.distinction:
            return '%s (%s)' % (self.name, self.distinction)
        return self.name


class RiverNote(NoteItem):

    def __init__(self, name, dep_list, len, basin, desc1, desc2):
        NoteItem.__init__(self, name, 'RIVER')
        self.list_departments = dep_list
        self.length = len
        self.basin = basin
        self.description1 = desc1
        self.description2 = desc2
        return

    def get_departments(self):
        return self.list_departments


class LagoonNote(NoteItem):

    def __init__(self, name, dep_list, surface, desc1, desc2):
        NoteItem.__init__(self, name, 'LAGOON')
        self.list_departments = dep_list
        self.surface = surface
        self.description1 = desc1
        self.description2 = desc2
        return

    def get_departments(self):
        return self.list_departments


class HillNote(NoteItem):

    def __init__(self, name, article, dep, height, desc1, desc2):
        NoteItem.__init__(self, name, 'HILL')
        self.department = dep
        self.article = article
        self.height = height
        self.description1 = desc1
        self.description2 = desc2
        return

    def get_departments(self):
        return [self.department]


class HistoryFactNote(NoteItem):

    def __init__(self, s_start, article, name, dep_list, date, desc1, desc2):
        NoteItem.__init__(self, name, 'HISTORY_FACT')
        self.sentence_start = s_start
        self.article = article
        self.list_departments = dep_list
        self.date = date
        self.description1 = desc1
        self.description2 = desc2
        return

    def get_departments(self):
        return self.list_departments


class LocationNote(NoteItem):

    def __init__(self, name, dep, loc_type, s_start, population, desc, distinction=None):
        NoteItem.__init__(self, name, 'LOCATION', distinction)
        self.department = dep
        self.location_type = loc_type
        self.sentence_start = s_start
        self.population = population
        self.description = desc
        return

    def get_departments(self):
        return [self.department]


class WriterNote(NoteItem):

    def __init__(self, name, sex, dep, dates, desc):
        NoteItem.__init__(self, name, 'WRITER')
        self.sex = sex
        self.department = dep
        self.dates = dates
        self.description = desc
        return

    def get_departments(self):
        return [self.department]


class Witness:

    def __init__(self, name, img):
        self.image = img
        self.name = name
        self.identikit_added = False
        self.department = ''
        self.city = ''
        return


class JanitorStatement:

    def __init__(self, text=None, type=None, sex=None, cat1=None, cat2=None, cat3=None):
        self.type = type
        self.category1 = cat1
        self.category2 = cat2
        self.category3 = cat3
        self.text = text
        self.thief_sex = sex
        return


class Statement:

    def __init__(self, text):
        self.text = text
        return


class IdentikitStatement:

    def __init__(self, text, sex_f, height_f, hair_f, distinctive_f):
        self.text = text
        self.sex_feature = sex_f
        self.height_feature = height_f
        self.hair_feature = hair_f
        self.distinctive_feature = distinctive_f
        return


class WitnessStatement:

    def __init__(self, intro_s, j_s, i_s, l_s=None):
        self.intro_statement = intro_s
        self.janitor_statement = j_s
        self.location_statement = l_s
        self.identikit_statement = i_s
        return

    def are_equal(self, s):
        result = self.intro_statement == s.intro_statement and self.janitor_statement == s.janitor_statement and self.location_statement == s.location_statement and self.identikit_statement == s.identikit_statement
        return result


class Thief:

    def __init__(self, sex, height, hair, d_feature, pet, sport, name, nick, age, desc, i_img, i_l_img_f, i_l_img_s, i_p3_img):
        self.name = name
        self.nickname = nick
        self.age = age
        self.description = desc
        self.sex = sex
        self.height = height
        self.hair = hair
        self.distinctive_feature = d_feature
        self.animal = pet
        self.sport = sport
        self.identikit_image = i_img
        self.identikit_large_image_side = i_l_img_s
        self.identikit_large_image_front = i_l_img_f
        self.phase3_image = i_p3_img
        return

    def new_thief(self, c):
        print('')
        return

    def open_thief(self, char_name):
        print('')
        return

    def delete_character(self, char_name):
        print('')
        return


class CharacterInfo:

    def __init__(self, active, id, name, avatar, sex, location, range_level):
        self.active = active
        self.id = id
        self.name = name
        self.avatar = avatar
        self.sex = sex
        self.location = location
        self.range_level = range_level
        return


class Character:

    def __init__(self, charinfo, dep, uuid):
        self.charinfo = charinfo
        self.department = dep
        self.uuid = uuid
        image_name = 'p0_detective_'
        if charinfo.sex == 'M':
            image_name += 'male_'
        else:
            image_name += 'female_'
        image_name += '%03d' % charinfo.avatar
        self.avatar_image = assets.load_image(image_name + '.png')
        self.avatar_rollover_image = assets.load_image(image_name + '_rollover.png')
        self.avatar_asleep_image = assets.load_image(image_name + '_asleep.png')
        if charinfo.sex == 'M':
            if charinfo.avatar == 1:
                self.avatar_asleep_pos = (77, 41)
            elif charinfo.avatar == 2:
                self.avatar_asleep_pos = (58, 58)
            elif charinfo.avatar == 3:
                self.avatar_asleep_pos = (79, 35)
            elif charinfo.avatar == 4:
                self.avatar_asleep_pos = (76, 44)
            else:
                raise Exception('Missing asleep position')
        elif charinfo.avatar == 1:
            self.avatar_asleep_pos = (67, 51)
        elif charinfo.avatar == 2:
            self.avatar_asleep_pos = (47, 19)
        elif charinfo.avatar == 3:
            self.avatar_asleep_pos = (54, 42)
        elif charinfo.avatar == 4:
            self.avatar_asleep_pos = (70, 50)
        else:
            raise Exception('Missing asleep position')
        return


class HighscoreCharacter:

    def __init__(self, name, uuid, score):
        self.name = name
        self.uuid = uuid
        self.score = score
        return


class CharacterProgress:

    def __init__(self, char, score=0, resolved_cases=0, medals=[], l_dep_solved=[], gardener_seen=False, shoptender_seen=False, librarian_seen=False, bricklayer_seen=False, phase2_help=False, phase3_help=False, identikit_help=False, show_folder=False, show_notes_animation=False, notes=[], new_notes=[], bricklayer_pictures_seen=[], last_help_step_seen=0, captured_thieves=[]):
        self.character = char
        self.score = score
        self.resolved_cases = resolved_cases
        self.medals = medals
        self.list_departments_solved = l_dep_solved
        self.minigame_gardener_help_seen = gardener_seen
        self.minigame_shoptender_help_seen = shoptender_seen
        self.minigame_librarian_help_seen = librarian_seen
        self.minigame_bricklayer_help_seen = bricklayer_seen
        self.phase2_help = phase2_help
        self.phase3_help = phase3_help
        self.identikit_help = identikit_help
        self.show_folder = show_folder
        self.show_notes_animation = show_notes_animation
        self.notes = notes
        self.new_notes = new_notes
        self.bricklayer_pictures_seen = bricklayer_pictures_seen
        self.case = None
        self.last_help_step_seen = last_help_step_seen
        self.range = Range(self)
        self.captured_thieves = captured_thieves
        return

    def set_case(self, c):
        self.case = c
        return

    def add_medal(self, name):
        for medal in self.medals:
            if medal.name == name:
                if medal.count < 999:
                    medal.count += 1
                return

        self.medals.append(Medal(name, 1))
        return


class Range:

    def __init__(self, character_progress):
        self.__character_progress = character_progress
        self.level = 0
        self.update()
        return

    def update(self):
        resolved_cases = self.__character_progress.resolved_cases
        previous_level = self.level
        if resolved_cases < 3:
            self.level = 0
            self.next_range_cases = 3
            self.distance = 2
            self.time_limit_percentage = 2
            self.max_departments = 3
            self.minigame_level = 1
        elif resolved_cases < 6:
            self.level = 1
            self.next_range_cases = 6
            self.distance = 3
            self.time_limit_percentage = 1.8
            self.max_departments = 5
            self.minigame_level = 1
        elif resolved_cases < 10:
            self.level = 2
            self.next_range_cases = 10
            self.distance = 4
            self.time_limit_percentage = 1.6
            self.max_departments = 7
            self.minigame_level = 2
        elif resolved_cases < 14:
            self.level = 3
            self.next_range_cases = 14
            self.distance = 5
            self.time_limit_percentage = 1.4
            self.max_departments = 10
            self.minigame_level = 2
        elif resolved_cases < 18:
            self.level = 4
            self.next_range_cases = 18
            self.distance = 6
            self.time_limit_percentage = 1.2
            self.max_departments = 13
            self.minigame_level = 3
        else:
            self.level = 5
            self.next_range_cases = None
            self.distance = 7
            self.time_limit_percentage = 1
            self.max_departments = 18
            self.minigame_level = 3
        self.__character_progress.character.charinfo.range_level = self.level
        return previous_level != self.level


def get_range_name(level):
    if level == 0:
        return 'Agente'
    elif level == 1:
        return 'Oficial'
    elif level == 2:
        return 'Sub Comisario'
    elif level == 3:
        return 'Comisario'
    elif level == 4:
        return 'Inspector'
    else:
        return 'Inspector en jefe'
    return


class Medal:

    def __init__(self, name, count):
        self.name = name
        self.count = count
        return


class Case:

    def __init__(self, n=None, ldl=None, ldv=None, cl=None, so=None, tl=None, ts=None, cf=None, wwv=False, t=None, aot=None, ci=False, list_t=[], list_w=[], list_ws=[], list_wv=[], list_wf=[], list_d=[], list_tc=[], list_pd=[], tls=1, list_c=[], list_sf=[], ct=None, tcc=None):
        self.number = n
        self.last_department_lair = ldl
        self.last_department_visited = ldv
        self.crime_location = cl
        self.stolen_object = so
        self.time_limit = tl
        self.time_spend = ts
        self.clues_found = cf
        self.wrong_witness_visited = wwv
        self.thief = t
        self.arrest_order_thief = aot
        self.clues_identified = ci
        self.list_thieves = list_t
        self.list_witnesses = list_w
        self.list_witness_statements = list_ws
        self.list_visited_witnesses = list_wv
        self.list_folder_witnesses = list_wf
        self.list_departments = list_d
        self.list_target_cities = list_tc
        self.list_posible_departments = list_pd
        self.thief_lair_set = tls
        self.list_stage_clues = list_c
        self.list_selected_features = list_sf
        self.caught_thief = ct
        self.thief_car_color = tcc
        if not self.time_spend:
            self.time_spend = 0
        return

    def update_visited_witnesses(self, witness_visited):
        if witness_visited not in self.list_visited_witnesses:
            self.list_visited_witnesses.append(witness_visited)
        return

    def actual_days(self):
        t = self.time_spend
        days = int(t / 8) + 1
        hours = t + -8 * int(t / 8) + 12
        return (days, hours)

    def get_turns(self, days, hour):
        return (days - 1) * 8 + (hour - 12)

    def enough_time_left(self):
        if self.time_limit > self.time_spend:
            return True
        else:
            return False
        return

    @classmethod
    def _turns_to_time(self, t):
        return (int(t / 8) + 1, t % 8 + 12)

    def get_time_limit(self):
        return self._turns_to_time(self.time_limit)

    def get_full_text(self, user_character, user_character_progress):
        place_prep = self.crime_location.preposition
        place = self.crime_location.name
        stolen_obj_prep = self.stolen_object.preposition
        stolen_obj = self.stolen_object.description1
        stolen_obj2 = self.stolen_object.description2
        if user_character_progress.case.thief.sex == 1:
            sex = 'Masculino'
        else:
            sex = 'Femenino'
        department = self.crime_location.department.name
        (days, hour) = self._turns_to_time(self.time_limit)
        time = 'día ' + str(days) + ' a las ' + str(hour) + ' horas '
        agent = user_character.charinfo.name
        text1 = 'Robo en '
        text2 = ' de '
        text3 = '.\n\nEl director del museo reportó la desaparición '
        text4 = ' de su colección.\n\nVarios testigos afirman haber visto una silueta de aspecto sospechoso retirarse de la escena del crimen durante la noche, todos coinciden en que se trataba de una persona del sexo '
        text5 = '.\n\nPor las características del caso se sospecha que sea otra fechoría de la organización criminal C.U.L.T. por lo que la Intendencia de '
        text6 = ' se ha puesto en contacto con nuestra división para resolver este caso.\n\nContamos contigo para que encuentres al ladrón y devuelvas '
        text7 = ' a su respectivo dueño antes del '
        text8 = 'o será demasiado tarde para atraparlo.\n\nBuena suerte ' + text.to_lower(get_range_name(user_character_progress.range.level)) + '\n'
        text9 = '!'
        begin_highlight = '&#c149,0,0!'
        end_highlight = '&#c!'
        full_text = text1 + place_prep + ' ' + begin_highlight + place + end_highlight + text2 + begin_highlight + department + end_highlight + text3 + stolen_obj_prep + ' ' + begin_highlight + stolen_obj + end_highlight + text4 + begin_highlight + sex + end_highlight + text5 + begin_highlight + department + end_highlight + text6 + begin_highlight + stolen_obj2 + end_highlight + text7 + begin_highlight + time + end_highlight + text8 + begin_highlight + agent + end_highlight + text9
        return full_text


class Animal:

    def __init__(self, name, clas, diet, mov):
        self.name = name
        self.classification = clas
        self.diet = diet
        self.movement = mov
        return


class Sport:

    def __init__(self, name, cat, team, ball):
        self.name = name
        self.category = cat
        self.team = team
        self.ball = ball
        return


