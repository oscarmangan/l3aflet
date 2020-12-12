from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from world.forms import SignUpForm, PasswordChange
from . import models
from datetime import datetime
import requests
import json
# from rest_framework import permissions, status
# from .serializers import UserSerializer, UserSerializerToken
# from rest_framework.response import Response
# from rest_framework.views import APIView


# View for updating user's profile with their current location
@login_required
def update_location(request):
    try:
        user_profile = models.Profile.objects.get(user=request.user)
        if not user_profile:
            raise ValueError("Can't get User details")

        # Adding the coordinates to the users profile
        point = request.POST["point"].split(",")
        coords = request.POST["point"].replace(" ", "")
        point = [float(part) for part in point]
        point = Point(point, srid=4326)

        # Reverse geocoding the coordinates to retrieve their address
        with open('opencagekey.txt') as f:
            opencage_key = f.read().strip()
        url = "https://api.opencagedata.com/geocode/v1/json?q=" + coords + "&key=" + opencage_key
        open_response = requests.get(url)
        data = open_response.json()

        # Set the user's profile data to the point and data retrieved from the OpenCage API
        user_profile.road = data["results"][0]["components"]["road"]
        user_profile.locale = data["results"][0]["components"]["locality"]
        user_profile.city = data["results"][0]["components"]["city"]
        user_profile.county = data["results"][0]["components"]["county"]
        user_profile.country = data["results"][0]["components"]["country"]
        user_profile.last_location = point

        user_profile.save()

        return JsonResponse({"message": f"Set location to {point.wkt}."}, status=200)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=400)


# Method to update the users closest airport on their profile
def updateUserAirport(request):
    try:
        user_profile = models.Profile.objects.get(user=request.user)
        if not user_profile:
            raise ValueError("Cannot find user")

        airPoint = request.POST["coords"].split(",")
        airPoint = [float(part) for part in airPoint]
        airPoint = Point(airPoint, srid=4326)

        user_profile.nearest_airport_location = airPoint
        user_profile.nearest_airport_name = request.POST["airportName"]
        user_profile.nearest_airport_code = request.POST["airportCode"]
        user_profile.nearest_airport_country = request.POST["airportCountry"]
        user_profile.save()

        return JsonResponse({"message": f"Update users nearby airport info {airPoint.wkt}"}, status=200)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=400)


# Method to handle a signup request using the edited form at signup.html
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("map")
    else:
            form = SignUpForm()
    return render(request, "../templates/registration/signup.html", {"form": form})


# Method to handle a password change (login required to do so, like other methods)
@login_required
def passwordChange(request):
    if request.method == 'POST':
        form = PasswordChange(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            username = request.user.username
            password = form.cleaned_data.get("new_password1")
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("profile")
    else:
        form = PasswordChange(user=request.user)
    return render(request, "../templates/registration/password_change.html", {"form": form})


# Method to POST to the Lufthansa API to retrieve the token that will be used to get requests
@login_required
def getLufthansaToken(request):
    try:
        with open('lufthansa_key.txt') as f:
            client_key = f.read().strip()
        with open('lufthansa_secret.txt') as f:
            client_secret = f.read().strip()

        url = 'https://api.lufthansa.com/v1/oauth/token'

        data = {
            'client_id': client_key,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, data=data)

        return JsonResponse(response.json(), status=response.status_code)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=400)


# Method to get the nearest airport using the Lufthansa API, passing the coordinates of the users
# current coordinates, the API then returns a JSON response of a list of nearest airports, we pass
# back only the nearest one to the user
@login_required
def getNearbyAirport(request):
    try:
        user_profile = models.Profile.objects.get(user=request.user)
        latlong = str(user_profile.last_location)
        # strip latlong to be just the string of coordinates
        latlong = latlong[latlong.find('(')+1:-1].replace(' ', ',')
        token = request.POST["auth"]
        token = token[1:-1]
        url = 'https://api.lufthansa.com/v1/references/airports/nearest/' + latlong

        headers = {
            'Authorization': 'Bearer ' + token
        }

        response = requests.get(url, headers=headers)
        airport_data = response.json()['NearestAirportResource']['Airports']['Airport'][0]

        # Getting the necessary data from the response to return to the JS front-end
        airport_lat = airport_data['Position']['Coordinate']['Latitude']
        airport_lon = airport_data['Position']['Coordinate']['Longitude']
        airport_name = airport_data['Names']['Name'][0]['$']
        airport_code = airport_data['AirportCode']
        airport_country = airport_data['CountryCode']

        # Return the JsonResponse to the front end to handle
        return JsonResponse({
            "lat": airport_lat,
            "lon": airport_lon,
            "name": airport_name,
            "code": airport_code,
            "country": airport_country
        }, status=response.status_code)

    except Exception as e:
        return JsonResponse({"message": str(e)}, status=400)


