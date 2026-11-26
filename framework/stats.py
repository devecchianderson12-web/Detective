import uuid, os, sys, traceback
from . import assets
from datetime import *
import time
from . import external

class Stats:

    def __init__(self):
        self.__uuid = None
        self.__start_date = None
        self.__data = None
        self.__pending_save = False
        self.__active_time_events = {}
        return

    def start_time_event(self, code):
        if self.__data == None:
            self.__load_data()
        if code not in self.__active_time_events:
            self.__active_time_events[code] = datetime.now()
        return

    def end_time_event(self, code, accumulate_code=None):
        if self.__data == None:
            self.__load_data()
        start_time = self.__active_time_events.get(code)
        if start_time != None:
            self.__update_time_event(self.__data, code, start_time)
            if accumulate_code != None:
                self.__update_time_event(self.__data, accumulate_code, start_time)
            del self.__active_time_events[code]
            self.__pending_save = True
        return

    def increment_count_event(self, code):
        if self.__data == None:
            self.__load_data()
        if code in self.__data:
            self.__data[code][0] += 1
        else:
            self.__data[code] = [
             1]
        self.__pending_save = True
        return

    def get_data(self):
        data_to_save = [
         [
          str(self.__uuid), self.__to_datetime_str(self.__start_date), self.__to_datetime_str(datetime.now())]]
        data = self.__data.copy()
        for (code, value) in list(self.__active_time_events.items()):
            self.__update_time_event(data, code, value)

        for (key, value) in list(data.items()):
            key_data = [str(key)]
            for term in value:
                key_data.append(str(term))

            data_to_save.append(key_data)

        return data_to_save

    def save_if_pending(self):
        if self.__pending_save:
            assets.save_data('game.dat', self.get_data())
            self.__pending_save = False
        return

    def __load_data(self):
        lines = assets.load_data('game.dat', ';', False, from_dynamic_path=True)
        self.__data = {}
        if len(lines) == 0:
            self.__uuid = uuid.uuid4()
            self.__start_date = datetime.now()
        else:
            first_line = lines[0]
            if len(first_line) >= 2:
                self.__uuid = uuid.UUID(first_line[0])
                self.__start_date = self.__from_datetime_str(first_line[1])
                for line in lines[1:]:
                    code = line[0]
                    k = 1
                    code_data = []
                    try:
                        while k < len(line):
                            if line[k] == '|':
                                code_data.append('|')
                            else:
                                code_data.append(int(line[k]))
                            k += 1

                        self.__data[code] = code_data
                    except Exception:
                        print('Error reading statistics')
                        (type, value, tb) = sys.exc_info()
                        report_error(type, value, tb)

        return

    def __update_time_event(self, data, code, start_time):
        elapsed_time = (datetime.now() - start_time).seconds
        if code not in data:
            data[code] = [
             elapsed_time, elapsed_time, elapsed_time, 
             1, 2, elapsed_time]
        else:
            new_data = data[code][:]
            code_data = data[code]
            new_data[0] = new_data[0] + elapsed_time
            new_data[1] = min(new_data[1], elapsed_time)
            new_data[2] = max(new_data[2], elapsed_time)
            new_data[3] = new_data[3] + 1
            part_count = 4
            n = 20
            if len(new_data) == part_count:
                new_data.append('|')
            new_data.append(elapsed_time)
            max_size = part_count + n + 1
            if len(new_data) > max_size:
                del new_data[part_count + 1:part_count + 1 + len(code_data) - max_size + 1]
            data[code] = new_data
        return

    def __to_datetime_str(self, dt):
        return dt.strftime('%Y-%m-%dT%H:%M:%S')

    def __from_datetime_str(self, s):
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


def report_error(type, value, tb):
    full_name = os.path.join(external.data_path, 'data', 'game_err.dat')
    file = open(full_name, 'a')
    file.write('[')
    file.write(str(datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
    file.write('] ')
    file.write('%s: %s\n' % (type.__name__, str(value)))
    traceback.print_tb(tb, None, file)
    file.close()
    size = os.path.getsize(full_name)
    if size > 10000:
        data = get_error_data(10000)
        file = open(full_name, 'w')
        file.write(data)
        file.close()
    return


def get_error_data(size_to_end=None):
    path = os.path.join(external.data_path, 'data', 'game_err.dat')
    if not os.path.exists(path):
        return
    size = os.path.getsize(path)
    file = open(path, 'r')
    if size_to_end and size > size_to_end:
        file.seek(size - size_to_end)
    data = file.read()
    file.close()
    return data


def delete_error_data():
    path = os.path.join(external.data_path, 'data', 'game_err.dat')
    os.remove(path)
    return


