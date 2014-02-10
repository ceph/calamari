from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.exceptions import ParseError
from rest_framework.pagination import PaginationSerializer
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

        class LocalPaginationSerializer(PaginationSerializer):
            class Meta:
                object_serializer_class = self.serializer_class

        self._pagination_serializer = LocalPaginationSerializer

    def _paginate(self, request, objects):
        # Pagination is, of course, separate to databaseyness, so you might think
        # to put this in a different mixin.  However, the *way* you do pagination
        # with LIMIT et al is rather coupled to the database, so here we are.

        page_number = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)

        # The django paginator conveniently works for sqlalchemy querysets because
        # they both have .count() and support array slicing
        try:
            paginator = Paginator(objects, page_size)
            page = paginator.page(page_number)
        except (ValueError, EmptyPage, PageNotAnInteger) as e:
            # Raise 400 is 'page' or 'page_size' were bad
            raise ParseError(str(e))
        ps = self._pagination_serializer(instance=page, context={'request': request})
        return ps.data
