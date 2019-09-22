#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from cash_register.models import CashEntry, Category, DailyCashSet


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'statement', 'is_deleted')


class CashEntryAdmin(admin.ModelAdmin):
    readonly_fields = ('price', 'set', 'statement')
    list_display = ('created_date', 'created_by')

    def get_queryset(self, request):
        return CashEntry.all_objects.all()


class CashEntryInline(admin.StackedInline):
    model = CashEntry
    extra = 1
    readonly_fields = ('confirmation_id',)


class DailyCashSetAdmin(admin.ModelAdmin):
    list_display = ('date', 'branch', 'balance', 'is_locked')
    list_filter = ("branch__name",)
    inlines = [CashEntryInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(CashEntry, CashEntryAdmin)
admin.site.register(DailyCashSet, DailyCashSetAdmin)
