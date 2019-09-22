#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mock
import pytz

import httplib as http

from model_mommy import mommy
from datetime import date as Date, datetime, timedelta
from django.contrib.auth.models import User, Permission, Group

from django.core.urlresolvers import reverse
from django.test import TestCase

from cash_register.models import Category, CashEntry, DailyCashSet
from business.models import Branch
from invoices.models import Invoice


class CashRegisterFormTestCase(TestCase):
    """
    Common test case for income and expense cash register forms
    """

    def setUp(self):
        self.user = User.objects.create_user(
            'test_user', '', 'password'
        )
        self.permission_codename = "create_cashentry"
        self.branch = mommy.make(Branch)
        self.example_date = Date(2015, 12, 25)

        self.category_income = mommy.make(Category, statement='income')
        self.category_expense = mommy.make(Category, statement='expense')

        self.inbox_url = self._get_url('index')
        self.income_url = self._get_url('income')
        self.expense_url = self._get_url('expense')

    def _get_url(self, page, branch=None, date=None, cash_entry_id=None,
                 invoice_id=None):
        path = "cash_register:{}".format(page)
        example_date = date if date else self.example_date
        example_branch = branch if branch else self.branch

        params = dict(
            branch_id=example_branch.id,
            year=example_date.year,
            month=example_date.month,
            day=example_date.day,
        )

        if cash_entry_id:
            params['id'] = cash_entry_id

        if invoice_id:
            params['invoice_id'] = invoice_id

        return reverse(path, kwargs=params)

    def _login_as_user(self, user=None, with_permissions=True, auth_branch=True):
        user = user or self.user
        if with_permissions:
            permission, __ = Permission.objects.get_or_create(
                codename=self.permission_codename
            )
            user.user_permissions.add(permission)

        if auth_branch:
            # Ensure user has auth branch
            user.branches.add(self.branch)

        self.client.login(
            username=user.username,
            password='password'
        )

    def test_cannot_create_entry_for_locked_set(self):
        """
        Check if user cannot create entry for locked set
        """
        mommy.make(
            DailyCashSet,
            is_locked=True,
            date=self.example_date,
            branch=self.branch
        )
        self._login_as_user()
        response = self.client.get(self._get_url('income'))
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_cannot_create_entry_for_set_with_date_lte_last_locked_set(self):
        """
        Check if user cannot create entry for set with date lower
        then or equal date of last locked set
        """
        dates = [
            self.example_date - timedelta(days=days_delta)
            for days_delta in [30, 15, 0]
        ]
        for _date in dates:
            mommy.make(
                DailyCashSet,
                is_locked=True,
                date=_date,
                branch=self.branch
            )

        self._login_as_user()

        example_date = self.example_date - timedelta(days=40)
        url = self._get_url('income', date=example_date)
        response = self.client.get(url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

        example_date = self.example_date - timedelta(days=30)
        url = self._get_url('income', date=example_date)
        response = self.client.get(url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

        example_date = self.example_date - timedelta(days=20)
        url = self._get_url('income', date=example_date)
        response = self.client.get(url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

        example_date = self.example_date - timedelta(days=10)
        url = self._get_url('income', date=example_date)
        response = self.client.get(url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

        example_date = self.example_date - timedelta(days=5)
        url = self._get_url('income', date=example_date)
        response = self.client.get(url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

        response = self.client.get(self.income_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_cannot_create_entry_for_set_with_date_gt_last_locked_set(self):
        """
        Check if user cannot create entry for set with date grater
        then date of last set when last set in not locked
        """
        mommy.make(
            DailyCashSet,
            is_locked=False,
            date=self.example_date - timedelta(days=1),
            branch=self.branch
        )
        self._login_as_user()
        response = self.client.get(self.income_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)


class CashRegisterIncomeTestCase(CashRegisterFormTestCase):
    """
    Test Case for income form view for cash register app
    """

    def test_income_form_invisible_for_anonymous(self):
        """
        Check if anonymous user are redirected to login page
        """
        expected_path = '/login/?next={}'.format(self.income_url)
        response = self.client.get(self.income_url)

        self.assertEqual(response.status_code, http.FOUND)
        self.assertTrue(response.url.endswith(expected_path))

    def test_income_form_not_available_for_users_without_permission(self):
        """
        Check if users without proper permission can't see the content
        """
        self._login_as_user(with_permissions=False)
        response = self.client.get(self.income_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_income_form_invisible_for_users_without_branch_auth(self):
        """
        Check if users without proper permission can't see the content
        """
        self._login_as_user(auth_branch=False)
        response = self.client.get(self.income_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_income_form_available_for_users_with_permission(self):
        """
        Check if users with proper permission can see the content
        """
        self._login_as_user()
        response = self.client.get(self.income_url)
        self.assertEqual(response.status_code, http.OK)

    def test_income_form_invalid(self):
        """
        Invalid income form
        """
        self._login_as_user()
        response = self.client.post(self.income_url, {})
        self.assertEqual(response.status_code, http.OK)

        initial = response.context_data['form'].initial
        self.assertEqual(len(initial), 2)
        self.assertIn('created_by', initial)
        self.assertIn('statement', initial)

        errors = response.context_data['form'].errors
        self.assertEqual(len(errors), 2)
        self.assertIn('price', errors)
        self.assertIn('category', errors)

    def test_income_form_invalid_price(self):
        """
        Invalid income form by wrong price
        """
        self._login_as_user()
        response = self.client.post(self.income_url, {
            'price': -100,
            'category': self.category_income.id
        })
        self.assertEqual(response.status_code, http.OK)

        errors = response.context_data['form'].errors
        self.assertEqual(len(errors), 1)
        self.assertIn('price', errors)

    @mock.patch('cash_register.models.datetime')
    def test_income_form_valid(self, mocked_datetime):
        """
        Valid income form
        """
        self._login_as_user()

        # Mock datetime, to make sure expected datetime
        datetime_now = datetime.now().replace(tzinfo=pytz.utc)
        mocked_datetime.now.return_value = datetime_now

        response = self.client.post(self.income_url, {
            'price': 100,
            'category': self.category_income.id
        })
        self.assertEqual(response.status_code, http.FOUND)
        self.assertTrue(response.url.endswith(self.inbox_url))

        entries = CashEntry.objects.filter(
            created_date=datetime_now,
            category=self.category_income,
            price=100
        )
        self.assertEqual(len(entries), 1)

    def test_income_form_with_initial_invoice(self):
        """
        Check if users with proper permission can see the content
        """
        self._login_as_user()
        invoice = mommy.make(
            Invoice,
            customer_name="Name",
            customer_address="Address",
            total_value=1000,
            document_appearance='X',
            tax='X',
        )
        income_url = self._get_url('income', invoice_id=invoice.id)
        response = self.client.get(income_url)

        self.assertEqual(response.status_code, http.OK)

        initial = response.context_data['form'].initial
        self.assertEqual(len(initial), 6)
        self.assertIn('created_by', initial)
        self.assertIn('statement', initial)
        self.assertIn('person_refer', initial)
        self.assertIn('document_refer', initial)
        self.assertIn('price', initial)
        self.assertIn('confirmation', initial)


class CashRegisterExpenseTestCase(CashRegisterFormTestCase):
    """
    Test Case for expense form view for cash register app
    """

    def test_expense_form_invisible_for_anonymous(self):
        """
        Check if anonymous user are redirected to login page
        """
        expected_path = '/login/?next={}'.format(self.expense_url)
        response = self.client.get(self.expense_url)

        self.assertEqual(response.status_code, http.FOUND)
        self.assertTrue(response.url.endswith(expected_path))

    def test_expense_form_not_available_for_users_without_permission(self):
        """
        Check if users without proper permission can't see the content
        """
        self._login_as_user(with_permissions=False)
        response = self.client.get(self.expense_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_expense_form_invisible_for_users_without_branch_auth(self):
        """
        Check if users without proper permission can't see the content
        """
        self._login_as_user(auth_branch=False)
        response = self.client.get(self.expense_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_expense_form_available_for_users_with_permission(self):
        """
        Check if users with proper permission can see the content
        """
        self._login_as_user()
        response = self.client.get(self.expense_url)
        self.assertEqual(response.status_code, http.OK)

    def test_expense_form_invalid(self):
        """
        Invalid expense form
        """
        self._login_as_user()
        response = self.client.post(self.expense_url, {})
        self.assertEqual(response.status_code, http.OK)

        initial = response.context_data['form'].initial
        self.assertEqual(len(initial), 2)
        self.assertIn('created_by', initial)
        self.assertIn('statement', initial)

        errors = response.context_data['form'].errors
        self.assertEqual(len(errors), 2)
        self.assertIn('price', errors)
        self.assertIn('category', errors)

    def test_expense_form_invalid_price(self):
        """
        Invalid expense form by wrong price
        """
        self._login_as_user()
        response = self.client.post(self.expense_url, {
            'price': 100,
            'category': self.category_expense.id
        })
        self.assertEqual(response.status_code, http.OK)

        errors = response.context_data['form'].errors
        self.assertEqual(len(errors), 1)
        self.assertIn('price', errors)

    @mock.patch('cash_register.models.datetime')
    def test_expense_form_valid(self, mocked_datetime):
        """
        Valid expense form
        """
        self._login_as_user()

        # Mock datetime, to make sure expected datetime
        datetime_now = datetime.now().replace(tzinfo=pytz.utc)
        mocked_datetime.now.return_value = datetime_now

        response = self.client.post(self.expense_url, {
            'price': -100,
            'category': self.category_expense.id
        })
        self.assertEqual(response.status_code, http.FOUND)
        self.assertTrue(response.url.endswith(self.inbox_url))

        entries = CashEntry.objects.filter(
            created_date=datetime_now,
            category=self.category_expense,
            price=-100
        )
        self.assertEqual(len(entries), 1)


class CashRegisterUpdateEntryTestCase(CashRegisterFormTestCase):
    """
    Test Case for update form view for cash register app
    """

    def setUp(self):
        super(CashRegisterUpdateEntryTestCase, self).setUp()
        self.permission_codename = "update_cashentry"
        self.cash_entry = mommy.make(
            CashEntry,
            created_by=self.user,
            statement='income',
        )
        self.update_url = self._get_url(
            'update',
            cash_entry_id=self.cash_entry.id
        )

    def test_update_form_invisible_for_anonymous(self):
        """
        Check if anonymous user are redirected to login page
        """
        expected_path = '/login/?next={}'.format(self.update_url)
        response = self.client.get(self.update_url)

        self.assertEqual(response.status_code, http.FOUND)
        self.assertTrue(response.url.endswith(expected_path))

    def test_update_form_not_available_for_users_without_permission(self):
        """
        Check if users without proper permission can't see the content
        """
        self._login_as_user(with_permissions=False)
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_update_form_invisible_for_users_without_branch_auth(self):
        """
        Check if users without proper permission can't see the content
        """
        self._login_as_user(auth_branch=False)
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_update_form_invisible_for_user_who_is_not_owner(self):
        """
        Check if users who is not owner can't see the content
        """
        user = User.objects.create_user(
            'user_non_owner', '', 'password'
        )
        self._login_as_user(user=user)
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, http.NOT_FOUND)

    def test_update_form_available_for_user_who_is_admin(self):
        """
        Check if users who is admin can see the content
        """
        superuser = User.objects.create_superuser(
            'admin', '', 'password'
        )
        self._login_as_user(user=superuser)
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, http.OK)

    def test_update_form_available_for_users_with_permission(self):
        """
        Check if users with proper permission can see the content
        """
        self._login_as_user()
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, http.OK)

    def test_update_form_invalid(self):
        """
        Invalid update form
        """
        self._login_as_user()
        response = self.client.post(self.update_url, {})
        self.assertEqual(response.status_code, http.OK)

        initial = response.context_data['form'].initial
        self.assertEqual(len(initial), 8)

        errors = response.context_data['form'].errors
        self.assertEqual(len(errors), 4)
        self.assertIn('price', errors)
        self.assertIn('category', errors)
        self.assertIn('created_by', errors)
        self.assertIn('statement', errors)

    def test_update_form_invalid_price(self):
        """
        Invalid update form by wrong price
        """
        self._login_as_user()
        response = self.client.post(self.update_url, {
            'statement': 'income',
            'created_by': self.user.id,
            'price': -100,
            'category': self.category_income.id
        })
        self.assertEqual(response.status_code, http.OK)

        errors = response.context_data['form'].errors
        self.assertEqual(len(errors), 1)
        self.assertIn('price', errors)

    @mock.patch('cash_register.models.datetime')
    def test_update_form_valid(self, mocked_datetime):
        """
        Valid update form
        """
        self._login_as_user()

        # Mock datetime, to make sure expected datetime
        datetime_now = datetime.now().replace(tzinfo=pytz.utc)
        mocked_datetime.now.return_value = datetime_now

        response = self.client.post(self.update_url, {
            'statement': 'income',
            'created_by': self.user.id,
            'price': 100,
            'category': self.category_expense.id,
            'note': 'New note'
        })

        self.assertEqual(response.status_code, http.FOUND)
        self.assertTrue(response.url.endswith(self.inbox_url))

        entry = CashEntry.objects.get(id=self.cash_entry.id)
        self.assertEqual(entry.price, 100)
        self.assertEqual(entry.note, 'New note')
