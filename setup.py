from setuptools import setup, find_packages
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session='hack')
reqs = [str(ir.req) for ir in install_reqs]


setup(name='fts3_webdav_sync',
    version='0.1',
    description='Synchronized a source webdav to a destination webdav using a fts instance',
    author='Tobias Wochinger',
    author_email='tobias.wochinger@student.htw-berlin.de',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=reqs,
    test_suite='tests',
    tests_require=['mock'],
)
