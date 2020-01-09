from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
# from users.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from uuid import uuid4
import random
import math
import json

class Room(models.Model):
    id = models.IntegerField(primary_key=True, default=0)
    room_type = models.CharField(max_length=50, default="ROOM")
    # title = models.CharField(max_length=50, default="DEFAULT TITLE")
    description = models.CharField(
        max_length=500, default="DEFAULT DESCRIPTION")
    room_up = models.IntegerField(default=0)
    room_down = models.IntegerField(default=0)
    room_right = models.IntegerField(default=0)
    room_left = models.IntegerField(default=0)
    # players = []
    # players_list = models.TextField(default=json.dumps({}))
    # items = []
    # items_list = models.TextField(default=json.dumps({}))
    grid_x = models.IntegerField(default=None)
    grid_y = models.IntegerField(default=None)
    # def __repr__(self):
    #     pass

    ################ These were provided ################
    def get_room_in_direction(self, direction):
        '''
        Return room in corresponding direction
        '''
        return getattr(self, f"room_{direction}")

    def get_by_id(self, id):
        # print("id", id)
        # print(Room.objects.filter(id=id)[0])
        return Room.objects.filter(id=id).first()

    def connect_rooms(self, connecting_room, direction):
        '''
        Connect two rooms in the given n/s/e/w direction
        '''
        reverse_dir = {"up": "down", "down": "up",
                        "right": "left", "left": "right"}[direction]
        setattr(self, f"room_{direction}", connecting_room.id)
        self.save()
        setattr(connecting_room, f"room_{reverse_dir}", self.id)
        connecting_room.save()

        # print(self.id, direction, getattr(self, f"room_{direction}"), connecting_room.id, reverse_dir, getattr(connecting_room, f"room_{reverse_dir}"))

    def playerNames(self):
        return [p.user.username for p in Player.objects.filter(location=self.id)] #if p.id != int(currentPlayerID)

    def playerUUIDs(self):
        return [p.uuid for p in Player.objects.filter(location=self.id)] #if p.id != int(currentPlayerID)
    #####################################################
    

    def roomItemNames(self):
        return [i.name for i in Item.objects.filter(room_id=self.id)] #if p.id != int(currentPlayerID)

    def player_entered(self, player):
        self.players.append(player)
    # def player_entered(self, player):
    #     self.players.append(player)
    #     self.players_list = json.dumps([player.user.username for player in players])
    #     self.save()

    # def player_departed(self, player):
    #     self.players.remove(player)
    #     self.players_list = json.dumps([player.user.username for player in players])
    #     self.save()

    def add_item(self, item):
        self.items.append(item)
        self.save()

    def remove_item(self, item):
        self.items.remove(item)
        self.save()

    def set_room_up(self, room):
        self.room_up = room
        self.save()

    def set_room_down(self, room):
        self.room_down = room
        self.save()

    def set_room_left(self, room):
        self.room_left = room
        self.save()

    def set_room_right(self, room):
        self.room_right = room
        self.save()


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    location = models.IntegerField(default=1)
    items = []

    ############# These were provided ###############
    def initialize(self):
        if self.location == 1:
            self.location = Room.objects.first().id
            self.save()

    def room(self):
        try:
            return Room.objects.get(id=self.location)
        except Room.DoesNotExist:
            self.initialize()
            return self.room()

    def item(self):
        try:
            return Item.objects.filter(player_id=self.user.id)
        except Item.DoesNotExist:
            self.initialize()
            return self.item()

    def getItem(self, item):
        return Item.objects.get(name=item)
    ###############################################

    # def __str__(self):
    #     return self.username
    
    def playerItemNames(self):
        return [i.name for i in Item.objects.filter(player_id=self.user.id)] #if p.id != int(currentPlayerID)

    # Get the room object from the location integer
    def get_room(self, id):
        return Room.objects.get(id=self.location)

    def get_items(self):
        return Item.objects.filter(player_id=self.user.id)

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
    player_id = models.IntegerField(default=0)
    room_id = models.IntegerField(default=0)

