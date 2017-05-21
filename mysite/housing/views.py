# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, render_to_response, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from models import Lot, House, Kitchen, Bathroom, PricePerSquareFootUpgrade, UserChoice, Bedroom, LivingRoom, DiningRoom, Garage, UserRoomUpgradeMapping, FlatPriceUpgrade, Room, Subdivision
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

room_types_array = ["Kitchen", "Bathroom", "Dining Room", "Living Room", "Garage", "Bedroom"]

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
	subdiv = Subdivision.objects.all()
	context = {'lots': lots, 'subdiv': subdiv}
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
def room_types(request):
	request.session['total_price'] = int(calcTotalPrice(request))
	context = { 'room_types' : room_types_array }
	return render(request, 'room_types.html', context)

@login_required
def select_room_type(request):
	user_choice = get_user_choice_for_user(request.user.username)
	room_type = request.POST['room_type']
	if room_type in 'Kitchen':
		context = { 'rooms' : user_choice.house.kitchen.all() }
	if room_type == 'Bathroom':
		context = { 'rooms' : user_choice.house.bathroom.all() }
	if room_type == 'Bedroom':
		context = { 'rooms' : user_choice.house.bedroom.all() }
	if room_type == 'Garage':
		context = { 'rooms' : user_choice.house.garage.all() }
	if room_type == 'Living Room': 
		context = { 'rooms' : user_choice.house.livingRoom.all() }
	if room_type == 'Dining Room':
		context = { 'rooms' : user_choice.house.diningRoom.all() }
	context['roomname'] = room_type
	return render(request, 'rooms.html', context)

@login_required
def select_feature(request):
	user_choice = get_user_choice_for_user(request.user.username)
	room = request.POST['room']
	room_info = room.split(",")
	room_type = room_info[0]
	room_id = room_info[1]
	room_chosen = get_all_apgrades_for_chosen_room(room_type, room_id, user_choice)
	context = {
		'upgrades' : room_chosen.ppsf_upgrades.all(),
		'flat_price_upgrades' : room_chosen.flat_price_upgrades.all(),
		'room' : room_id,
		'room_type' : room_type
	}
	return render(request, 'upgrades.html', context)

@login_required
def select_room_upgrade(request):
	user_choice = get_user_choice_for_user(request.user.username)
	request_variables = request.POST['upgrade'].split(",")
	print(request_variables)
	chosen_upgrade_id = request_variables[0]
	room_id = request_variables[1]
	room_type = request_variables[3]
	room_object = get_object_for_room_type(room_type, room_id)
	is_ppsf_upgrade = request_variables[2]

	#create a new mapping for the new upgrade chosen
	if is_ppsf_upgrade == 'True':
		chosen_upgrade = PricePerSquareFootUpgrade.objects.get(pk=chosen_upgrade_id)
		new_mapping = UserRoomUpgradeMapping(user=user_choice, room=room_object, ppsf_upgrade=chosen_upgrade, upgrade_type=chosen_upgrade.upgrade_type, roomname=room_object.name)
	else:
		chosen_upgrade = FlatPriceUpgrade.objects.get(pk=chosen_upgrade_id)
		new_mapping = UserRoomUpgradeMapping(user=user_choice, room=room_object, flat_price_upgrade=chosen_upgrade, upgrade_type=chosen_upgrade.upgrade_type, roomname=room_object.name)
	
	#check if old upgrade already had a mapping, if so, delete it
	try:
		same_type_upgrade = UserRoomUpgradeMapping.objects.filter(user=user_choice, room=room_object, upgrade_type=chosen_upgrade.upgrade_type)
		if same_type_upgrade.exists():
			same_type_upgrade.delete()
	except ObjectDoesNotExist:
		print("no objects found")

	new_mapping.save()
	return room_types(request)

@login_required
def calcTotalPrice(request):
	user_choice = get_user_choice_for_user(request.user.username)
	return user_choice.getTotalCost()

@login_required
def select_house(request):
	user_choice = get_user_choice_for_user(request.user.username)
	user_choice.house = House.objects.get(pk=request.POST['house_id'])
	user_choice.save()
	return room_types(request)

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

def get_object_for_room_type(room_type, room_id):
	if room_type == "Kitchen":
		return Kitchen.objects.get(pk=room_id)
	if room_type == "Bathroom":
		return Bathroom.objects.get(pk=room_id)
	if room_type == "LivingRoom":
		return LivingRoom.objects.get(pk=room_id)
	if room_type == "Garage":
		return Garage.objects.get(pk=room_id)
	if room_type == "DiningRoom":
		return DiningRoom.objects.get(pk=room_id)
	if room_type == "Bedroom":
		return Bedroom.objects.get(pk=room_id)

def get_all_apgrades_for_chosen_room(room_type, room_id, user_choice):
	if room_type == "Kitchen":
		return user_choice.house.kitchen.get(pk=room_id)
	if room_type == "Bathroom":
		return user_choice.house.bathroom.get(pk=room_id)
	if room_type == "LivingRoom":
		return user_choice.house.livingRoom.get(pk=room_id)
	if room_type == "Garage":
		return user_choice.house.garage.get(pk=room_id)
	if room_type == "DiningRoom":
		return user_choice.house.diningRoom.get(pk=room_id)
	if room_type == "Bedroom":
		return user_choice.house.bedroom.get(pk=room_id)