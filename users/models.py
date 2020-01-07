from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid import uuid4

# Create your models here.
class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    location = None
    items = []
    
    def __str__(self):
        return self.username

    def move_up(self):
        self.location.player_departed(self)
        self.location = self.location.room_up
        self.location.player_entered(self)

    def move_down(self):
        self.location.player_departed(self)
        self.location = self.location.room_down
        self.location.player_entered(self)
      
    def move_right(self):
        self.location.player_departed(self)
        self.location = self.location.room_right
        self.location.player_entered(self)
    
    def move_left(self):
        self.location.player_departed(self)
        self.location = self.location.room_left
        self.location.player_entered(self)


    def grab_item(self, item):
        self.items.append(item)
    
    def drop_item(self, item):
        self.items.remove(item)


