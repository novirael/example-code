# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import django_filters
from rest_framework.filters import FilterSet

from invoices.models import Invoice


class InvoiceFilter(FilterSet):
    branch = django_filters.CharFilter(name='branch__shortname')
    category = django_filters.CharFilter(name='category__shortname')
    is_paid = django_filters.Filter(method='filter_paid')
    is_draft = django_filters.Filter(method='filter_drafts')

    class Meta:
        model = Invoice
        fields = ['branch', 'category', 'payment_methods', "is_paid"]

    @staticmethod
    def filter_paid(queryset, name, value):
        if value in (True, 'True', 'true', '1'):
            return queryset.exclude(paid__exact="")
        elif value in (False, 'False', 'false', '0'):
            return queryset.filter(paid__exact="")

    @staticmethod
    def filter_drafts(queryset, name, value):
        if value in (False, 'False', 'false', '0'):
            return queryset.filter(
                no__isnull=False
            )
        return queryset
