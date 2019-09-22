# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import routers

from cash_register.rest.views import CashCategoryViewSet, CashEntryViewSet

router = routers.DefaultRouter()
router.register(r'entries', CashEntryViewSet, base_name='entry')
router.register(r'categories', CashCategoryViewSet, base_name='category')

urlpatterns = router.urls
