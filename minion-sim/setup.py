from setuptools import setup

setup(
    name="minion_sim",
    version="0.1",
    packages=['minion_sim'],
    url="http://www.inktank.com/enterprise/",
    author="Inktank Storage Inc.",
    author_email="info@inktank.com",
    license="Inktank Ceph Enterprise Software License",
    entry_points={
        'console_scripts': [
            'minion-sim = minion_sim.cli:main',
            'minion-child = minion_sim.cli:child'
        ]
    }
)
