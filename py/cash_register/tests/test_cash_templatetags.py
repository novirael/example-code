from datetime import datetime

from unittest import TestCase

from cash_register.templatetags.cashfilters import to_previous, to_next


class CashRegisterTemplatetagsTestCase(TestCase):
    """
    Test Case for cash register template tags
    """

    def test_to_previous_uppercase(self):
        date = datetime(2015, 12, 25)
        self.assertEqual(to_previous(date, 'Y'), 2015)
        self.assertEqual(to_previous(date, 'M'), 12)
        self.assertEqual(to_previous(date, 'D'), 24)

        date = datetime(2015, 3, 1)
        self.assertEqual(to_previous(date, 'Y'), 2015)
        self.assertEqual(to_previous(date, 'M'), 2)
        self.assertEqual(to_previous(date, 'D'), 28)

        date = datetime(2015, 1, 1)
        self.assertEqual(to_previous(date, 'Y'), 2014)
        self.assertEqual(to_previous(date, 'M'), 12)
        self.assertEqual(to_previous(date, 'D'), 31)

    def test_to_previous_lowercase(self):
        date = datetime(2015, 12, 25)
        self.assertEqual(to_previous(date, 'y'), 2015)
        self.assertEqual(to_previous(date, 'm'), 12)
        self.assertEqual(to_previous(date, 'd'), 24)

        date = datetime(2015, 3, 1)
        self.assertEqual(to_previous(date, 'y'), 2015)
        self.assertEqual(to_previous(date, 'm'), 2)
        self.assertEqual(to_previous(date, 'd'), 28)

        date = datetime(2015, 1, 1)
        self.assertEqual(to_previous(date, 'y'), 2014)
        self.assertEqual(to_previous(date, 'm'), 12)
        self.assertEqual(to_previous(date, 'd'), 31)

    def test_to_previous_invalid(self):
        date = datetime(2015, 12, 25)
        self.assertEqual(to_previous(date, 'should-not-match'), None)

    def test_to_next_uppercase(self):
        date = datetime(2015, 12, 25)
        self.assertEqual(to_next(date, 'Y'), 2015)
        self.assertEqual(to_next(date, 'M'), 12)
        self.assertEqual(to_next(date, 'D'), 26)

        date = datetime(2015, 2, 28)
        self.assertEqual(to_next(date, 'Y'), 2015)
        self.assertEqual(to_next(date, 'M'), 3)
        self.assertEqual(to_next(date, 'D'), 1)

        date = datetime(2015, 12, 31)
        self.assertEqual(to_next(date, 'Y'), 2016)
        self.assertEqual(to_next(date, 'M'), 1)
        self.assertEqual(to_next(date, 'D'), 1)

    def test_to_next_lowercase(self):
        date = datetime(2015, 12, 25)
        self.assertEqual(to_next(date, 'y'), 2015)
        self.assertEqual(to_next(date, 'm'), 12)
        self.assertEqual(to_next(date, 'd'), 26)

        date = datetime(2015, 2, 28)
        self.assertEqual(to_next(date, 'y'), 2015)
        self.assertEqual(to_next(date, 'm'), 3)
        self.assertEqual(to_next(date, 'd'), 1)

        date = datetime(2015, 12, 31)
        self.assertEqual(to_next(date, 'y'), 2016)
        self.assertEqual(to_next(date, 'm'), 1)
        self.assertEqual(to_next(date, 'd'), 1)

    def test_to_next_invalid(self):
        date = datetime(2015, 12, 25)
        self.assertEqual(to_next(date, 'should-not-match'), None)
