from framework import assets, stats, external
from game.data import datamodel
import random, os, time, uuid, sys

def save_character(datastore, c, cp, game, stage, check_save_in_development):
    character_data = []
    if stage != None:
        character_data.append(('stage', stage))
    character_data.append(('info', str(datastore.list_departments.index(c.department))))
    character_data.append(('uuid', str(c.uuid)))
    character_data.append(('casenum', str(cp.case.number)))
    character_data.append(('lair', str(datastore.list_departments.index(cp.case.last_department_lair))))
    character_data.append(('lastvisited', str(datastore.list_departments.index(cp.case.last_department_visited))))
    character_data.append(('crimeloc', str(datastore.list_crime_locations.index(cp.case.crime_location))))
    character_data.append(('stolenobj', str(datastore.list_stolen_objects.index(cp.case.stolen_object))))
    character_data.append(('timelimit', str(cp.case.time_limit)))
    character_data.append(('timespend', str(cp.case.time_spend)))
    clues_found = [
     'cluesfound']
    for clue_found in cp.case.clues_found:
        clues_found.append(clue_found)

    character_data.append(clues_found)
    if cp.case.wrong_witness_visited:
        character_data.append(('wrongwitness', '1'))
    else:
        character_data.append(('wrongwitness', '0'))
    character_data.append(('thief', str(datastore.list_thieves.index(cp.case.thief))))
    if cp.case.arrest_order_thief != None:
        thief_index = datastore.list_thieves.index(cp.case.arrest_order_thief)
        character_data.append(('arrestorder', str(thief_index)))
    else:
        character_data.append(('arrestorder', '-1'))
    if cp.case.caught_thief == None:
        character_data.append(('caughtthief', '-1'))
    else:
        character_data.append(('caughtthief', str(cp.case.caught_thief)))
    if cp.case.clues_identified:
        character_data.append(('cluesidentified', '1'))
    else:
        character_data.append(('cluesidentified', '0'))
    thieves = ['thieves']
    for thief in cp.case.list_thieves:
        thieves.append(str(datastore.list_thieves.index(thief)))

    character_data.append(thieves)
    departments = [
     'departments']
    for department in cp.case.list_departments:
        departments.append(str(datastore.list_departments.index(department)))

    character_data.append(departments)
    target_cities = [
     'targetcities']
    for tc in cp.case.list_target_cities:
        target_cities.append(str(tc))

    character_data.append(target_cities)
    witnesses = [
     'witnesses']
    wit_dep = None
    wit_dep_index = 0
    for w in cp.case.list_witnesses:
        for i in range(len(datastore.list_witnesses)):
            if datastore.list_witnesses[i].name == w.name:
                if wit_dep == None or w.city not in cp.case.list_departments[wit_dep_index].city_pins:
                    wit_dep_index = 0
                    for j in range(len(cp.case.list_departments)):
                        d = cp.case.list_departments[j]
                        if w.city in d.city_pins:
                            wit_dep = d
                            wit_dep_index = j

                witnesses.append(str(i))
                witnesses.append(str(wit_dep_index))
                witnesses.append(str(wit_dep.city_pins.index(w.city)))
                if w.witness_statement in datastore.list_statements:
                    witnesses.append(str(datastore.list_statements.index(w.witness_statement)))
                else:
                    found = False
                    for k in range(len(cp.case.list_witness_statements)):
                        s = cp.case.list_witness_statements[k]
                        if s.are_equal(w.witness_statement):
                            witnesses.append(str(-k - 1))
                            found = True
                            break

                    if not found:
                        raise Exception('Statement not defined (' + str(w.witness_statement) + ')')

    character_data.append(witnesses)
    statements = [
     'statements']
    for s in cp.case.list_witness_statements:
        if s.location_statement:
            location = '1'
        else:
            location = '-1'
        if s.identikit_statement:
            identikit = str(datastore.list_identikit_statements.index(s.identikit_statement))
        else:
            identikit = '-2'
        statements.append(str(datastore.list_statements.index(s.intro_statement)))
        statements.append(str(datastore.list_janitor_statements.index(s.janitor_statement)))
        statements.append(location)
        statements.append(identikit)

    character_data.append(statements)
    visited_witnesses = [
     'visitedwit']
    for w in cp.case.list_visited_witnesses:
        visited_witnesses.append(str(cp.case.list_witnesses.index(w)))

    character_data.append(visited_witnesses)
    folder_witnesses = [
     'folderwit']
    for w in cp.case.list_folder_witnesses:
        folder_witnesses.append(str(cp.case.list_witnesses.index(w)))

    character_data.append(folder_witnesses)
    posible_departments = [
     'posdepts']
    for d in cp.case.list_posible_departments:
        posible_departments.append(str(datastore.list_departments.index(d)))

    character_data.append(posible_departments)
    lair_set = [
     'thieflair', str(cp.case.thief_lair_set[0][0]), str(cp.case.thief_lair_set[0][1])]
    if cp.case.thief_lair_set[1] != None:
        for item in cp.case.thief_lair_set[1]:
            lair_set.append(item[0])
            lair_set.append(str(item[1]))
            lair_set.append(str(item[2]))

    character_data.append(lair_set)
    clues = [
     'clues']
    for stage_clue in cp.case.list_stage_clues:
        clues.append(str(datastore.list_clues.index(stage_clue.clue)))
        save_note(clues, stage_clue.note_item, datastore)

    character_data.append(clues)
    character_data.append(('selectedfeatures',
     str(cp.case.list_selected_features[0]),
     str(cp.case.list_selected_features[1]),
     str(cp.case.list_selected_features[2]),
     str(cp.case.list_selected_features[3])))
    department_solved = [
     'depsolved']
    for d in cp.list_departments_solved:
        department_solved.append(str(datastore.list_departments.index(d)))

    character_data.append(department_solved)
    if cp.minigame_gardener_help_seen:
        character_data.append(('mggardenerhelp', '1'))
    else:
        character_data.append(('mggardenerhelp', '0'))
    if cp.minigame_shoptender_help_seen:
        character_data.append(('mgshoptenderhelp', '1'))
    else:
        character_data.append(('mgshoptenderhelp', '0'))
    if cp.minigame_librarian_help_seen:
        character_data.append(('mglibrarianhelp', '1'))
    else:
        character_data.append(('mglibrarianhelp', '0'))
    if cp.minigame_bricklayer_help_seen:
        character_data.append(('mgbricklayerhelp', '1'))
    else:
        character_data.append(('mgbricklayerhelp', '0'))
    if cp.phase2_help:
        character_data.append(('phase2help', '1'))
    else:
        character_data.append(('phase2help', '0'))
    if cp.phase3_help:
        character_data.append(('phase3help', '1'))
    else:
        character_data.append(('phase3help', '0'))
    if cp.identikit_help:
        character_data.append(('identikithelp', '1'))
    else:
        character_data.append(('identikithelp', '0'))
    if cp.show_folder:
        character_data.append(('showfolder', '1'))
    else:
        character_data.append(('showfolder', '0'))
    if cp.show_notes_animation:
        character_data.append(('shownotesanimation', '1'))
    else:
        character_data.append(('shownotesanimation', '0'))
    character_data.append(('score', str(cp.score)))
    character_data.append(('resolvedcases', str(cp.resolved_cases)))
    medals = [
     'medals']
    for medal in cp.medals:
        medals.append(medal.name)
        medals.append(str(medal.count))

    character_data.append(medals)
    notes = [
     'notes']
    for n in cp.notes:
        save_note(notes, n, datastore)

    character_data.append(notes)
    new_notes = [
     'newnotes']
    for n in cp.new_notes:
        save_note(new_notes, n, datastore)

    character_data.append(new_notes)
    bricklayer_pictures = [
     'bricklayerpics']
    for picture in cp.bricklayer_pictures_seen:
        bricklayer_pictures.append(str(picture))

    character_data.append(bricklayer_pictures)
    character_data.append(('lasthelpstep', str(cp.last_help_step_seen)))
    captured_thieves = [
     'capturedthieves']
    for t in cp.captured_thieves:
        captured_thieves.append(str(datastore.list_thieves.index(t)))

    character_data.append(captured_thieves)
    file_name = 'c' + str(c.charinfo.id) + '.dat'
    assets.save_data(file_name, character_data)
    return


