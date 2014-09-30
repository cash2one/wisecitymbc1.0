from common.permissions import IsSubClass, HasObject
from .mixins import *

__all__ = ['HasStock']

HasStock = IsSubClass(HasStockMixin)
