from setuptools import find_packages, setup

setup(
    name='spaced-repetition',
    version='0.0.1',
    description='Tool for effective study of algorithms',
    author='Marcel Blistein',
    author_email='marcel.blistein@gmail.com',
    url='https://github.com/MBlistein/spaced-repetition',
    packages=find_packages(exclude=('test*', '*.db', '*.utils', '*.migrations')),
    install_requires=['Django',
                      'numpy',
                      'pandas',
                      'tabulate',
                      'python-dateutil'],
    entry_points={
        'console_scripts': [
            'srep=scripts.run_cli:main',
        ]
    }
)
