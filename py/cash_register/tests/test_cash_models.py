#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mock
import pytz

from decimal import Decimal
from datetime import datetime, date
from unittest import TestCase
from model_mommy import mommy

from cash_register.models import CashEntry, DailyCashSet
from business.models import Branch


class DailyCashSetModelsTestCase(TestCase):
    """
    Test Case for cash register model interface
    """

    def test_lock_cash_set(self):
        """
        Lock cash set should set is_locket flag
        """
        cash_set = mommy.make(DailyCashSet, is_locked=False)
        cash_set.lock()
        cash_set_new = DailyCashSet.objects.get(id=cash_set.id)
        self.assertTrue(cash_set_new.is_locked)

    def test_update_cash_set(self):
        """
        Update cash set should set set and change balance from entry
        """
        cash_set = mommy.make(DailyCashSet)
        cash_entry = mommy.make(CashEntry, price=Decimal(100))
        cash_set.update(cash_entry)
        self.assertEqual(cash_entry.set, cash_set)

    def test_save_cash_set_balance(self):
        """
        Save cash set should save proper balance
        """
        cash_set = mommy.make(
            DailyCashSet,
            balance=None,
            date=date(2015, 12, 28)
        )
        self.assertEqual(cash_set.balance, Decimal(0))

        cash_set.balance = Decimal(1500)
        cash_set.save(update_fields=['balance'])

        next_cash_set = mommy.make(
            DailyCashSet,
            branch=cash_set.branch,
            balance=None,
            date=date(2015, 12, 29)
        )
        self.assertEqual(next_cash_set.balance, Decimal(1500))


class CashEntryModelsTestCase(TestCase):
    """
    Test Case for cash register model interface
    """

    def test_delete_cash_entry(self):
        """
        Delete cash entry should change balance
        """
        cash_set = mommy.make(DailyCashSet, balance=Decimal(100))
        cash_entry = mommy.make(CashEntry, set=cash_set, price=Decimal(10))

        cash_entry.delete()

        cash_entry_new = CashEntry.all_objects.get(id=cash_entry.id)
        cash_set_new = DailyCashSet.objects.get(id=cash_set.id)

        self.assertTrue(cash_entry_new.is_deleted)
        self.assertEqual(cash_set_new.balance, Decimal(90))

    @mock.patch('cash_register.models.datetime')
    def test_save_cash_entry_created_date(self, mocked_datetime):
        """
        Save cash entry should set created date
        """
        # Mock datetime, to make sure expected datetime
        datetime_now = datetime.now().replace(tzinfo=pytz.utc)
        mocked_datetime.now.return_value = datetime_now

        cash_entry = mommy.make(CashEntry)
        self.assertEqual(cash_entry.created_date, datetime_now)

    def test_save_cash_entry_without_confirmation(self):
        """
        Save cash entry without confirmation shouldn't
        set confirmation id
        """
        cash_entry = mommy.make(CashEntry, confirmation=False)
        self.assertFalse(cash_entry.confirmation)
        self.assertFalse(cash_entry.confirmation_id)

    def test_save_cash_entry_with_confirmation(self):
        """
        Save cash entry with confirmation should set proper id
        """
        branch = mommy.make(Branch)

        cash_entries = mommy.make(
            CashEntry,
            set__branch=branch,
            confirmation=True,
            statement='income',
            created_date=datetime(2015, 12, 28),
            _quantity=2
        )
        new_year_entry = mommy.make(
            CashEntry,
            set__branch=branch,
            confirmation=True,
            statement='income',
            created_date=datetime(2016, 1, 1)
        )
        self.assertEqual(cash_entries[0].confirmation_id, 'KP/15/0001')
        self.assertEqual(cash_entries[1].confirmation_id, 'KP/15/0002')
        self.assertEqual(new_year_entry.confirmation_id, 'KP/16/0001')

        cash_entries = mommy.make(
            CashEntry,
            set__branch=branch,
            confirmation=True,
            statement='expense',
            created_date=datetime(2015, 12, 28),
            _quantity=2
        )
        new_year_entry = mommy.make(
            CashEntry,
            set__branch=branch,
            confirmation=True,
            statement='expense',
            created_date=datetime(2016, 1, 1)
        )

        self.assertEqual(cash_entries[0].confirmation_id, 'KW/15/0001')
        self.assertEqual(cash_entries[1].confirmation_id, 'KW/15/0002')
        self.assertEqual(new_year_entry.confirmation_id, 'KW/16/0001')

    def test_save_cash_entry_with_confirmation_many_branches(self):
        """
        Save cash entry with confirmation should set proper id
        for different branches
        """
        branches = mommy.make(Branch, _quantity=2)

        cash_entries = [
            mommy.make(
                CashEntry,
                set__branch=branches[0],
                confirmation=True,
                statement='income',
                created_date=datetime(2015, 12, 28),
            ),
            mommy.make(
                CashEntry,
                set__branch=branches[1],
                confirmation=True,
                statement='income',
                created_date=datetime(2015, 12, 28),
            )
        ]
        self.assertEqual(cash_entries[0].confirmation_id, 'KP/15/0001')
        self.assertEqual(cash_entries[1].confirmation_id, 'KP/15/0001')

        cash_entries = [
            mommy.make(
                CashEntry,
                set__branch=branches[0],
                confirmation=True,
                statement='expense',
                created_date=datetime(2015, 12, 28),
            ),
            mommy.make(
                CashEntry,
                set__branch=branches[1],
                confirmation=True,
                statement='expense',
                created_date=datetime(2015, 12, 28),
            )
        ]
        self.assertEqual(cash_entries[0].confirmation_id, 'KW/15/0001')
        self.assertEqual(cash_entries[1].confirmation_id, 'KW/15/0001')