def open_character(datastore, charinfo):
    file_name = get_character_file_name(charinfo.id)
    character_data = assets.load_data(file_name, ';', False, from_dynamic_path=True)
    if character_data == None or character_data == []:
        return create_new_character(datastore, charinfo)
    else:
        c_id = charinfo.id
        c_uuid = None
        stage = None
        score = 0
        resolved_cases = 0
        medals = []
        bricklayer_pictures_seen = []
        list_dep = []
        list_dep_solved = []
        list_target_cities = []
        list_thieves = []
        list_sel_feat = []
        list_posible_deps = []
        list_wit_statements = []
        list_witnesses = []
        list_visited_witnesses = []
        list_folder_witnesses = []
        last_dep_lair = datastore.list_departments[0]
        last_dep_visited = datastore.list_departments[0]
        crime_loc = datastore.list_crime_locations[0]
        stolen_obj = datastore.list_stolen_objects[0]
        time_spend = 0
        time_limit = 0
        clues_found = 0
        list_clues = []
        thief_lair_set = 1
        case_number = 0
        gardener_help_seen = False
        bricklayer_help_seen = False
        shoptender_help_seen = None
        last_help_step_seen = 0
        phase2_help = False
        phase3_help = False
        identikit_help = False
        show_folder = False
        show_notes_animation = False
        caught_thief = None
        clues_identified = False
        wrong_witness_visited = False
        thief = None
        arrest_order_thief = None
        notes = []
        new_notes = []
        captured_thieves = []
        pending_witness_statements = []
        for line in character_data:
            type = line[0]
            if type == 'stage':
                stage = line[1]
            elif type == 'info':
                c_dep = datastore.list_departments[int(line[1])]
            elif type == 'uuid':
                c_uuid = uuid.UUID(line[1])
            elif type == 'casenum':
                case_number = line[1]
            elif type == 'lair':
                last_dep_lair = datastore.list_departments[int(line[1])]
            elif type == 'lastvisited':
                last_dep_visited = datastore.list_departments[int(line[1])]
            elif type == 'crimeloc':
                crime_loc = datastore.list_crime_locations[int(line[1])]
            elif type == 'stolenobj':
                stolen_obj = datastore.list_stolen_objects[int(line[1])]
            elif type == 'timelimit':
                time_limit = int(line[1])
            elif type == 'timespend':
                time_spend = int(line[1])
            elif type == 'cluesfound':
                clues_found = []
                k = 1
                while k < len(line):
                    clues_found.append(line[k])
                    k += 1

            elif type == 'wrongwitness':
                if int(line[1]) == 1:
                    wrong_witness_visited = True
                else:
                    wrong_witness_visited = False
            elif type == 'thief':
                thief = datastore.list_thieves[int(line[1])]
            elif type == 'arrestorder':
                thief_index = int(line[1])
                if thief_index == -1:
                    arrest_order_thief = None
                else:
                    arrest_order_thief = datastore.list_thieves[thief_index]
            elif type == 'thieves':
                for t in line[1:]:
                    list_thieves.append(datastore.list_thieves[int(t)])

            elif type == 'departments':
                for department in line[1:]:
                    list_dep.append(datastore.list_departments[int(department)])

            elif type == 'targetcities':
                for tc in line[1:]:
                    list_target_cities.append(int(tc))

            elif type == 'witnesses':
                k = 1
                while k < len(line):
                    wit_ori = datastore.list_witnesses[int(line[k])]
                    witness = datamodel.Witness(wit_ori.name, wit_ori.image)
                    witness.department = list_dep[0]
                    dep_index = int(line[k + 1])
                    witness.city = list_dep[dep_index].city_pins[int(line[k + 2])]
                    statement_index = int(line[k + 3])
                    pending_witness_statements.append((witness, statement_index))
                    list_witnesses.append(witness)
                    k += 4

            elif type == 'statements':
                k = 1
                while k < len(line):
                    intro_statement = datastore.list_statements[int(line[k])]
                    janitor_statement = datastore.list_janitor_statements[int(line[k + 1])]
                    if int(line[k + 2]) != -1:
                        city = list_dep[0].city_pins[list_target_cities[0]]
                        from game.stages import phase1
                        location_statement = datamodel.Statement(phase1.generate_thief_location_statement(city))
                    else:
                        location_statement = None
                    if int(line[k + 3]) != -2:
                        identikit_statement = datastore.list_identikit_statements[int(line[k + 3])]
                    else:
                        identikit_statement = None
                    w_s = datamodel.WitnessStatement(intro_statement, janitor_statement, identikit_statement, location_statement)
                    list_wit_statements.append(w_s)
                    k += 4

            elif type == 'visitedwit':
                for w in line[1:]:
                    index = int(w)
                    list_visited_witnesses.append(list_witnesses[index])

            elif type == 'folderwit':
                for w in line[1:]:
                    index = int(w)
                    list_folder_witnesses.append(list_witnesses[index])

            elif type == 'posdepts':
                for d in line[1:]:
                    list_posible_deps.append(datastore.list_departments[int(d)])

            elif type == 'thieflair':
                set_elements = [
                 int(line[1]), int(line[2])]
                if len(line) <= 3:
                    layout = None
                else:
                    layout = []
                    k = 3
                    while k < len(line):
                        item_type = line[k]
                        place_holder = int(line[k + 1])
                        category = int(line[k + 2])
                        layout.append((item_type, place_holder, category))
                        k += 3

                thief_lair_set = [
                 set_elements, layout]
            elif type == 'clues':
                k = 1
                while k < len(line):
                    clue = datastore.list_clues[int(line[k])]
                    k += 1
                    (note_item, size) = read_note(line, k, datastore)
                    k += size
                    list_clues.append(datamodel.StageClue(clue, note_item))

            elif type == 'selectedfeatures':
                list_sel_feat.append(int(line[1]))
                list_sel_feat.append(int(line[2]))
                list_sel_feat.append(int(line[3]))
                list_sel_feat.append(int(line[4]))
            elif type == 'depsolved':
                for d in line[1:]:
                    list_dep_solved.append(datastore.list_departments[int(d)])

            elif type == 'mggardenerhelp':
                if line[1] == '1':
                    gardener_help_seen = True
                else:
                    gardener_help_seen = False
            elif type == 'mgshoptenderhelp':
                if line[1] == '1':
                    shoptender_help_seen = True
                else:
                    shoptender_help_seen = False
            elif type == 'mglibrarianhelp':
                if line[1] == '1':
                    librarian_help_seen = True
                else:
                    librarian_help_seen = False
            elif type == 'mgbricklayerhelp':
                if line[1] == '1':
                    bricklayer_help_seen = True
                else:
                    bricklayer_help_seen = False
            elif type == 'phase2help':
                if line[1] == '1':
                    phase2_help = True
                else:
                    phase2_help = False
            elif type == 'phase3help':
                if line[1] == '1':
                    phase3_help = True
                else:
                    phase3_help = False
            elif type == 'identikithelp':
                if int(line[1]) == 1:
                    identikit_help = True
                else:
                    identikit_help = False
            elif type == 'showfolder':
                if int(line[1]) == 1:
                    show_folder = True
                else:
                    show_folder = False
            elif type == 'shownotesanimation':
                if int(line[1]) == 1:
                    show_notes_animation = True
                else:
                    show_notes_animation = False
            elif type == 'score':
                score = int(line[1])
            elif type == 'resolvedcases':
                resolved_cases = int(line[1])
            elif type == 'medals':
                k = 1
                while k < len(line):
                    medal = datamodel.Medal(line[k], int(line[k + 1]))
                    medals.append(medal)
                    k += 2

            elif type == 'notes':
                k = 1
                while k < len(line):
                    (note_item, size) = read_note(line, k, datastore)
                    k += size
                    notes.append(note_item)

            elif type == 'newnotes':
                k = 1
                while k < len(line):
                    (note_item, size) = read_note(line, k, datastore)
                    k += size
                    new_notes.append(note_item)

            elif type == 'bricklayerpics':
                k = 1
                while k < len(line):
                    bricklayer_pictures_seen.append(int(line[k]))
                    k += 1

            elif type == 'lasthelpstep':
                last_help_step_seen = int(line[1])
            elif type == 'caughtthief':
                if line[1] == '-1':
                    caught_thief = None
                else:
                    value = line[1]
                    if value.startswith('('):
                        k = value.index(',')
                        value = value[1:k]
                    caught_thief = int(value)
            elif type == 'cluesidentified':
                if int(line[1]) == 1:
                    clues_identified = True
                else:
                    clues_identified = False
            elif type == 'capturedthieves':
                k = 1
                while k < len(line):
                    ct = datastore.list_thieves[int(line[k])]
                    if ct not in captured_thieves:
                        captured_thieves.append(ct)
                    k += 1

        for (witness, statement_index) in pending_witness_statements:
            if statement_index >= 0:
                witness.witness_statement = datastore.list_statements[statement_index]
            else:
                witness.witness_statement = list_wit_statements[-statement_index - 1]

        if c_uuid == None:
            c_uuid = uuid.uuid4()
        char = datamodel.Character(charinfo, c_dep, c_uuid)
        char_progress = datamodel.CharacterProgress(char, score, resolved_cases, medals, list_dep_solved, gardener_help_seen, shoptender_help_seen, gardener_help_seen, bricklayer_help_seen, phase2_help, phase3_help, identikit_help, show_folder, show_notes_animation, notes, new_notes, bricklayer_pictures_seen, last_help_step_seen, captured_thieves)
        case = datamodel.Case(case_number, last_dep_lair, last_dep_visited, crime_loc, stolen_obj, time_limit, time_spend, clues_found, wrong_witness_visited, thief, arrest_order_thief, clues_identified, list_thieves, list_witnesses, list_wit_statements, list_visited_witnesses, list_folder_witnesses, list_dep, list_target_cities, list_posible_deps, thief_lair_set, list_clues, list_sel_feat, caught_thief)
        char_progress.set_case(case)
    return (
     char, char_progress, stage)


