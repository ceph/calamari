
from setuptools import setup

setup(
    name="calamari-rest-api",
    version="0.1",
    packages=['calamari_rest',
              'calamari_rest.urls',
              'calamari_rest.views',
              'calamari_rest.viewsets',
              'calamari_rest.serializers',
              'calamari_rest.renderers',
              'calamari_rest.parsers',
              'calamari_rest.permissions',
              ],
    url="http://www.inktank.com/enterprise/",
    author="Inktank Storage Inc.",
    author_email="info@inktank.com",
    license="LGPL-2.1+",
    zip_safe=False,
)
