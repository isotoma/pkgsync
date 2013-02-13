def name_version(dist_spec):
    if '==' in dist_spec:
        return dist_spec.split('==')
    return dist_spec, None

def dictify_package_list(l):
    """
    Take a list of package names, optionally with version numbers, e.g.

        >> dictify_package_list(['foo', 'bar==1.2.3', 'bar==1.2.4', 'quux'])
        {'foo': [], 'bar': ['1.2.3', '1.2.4'], 'quux': []}
    """
    package_versions = {}
    for dist_spec in l:
        name, version = name_version(dist_spec)
        if not name in package_versions:
            package_versions[name] = []
        if version and not version in package_versions[name]:
            package_versions[name].append(version)
    return package_versions


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
