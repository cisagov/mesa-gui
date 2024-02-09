from django.contrib import admin

from .models import Settings, MesaJob

admin.site.register([Settings, MesaJob])
