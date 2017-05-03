# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from housing import models

# Register your models here.
admin.site.register(models.Subdivision)
admin.site.register(models.House)
admin.site.register(models.Kitchen)
admin.site.register(models.Bathroom)
admin.site.register(models.Material)