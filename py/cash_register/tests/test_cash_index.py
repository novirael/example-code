#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib as http

from datetime import date as Date, timedelta
from django.contrib.auth.models import User, Permission, Group
from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from cash_register.models import DailyCashSet, CashEntry
from business.models import Branch


class CashRegisterIndexTestCase(TestCase):
    """
    Test Case for index view for cash register app
    """

    def setUp(self):
        self.branch = mommy.make(Branch)
        self.example_date = Date(2015, 12, 25)
        params = dict(
            branch_id=self.branch.id,
            year=self.example_date.year,
            month=self.example_date.month,
            day=self.example_date.day,
        )

        self.index_url = reverse('cash_register:index', kwargs=params)

    def _login_as_user(self, with_permissions=True, auth_branch=True,
                       is_superuser=False):
        user = User.objects.create_user(
            'test_user', '', 'password'
        )
        if with_permissions:
            permission, __ = Permission.objects.get_or_create(
                codename='view_cashregister'
            )
            user.user_permissions.add(permission)

        if auth_branch:
            # Ensure user has auth branch
            user.branches.add(self.branch)

        if is_superuser:
            user.is_superuser = True
            user.save(update_fields=["is_superuser"])

        self.client.login(
            username=user.username,
            password='password'
        )

    def test_index_page_invisible_for_anonymous(self):
        """
        Check if anonymous user are redirected to login page
        """
        expected_path = '/login/?next={}'.format(self.index_url)
        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, http.FOUND)
        self.assertTrue(response.url.endswith(expected_path))

    def test_index_page_not_available_for_users_without_permission(self):
        """
        Check if users without proper permission can't see the content
        """
        self._login_as_user(with_permissions=False)
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_index_page_invisible_for_users_without_branch_auth(self):
        """
        Check if users without proper permission can't see the content
        """
        self._login_as_user(auth_branch=False)
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_index_page_available_for_users_with_permission(self):
        """
        Check if users with proper permission can see the content
        """
        self._login_as_user()
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, http.OK)

        self.assertEqual(response.context_data['branch'], self.branch)
        self.assertEqual(response.context_data['date'], self.example_date)

        self.assertEqual(response.context_data['today'], Date.today())
        self.assertIsNone(response.context_data['latest_cash_set'])
        self.assertFalse(response.context_data['show_message'])
        self.assertIsNone(response.context_data.get('entries'))
        self.assertIsNone(response.context_data.get('daily_cash_set'))

    def test_index_page_with_initial_data(self):
        """
        Index page should contain cash set and entries for given branch
        """
        cash_set = mommy.make(
            DailyCashSet,
            date=self.example_date,
            branch=self.branch
        )
        cash_entry = mommy.make(CashEntry, set=cash_set)

        self._login_as_user()
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, http.OK)

        self.assertEqual(response.context_data['daily_cash_set'], cash_set)
        entries = response.context_data['entries']
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], cash_entry)

    def test_index_page_user_cant_see_deleted_entries(self):
        """
        Index page shouldn't contain deleted cash entries
        """
        cash_set = mommy.make(
            DailyCashSet,
            date=self.example_date,
            branch=self.branch
        )
        mommy.make(CashEntry, set=cash_set)
        mommy.make(CashEntry, set=cash_set, is_deleted=True, _quantity=2)

        self._login_as_user()
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, http.OK)

        entries = response.context_data['entries']
        self.assertEqual(len(entries), 1)

    def test_index_page_superuser_can_see_deleted_entries(self):
        """
        Index page should contain deleted cash entries when superuser
        """
        cash_set = mommy.make(
            DailyCashSet,
            date=self.example_date,
            branch=self.branch
        )
        mommy.make(CashEntry, set=cash_set)
        mommy.make(CashEntry, set=cash_set, is_deleted=True, _quantity=2)
        mommy.make(CashEntry, is_deleted=True)

        self._login_as_user(is_superuser=True)
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, http.OK)

        entries = response.context_data['entries']
        self.assertEqual(len(entries), 3)

    def test_index_page_show_message_when_last_set_not_locked(self):
        """
        Info message should be visible on index page where previous
        cash set hasn't been locked yet
        """
        mommy.make(
            DailyCashSet,
            date=self.example_date,
            branch=self.branch
        )
        mommy.make(
            DailyCashSet,
            date=self.example_date - timedelta(days=1),
            branch=self.branch,
            is_locked=False
        )

        self._login_as_user()
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, http.OK)
        self.assertTrue(response.context_data['show_message'])

    def test_index_page_not_found_non_parsing_date(self):
        """
        Should return not found when gets wrong date from kwargs
        """
        self._login_as_user()
        params = dict(
            branch_id=self.branch.id,
            year=2015,
            month=2,
            day=30,
        )
        bad_index_url = reverse('cash_register:index', kwargs=params)
        response = self.client.get(bad_index_url)
        self.assertEqual(response.status_code, http.NOT_FOUND)
