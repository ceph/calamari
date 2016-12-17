from setuptools import setup

setup(
    name="calamari_rlyeh",
    version="0.1",
    packages=['rlyeh', 'rlyeh.manager'],
    url="http://www.inktank.com/enterprise/",
    author="Inktank Storage Inc.",
    author_email="info@inktank.com",
    license="LGPL-2.1+",
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'rlyeh-manager = rlyeh.manager.manager:main',
        ]
    }
)
