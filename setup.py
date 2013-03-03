from setuptools import setup, find_packages

def long_description():
    return open('README.rst', 'r').read() + '\n\n' + \
           open('CHANGES', 'r').read()

setup(
    name='pkgsync',
    version='0.2.0dev',
    author='Alex Holmes',
    author_email='alex.holmes@isotoma.com',
    description='Synchronise packages between two python software repositories',
    long_description=long_description(),
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pkginfo>=0.9.1,<=1.0',
        'requests',
        'setuptools',
    ],
    extras_require={
        'test': ['unittest2', 'mock'],
    },
    entry_points='''
    [console_scripts]
    pkgsync = pkgsync:main
    '''
)
