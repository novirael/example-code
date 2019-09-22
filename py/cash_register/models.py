#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _
from django.conf import settings

from bmsutils.models import SoftDeleteModel
from business.models import Branch


STATEMENT = (
    ('income', _(u'Wpłata')),
    ('expense', _(u'Wypłata')),
)


class Category(SoftDeleteModel):
    name = models.CharField(max_length=64)
    shortname = models.CharField(max_length=64, unique=True)
    statement = models.CharField(max_length=8, choices=STATEMENT)

    def __unicode__(self):
        return self.name

    class Meta:
        default_permissions = ()
        verbose_name_plural = _('Categories')
        ordering = ['statement', 'name']


class DailyCashSet(models.Model):
    date = models.DateField()
    branch = models.ForeignKey(Branch)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    is_locked = models.BooleanField(default=False)

    class Meta:
        get_latest_by = 'date'
        permissions = (
            ("view_cashregister", "Can view cash register"),
            ("create_cashentry", "Can create cash entry"),
            ("update_cashentry", "Can update cash entry"),
            ("delete_cashentry", "Can delete cash entry"),
        )

    def lock(self):
        self.is_locked = True
        self.save()

    def update(self, new_entry):
        self.balance += new_entry.price
        self.save()
        new_entry.set = self
        new_entry.save()

    def save(self, *args, **kwargs):
        if self.balance is None:
            last_day = DailyCashSet.objects.filter(branch=self.branch).last()
            if last_day is not None:
                self.balance = last_day.balance
            else:
                self.balance = 0

        super(DailyCashSet, self).save(*args, **kwargs)


class CashEntry(SoftDeleteModel):
    set = models.ForeignKey(DailyCashSet, related_name='entries')
    created_by = models.ForeignKey(User)
    created_date = models.DateTimeField(editable=False, blank=True)
    statement = models.CharField(max_length=8, choices=STATEMENT)
    category = models.ForeignKey(Category)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    document_refer = models.CharField(max_length=128, blank=True)
    person_refer = models.CharField(max_length=256, blank=True)
    note = models.TextField(blank=True)
    confirmation = models.BooleanField(default=False)
    confirmation_id = models.CharField(max_length=16, blank=True)

    class Meta:
        ordering = ("created_date",)
        get_latest_by = 'created_date'
        default_permissions = ()
        verbose_name_plural = _('Cash entries')

    @property
    def is_income(self):
        return self.statement == 'income'

    @property
    def is_expense(self):
        return self.statement == 'expense'

    def _set_confirmation_id(self):
        try:
            latest = CashEntry.objects.filter(
                confirmation=True,
                statement=self.statement,
                set__branch=self.set.branch,
                created_date__year=self.created_date.year
            ).latest()
        except self.DoesNotExist:
            latest = None

        # Extract last entry number from confirmation_id
        last_number = int(latest.confirmation_id[6:]) if latest else 0

        # for eg. KP/15/0001
        self.confirmation_id = "{descriptor}/{year}/{number:04d}".format(
            descriptor='KP' if self.is_income else 'KW',
            year=self.created_date.strftime('%y'),
            number=last_number + 1
        )

    def save(self, *args, **kwargs):
        if not self.created_date:
            self.created_date = datetime.now(settings.LOCAL_TZ)
        if self.confirmation and not self.confirmation_id:
            self._set_confirmation_id()
        super(CashEntry, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.set.balance -= self.price
        self.set.save()
        super(CashEntry, self).delete(*args, **kwargs)
