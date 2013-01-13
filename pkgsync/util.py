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
