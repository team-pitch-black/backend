from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Player, Room

# class PlayerAdmin(admin.ModelAdmin):
#     readonly_fields = ('items', 'current_room')

admin.site.register(Player)
admin.site.register(Room)
# admin.site.register(World)
