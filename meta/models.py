from django.db import models
from django.db.models.sql.query import Query
from model_utils.managers import create_pass_through_manager_for_queryset_class

# class MetaQ(models.Q):

#     def __init__(self, *args, **kwargs):
#         super(MetaQ, self).__init__(children = ) 

#     def _generate_sql(self, *args, **kwargs):

def create_meta_table(model_class):
"""
    Create a meta table for `model_class`. The fields information are stored in `meta_fields` member.
"""

    class _QuerySet(models.QuerySet):
        
        def __init__(self, *args, **kwargs):
            super(_QuerySet, self).__init__(*args, **kwargs)
            self.query = Query()

        def filter_meta(self, *args, **kwargs):
            pass


        def update_meta(self, *args, **kwargs):
            pass

        def delete_meta(self, *args, **kwargs):
            pass

    class _Meta(models.Model):
    """
        Abstract vertical table.
    """

        model_class = model_class
        meta_fields = getattr(model_class, 'meta_fields', [])

        meta_key = models.CharField(max_length = 255)
        meta_value = models.TextField()
        meta_type = models.CharField(max_length = 36)
        entity_id = models.PositiveIntegerField(required = True)

        class Meta:
            db_table = "%s_meta" % model_class._meta.db_table
    
        def __unicode__(self):
            return u"Meta for %s" % model_class.__name__
        
    model_class.objects = create_pass_through_manager_for_queryset_class(model_class.objects.__class__, _QuerySet)
    model_class.meta_class = _Meta
    return _Meta