# Method to search airports, again using Lufthansa API,
@login_required
def searchAirport(request):
    try:
        iataCode = request.POST["iata"]
        token = request.POST["auth"]
        token = token[1:-1]
        url = 'https://api.lufthansa.com/v1/mds-references/airports/' + iataCode
        headers = {
            'Authorization': 'Bearer ' + token
        }

        response = requests.get(url, headers=headers)
        airport_data = response.json()['AirportResource']['Airports']['Airport'][0]

        # Getting the necessary data from the response to return to the JS front-end
        airport_lat = airport_data['Position']['Coordinate']['Latitude']
        airport_lon = airport_data['Position']['Coordinate']['Longitude']
        airport_code = airport_data['AirportCode']
        airport_country = airport_data['CountryCode']

        # for loop to get the English version of the name of the airport
        for names in airport_data['Names']['Name']:
            if names['@LanguageCode'] == 'EN':
                airport_name = names['$']
                break
            else:
                airport_name = airport_data['Names']['Name'][0]['$']

        # if the response is a 404, no airport was found with the users query
        # else a response was found, return the details
        if response.status_code == 404:
            return JsonResponse({"message": "Not found"}, status=response.status_code)
        else:
            return JsonResponse({
                "lat": airport_lat,
                "lon": airport_lon,
                "name": airport_name,
                "code": airport_code,
                "country": airport_country
            }, status=response.status_code)

    except Exception as e:
        return JsonResponse({"message": str(e)}, status=400)


# Method to get departures for nearest or searched airport using the API
@login_required
def retrieveDepartures(request):
    try:
        iata = request.POST["iata"]
        token = request.POST["auth"]
        token = token[1:-1]
        headers = {
            'Authorization': 'Bearer ' + token
        }
        now = datetime.now()
        dt = now.strftime("%Y-%m-%dT%H:%M")

        # we only retrieve the top 30 departures
        url = 'https://api.lufthansa.com/v1/operations/flightstatus/departures/' + iata + '/' + dt + '?serviceType=all'

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            flight_data = response.json()['FlightStatusResource']['Flights']
            return JsonResponse(flight_data, status=response.status_code)
        elif response.status_code == 404:
            return JsonResponse({"message": "No departures found"}, status=response.status_code)
        else:
            return JsonResponse(response.json(), status=response.status_code)

    except Exception as e:
        return JsonResponse({"message": str(e)}, status=400)


# Method to retrieve all arrivals for the current date at the desired airport, either nearest or searched
@login_required()
def retrieveArrivals(request):
    try:
        iata = request.POST["iata"]

        token = request.POST["auth"]
        token = token[1:-1]

        headers = {
            'Authorization': 'Bearer ' + token
        }

        # API requires date in a YYYY-MM-DDTHH:MM format
        now = datetime.now()
        dt = now.strftime("%Y-%m-%dT%H:%M")

        # we only retrieve the top 30 departures
        url = 'https://api.lufthansa.com/v1/operations/flightstatus/arrivals/' + iata + '/' + dt + '?serviceType=all'

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            flight_data = response.json()['FlightStatusResource']['Flights']
            return JsonResponse(flight_data, status=response.status_code)
        elif response.status_code == 404:
            return JsonResponse({"message": "No arrivals found"}, status=response.status_code)
        else:
            return JsonResponse(response.json(), status=response.status_code)

    except Exception as e:
        return JsonResponse({"message": str(e)}, status=400)


# REST API / React implementation attempt

# class CreateUser(APIView):
#
#     permission_classes = (permissions.AllowAny,)
#
#     def post(self, request, format=None):
#         serializer = UserSerializerToken(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# def current_user(request):
#     # Determine current user by their token
#     serializer = UserSerializer(request.user)
#     return Response(serializer.data)


# def jwt_response_handler(token, user=None, request=None):
#     return {
#         'token': token,
#         'user': UserSerializer(user, context={'request': request}).data
#     }
