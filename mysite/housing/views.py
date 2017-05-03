# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, render_to_response, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from models import Subdivision, House, Kitchen, Bathroom, Material

# Create your views here.
def index(request):
	subdivisions = Subdivision.objects.all()
	context = {'subdivisions': subdivisions}
	return render(request, 'index.html', context)

def subdivision(request):
	request.session['subdivision'] = request.POST['subdivision_id']
	return HttpResponseRedirect(reverse('housing:house', args=()))

def house(request):
	houses = House.objects.filter(subdivision=request.session['subdivision'])
	context = {'houses': houses}
	request.session['bathroom_material_id'] = -1
	request.session['kitchen_material_id'] = -1
	return render(request, 'houses.html', context)

def features(request, context):
	request.session['total_price'] = calcTotalPrice(request)
	return render(request, 'features.html', context)

def select_feature(request):
	feature = request.POST['feature']
	context = {
		'materials' : Material.objects.all()
	}
	if feature == 'kitchen':
		return render(request, 'kitchen.html', context)
	if feature == 'bathroom':
		return render(request, 'bathroom.html', context)

def select_kitchen_material(request):
	request.session['kitchen_material_id'] = request.POST['material_id']
	context = {
		'kitchens' : Kitchen.objects.filter(pk=request.session['kitchen']), 
		'bathrooms' : Bathroom.objects.filter(pk=request.session['bathroom'])
		}
	return features(request, context)

def select_bathroom_material(request):
	request.session['bathroom_material_id'] = request.POST['material_id']
	context = {
		'kitchens' : Kitchen.objects.filter(pk=request.session['kitchen']), 
		'bathrooms' : Bathroom.objects.filter(pk=request.session['bathroom'])
		}
	return features(request, context)

def calcTotalPrice(request):
	if request.session['bathroom_material_id'] != -1:
		bathroom_material_price = Material.objects.filter(id=request.session['bathroom_material_id']).values('ppsf')[0].get('ppsf')
		bathroom_square_ft = Bathroom.objects.filter(pk=request.session['bathroom']).values('sqft')[0].get('sqft')
		bathroom_total_price = bathroom_material_price * bathroom_square_ft
	else:
		bathroom_total_price = 0
	if request.session['kitchen_material_id'] != -1:
		kitchen_material_price = Material.objects.filter(id=request.session['kitchen_material_id']).values('ppsf')[0].get('ppsf')
		kitchen_square_ft = Kitchen.objects.filter(pk=request.session['kitchen']).values('sqft')[0].get('sqft')
		kitchen_total_price = kitchen_material_price * kitchen_square_ft
	else:
		kitchen_total_price = 0
	return request.session['house_price'] + bathroom_total_price + kitchen_total_price

def select_house(request):
	request.session['house'] = request.POST['house_id']
	request.session['house_price'] = House.objects.filter(id=request.session['house']).values('price')[0].get('price')
	request.session['kitchen'] = House.objects.filter(id=request.session['house']).values('kitchen')[0].get('kitchen')
	request.session['bathroom'] = House.objects.filter(id=request.session['house']).values('bathroom')[0].get('bathroom')
	context = {
		'kitchens' : Kitchen.objects.filter(pk=request.session['kitchen']), 
		'bathrooms' : Bathroom.objects.filter(pk=request.session['bathroom'])
		}
	return features(request, context)