def create_new_character(datastore, charinfo):
    dep = datastore.list_departments[int(0)]
    for d in datastore.list_departments:
        if d.name == charinfo.location:
            dep = d
            break

    char_uuid = uuid.uuid4()
    char = datamodel.Character(charinfo, dep, char_uuid)
    char_progress = datamodel.CharacterProgress(char)
    stage = None
    return (
     char, char_progress, stage)


def get_character_file_name(char_id):
    return 'c' + str(char_id) + '.dat'


def delete_character(char_id):
    file_name = get_character_file_name(char_id)
    file_to_delete = os.path.join(external.data_path, 'data', file_name)
    if os.path.exists(file_to_delete):
        try:
            os.remove(file_to_delete)
        except Exception as message:
            print(('Cannot delete data file:', file_to_delete, '(message:', message, ')'))

    return


def save_note(list, note, datastore):
    dep = note.get_departments()[0]
    item_type = note.type
    list.append(str(datastore.department_type_index[dep.name][item_type].index(note)))
    list.append(str(datastore.list_departments.index(dep)))
    list.append(item_type)
    return


def read_note(line, k, datastore):
    note_index = int(line[k])
    dep_index = int(line[k + 1])
    note_item_type = line[k + 2]
    dep_name = datastore.list_departments[dep_index].name
    note_item = datastore.department_type_index[dep_name][note_item_type][note_index]
    return (
     note_item, 3)


