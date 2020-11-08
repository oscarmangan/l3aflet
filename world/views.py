from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point
from django.views.generic import CreateView

from . import models

# Create your views here.
class signUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

# View for updating user's profile with their current location
@login_required
def update_location(request):
    try:
        user_profile = models.Profile.objects.get(user=request.user)
        if not user_profile:
            raise ValueError("Can't get User details")

        point = request.POST["point"].split(",")
        point = [float(part) for part in point]
        point = Point(point, srid=4326)

        user_profile.last_location = point
        user_profile.save()

        return JsonResponse({"message": f"Set location to {point.wkt}."}, status=200)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=400)

