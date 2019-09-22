# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import serializers

from cash_register.models import CashEntry, Category as CashCategory


class CashEntrySerializer(serializers.ModelSerializer):
    branch = serializers.ReadOnlyField(source='set.branch.id')

    class Meta:
        model = CashEntry
        fields = (
            "branch",
            "id",
            "created_by",
            "created_date",
            "statement",
            "category",
            "price",
            "document_refer",
            "person_refer",
            "note",
            "confirmation",
            "confirmation_id",
        )


class CashCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = CashCategory
        fields = (
            "name",
            "shortname",
            "statement",
        )
