#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import template
from datetime import timedelta


register = template.Library()


@register.filter(name='previous')
def to_previous(value, prev):
    previous_date = value - timedelta(1)
    if prev == 'Y' or prev == 'y':
        return previous_date.year
    elif prev == 'M' or prev == 'm':
        return previous_date.month
    elif prev == 'D' or prev == 'd':
        return previous_date.day


@register.filter(name='next')
def to_next(value, next):
    next_date = value + timedelta(1)
    if next == 'Y' or next == 'y':
        return next_date.year
    elif next == 'M' or next == 'm':
        return next_date.month
    elif next == 'D' or next == 'd':
        return next_date.day
