from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField('Population 2005')
    fips = models.CharField('FIPS Code', max_length=2, null=True)
    iso2 = models.CharField('2 Digit ISO', max_length=2)
    iso3 = models.CharField('3 Digit ISO', max_length=3)
    un = models.IntegerField('United Nations Code')
    region = models.IntegerField('Region Code')
    subregion = models.IntegerField('Sub-Region Code')
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField)
    mpoly = models.MultiPolygonField()

    # Returns the string representation of the model.
    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    road = models.CharField('Road', max_length=50, default='Road')
    locale = models.CharField('Locale', max_length=50, default='Locale')
    city = models.CharField('City', max_length=50, default='City')
    county = models.CharField('County', max_length=50, default='County')
    country = models.CharField('Country', max_length=50, default='Country')
    last_location = models.PointField(
        editable=False,
        blank=True,
        null=True,
        default=None,
    )
    nearest_airport_location = models.PointField(
        editable=False,
        blank=True,
        null=True,
        default=None,
    )
    nearest_airport_name = models.CharField('Nearest Airport Info', max_length=50, null=True)
    nearest_airport_code = models.CharField('Nearest Airport IATA', max_length=3, null=True)
    nearest_airport_country = models.CharField('Nearest Airport Country', max_length=20, null=True)

    def __str__(self):
        return f"{self.user}"


@receiver(post_save, sender=get_user_model())
def manage_user_profile(sender, instance, created, **kwargs):
    try:
        my_profile = instance.profile
        my_profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)
