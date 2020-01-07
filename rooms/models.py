from django.db import models
from uuid import uuid4

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    room_up = None
    room_down = None
    room_left = None
    room_right = None
    room_type = None
    players = []
    items = []

    def player_entered(self, player):
        self.players.append(player)

    def player_departed(self, player):
        self.players.remove(player)

    def add_item(self, item):
        self.items.append(item)
    
    def remove_item(self, item):
        self.items.remove(item)
    
    def set_room_up(self, room):
        self.room_up = room

    def set_room_down(self, room):
        self.room_down = room

    def set_room_left(self, room):
        self.room_left = room

    def set_room_right(self, room):
        self.room_right = room


