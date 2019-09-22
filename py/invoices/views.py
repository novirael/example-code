# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from invoices.models import Invoice, Category
from invoices.rest.filters import InvoiceFilter
from invoices.rest.serializers import (
    CategorySerializer,
    InvoiceListSerializer,
    InvoiceSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows sale categories to be seen.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows invoices to be viewed.
    """
    queryset = Invoice.objects.select_related('branch', 'category')
    serializer_class = InvoiceSerializer
    list_serializer_class = InvoiceListSerializer
    search_fields = ('customer_name', 'customer_address')
    filter_class = InvoiceFilter

    def get_queryset(self):
        """
        Invoices are filtered by branches which user has access to and
        not null no attribute (order drafts)
        """
        queryset = super(InvoiceViewSet, self).get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(branch__in=self.request.user.branches.all())
