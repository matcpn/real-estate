# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from housing import models

# Register your models here.
admin.site.register(models.Lot)
admin.site.register(models.House)
admin.site.register(models.Kitchen)
admin.site.register(models.Bathroom)
admin.site.register(models.Bedroom)
admin.site.register(models.Garage)
admin.site.register(models.DiningRoom)
admin.site.register(models.LivingRoom)
admin.site.register(models.PricePerSquareFootUpgrade)
admin.site.register(models.FlatPriceUpgrade)
admin.site.register(models.UserChoice)
admin.site.register(models.UserRoomUpgradeMapping)
admin.site.register(models.Room)
admin.site.register(models.UpgradeType)
admin.site.register(models.Subdivision)