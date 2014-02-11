
from rest_framework.viewsets import ViewSet
from sqlalchemy import create_engine
from calamari_web.settings import config

from sqlalchemy.orm import sessionmaker
Session = sessionmaker()


class DatabaseViewSet(ViewSet):
    @property
    def serializer_class(self):
        raise NotImplementedError()

    def __init__(self, *args, **kwargs):
        super(DatabaseViewSet, self).__init__(*args, **kwargs)

        if not hasattr(DatabaseViewSet, 'engine'):
            DatabaseViewSet.engine = create_engine(config.get('cthulhu', 'db_path'))
            Session.configure(bind=self.engine)

        self.session = Session()
