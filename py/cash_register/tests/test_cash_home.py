#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib as http

from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase


class CashRegisterHomeTestCase(TestCase):
    """
    Test Case for home view for cash register app
    """

    def _login_as_user(self, with_permissions=True):
        user = User.objects.create_user(
            'test_user', '', 'password'
        )
        if with_permissions:
            permission, __ = Permission.objects.get_or_create(
                codename='view_cashregister'
            )
            user.user_permissions.add(permission)

        self.client.login(
            username=user.username,
            password='password'
        )

    def test_home_page_invisible_for_anonymous(self):
        """
        Check if anonymous user are redirected to login page
        """
        url = reverse('cash_register:home')
        expected_path = '/login/?next={}'.format(url)
        response = self.client.get(url)

        self.assertEqual(response.status_code, http.FOUND)
        self.assertTrue(response.url.endswith(expected_path))

    def test_home_page_not_available_for_users_without_permission(self):
        """
        Check if users without proper permission can't see the content
        """
        self._login_as_user(with_permissions=False)
        response = self.client.get(reverse('cash_register:home'))
        self.assertEqual(response.status_code, http.FORBIDDEN)

    def test_home_page_available_for_users_with_permission(self):
        """
        Check if users with proper permission can see the content
        """
        self._login_as_user()
        response = self.client.get(reverse('cash_register:home'))
        self.assertEqual(response.status_code, http.OK)
