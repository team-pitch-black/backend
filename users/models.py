from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    location = None
    items = []
    
    def __str__(self):
        return self.username

    def move_up(self):
        pass

    def move_down(self):
        pass
      
    def move_right(self):
        pass
    
    def move_left(self):
        pass


    def grab_item(self, item):
        self.items.append(item)
    
    def drop_item(self, item):
        self.items.pop(self.items.index(item))


