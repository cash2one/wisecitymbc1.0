from common.permissions import IsSubClass, HasObject
from .mixins import *

__all__ = ['HasFund', 'OwnFund','HasFundShare']

HasFund = IsSubClass(HasFundMixin)
OwnFund = IsSubClass(HasFundMixin)
HasFundShare = HasObject('owner.profile.user')
