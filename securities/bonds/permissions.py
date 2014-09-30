from common.permissions import IsSubClass, HasObject
from .mixins import *

__all__ = ['HasBond', 'OwnBond', 'HasBondObject', 'HasBondShare']

HasBond = IsSubClass(HasBondMixin)
OwnBond = IsSubClass(OwnBondMixin)
HasBondObject = HasObject('publisher.profile.user')
HasBondShare = HasObject('owner.profile.user')
