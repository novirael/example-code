# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import urllib
from copy import copy

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse

from cash_register.models import Category as CashCategory, CashEntry
from cash_register.rest.filters import CashEntryFilter
from cash_register.rest.serializers import (
    CashCategorySerializer,
    CashEntrySerializer,
)


class CashCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows cash categories with extra fields to be seen.
    """
    permission_classes = (IsAdminUser,)
    serializer_class = CashCategorySerializer
    queryset = CashCategory.objects.all()

    def list(self, *args, **kwargs):
        categories = []

        for category in CashCategory.objects.all():
            prices = self._get_entries_prices(category)

            if not prices:
                continue

            categories.append({
                "id": category.id,
                "name": category.name,
                "shortname": category.shortname,
                "statement": category.statement,
                "summary_value": sum(prices),
                "entries_count": len(prices),
                "entries": self._get_entries_url(category)
            })

        return Response({
            "count": len(categories),
            "results": categories
        })

    def _get_entries_prices(self, category):
        filter_fields = {
            'year': 'set__date__year',
            'month': 'set__date__month',
            'statement': 'category__statement'
        }
        qs_filters = {
            filter_fields[key]: value
            for key, value in self.request.query_params.items()
            if key in filter_fields
        }
        return category.cashentry_set.filter(**qs_filters).values_list(
            'price', flat=True
        )

    def _get_entries_url(self, category):
        query_params = copy(self.request.query_params)
        query_params.pop('statement', None)
        query_params['category'] = category.id
        return (
            reverse('cash_register_api:entry-list', request=self.request) +
            '?%s' % urllib.urlencode(query_params)
        )


class CashEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows cash entries to be seen.
    """
    permission_classes = (IsAdminUser,)
    queryset = CashEntry.objects.select_related('set__branch', 'category', 'created_by')
    serializer_class = CashEntrySerializer
    filter_class = CashEntryFilter
