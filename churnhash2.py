import base64
import os.path

class ChurnHashError(Exception):
    def __init__(self, msg):
        self.value = msg
    def __str__(self):
        return repr(self.value)


class ChurnHash(object):
    '''
    A hash of file paths and churn data associated with that path.
    '''
    def __init__(self):
        self._hash = {}

    def _add_entry(self, file_path, lines_added, lines_removed):
        if file_path == '':
            raise ChurnHashError("Empty File path being added to FileHash")

        # Note we base64 encode the path so that two files with the same name
        # but different paths will not match could use the file path but then
        # the keys get really unwieldy
        encodedpath = base64.b64encode(file_path)
        if encodedpath in self._hash:
            self._hash[encodedpath]['lines_added'] += lines_added
            self._hash[encodedpath]['lines_removed'] += lines_removed
        else:
            self._hash[encodedpath] = {}
            self._hash[encodedpath]['file'] = file_path
            self._hash[encodedpath]['lines_added'] = lines_added
            self._hash[encodedpath]['lines_removed'] = lines_removed
    
    def _get_entry(self, file_path):
        encodedpath = base64.b64encode(file_path)
        if encodedpath not in self._hash:
            raise ChurnHashError("%s not found in FileHash" % file_path)
        return self._hash[encodedpath]['lines_changed']

    def add_file_path(self, file_path, lines_added, lines_removed):
        # This makes the assumption that it is called with fully specified files
        # with a common root and unix style ('/') paths
        if file_path == '':
            raise ChurnHashError("Empty File path used in ChurnHash add file")
        for pathsnippet in self._path_generator(file_path):
            self._add_entry(pathsnippet, lines_added, lines_removed)

    def get_churn(self, file_path):
        return self._get_entry(file_path)

    def _path_generator(self, file_path):
        f = file_path
        while(f != ''):
            yield f
            # Replace f with the path minus its last element
            f = os.path.split(f)[0]
            # Handle the case where path starts with a '/'
            if f == '/':
                f = ''

    def get_hash(self):
        return self._hash


