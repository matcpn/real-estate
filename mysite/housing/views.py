# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, render_to_response, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from models import Lot, House, Kitchen, Bathroom, PricePerSquareFootUpgrade, UserChoice, Bedroom, LivingRoom, DiningRoom, Garage, UserRoomUpgradeMapping, FlatPriceUpgrade, Room, Subdivision
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
import json

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
		if 'email' not in request.POST or 'password' not in request.POST:
			return JsonResponse({'password': 'Invalid email or password.'}, status=401)
		email = request.POST['email']
		password = request.POST['password']
		user = authenticate(request, username=email, password=password)
		if user is not None:
			auth_login(request, user)
			# redirect to the value of next if it is entered
			return JsonResponse({'success': 'success'}, status=200)
		else:
			return JsonResponse({'password': 'Invalid email or password.'}, status=401)

def create_user(request):
	if request.method == 'POST':
		# .. authenticate your user
		password = request.POST['password']
		email = request.POST['email']
		username = request.POST['username']
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		user = User.objects.create_user(username, email, password)
		user.last_name = last_name
		user.first_name = first_name
		user.save()
		if user is not None:
			auth_login(request, user)
			# redirect to the value of next if it is entered
			return redirect(request.POST.get('next','/'))
		else:
			return render(request, 'login.html')

@login_required
def index(request):
	lots = Lot.objects.all()
	subdiv = Subdivision.objects.all()
	user_choice = get_user_choice_for_user(request.user.username)
	lots_clickable = {}
	user_has_lot = True
	try:
		user_choice.lot is None
	except UserChoice.lot.RelatedObjectDoesNotExist:
		user_has_lot = False
	for lot in lots:
		if lot.status == "p" or lot.status == "s":
			lots_clickable[lot] = user_choice.lot == lot if user_has_lot else False
		else:
			lots_clickable[lot] = True
	context = {'lots': lots_clickable, 'subdiv': subdiv}
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
	user_choice = get_user_choice_for_user(request.user.username)
	request.session['total_price'] = int(calcTotalPrice(request))
	context = {
		'room_types' : room_types_array,
		'house' : user_choice.house
	}
	return render(request, 'room_types.html', context)

@login_required
def select_room_type(request):
	if request.method == 'POST':
		request.session['room_type'] = request.POST['room_type']
		return HttpResponseRedirect(reverse('housing:select_room_type', args=()))
	else:
		room_type = request.session['room_type']
		user_choice = get_user_choice_for_user(request.user.username)
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
	if request.method == 'POST':
		request.session['room'] = request.POST['room']
		return HttpResponseRedirect(reverse('housing:select_feature', args=()))
	else:
		room = request.session['room']
		user_choice = get_user_choice_for_user(request.user.username)
		room_info = room.split(",")
		room_type = room_info[0]
		room_id = room_info[1]
		room_chosen = get_all_upgrades_for_chosen_room(room_type, room_id, user_choice)
		ppsf_upgrades = room_chosen.ppsf_upgrades.all().order_by('upgrade_type')
		flat_price_upgrades = room_chosen.flat_price_upgrades.all().order_by('upgrade_type')
		upgrades_by_type = {}
		for upgrade in ppsf_upgrades:
			key = upgrade.upgrade_type
			upgrades_by_type.setdefault(key, [])
			upgrades_by_type[key].append(upgrade)
		for upgrade in flat_price_upgrades:
			key = upgrade.upgrade_type
			upgrades_by_type.setdefault(key, [])
			upgrades_by_type[key].append(upgrade)
		context = {
			'upgrades_by_type' : upgrades_by_type,
			'upgrades' : room_chosen.ppsf_upgrades.all(),
			'flat_price_upgrades' : room_chosen.flat_price_upgrades.all(),
			'room' : room_id,
			'room_type' : room_type
		}
		try:
			context['already_chosen'] = UserRoomUpgradeMapping.objects.filter(user=user_choice, room=Room.objects.get(id=room_id))
		except ObjectDoesNotExist:
			print("no objects found")

		print(context)
		return render(request, 'upgrades.html', context)

