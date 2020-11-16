from setuptools import setup, find_packages
from version import get_version
from pathlib import Path

current_dir = Path(__file__).resolve().parent
description = 'A Prometheus middleware for your Python Flask app.'
try:
    history = current_dir.joinpath('CHANGELOG.md').read_text()
    long_description = '\n\n'.join([current_dir.joinpath('../README.md').read_text(), history])
except FileNotFoundError:
    long_description = 'A Prometheus middleware to add basic but very useful metrics for your Python Flask app.'

setup(
    name='bb_flask_monitor',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Flask',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
    ],
    author='Gustavo Coelho',
    author_email='gutorc@hotmail.com',
    url='https://github.com/labbsr0x/flask-monitor',
    version=get_version(),
    license='MIT',
    python_requires='>=3.6',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'prometheus-client>=0.6.0',
        'APScheduler>=3.6.3',
        'flask>=1.0.0',
        'requests',
    ],
    extras_require={
        'flask': ['Flask>=1.0.0'],
    },
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'packaging'
    ],
)
