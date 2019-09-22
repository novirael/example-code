# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import serializers

from business.models import Contractor
from invoices.models import Invoice, InvoiceItem, Category
from orders.rest.serializers import OrderSimpleSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'shortname')


class InvoiceListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='sale_api:invoice-detail')
    order = OrderSimpleSerializer()

    class Meta:
        model = Invoice
        fields = (
            'url', 'id', 'unique_number', 'date', 'customer_details',
            'total_value', 'status', 'is_done', 'payment_methods', 'order',
        )

class InvoiceItemSerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField()

    def get_item(self, obj):
        return obj.item or obj.name

    class Meta:
        model = InvoiceItem
        fields = (
            'id',
            'item',
            'measure',
            'pkwiu',
            'quantity',
            'single_price',
            'value_vat',
            'vat',
        )

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    date = serializers.DateField(format="%d.%m.%Y")
    date_of_sale = serializers.DateField(format="%d.%m.%Y")
    customerId = serializers.PrimaryKeyRelatedField(
        queryset=Contractor.objects.all(),
        source='customer',
    )
    receiverId = serializers.PrimaryKeyRelatedField(
        queryset=Contractor.objects.all(),
        source='receiver',
    )

    class Meta:
        model = Invoice
        fields = (
            'id',
            'unique_number',
            'advance_payment',
            'branch',
            'category',
            'date',
            'date_of_sale',
            'is_fully_paid_in_advance',
            'items',
            'note',
            'payment_maturnity',
            'payment_methods',
            'who',
            'customerId',
            'receiverId',
            'authorized_to_receive',
        )