class CaseGenerator():

    def __init__(self, datastore):
        self.use_fixed_route = False
        self.datastore = datastore
        return

    def new_case(self):
        self.__seed = time.time()
        random.seed(self.__seed)
        last_department_visited = self.datastore.user_character_progress.character.department
        last_department_lair = self.generate_case_department()
        (list_departments, list_posible_departments) = self.generate_departments(last_department_lair)
        list_target_cities = self.generate_target_cities(list_departments)
        crime_location = self.generate_crime_location(last_department_lair)
        stolen_object = self.generate_stolen_object(crime_location)
        (thief, list_thieves) = self.generate_thiefs()
        list_witnesses = self.generate_witnesses(list_departments)
        time_limit = self.generate_time_limit(list_departments)
        thief_lair_set = self.generate_thief_lair_set()
        list_witness_statements = self.generate_witness_statements(thief, self.datastore)
        case_number = self.generate_case_number()
        list_clues = self.generate_clues(list_departments)
        list_visited_witnesses = []
        list_folder_witnesses = []
        list_selected_features = [0, 0, 0, 0]
        return datamodel.Case(case_number, last_department_lair, last_department_visited, crime_location, stolen_object, time_limit, 0, [], False, thief, None, False, list_thieves, list_witnesses, list_witness_statements, list_visited_witnesses, list_folder_witnesses, list_departments, list_target_cities, list_posible_departments, thief_lair_set, list_clues, list_selected_features, None)

    def generate_thief_lair_set(self):
        thief_set = random.choice(self.datastore.list_lair_sets)
        return [
         thief_set, None]

    def select_clue_types(self, notes, clues, added_clues):
        if len(clues) == 3:
            return True
        if notes:
            list_clues = self.datastore.list_clues[:]
            random.shuffle(list_clues)
            for clue in list_clues:
                if notes[0].type in [type.type for type in clue.list_types] and clue not in added_clues:
                    clues.append(datamodel.StageClue(clue, notes[0]))
                    added_clues.append(clue)
                    if self.select_clue_types(notes[1:], clues, added_clues):
                        return True
                    else:
                        added_clues.pop()
                        clues.pop()

        return False

    def generate_department_clues(self, department):
        types = list(self.datastore.list_clue_types)
        random.shuffle(types)
        notes = []
        for type in types:
            if type.type == 'MUSICIAN':
                continue
            candidates = self.datastore.department_type_index[department.name][type.type]
            if candidates:
                notes.append(random.choice(candidates))
            if len(notes) == 3:
                break

        if len(notes) != 3:
            raise Exception('Less notes:' + str(len(notes)) + ', seed: ' + str(self.__seed) + '; depart: ' + department.name)
        clues = []
        added_clues = []
        if not self.select_clue_types(notes, clues, added_clues):
            raise Exception('Not enough clues, seed: ' + str(self.__seed) + '; depart: ' + department.name)
        if len(set(added_clues)) != len(added_clues):
            raise Exception('repeated clues, seed: ' + str(self.__seed) + '; depart: ' + department.name)
        return clues

    def generate_clues(self, list_departments):
        return self.generate_department_clues(list_departments[1])

    def generate_witness_statements(self, thief, datastore):
        list_identikit_statements = []
        list_janitor_statements = []
        list_sport_statements = []
        list_pet_statements = []
        list_w_statements = []
        if thief.sex == 1:
            intro_statement = datastore.list_statements[1]
        else:
            intro_statement = datastore.list_statements[2]
        for s in datastore.list_identikit_statements:
            if thief.sex == s.sex_feature and thief.height == s.height_feature:
                list_identikit_statements.append(s)
            elif thief.sex == s.sex_feature and thief.hair == s.hair_feature:
                list_identikit_statements.append(s)
            elif thief.distinctive_feature == s.distinctive_feature:
                list_identikit_statements.append(s)

        selection = random.choice([thief.animal, thief.sport])
        if selection == thief.sport:
            selection = thief.animal
            list_sport_statements = []
            for s in datastore.list_janitor_statements:
                if s.type == 1:
                    if s.category1 == thief.sport.category or s.category2 == thief.sport.team or s.category3 == thief.sport.ball:
                        if thief.sex == s.thief_sex or s.thief_sex == -1:
                            list_sport_statements.append(s)

            for i in range(3):
                list_janitor_statements.append(list_sport_statements.pop(list_sport_statements.index(random.choice(list_sport_statements))))

        else:
            selection = thief.sport
            list_animal_statements = []
            for s in datastore.list_janitor_statements:
                if s.type == 2:
                    if s.category1 == thief.animal.classification or s.category2 == thief.animal.diet or s.category3 == thief.animal.movement:
                        if thief.sex == s.thief_sex or s.thief_sex == -1:
                            list_animal_statements.append(s)

            for i in range(3):
                list_janitor_statements.append(list_animal_statements.pop(list_animal_statements.index(random.choice(list_animal_statements))))

        added = False
        for i in range(3):
            identikit_statement = None
            if i == 0:
                identikit_statement = list_identikit_statements[0]
            elif i == 1:
                identikit_statement = list_identikit_statements[1]
            elif i == 2:
                identikit_statement = list_identikit_statements[2]
            janitor_statement = list_janitor_statements[i]
            list_w_statements.append(datamodel.WitnessStatement(intro_statement, janitor_statement, identikit_statement))

        return list_w_statements

    def generate_case_number(self):
        first_7_digits = random.choice(list(range(9999999)))
        last_digit = random.choice(list(range(10)))
        return str(first_7_digits) + '-' + str(last_digit)

    def generate_time_limit(self, list_departments):
        proximity_matrix = self.datastore.generate_departments_proximity_matrix()
        char_range = self.datastore.user_character_progress.range
        minigame_turns = 1
        thief_lair = 1
        times_resolution = 1
        basic_turns = (minigame_turns * 3 + thief_lair) * times_resolution
        travel_turns = 0
        for i in range(1):
            dep_distance = get_travel_turns(self.datastore, [list_departments[i], list_departments[i + 1]])
            travel_turns = travel_turns + dep_distance

        total_turns = int((basic_turns + travel_turns) * char_range.time_limit_percentage) + 1
        return total_turns

    def generate_thiefs(self):
        possible_thieves = self.datastore.list_thieves[:]
        captured_thieves = self.datastore.user_character_progress.captured_thieves
        if len(captured_thieves) == len(possible_thieves):
            del captured_thieves[0:_div(len(possible_thieves) , 2)]
        for t in captured_thieves:
            if t in possible_thieves:
                possible_thieves.remove(t)

        case_thief = random.choice(possible_thieves)
        thieves = list(filter((lambda x: x.sex == case_thief.sex), self.datastore.list_thieves))
        thieves.append(random.choice(list(filter((lambda x: x.sex != case_thief.sex), self.datastore.list_thieves))))
        random.shuffle(thieves)
        return (
         case_thief, thieves)

    def generate_stolen_object(self, crime_location):
        list_posible_stolen_objects = []
        for type_loc in crime_location.type_locations:
            for stolen_obj in self.datastore.list_stolen_objects:
                if stolen_obj.type_location == type_loc:
                    list_posible_stolen_objects.append(stolen_obj)
                    so = random.choice(list_posible_stolen_objects)

        return so

    def generate_witnesses(self, list_departments):
        list_witnesses = []
        dep = list_departments[0]
        list_pos_cities = []
        for c in dep.city_pins:
            list_pos_cities.append(c)

        witnesses = []
        for i in range(len(dep.city_pins)):
            if len(witnesses) == 0:
                witnesses = self.datastore.list_witnesses[:]
            random_wit = random.choice(witnesses)
            witnesses.remove(random_wit)
            wit_ori = random_wit
            wit = datamodel.Witness(wit_ori.name, wit_ori.image)
            wit.department = dep
            wit.city = list_pos_cities.pop(list_pos_cities.index(random.choice(list_pos_cities)))
            wit.witness_statement = self.datastore.list_statements[0]
            list_witnesses.append(wit)

        return list_witnesses

    def generate_crime_location(self, last_department_lair):
        list_posible_crime_locs = []
        for crime_loc in self.datastore.list_crime_locations:
            if crime_loc.department == last_department_lair:
                list_posible_crime_locs.append(crime_loc)

        cl = random.choice(list_posible_crime_locs)
        return cl

    def generate_case_department(self):
        list_case_departments = []
        for dep in self.datastore.list_departments:
            if not self.datastore.user_character_progress.list_departments_solved.__contains__(dep):
                list_case_departments.append(dep)

        if len(list_case_departments) == 0:
            self.datastore.user_character_progress.list_departments_solved = []
            return self.generate_case_department()
        elif self.use_fixed_route:
            return list_case_departments[8]
        else:
            return random.choice(list_case_departments)
        return

    def generate_departments(self, last_department_lair):
        IN_RANGE = True
        OUT_OF_RANGE = False
        proximity_matrix = self.datastore.generate_departments_proximity_matrix()
        char_range = self.datastore.user_character_progress.range
        last_dep = last_department_lair
        list_posible_deps = []
        list_deps_to_visit = []
        list_deps_to_visit.append(last_department_lair)
        list_border_deps = self.get_border_departments(last_dep)
        t1 = ''
        for i in range(len(list_border_deps)):
            t1 += list_border_deps[i].name + ', '

        for d in list_border_deps:
            if self.department_in_range(proximity_matrix, char_range, last_dep, d) and not list_deps_to_visit.__contains__(d):
                list_posible_deps.append(d)

        for d in list_posible_deps:
            list_border_deps.remove(d)

        t2 = ''
        for i in range(len(list_posible_deps)):
            t2 += list_posible_deps[i].name + ', '

        if len(list_posible_deps) > char_range.max_departments:
            while len(list_posible_deps) > char_range.max_departments:
                list_posible_deps.remove(random.choice(list_posible_deps))

        elif len(list_posible_deps) < char_range.max_departments:
            list_posible_border_departments = self.generate_posible_departments(proximity_matrix, char_range, list_deps_to_visit, list_posible_deps, last_dep, IN_RANGE)
            while len(list_posible_border_departments) > 0 and len(list_posible_deps) < char_range.max_departments:
                dep_selection = list_posible_border_departments.pop(list_posible_border_departments.index(random.choice(list_posible_border_departments)))
                if len(list_posible_deps) < char_range.max_departments and not list_posible_deps.__contains__(dep_selection) and not list_deps_to_visit.__contains__(dep_selection):
                    list_posible_deps.append(dep_selection)

            while len(list_border_deps) > 0 and len(list_posible_deps) < char_range.max_departments:
                dep_selection = list_border_deps.pop(list_border_deps.index(random.choice(list_border_deps)))
                if len(list_posible_deps) < char_range.max_departments and not list_posible_deps.__contains__(dep_selection) and not list_deps_to_visit.__contains__(dep_selection):
                    list_posible_deps.append(dep_selection)

            while len(list_posible_deps) < char_range.max_departments:
                if len(list_posible_deps) == 17 and len(list_deps_to_visit) == 2:
                    break
                list_posible_border_departments = self.generate_posible_departments(proximity_matrix, char_range, list_deps_to_visit, list_posible_deps, last_dep, OUT_OF_RANGE)
                while len(list_posible_border_departments) > 0 and len(list_posible_deps) < char_range.max_departments:
                    dep_selection = list_posible_border_departments.pop(list_posible_border_departments.index(random.choice(list_posible_border_departments)))
                    if len(list_posible_deps) < char_range.max_departments and not list_posible_deps.__contains__(dep_selection) and not list_deps_to_visit.__contains__(dep_selection):
                        list_posible_deps.append(dep_selection)

        if self.use_fixed_route:
            last_dep = list_posible_deps[0]
        else:
            last_dep = random.choice(list_posible_deps)
        list_deps_to_visit.append(last_dep)
        return (
         list_deps_to_visit, list_posible_deps)

    def generate_target_cities(self, deps):
        target_cities = []
        for d in deps:
            target_cities.append(random.choice(list(range(len(d.city_pins)))))

        return target_cities

    def generate_posible_departments(self, proximity_matrix, range, list_deps_to_visit, list_deps_added, last_dep, in_range):
        list_border_deps = []
        for d in list_deps_added:
            test_list_border_deps = self.get_border_departments(d)
            for td in test_list_border_deps:
                if not list_border_deps.__contains__(td) and not list_deps_added.__contains__(td) and not list_deps_to_visit.__contains__(td):
                    if in_range:
                        if self.department_in_range(proximity_matrix, range, last_dep, td):
                            list_border_deps.append(td)
                    else:
                        list_border_deps.append(td)

        return list_border_deps

    def department_in_range(self, proximity_matrix, range, start_dep, end_dep):
        max_allowed_distance = self.datastore.user_character_progress.range.distance
        dep_in_matrix_position = self.datastore.list_departments.index(start_dep)
        dep_distance = proximity_matrix[dep_in_matrix_position][self.datastore.list_departments.index(end_dep)]
        if dep_distance <= max_allowed_distance and dep_distance != 0:
            return True
        else:
            return False
        return

    def get_border_departments(self, start_dep):
        border_matrix = self.datastore.generate_departments_bordering_matrix()
        dep_in_matrix_position = self.datastore.list_departments.index(start_dep)
        list_border_deps = []
        for i in range(19):
            border = border_matrix[dep_in_matrix_position][i]
            if border == 1:
                list_border_deps.append(self.datastore.list_departments[i])

        return list_border_deps


