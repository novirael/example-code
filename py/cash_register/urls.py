#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from cash_register.views import (
    CashRegisterHome,
    CashRegisterIndex,
    CashRegisterIncome,
    CashRegisterExpense,
    CashEntryDelete,
    DailyCashSetLock,
    CashEntryUpdate)
from reports.cash_reports import (
    CashRegisterDailyReportPDF,
    CashRegisterConfirmationPDF,
)


urlpatterns = [
    url(r'^$', CashRegisterHome.as_view(), name='home'),

    url(r'^confirmation/(?P<entry_id>\d+)/$',
        CashRegisterConfirmationPDF.as_view(), name='pdf_confirmation'
    ),
    url(r'^reports/daily/(?P<cash_set_id>\d+)/$',
        CashRegisterDailyReportPDF.as_view(), name='pdf_daily_report'
    ),
    url(r'^(?P<branch_id>\d+)/(?P<year>[0-9]{4})/(?P<month>[1-9]|1[0-2])/(?P<day>[1-9]|[1-2][0-9]|3[0-1])/$',
        CashRegisterIndex.as_view(), name='index',
    ),
    url(r'^(?P<branch_id>\d+)/(?P<year>[0-9]{4})/(?P<month>[1-9]|1[0-2])/(?P<day>[1-9]|[1-2][0-9]|3[0-1])/income/(?P<invoice_id>\d+)?$',
        CashRegisterIncome.as_view(), name='income',
    ),
    url(r'^(?P<branch_id>\d+)/(?P<year>[0-9]{4})/(?P<month>[1-9]|1[0-2])/(?P<day>[1-9]|[1-2][0-9]|3[0-1])/expense/$',
        CashRegisterExpense.as_view(), name='expense'
    ),
    url(r'^(?P<branch_id>\d+)/(?P<year>[0-9]{4})/(?P<month>[1-9]|1[0-2])/(?P<day>[1-9]|[1-2][0-9]|3[0-1])/(?P<id>\d+)/update/$',
        CashEntryUpdate.as_view(), name='update'
    ),
    url(r'^(?P<branch_id>\d+)/(?P<year>[0-9]{4})/(?P<month>[1-9]|1[0-2])/(?P<day>[1-9]|[1-2][0-9]|3[0-1])/(?P<id>\d+)/delete/$',
        CashEntryDelete.as_view(), name='delete'
    ),
    url(r'^(?P<branch_id>\d+)/(?P<year>[0-9]{4})/(?P<month>[1-9]|1[0-2])/(?P<day>[1-9]|[1-2][0-9]|3[0-1])/(?P<id>\d+)/lock/$',
        DailyCashSetLock.as_view(), name='lock'
    ),
]