class World:
    def __init__(self):
        self.grid = None
        self.width = 0
        self.height = 0
        self.rooms = []
        self.room_count = 1
        self.prev_direction = "up"

    def generate_rooms(self, size_x, size_y, num_rooms):
        '''
        Algorithm to be described once it's working
        '''

        def limit(new, orig, maximum):
            if new < 0 or new >= maximum:
                return orig
            else:
                return new

        def draw_horizontal(x1, x2, y):
            if x1 == x2:
                return
            for x in range(min(x1, x2), max(x1, x2) + 1):
                # print(x, y)
                if self.grid[y][x] == 0:
                    self.room_count += 1
                    self.grid[y][x] = self.room_count

        def draw_vertical(y1, y2, x):
            if y1 == y2:
                return
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if self.grid[y][x] == 0:
                    self.room_count += 1
                    self.grid[y][x] = self.room_count

        def random_direction(room):
            directions = ["up", "down", "left", "right"]
            open_paths = [(x, room.get_room_in_direction(x)) for x in directions if room.get_room_in_direction(x) == 0]
            print(open_paths)
            input()
            if (len(open_paths)):
                return random.choice(open_paths)
            else:
                return random.choice(directions)

        # Initialize the grid
        self.grid = [0] * size_y
        self.width = size_x
        self.height = size_y
        self.room_count = 1
        for i in range(len(self.grid)):
            self.grid[i] = [0] * size_x

        # Start from middle
        x = size_x // 2
        y = size_y // 2

        # Create first room
        self.current_room = Room(id=1, room_type=1, grid_x=x, grid_y=y)
        self.grid[y][x] = 1

        while self.room_count < num_rooms:

            # offset_x, offset_y = random.choice([(0, 1), (0, -1), (-1, 0), (1, 0)])
            # new_x, new_y = limit(x+offset_x, x, size_x), limit(y+offset_y, y, size_y)
            # print(x, y, new_x, new_y, self.grid[new_y][new_x])
            # if (new_x != x or new_y != y) and self.grid[new_y][new_x] == 0:
            #     self.room_count += 1
            #     self.grid[new_y][new_x] = self.room_count
            # x, y = new_x, new_y

            # self.print_rooms()
            # input()

            offset = random.choice([-3, 1, 3])
            if random.random() > 0.5:
                new_x = limit(x+offset, x, size_x)
                draw_horizontal(x, new_x, y)
                x = new_x
            else:
                new_y = limit(y+offset, y, size_y)
                draw_vertical(y, new_y, x)
                y = new_y

            # self.print_rooms()
        
        print("Linking rooms... ", end="")

        cache = {}
        def create_or_retrieve_room(id, x, y):
            if id in cache:
                room = cache[id]
            else:
                room = Room(id=id, room_type=1, grid_x=x, grid_y=y)
                room.save()
                cache[id] = room
            return room

        for y in range(0, size_y):
            for x in range(0, size_x):
                current_id = self.grid[y][x]
                right_id = self.grid[y][x+1] if x + 1 < size_x else 0
                down_id = self.grid[y+1][x] if y + 1 < size_y else 0

                if current_id:
                    current_room = create_or_retrieve_room(current_id, x, y)
                    if right_id:
                        print("right ", end="")
                        new_room = create_or_retrieve_room(right_id, x+1, y)
                        print(current_room, new_room)
                        current_room.connect_rooms(new_room, "right")
                    if down_id:
                        print("down ", end="")
                        new_room = create_or_retrieve_room(down_id, x, y+1)
                        print(current_room, new_room)
                        current_room.connect_rooms(new_room, "up")

        print("done")
        print(f"${self.room_count} rooms generated")

    def print_rooms(self):
        '''
        Print the rooms in room_grid in ascii characters.
        '''

        reverse_grid = list(self.grid)  # make a copy of the list
        # reverse_grid.reverse()

        for row in reverse_grid:
            for room in row:
                if room != 0:
                    print(str(room).zfill(3), end=" ")
                else:
                    print("   ", end=" ")
            print()
