from queue import Queue
from threading import Lock, Thread
import urllib.request, urllib.error, urllib.parse, urllib.request, urllib.parse, urllib.error, json, zlib
__send_queue = Queue(0)
__results = {}
__results_lock = Lock()
OFFLINE = True

def __simple_task_method(func):

    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            if response.headers.get('Content-Type', '') in ('application/json', 'application/javascript'):
                data = json.loads(response.read())
            else:
                data = response.read()
            response.close()
            del response
            return TaskResult(data)
        except urllib.error.URLError as e:
            return TaskResult(None, error=True)

        return

    return wrapper


def synchronized(lock):

    def apply(func):

        def wrapper(*args, **kwargs):
            lock.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                lock.release()

            return

        return wrapper

    return apply


class __PendingTask:

    def __init__(self, method, key=None, callback=None):
        self.method = method
        self.key = key
        self.callback = callback
        return


class TaskResult:

    def __init__(self, data, error=False):
        self.error = error
        self.data = data
        return


def send_data(to, data, key=None, callback=None, encoding='json', compressed=False):

    @__simple_task_method
    def __send_data():
        req = urllib.request.Request(to)
        send_data = data
        if encoding is None:
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            send_data = urllib.parse.urlencode(send_data)
        elif encoding == 'json':
            send_data = json.dumps(send_data)
            req.add_header('Content-Type', 'application/json')
        elif encoding == 'text':
            req.add_header('Content-Type', 'text/plain')
        if compressed:
            req.add_header('Content-Encoding', 'gzip')
            send_data = zlib.compress(send_data)
        req.data = send_data
        return urllib.request.urlopen(req)

    __send_queue.put(__PendingTask(__send_data, key, callback))
    return


def query(to, parameters=None, key=None, callback=None):

    @__simple_task_method
    def __query():
        if parameters:
            local_to = to + '?' + urllib.parse.urlencode(parameters)
        else:
            local_to = to
        return urllib.request.urlopen(local_to)

    __send_queue.put(__PendingTask(__query, key, callback))
    return


def download_file(to, path, parameters=None, key=None, callback=None):

    def __get_file():
        if parameters:
            local_to = to + '?' + urllib.parse.urlencode(parameters)
        else:
            local_to = to
        try:
            return TaskResult(urllib.request.urlretrieve(local_to, path)[1])
        except IOError:
            return TaskResult(None, error=True)

        return

    __send_queue.put(__PendingTask(__get_file, key, callback))
    return


@synchronized(__results_lock)
def get_result_and_delete(key):
    if key in __results:
        ret = __results[key]
        __results.pop(key)
        return ret
    return


@synchronized(__results_lock)
def __add_result(key, data):
    __results[key] = data
    return


def __thread_main():
    while True:
        task = __send_queue.get()
        # Port Android: sin conexión. Los servidores del original (estadísticas, actualizaciones, errores)
        # ya no existen y no se envían datos del jugador; cada pedido termina como "error de red".
        result = TaskResult(None, error=True) if OFFLINE else task.method()
        if task.callback:
            task.callback(result)
        if task.key:
            __add_result(task.key, result)

    return


__thread = Thread(group=None, target=__thread_main, name='web_thread')
__thread.daemon = True
__thread.start()
del __thread
