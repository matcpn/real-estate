# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, render_to_response, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from models import Lot, House, Kitchen, Bathroom, PricePerSquareFootUpgrade, UserChoice, Bedroom, LivingRoom, DiningRoom, Garage, UserRoomUpgradeMapping, FlatPriceUpgrade
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def login(request):
	return render(request, 'login.html')

def logout_view(request):
	logout(request)
	return render(request, 'login.html')

def authenticate_user(request):
	if request.method == 'POST':
		# .. authenticate your user
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			auth_login(request, user)
			# redirect to the value of next if it is entered, otherwise
			# to /accounts/profile/
			return redirect(request.POST.get('next','/'))
		else:
			return render(request, 'login.html')

def create_user(request):
	if request.method == 'POST':
		# .. authenticate your user
		username = request.POST['username']
		password = request.POST['password']
		email = request.POST['email']
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		user = User.objects.create_user(username, email, password)
		user.last_name = last_name
		user.first_name = first_name
		user.save()
		if user is not None:
			auth_login(request, user)
			# redirect to the value of next if it is entered, otherwise
			# to /accounts/profile/
			return redirect(request.POST.get('next','/'))
		else:
			return render(request, 'login.html')

@login_required
def index(request):
	lots = Lot.objects.all()
	context = {'lots': lots}
	return render(request, 'index.html', context)

@login_required
def lot(request):
	lot = Lot.objects.get(pk=request.POST['lot_id'])
	user_choice = get_user_choice_for_user(request.user.username)
	user_choice.lot = lot
	user_choice.save()
	return HttpResponseRedirect(reverse('housing:house', args=()))

@login_required
def house(request):
	user_choice = get_user_choice_for_user(request.user.username)
	houses = House.objects.filter(lot=user_choice.lot)
	context = {'houses': houses}
	return render(request, 'houses.html', context)

@login_required
def features(request, context):
	request.session['total_price'] = int(calcTotalPrice(request))
	return render(request, 'features.html', context)

@login_required
def select_feature(request):
	user_choice = get_user_choice_for_user(request.user.username)
	feature = request.POST['feature']
	if 'kitchen' in feature:
		kitchen_id = feature.split(",")[1]
		context = {
			'upgrades' : user_choice.house.kitchen.get(pk=kitchen_id).ppsf_upgrades.all(),
			'flat_price_upgrades' : user_choice.house.kitchen.get(pk=kitchen_id).flat_price_upgrades.all(),
			'kitchen' : kitchen_id
		}
		return render(request, 'kitchen.html', context)
	if 'bathroom' in feature:
		bathroom_id = feature.split(",")[1]
		context = {
			'upgrades' : Bathroom.objects.get(pk=bathroom_id).ppsf_upgrades.all(),
			'flat_price_upgrades' : user_choice.house.bathroom.get(pk=bathroom_id).flat_price_upgrades.all(),
			'bathroom' : bathroom_id
		}
		return render(request, 'bathroom.html', context)

@login_required
def select_kitchen_upgrade(request):
	user_choice = get_user_choice_for_user(request.user.username)
	request_variables = request.POST['upgrade'].split(",")
	print(request_variables)
	chosen_upgrade_id = request_variables[0]
	kitchen_id = request_variables[1]
	kitchen = Kitchen.objects.get(pk=kitchen_id)
	is_ppsf_upgrade = request_variables[2]

	#create a new mapping for the new upgrade chosen
	if is_ppsf_upgrade == 'True':
		chosen_upgrade = PricePerSquareFootUpgrade.objects.get(pk=chosen_upgrade_id)
		new_mapping = UserRoomUpgradeMapping(user=user_choice, room=kitchen, ppsf_upgrade=chosen_upgrade, upgrade_type=chosen_upgrade.upgrade_type, roomname=kitchen.name)
	else:
		chosen_upgrade = FlatPriceUpgrade.objects.get(pk=chosen_upgrade_id)
		new_mapping = UserRoomUpgradeMapping(user=user_choice, room=kitchen, flat_price_upgrade=chosen_upgrade, upgrade_type=chosen_upgrade.upgrade_type, roomname=kitchen.name)
	
	#check if old upgrade already had a mapping, if so, delete it
	same_type_upgrade = UserRoomUpgradeMapping.objects.get(user=user_choice, room=kitchen, upgrade_type=chosen_upgrade.upgrade_type)
	if same_type_upgrade is not None:
		same_type_upgrade.delete()

	new_mapping.save()
	context = get_context_for_user_choice(request)
	return features(request, context)

@login_required
def select_bathroom_upgrade(request):
	user_choice = get_user_choice_for_user(request.user.username)
	request_variables = request.POST['upgrade'].split(",")
	chosen_upgrade_id = request_variables[0]
	bathroom_id = request_variables[1]
	bathroom = Bathroom.objects.get(pk=bathroom_id)
	is_ppsf_upgrade = request_variables[2]

	#create a new mapping for the new upgrade chosen
	if is_ppsf_upgrade == 'True':
		chosen_upgrade = PricePerSquareFootUpgrade.objects.get(pk=chosen_upgrade_id)
		new_mapping = UserRoomUpgradeMapping(user=user_choice, room=bathroom, ppsf_upgrade=chosen_upgrade, upgrade_type=chosen_upgrade.upgrade_type, roomname=bathroom.name)
	else:
		chosen_upgrade = FlatPriceUpgrade.objects.get(pk=chosen_upgrade_id)
		new_mapping = UserRoomUpgradeMapping(user=user_choice, room=bathroom, flat_price_upgrade=chosen_upgrade, upgrade_type=chosen_upgrade.upgrade_type, roomname=bathroom.name)

	#check if old upgrade already had a mapping, if so, delete it
	try:
		same_type_upgrade = UserRoomUpgradeMapping.objects.filter(user=user_choice, room=bathroom, upgrade_type=chosen_upgrade.upgrade_type)
		if same_type_upgrade.exists():
			same_type_upgrade.delete()
	except ObjectDoesNotExist:
		print("no objects found")

	new_mapping.save()
	context = get_context_for_user_choice(request)
	return features(request, context)

@login_required
def calcTotalPrice(request):
	user_choice = get_user_choice_for_user(request.user.username)
	return user_choice.getTotalCost()

@login_required
def select_house(request):
	user_choice = get_user_choice_for_user(request.user.username)
	user_choice.house = House.objects.get(pk=request.POST['house_id'])
	user_choice.save()
	context = get_context_for_user_choice(request)
	return features(request, context)

def get_user_choice_for_user(username):
	user = User.objects.get(username=username)
	try:
		user_choice = UserChoice.objects.get(user=user)
	except ObjectDoesNotExist:
		user_choice = UserChoice(user=user)
	return user_choice

def get_context_for_user_choice(request):
	user_choice = get_user_choice_for_user(request.user.username)
	context = {
		'kitchens' : user_choice.house.kitchen.all(), 
		'bathrooms' : user_choice.house.bathroom.all(),
		'bedrooms' : user_choice.house.bedroom.all(),
		'garages' : user_choice.house.garage.all(),
		'living_rooms' : user_choice.house.livingRoom.all(),
		'dining_rooms' : user_choice.house.diningRoom.all(),
		}
	return context