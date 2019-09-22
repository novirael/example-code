# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import django_filters
from rest_framework.filters import FilterSet

from cash_register.models import CashEntry


class CashEntryFilter(FilterSet):
    year = django_filters.NumberFilter(name='set__date__year')
    month = django_filters.NumberFilter(name='set__date__month')

    class Meta:
        model = CashEntry
        fields = ['year', 'month', 'category']
