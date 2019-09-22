#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from bmsutils.forms import UserFullnameChoiceField, ThemedModelForm

from cash_register.models import CashEntry, Category


class CashRegisterForm(ThemedModelForm):
    disabled_fields = ['branch', 'statement']
    auth_users = 'created_by'

    created_by = UserFullnameChoiceField(
        label=_(u'Osoba rejestrująca'),
        queryset=User.objects.none()
    )

    def clean_price(self):
        price = self.cleaned_data['price']
        statement = self.cleaned_data.get('statement')

        is_expense = statement == 'expense' or self.instance.is_expense
        is_income = statement == 'income' or self.instance.is_income

        if is_expense and float(price) >= 0:
            raise forms.ValidationError(
                _(u'Wypłata musi być kwotą ujemną.')
            )
        elif is_income and float(price) <= 0:
            raise forms.ValidationError(
                _(u'Wpłata musi być kwotą dodatnią.')
            )
        return price

    class Meta:
        model = CashEntry
        fields = [
            'created_by',
            'statement',
            'category',
            'price',
            'person_refer',
            'document_refer',
            'note',
            'confirmation',
        ]
        labels = {
            'statement': _(u'Operacja'),
            'category': _(u'Kategoria'),
            'price': _(u'Kwota'),
            'person_refer': _(u'Dotyczy osoby'),
            'document_refer': _(u'Dotyczy dokumentu'),
            'note': _(u'Inne informacje'),
            'confirmation': _(u'Czy wystawić potwierdzenie KP/KW'),
        }
        widgets = {
            'note': forms.Textarea(attrs={
                'rows': 2,
            }),
        }


class IncomeForm(CashRegisterForm):
    def __init__(self, *arg, **kwargs):
        super(IncomeForm, self).__init__(*arg, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(
            statement='income'
        )


class ExpenseForm(CashRegisterForm):
    def __init__(self, *arg, **kwargs):
        super(ExpenseForm, self).__init__(*arg, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(
            statement='expense'
        )


class CashEntryUpdateForm(CashRegisterForm):
    disabled_fields = [
        'statement',
        'category',
        'created_by',
        'confirmation'
    ]
