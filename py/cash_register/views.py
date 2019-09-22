#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date

from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404

from bmsutils.queryset import auth_branches
from bmsutils.views import (
    ThemedTemplateView,
    ThemedFormView,
    ThemedDeleteView,
    ThemedUpdateView,
)

from cash_register.forms import (
    CashEntryUpdateForm,
    IncomeForm,
    ExpenseForm,
)
from cash_register.models import CashEntry, DailyCashSet
from business.models import Branch
from invoices.models import Invoice


class CashRegisterHome(ThemedTemplateView):
    permission_required = 'cash_register.view_cashregister'
    template_name = 'cash_register/home.html'

    def get_context_data(self, **kwargs):
        context = super(CashRegisterHome, self).get_context_data(**kwargs)
        context['branches'] = auth_branches(self.request.user)
        context['today'] = date.today()
        return context


class CashRegisterMixin(object):
    invoice = None
    branch = None
    date = None
    daily_cash_set = None
    latest_cs = None
    earliest_cs = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return self.render_redirect_to_login(request)

        self.branch = get_object_or_404(
            Branch,
            id=int(kwargs.get('branch_id', 0))
        )

        invoice_id = kwargs.get('invoice_id')
        if invoice_id:
            self.invoice = get_object_or_404(
                Invoice,
                id=int(invoice_id)
            )

        if self.branch not in auth_branches(self.request.user):
            return HttpResponseForbidden()

        try:
            self.date = date(
                int(kwargs.get('year', 0)),
                int(kwargs.get('month', 0)),
                int(kwargs.get('day', 0))
            )
        except ValueError:
            raise Http404

        try:
            self.daily_cash_set = (
                DailyCashSet.objects.prefetch_related('entries').get(
                    branch=self.branch,
                    date=self.date
                )
            )
        except DailyCashSet.DoesNotExist:
            self.daily_cash_set = None

        self.latest_cs = (
            DailyCashSet.objects.filter(branch=self.branch).last()
        )
        self.earliest_cs = (
            DailyCashSet.objects.filter(branch=self.branch).first()
        )

        return super(CashRegisterMixin, self).dispatch(
            request, *args, **kwargs
        )

    def get_context_data(self, **kwargs):
        context = super(CashRegisterMixin, self).get_context_data(**kwargs)
        context['date'] = self.date
        context['branch'] = self.branch
        return context

    def get_redirect_url(self, *args, **kwargs):
        return reverse('cash_register:index', kwargs={
            "branch_id": self.branch.id,
            "year": self.date.year,
            "month": self.date.month,
            "day": self.date.day
        })

    def get_success_url(self):
        return self.get_redirect_url()


class CashRegisterSecureMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if self.daily_cash_set and self.daily_cash_set.is_locked:
            return HttpResponseForbidden()
        if self.earliest_cs and self.latest_cs:
            if self.date < self.earliest_cs.date:
                return HttpResponseForbidden()
            if self.date > self.latest_cs.date and not self.latest_cs.is_locked:
                return HttpResponseForbidden()
            if self.date < self.latest_cs.date and not self.daily_cash_set:
                return HttpResponseForbidden()

        return super(CashRegisterSecureMixin, self).dispatch(
            request, *args, **kwargs
        )


class CashRegisterIndex(CashRegisterMixin, ThemedTemplateView):
    permission_required = 'cash_register.view_cashregister'
    template_name = 'cash_register/index.html'

    def get_context_data(self, **kwargs):
        context = super(CashRegisterIndex, self).get_context_data(**kwargs)
        context['today'] = date.today()
        context['latest_cash_set'] = self.latest_cs

        context['show_message'] = (
            self.latest_cs is not None and
            self.date > self.latest_cs.date and
            not self.latest_cs.is_locked
        )

        if self.daily_cash_set is None:
            return context

        if self.request.user.is_superuser:
            obj = CashEntry.all_objects
        else:
            obj = CashEntry.objects

        context['entries'] = obj\
            .select_related('category', 'created_by')\
            .filter(set=self.daily_cash_set)
        context['daily_cash_set'] = self.daily_cash_set

        return context


class CashRegisterFormView(CashRegisterMixin, CashRegisterSecureMixin,
                           ThemedFormView):
    permission_required = 'cash_register.create_cashentry'
    template_name = 'cash_register/form.html'

    def get_form_kwargs(self):
        kwargs = super(CashRegisterFormView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super(CashRegisterFormView, self).get_initial()
        initial['created_by'] = self.request.user.id
        return initial

    def form_valid(self, form):
        cash_entry = form.save(commit=False)
        cash_set, __ = DailyCashSet.objects.get_or_create(
            branch=self.branch,
            date=self.date
        )
        cash_set.update(cash_entry)
        return super(CashRegisterFormView, self).form_valid(form)


class CashRegisterIncome(CashRegisterFormView):
    form_class = IncomeForm
    initial = {'statement': 'income'}

    def get_initial(self):
        initial = super(CashRegisterIncome, self).get_initial()

        if self.invoice:
            initial['price'] = self.invoice.total_value
            initial['document_refer'] = self.invoice.unique_number
            initial['person_refer'] = self.invoice.customer_details
            initial['confirmation'] = True

        return initial


class CashRegisterExpense(CashRegisterFormView):
    form_class = ExpenseForm
    initial = {'statement': 'expense'}


class CashEntryUpdate(CashRegisterMixin, CashRegisterSecureMixin, ThemedUpdateView):
    permission_required = 'cash_register.update_cashentry'
    form_class = CashEntryUpdateForm
    template_name = 'cash_register/form.html'
    cash_entry = None
    initial_price = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return self.render_redirect_to_login(request)

        self.cash_entry = get_object_or_404(
            CashEntry,
            id=kwargs.get('id', 0)
        )
        self.initial_price = self.cash_entry.price

        is_creator = self.cash_entry.created_by == request.user
        if not is_creator and not request.user.is_superuser:
            raise Http404

        return super(CashEntryUpdate, self).dispatch(
            request, *args, **kwargs
        )

    def get_object(self, queryset=None):
        return self.cash_entry

    def get_form_kwargs(self):
        kwargs = super(CashEntryUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        update_fields = ['price', 'person_refer', 'document_refer', 'note']

        cash_entry = form.save(commit=False)
        cash_entry.save(update_fields=update_fields)

        if self.cash_entry.price != self.initial_price:
            cash_entry.set.balance -= self.initial_price
            cash_entry.set.balance += cash_entry.price
            cash_entry.set.save(update_fields=['balance'])

        return HttpResponseRedirect(self.get_success_url())


class CashEntryDelete(CashRegisterMixin, CashRegisterSecureMixin, ThemedDeleteView):
    permission_required = 'cash_register.delete_cashentry'
    model = CashEntry


class DailyCashSetLock(CashRegisterMixin, CashRegisterSecureMixin, ThemedDeleteView):
    permission_required = 'cash_register.view_cashregister'
    model = DailyCashSet

    def get(self, request, *args, **kwargs):
        self.obj.lock()
        url = self.get_redirect_url(request, *args, **kwargs)
        return HttpResponseRedirect(url)