def get_travel_turns(datastore, list_deps):
    proximity_matrix = datastore.generate_departments_proximity_matrix()
    initial_dep_in_matrix_position = datastore.list_departments.index(list_deps[0])
    final_dep_in_matrix_position = datastore.list_departments.index(list_deps[1])
    dep_distance = proximity_matrix[initial_dep_in_matrix_position][final_dep_in_matrix_position]
    return dep_distance


def check_obj_equals(o1, name1, stack1, o2, name2, stack2, check_cache):
    if o1 == None:
        if o2 == None:
            return
        else:
            raise Exception("Objects are not equal. '" + name1 + "' is None, and '" + name2 + "' has value '" + str(o2) + "'")
    elif o2 == None:
        raise Exception("Objects are not equal. '" + name2 + "' is None, and '" + name1 + "' has value '" + str(o1) + "'")
    if o1 not in stack1 and o2 not in stack2:
        stack1.append(o1)
        stack2.append(o2)
        type1 = type(o1)
        type2 = type(o2)
        if type1 != type2:
            raise Exception("Objects are not equal. '" + name1 + "' (type '" + str(type1) + ") has a different type than '" + name2 + "' (type " + str(type2) + ')')
        from types import IntType, LongType, FloatType, StringType, TupleType, ListType, DictType, FunctionType
        if type1 is FunctionType:
            pass
        elif type1 is IntType or type1 is LongType or type1 is FloatType or type1 is StringType:
            if o1 != o2:
                raise Exception("Objects are not equal. '" + name1 + "' (=" + str(o1) + ") has a different value than '" + name2 + "' (=" + str(o2) + ')')
        elif type1 is assets.Image:
            if o1.get_file_name() != o2.get_file_name():
                raise Exception("Objects are not equal. '" + name1 + "' has a image '" + o1.get_file_name() + "' and '" + name2 + "' has image '" + o2.get_file_name() + "'")
        elif type1 is TupleType or type1 is ListType:
            if len(o1) != len(o2):
                raise Exception("Objects are not equal. '" + name1 + "' (count " + str(len(o1)) + ") has a different number of elements than '" + name2 + "' (count " + str(len(o2)) + ')')
            for i in range(len(o1)):
                check_obj_equals(o1[i], name1 + '[' + str(i) + ']', stack1, o2[i], name2 + '[' + str(i) + ']', stack2, check_cache)

        elif type1 is DictType:
            if len(o1) != len(o2):
                raise Exception("Objects are not equal. '" + name1 + "' has a different number of elements than '" + name2 + "'")
            for key in range(len(o1)):
                if key not in o2:
                    raise Exception("Objects are not equal. '" + name1 + "' has key '" + str(key) + " but dictionary '" + name2 + "' doesn't have it.")
                check_obj_equals(o1[key], name1 + '[' + str(key) + ']', stack1, o2[key], name2 + '[' + str(key) + ']', stack2, check_cache)

        elif o1 not in check_cache or check_cache[o1] != o2:
            check_cache[o1] = o2
            fields1 = dir(o1)
            fields2 = dir(o2)
            for field1 in fields1:
                if not field1.startswith('__'):
                    if field1 not in fields2:
                        raise Exception("Objects are not equal. Field '" + field1 + "' is defined in '" + name1 + "' (" + str(o1) + ") but it is not defined in '" + name2 + "' (" + str(o2) + ')')

            for field2 in fields2:
                if not field2.startswith('__'):
                    if field2 not in fields1:
                        raise Exception("Objects are not equal. Field '" + field2 + "' is defined in '" + name2 + "' (" + str(o2) + ") but it is not defined in '" + name1 + "' (" + str(o2) + ')')

            for field in fields1:
                if not field.startswith('__'):
                    check_obj_equals(getattr(o1, field), name1 + '.' + field, stack1, getattr(o2, field), name2 + '.' + field, stack2, check_cache)
                stack1.append(o1)

        stack1.remove(o1)
        stack2.remove(o2)
    return


