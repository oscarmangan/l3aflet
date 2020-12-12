"""registration URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.gis import admin
from django.urls import include, path
from django.views.generic.base import TemplateView
from world import views
# from rest_framework import routers
# from rest_framework.schemas import get_schema_view
# from rest_framework_jwt.views import obtain_jwt_token
# from world.serializers import UserViewSet

# Routers provide an easy way of automatically determining the URL conf
# from world.views import CreateUser
# router = routers.DefaultRouter()
# router.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('password_change/', views.passwordChange, name='password_change'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('', TemplateView.as_view(template_name='map.html'), name='map'),
    path('luft-auth/', views.getLufthansaToken, name='get_token'),
    path('nearby-airport/', views.getNearbyAirport, name='nearby_airport'),
    path('search-airport/', views.searchAirport, name='search_airport'),
    path('get-departures/', views.retrieveDepartures, name='get_departures'),
    path('get-arrivals/', views.retrieveArrivals, name='get_arrivals'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
    path('updatedb/', views.update_location, name='updatedb'),
    path('update-db-airport/', views.updateUserAirport, name='updateUserAirport'),
    path('', include('pwa.urls')),
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),


    # path('getaddress/', views.get_address, name='getaddress'),
    # path('api/', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('openapi', get_schema_view(
    #     title="l3aflet",
    #     description="API for all things ...",
    #     version="1.0.0"
    # ), name="openapi-schema"),
    # path('swagger-ui/', TemplateView.as_view(
    #     template_name='swagger-ui.html',
    #     extra_context={'schema_url':'openapi-schema'}
    # ), name='swagger-ui'),
    # path('token-auth/', obtain_jwt_token),
    # path('new-user/', CreateUser.as_view())
]
