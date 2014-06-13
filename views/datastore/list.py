
from  django.views.generic.list import MultipleObjectMixin

class MultipleEntitiesMixin(MultipleObjectMixin):
    queryset = None