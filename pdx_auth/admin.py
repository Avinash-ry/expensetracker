from django.contrib import admin
from .models import ConnectedApplication, PDXUser

admin.site.register(PDXUser)
admin.site.register(ConnectedApplication)