#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib as http

from django.contrib.auth.models import User, Permission, Group
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy

from cash_register.models import CashEntry, DailyCashSet


class CashRegisterActionsTestCase(TestCase):
    """
    Test Case for actions for cash register app
    """

    def setUp(self):
        self.cash_set = mommy.make(DailyCashSet)
        self.cash_entry = mommy.make(
            CashEntry,
            set=self.cash_set
        )

        params = dict(
            branch_id=self.cash_set.branch.id,
            year=self.cash_set.date.year,
            month=self.cash_set.date.month,
            day=self.cash_set.date.day,
        )

        self.index_url = reverse(
            'cash_register:index', kwargs=params
        )

        params['id'] = self.cash_entry.id
        self.delete_url = reverse('cash_register:delete', kwargs=params)

        params['id'] = self.cash_set.id
        self.lock_url = reverse('cash_register:lock', kwargs=params)

    def _login_as_user(self, permission=None, auth_branch=True):
        user = User.objects.create_user(
            'test_user', '', 'password'
        )
        if permission:
            perm, __ = Permission.objects.get_or_create(
                codename=permission
            )
            user.user_permissions.add(perm)

        if auth_branch:
            # Ensure user has auth branch
            user.branches.add(self.cash_set.branch)

        self.client.login(
            username=user.username,
            password='password'
        )

    def test_delete_action_impossible_for_anonymous(self):
        """
        Check if anonymous user are redirected to login page
        """
        expected_path = '/login/?next={}'.format(self.delete_url)
        response = self.client.get(self.delete_url)

        self.assertEqual(response.status_code, http.FOUND)
        self.assertTrue(response.url.endswith(expected_path))

    def test_delete_action_impossible_for_users_without_permission(self):
        """
        Check if users without proper permission can't see the content
        """
        self._login_as_user()
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_delete_action_impossible_for_users_without_branch_auth(self):
        """
        Check if users without proper permission can't see the content
        """
        self._login_as_user('delete_cashentry', False)
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_delete_action_possible_for_users_with_permission(self):
        """
        Check if users with proper permission can see the content
        """
        self._login_as_user('delete_cashentry')
        response = self.client.get(self.delete_url)

        self.assertFalse(self.cash_entry.is_deleted)
        self.assertEqual(response.status_code, http.FOUND)
        self.assertTrue(response.url.endswith(self.index_url))
        self.assertFalse(CashEntry.objects.filter(id=self.cash_entry.id).exists())
        self.assertTrue(CashEntry.all_objects.get(id=self.cash_entry.id).is_deleted)

    def test_lock_action_impossible_for_anonymous(self):
        """
        Check if anonymous user are redirected to login page
        """
        expected_path = '/login/?next={}'.format(self.lock_url)
        response = self.client.get(self.lock_url)

        self.assertEqual(response.status_code, http.FOUND)
        self.assertTrue(response.url.endswith(expected_path))

    def test_lock_action_impossible_for_users_without_permission(self):
        """
        Check if users without proper permission can't see the content
        """
        self._login_as_user()
        response = self.client.get(self.lock_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_lock_action_impossible_for_users_without_branch_auth(self):
        """
        Check if users without proper permission can't see the content
        """
        self._login_as_user('view_cashregister', False)
        response = self.client.get(self.lock_url)
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_lock_action_possible_for_users_with_permission(self):
        """
        Check if users with proper permission can see the content
        """
        self._login_as_user('view_cashregister')
        response = self.client.get(self.lock_url)

        self.assertFalse(self.cash_set.is_locked)
        self.assertEqual(response.status_code, http.FOUND)
        self.assertTrue(response.url.endswith(self.index_url))
        self.assertTrue(DailyCashSet.objects.get(id=self.cash_set.id).is_locked)
