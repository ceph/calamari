from setuptools import setup

setup(
    name="calamari_lite",
    version="0.1",
    packages=['calamari_lite'],
    url="http://www.inktank.com/enterprise/",
    author="Red Hat, Inc.",
    author_email="info@inktank.com",
    license="LGPL2.1 or later",
    entry_points={
        'console_scripts': [
            'calamari-lite = calamari_lite.server:main'
        ]
    }
)
