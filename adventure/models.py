from django.db import models
from django.contrib.auth.models import User
# from users.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from uuid import uuid4
import random

class Room(models.Model):
    id = models.IntegerField(primary_key=True,default=0)
    room_type = models.CharField(max_length=50, default="ROOM")
    # title = models.CharField(max_length=50, default="DEFAULT TITLE")
    description = models.CharField(max_length=500, default="DEFAULT DESCRIPTION")
    room_up = models.IntegerField(default=0)
    room_down = models.IntegerField(default=0)
    room_right = models.IntegerField(default=0)
    room_left = models.IntegerField(default=0)
    players = []
    items = []
    grid_x = models.IntegerField(default=None)
    grid_y = models.IntegerField(default=None)
    
    # def __repr__(self):
    #     pass

    def __getitem__(self, x):
        return getattr(self, x)

    ################ These were provided ################
    def get_room_in_direction(self, direction):
        '''
        Return room in corresponding direction
        '''
        return getattr(self, f"room_{direction}")
    
    def get_by_id(self, id):
        return Room.objects.filter(id=self.id)
    
    def connect_rooms(self, connecting_room, direction):
        '''
        Connect two rooms in the given n/s/e/w direction
        '''
        reverse_dirs = {"up": "down", "down": "up", "right": "left", "left": "right"}
        reverse_dir = reverse_dirs[direction]
        setattr(self, f"room_{direction}", connecting_room.id)
        setattr(connecting_room, f"room_{reverse_dir}", self.id)
        self.save()

    def playerNames(self, currentPlayerID):
        return [p.user.username for p in Player.objects.filter(current_room=self.id) if p.id != int(currentPlayerID)]

    def playerUUIDs(self, currentPlayerID):
        return [p.uuid for p in Player.objects.filter(current_room=self.id) if p.id != int(currentPlayerID)]
    #####################################################

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


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    current_room = models.IntegerField(default=0)
    items = []
    
    ############# These were provided ###############
    def initialize(self):
        if self.current_room == 0:
            self.current_room = Room.objects.first().id
            self.save()
    
    def room(self):
        try:
            return Room.objects.get(id=self.current_room)
        except Room.DoesNotExist:
            self.initialize()
            return self.room()


    ###############################################

    # def __str__(self):
    #     return self.username

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

@receiver(post_save, sender=User)
def create_user_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)
        Token.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_player(sender, instance, **kwargs):
    instance.player.save()


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50, default="ITEM")



class World:
    def __init__(self):
        self.grid = None
        self.width = 0
        self.height = 0
        self.rooms = []
        
    def generate_rooms(self, size_x, size_y, num_rooms):
        '''
        Algorithm to be described once it's working
        '''

        def random_direction(room):
            directions = ["up", "down", "left", "right"]
            open_paths = [x for x in directions if room[f"room_{x}"] == 0]
            if (len(open_paths)):
                return random.choice(open_paths)
            else:
                return random.choice(directions)

        # Initialize the grid
        self.grid = [None] * size_y
        self.width = size_x
        self.height = size_y
        room_count = 1
        for i in range( len(self.grid) ):
            self.grid[i] = [None] * size_x

        # Start from middle
        x = size_x // 2
        y = size_y // 2

        # While there are rooms to be created...
        current_room = Room(id = 1, grid_x = x, grid_y = y)
        self.grid[y][x] = 1

        while room_count < num_rooms:
            while True:
                offset = {"up": [0,1], "down": [0,-1], "left": [-1,0], "right": [1,0]}
                direction = random_direction(current_room)
                new_x = x + offset[direction][0]
                new_y = y + offset[direction][1]
                if (new_x < size_x and new_x > 0) and (new_y < size_y and new_y > 0):
                    break
            
            # If no room there already
            if current_room[f"room_{direction}"] == 0:
                room_count += 1
                new_room = Room(id = room_count, grid_x = new_x, grid_y = new_y)
                current_room.connect_rooms(new_room, direction)
                self.grid[new_y][new_x] = room_count
                # print(f"{current_room.grid_x}, {current_room.grid_y} | {new_room.grid_x}, {new_room.grid_y}")
                # reverse_dirs = {"up": "down", "down": "up", "right": "left", "left": "right"}
                # reverse_dir = reverse_dirs[direction]
                # print(current_room.id, current_room[f"room_{direction}"], '|', new_room.id, new_room[f"room_{reverse_dir}"])
            else:
                # Room already exists, let's link it
                new_room_id = current_room[f"room_{direction}"]
                new_room = current_room.get_by_id(new_room_id)
                current_room.connect_rooms(new_room, direction)

            current_room = new_room
            x = new_x
            y = new_y

        print(f"${room_count} rooms generated")



    def print_rooms(self):
        '''
        Print the rooms in room_grid in ascii characters.
        '''
        pass
        # # Add top border
        # str = "# " * ((3 + self.width * 5) // 2) + "\n"

        # # The console prints top to bottom but our array is arranged
        # # bottom to top.
        # #
        # # We reverse it so it draws in the right direction.
        # reverse_grid = list(self.grid) # make a copy of the list
        # reverse_grid.reverse()
        # for row in reverse_grid:
        #     # PRINT NORTH CONNECTION ROW
        #     str += "#"
        #     for room in row:
        #         if room is not None and room.n_to is not None:
        #             str += "  |  "
        #         else:
        #             str += "     "
        #     str += "#\n"
        #     # PRINT ROOM ROW
        #     str += "#"
        #     for room in row:
        #         if room is not None and room.w_to is not None:
        #             str += "-"
        #         else:
        #             str += " "
        #         if room is not None:
        #             str += f"{room.id}".zfill(3)
        #         else:
        #             str += "   "
        #         if room is not None and room.e_to is not None:
        #             str += "-"
        #         else:
        #             str += " "
        #     str += "#\n"
        #     # PRINT SOUTH CONNECTION ROW
        #     str += "#"
        #     for room in row:
        #         if room is not None and room.s_to is not None:
        #             str += "  |  "
        #         else:
        #             str += "     "
        #     str += "#\n"

        # # Add bottom border
        # str += "# " * ((3 + self.width * 5) // 2) + "\n"

        # # Print string
        # print(str)


w = World()
num_rooms = 44
width = 8
height = 7
w.generate_rooms(width, height, num_rooms)
w.print_rooms()