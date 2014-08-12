from setuptools import setup

setup(
    name="minion_sim",
    version="0.1",
    packages=['minion_sim'],
    url="http://www.inktank.com/enterprise/",
    author="Inktank Storage Inc.",
    author_email="info@inktank.com",
    license="LGPL-2.1+",
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'minion-sim = minion_sim.sim:main',
            'minion-child = minion_sim.child:main'
        ]
    }
)
