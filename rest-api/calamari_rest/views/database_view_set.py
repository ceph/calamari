
from calamari_rest.viewsets import ViewSet
from calamari_web.settings import config

try:
    import sqlalchemy
except ImportError:
    sqlalchemy = None
else:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker()


class DatabaseViewSet(ViewSet):
    @property
    def serializer_class(self):
        raise NotImplementedError()

    def __init__(self, *args, **kwargs):
        super(DatabaseViewSet, self).__init__(*args, **kwargs)

        if sqlalchemy is not None:
            if not hasattr(DatabaseViewSet, 'engine'):
                DatabaseViewSet.engine = create_engine(config.get('cthulhu', 'db_path'))
                Session.configure(bind=self.engine)

            self.session = Session()
        else:
            class NullSession(object):
                def query(self, *args, **kwargs):
                    return []

            self.session = NullSession()
