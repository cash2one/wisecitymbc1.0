from django.db.models import QuerySet
from django.db import connection

class MetaQuerySet(QuerySet):
    """
        Hack for QuerySet
    """

    def __init__(self, *args, **kwargs):
        super(MetaQuerySet, self).__init__(*args, **kwargs)
        self.meta_query = Query(self.model.meta_class)

    def meta_filter(self, *args, **kwargs):
        pass

    def meta_exclude(self, *args, **kwargs):
        pass

    def _meta_filter_or_exclude(self, *args, **kwargs):
        clone = self._clone()
        meta_db_table = self.model.meta_class._meta.meta_db_table

