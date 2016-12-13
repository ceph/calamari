from setuptools import setup

setup(
    name="calamari_common",
    version="0.1",
    packages=['calamari_common',
              'calamari_common.db',
              'calamari_common.remote',
              ],
    url="http://www.inktank.com/enterprise/",
    author="Inktank Storage Inc.",
    author_email="info@inktank.com",
    license="LGPL-2.1+",
    zip_safe=False,
    entry_points={
        'console_scripts': [
        ]
    }
)
