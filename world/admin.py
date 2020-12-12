from django.contrib.gis import admin
from .models import WorldBorder
from .models import Profile

# Register your models here.
admin.site.register(WorldBorder, admin.GeoModelAdmin)
admin.site.register(Profile, admin.ModelAdmin)
