def name_version(dist_spec):
    if '==' in dist_spec:
        return dist_spec.split('==')
    return dist_spec, None


class FileLikeResponseAdapter(object):
    def __init__(self, response):
        self.response = response
        self._line_generator = None
        self._read_generator = None

    def readline(self, size=1024):
        if not self._line_generator:
            self._line_generator = self.response.iter_lines(chunk_size=size)

        try:
            return self._line_generator.next() + '\n'
        except StopIteration:
            return

    def read(self, size=1024):
        if not self._read_generator:
            self._read_generator = self.response.iter_content(chunk_size=size)

        try:
            return self._read_generator.next()
        except StopIteration:
            return

    def __iter__(self):
        return self.response.iter_lines()
