# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class UpgradeType(models.Model):
	name = models.CharField(
		help_text="Type of the upgrade. This is to ensure that two upgrades for the same room of the same type cannot be chosen.",
		max_length=100,
		)
	def __unicode__(self):
		return self.name

class PricePerSquareFootUpgrade(models.Model):
	name = models.CharField(
		help_text='name of the material',
		max_length=100
	)
	ppsf = models.FloatField(
		help_text='price per square foot',
		)
	image = models.ImageField(default='media/no-img.png')
	upgrade_type = models.ForeignKey(UpgradeType,
		help_text="Type of the upgrade. This is to ensure that two upgrades for the same room of the same type cannot be chosen.",
		blank=True,
		default=None,
		null=True
		)
	def __unicode__(self):
		return self.name

class FlatPriceUpgrade(models.Model):
	name = models.CharField(
		help_text='name of the upgrade',
		max_length=100
	)
	price = models.FloatField(
		help_text='price of upgrade',
		)
	image = models.ImageField(default='media/no-img.png')
	upgrade_type = models.ForeignKey(UpgradeType,
		help_text="Type of the upgrade. This is to ensure that two upgrades for the same room of the same type cannot be chosen.",
		blank=True,
		default=None,
		null=True
		)
	def __unicode__(self):
		return self.name

class Room(models.Model):
	roomname =  models.CharField(
		help_text='name of the room',
		max_length=100
	)
	image = models.ImageField(default='media/no-img.png')
	sqft = models.IntegerField()
	ppsf_upgrades = models.ManyToManyField(PricePerSquareFootUpgrade, blank=True, help_text='choose potential upgrades you would like to be made available for this room',)
	flat_price_upgrades = models.ManyToManyField(FlatPriceUpgrade, blank=True, help_text='choose potential upgrades you would like to be made available for this room',)
	def __unicode__(self):
		return self.roomname

class Lot(models.Model):
	name = models.CharField(
		help_text='name of the lot',
		max_length=100
	)
	image = models.ImageField(default='media/no-img.png')
	price = models.IntegerField()
	status_choices = (
		('a', 'available'),
		('p', 'pending'),
		('s', 'sold'),
	)
	status = models.CharField(max_length=1, choices=status_choices,default='a')
	coords = models.CharField(max_length=100, default='0,0,0,0', help_text='use this website to generate these numbers: http://imagemap-generator.dariodomi.de/')
	shape = models.CharField(max_length=15, default='poly', help_text='use this website to generate this shape: http://imagemap-generator.dariodomi.de/')
	@property
	def highlight(self):
		if self.status == 'a':
			return '3fc653'
		if self.status == 'p':
			return 'e59e35'
		else:
			return 'd62831'
	@property
	def fillColor(self):
		if self.status == 'a':
			return 'b2ed93'
		if self.status == 'p':
			return 'ede893'
		else:
			return 'ef6b72'

	def __unicode__(self):
		return self.name

class Subdivision(models.Model):
	name = models.CharField(
		help_text='name of the subdivision',
		max_length=100
	)
	image = models.ImageField(default='media/no-img.png')
	lots = models.ManyToManyField(Lot, blank=True)
	def __unicode__(self):
		return self.name

class LivingRoom(Room):
	name = models.CharField(
		help_text='name of the living room',
		max_length=100
	)
	def __unicode__(self):
		return self.name

class DiningRoom(Room):
	name = models.CharField(
		help_text='name of the dining room',
		max_length=100
	)
	def __unicode__(self):
		return self.name

class Garage(Room):
	name = models.CharField(
		help_text='name of the garage',
		max_length=100
	)
	def __unicode__(self):
		return self.name

class Bedroom(Room):
	name = models.CharField(
		help_text='name of the bedroom',
		max_length=100
	)
	def __unicode__(self):
		return self.name

class Kitchen(Room):
	name = models.CharField(
		help_text='name of the kitchen',
		max_length=100
	)
	def __unicode__(self):
		return self.name

class Bathroom(Room):
	name = models.CharField(
		help_text='name of the bathroom',
		max_length=100
	)
	def __unicode__(self):
		return self.name

class House(models.Model):
	name = models.CharField(
		help_text='name of the house',
		max_length=100
	)
	sqft = models.IntegerField()
	price = models.FloatField()
	image = models.ImageField(default='media/no-img.png')
	kitchen = models.ManyToManyField(Kitchen, blank=True)
	livingRoom = models.ManyToManyField(LivingRoom, blank=True)
	diningRoom = models.ManyToManyField(DiningRoom, blank=True)
	garage = models.ManyToManyField(Garage, blank=True)
	bathroom = models.ManyToManyField(Bathroom, blank=True)
	bedroom = models.ManyToManyField(Bedroom, blank=True)
	lot = models.ForeignKey(Lot, default=None, null=True)
	def __unicode__(self):
		return self.name

class UserRoomUpgradeMapping(models.Model):
	user = models.ForeignKey('UserChoice')
	room = models.ForeignKey(Room)
	roomname = models.CharField(
		help_text='name of the room being upgraded',
		max_length=100,
		default=None,
		blank=True,
		null=True
		)
	ppsf_upgrade = models.ForeignKey(PricePerSquareFootUpgrade, blank=True, default=None, null=True)
	flat_price_upgrade = models.ForeignKey(FlatPriceUpgrade, blank=True, default=None, null=True)
	upgrade_type = models.ForeignKey(UpgradeType,
		help_text="Type of the upgrade. This is to ensure that two upgrades for the same room of the same type cannot be chosen.",
		blank=True,
		default=None,
		null=True
		)
	def __unicode__(self):
		if self.ppsf_upgrade is None:
			return self.roomname + ' upgrade: ' + self.flat_price_upgrade.name
		else:
			return self.roomname + ' upgrade: ' + self.ppsf_upgrade.name

class UserChoice(models.Model):
	user = models.ForeignKey(User)
	house = models.ForeignKey(House, null=True)
	lot = models.ForeignKey(Lot)
	room_upgrades = models.ManyToManyField(UserRoomUpgradeMapping)

	def __unicode__(self):
		return self.user.first_name + ' ' + self.user.last_name

	def getTotalCost(self):
		cost = self.lot.price
		for room_upgrade in UserRoomUpgradeMapping.objects.filter(user=self):
			if room_upgrade.ppsf_upgrade is not None:
				print(room_upgrade.room.sqft * room_upgrade.ppsf_upgrade.ppsf)
				cost += (room_upgrade.room.sqft * room_upgrade.ppsf_upgrade.ppsf)
			else:
				cost += room_upgrade.flat_price_upgrade.price

		cost += self.house.price

		return cost	