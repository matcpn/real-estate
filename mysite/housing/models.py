# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Subdivision(models.Model):
	name = models.CharField(
		help_text='name of the subdivision',
		max_length=100
	)
	image = models.ImageField(default='media/no-img.png')
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
	subdivision = models.ForeignKey(Subdivision, default=None, null=True)
	def __unicode__(self):
		return self.name

class Kitchen(models.Model):
	name = models.CharField(
		help_text='name of the kitchen',
		max_length=100
	)
	image = models.ImageField(default='media/no-img.png')
	sqft = models.IntegerField()
	house = models.ForeignKey(House, default=None, null=True)
	def __unicode__(self):
		return self.name

class Bathroom(models.Model):
	name = models.CharField(
		help_text='name of the kitchen',
		max_length=100
	)
	sqft = models.IntegerField()
	image = models.ImageField(default='media/no-img.png')
	house = models.ForeignKey(House, default=None, null=True)
	def __unicode__(self):
		return self.name

class Material(models.Model):
	name = models.CharField(
		help_text='name of the material',
		max_length=100
	)
	ppsf = models.FloatField(
		help_text='price per square foot',
		)
	image = models.ImageField(default='media/no-img.png')
	def __unicode__(self):
		return self.name
# Create your models here.
