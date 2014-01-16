from rest_framework.viewsets import ViewSet
from sqlalchemy import create_engine
from cthulhu.persistence.persister import Session
from calamari_web.settings import config


class DatabaseViewSet(ViewSet):
    def __init__(self, *args, **kwargs):
        super(DatabaseViewSet, self).__init__(*args, **kwargs)

        engine = create_engine(config.get('cthulhu', 'db_path'))
        Session.configure(bind=engine)

        self.session = Session()