@login_required
def select_room_upgrade(request, chosen_upgrade_id, room_id, is_ppsf_upgrade, room_type):
	user_choice = get_user_choice_for_user(request.user.username)
	room_object = get_object_for_room_type(room_type, room_id)

	#create a new mapping for the new upgrade chosen
	if is_ppsf_upgrade == 'True':
		chosen_upgrade = PricePerSquareFootUpgrade.objects.get(pk=chosen_upgrade_id)
		new_mapping = UserRoomUpgradeMapping(
			user=user_choice, 
			room=room_object, 
			ppsf_upgrade=chosen_upgrade, 
			upgrade_type=chosen_upgrade.upgrade_type, 
			roomname=room_object.name)
	else:
		chosen_upgrade = FlatPriceUpgrade.objects.get(pk=chosen_upgrade_id)
		new_mapping = UserRoomUpgradeMapping(
			user=user_choice, 
			room=room_object, 
			flat_price_upgrade=chosen_upgrade, 
			upgrade_type=chosen_upgrade.upgrade_type, 
			roomname=room_object.name)
	
	#check if old upgrade already had a mapping, if so, delete it
	try:
		same_type_upgrade = UserRoomUpgradeMapping.objects.filter(user=user_choice, room=room_object, upgrade_type=chosen_upgrade.upgrade_type)
		if same_type_upgrade.exists():
			same_type_upgrade.delete()
	except ObjectDoesNotExist:
		print("no objects found")

	new_mapping.save()
	request.session['total_price'] = int(calcTotalPrice(request))
	context = { 'room_types' : room_types_array }
	return HttpResponseRedirect(reverse('housing:room_types', args=()))

@login_required
def calcTotalPrice(request):
	user_choice = get_user_choice_for_user(request.user.username)
	return user_choice.getTotalCost()

@login_required
def select_house(request, house_id):
	user_choice = get_user_choice_for_user(request.user.username)
	user_choice.house = House.objects.get(pk=house_id)
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

@user_passes_test(lambda u: u.is_superuser)
def user_edit(request):
	context = { 'user_choices' : UserChoice.objects.all() }
	return render(request, 'user-edit.html', context)

@user_passes_test(lambda u: u.is_superuser)
def user_edit_for_user(request, user_id):
	user_choice = UserChoice.objects.get(pk=user_id)
	context = { 
		'user_choice' : user_choice,
		'myTree'      : get_user_choice_tree(user_choice)
		}
	return render(request, 'user-edit-for-user.html', context)

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

def get_all_upgrades_for_chosen_room(room_type, room_id, user_choice):
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

def get_all_chosen_upgrades_for_chosen_room(room, user_choice):
	mapping = UserRoomUpgradeMapping.objects.filter(user=user_choice, roomname=room.name)
	return mapping

def get_all_rooms_for_chosen_room_type_in_house(room_type, user_choice):
	if user_choice.house is not None:
		if room_type == "Kitchen":
			return user_choice.house.kitchen.all()
		if room_type == "Bathroom":
			return user_choice.house.bathroom.all()
		if room_type == "LivingRoom":
			return user_choice.house.livingRoom.all()
		if room_type == "Garage":
			return user_choice.house.garage.all()
		if room_type == "DiningRoom":
			return user_choice.house.diningRoom.all()
		if room_type == "Bedroom":
			return user_choice.house.bedroom.all()
	else:
		return []

#the most complicated nonsense function ive ever written
def get_user_choice_tree(user_choice):
	tree = []

	for room_type in room_types_array:
		dropdown = {}
		state_dict = {}
		state_dict["expanded"] = "false"
		dropdown['text'] = room_type
		dropdown['state'] = state_dict
		dropdown['nodes'] = []

		for room in get_all_rooms_for_chosen_room_type_in_house(room_type.replace(" ", ""), user_choice):
			room_name_submenu = {}
			room_name_submenu['text'] = room.name
			room_name_submenu['nodes'] = []

			upgrades = get_all_chosen_upgrades_for_chosen_room(room, user_choice)
			if upgrades is not None:
				for upgrade in upgrades:
					upgrade_submenu = {}
					#set the upgrade text
					if upgrade.upgrade_type is not None:
						if upgrade.ppsf_upgrade is not None:
							upgrade_submenu['text'] = upgrade.upgrade_type.name + " upgrade: " + upgrade.upgrade_name + ", $" + str(upgrade.ppsf_upgrade.ppsf) + " per square foot"
						else:
							upgrade_submenu['text'] = upgrade.upgrade_type.name + " upgrade: " + upgrade.upgrade_name + ", $" + str(upgrade.flat_price_upgrade.price)
					else:
						upgrade_submenu['text'] = upgrade.name
  					# set the upgrade link
  					upgrade_submenu['href'] = "/admin/housing/userroomupgrademapping/" + str(upgrade.id) + "/change"
					room_name_submenu['nodes'].append(upgrade_submenu)

			dropdown['nodes'].append(room_name_submenu)

		tree.append(dropdown)

	return json.dumps(tree)
