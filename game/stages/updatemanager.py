import os, hashlib
from framework import web, external
from game.data.datastore import VERSION, BASE_REQUEST_URL

def md5_for_file(f, block_size=1048576):
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)

    return md5.digest()


class UpdateManager:
    TITLE = '\\utualizar Divisi0xf3n Especial de Detectives'

    def __init__(self):
        self.description = None
        self.package = None
        self.url = None
        return

    def exists_update(self):
        return self.package is not None or self.url is not None

    def execute_update(self):
        if self.package:
            external.execute_package(self.package, self.TITLE)
        elif self.url:
            external.open_browser(self.url, self.TITLE)
        return

    def web_cb(self, result):
        if result.error:
            return
        update_data = result.data.get('update', None)
        if not update_data:
            return
        if 'description' in update_data:
            self.description = update_data['description']
        if update_data is None:
            return
        if 'new_version' in update_data and 'file_md5' in update_data and external.is_sugar:
            file = os.path.join(external.data_path, ('update-%s-%s' % (VERSION, update_data['new_version'])).replace('/', ''))
            try:
                md5 = int(update_data['file_md5'])
            except:
                md5 = -1
            else:
                if os.path.exists(file) and md5_for_file(open(file, 'rb')) == md5:
                    self.package = file
                    return
                elif 'file_url' in update_data:
                    web.download_file(BASE_REQUEST_URL + update_data['file_url'], file, callback=(lambda result: self.get_file_cb(result, file)))
        elif 'update_url' in update_data:
            self.url = update_data['update_url']
        return

    def get_file_cb(self, result, file):
        if result.error:
            return
        self.package = file
        return


