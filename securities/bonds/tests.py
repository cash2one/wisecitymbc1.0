"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

from accounts.models import *
from models import *
from datetime import datetime , timedelta

try:
	bond = Bond.objects.get(pk=5)
except Bond.DoesNotExist:
	bond = Bond.objects.create(publisher = Bank.objects.get(pk=1), lasted_time = timedelta(seconds=12), published_time = datetime.now(), profit_rate = '0.6')
person = Person.objects.get(pk=1)
person.buy_bond(bond, 12)
bond.publish()
