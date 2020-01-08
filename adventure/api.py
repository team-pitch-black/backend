from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view, permission_classes
# from rest_framework import permissions, serializers
from rest_framework import permissions
# from rest_framework import serializers, viewsets
import json

# instantiate pusher
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

@api_view(["POST"])
def create_world(request):
    Room.objects.all().delete()
    w = World()
    w.generate_rooms(25, 25, 100)
    response = []
    rooms = list(Room.objects.all())
    for room in rooms:
        response.append({
            'id': room.id,
            'room_type': room.room_type,
            'grid_x': room.grid_x,
            'grid_y': room.grid_y,
            'players': room.playerNames(),
            'items': []
        })

    return JsonResponse(response, safe=False)


@api_view(["GET"])
@permission_classes((permissions.AllowAny,))
def get_map(request, room_id=None):
    if room_id:
        rooms = list(Room.objects.filter(id=room_id))
    else:
        rooms = list(Room.objects.all())
    response = []
    for room in rooms:
        response.append({
            'id': room.id,
            'room_type': room.room_type,
            'grid_x': room.grid_x,
            'grid_y': room.grid_y,
            'players': room.playerNames(),
            'items': []
        })

    return JsonResponse(response, safe=False)


"""
GET /api/adv/init/
REQUEST: No Body
RETURNS:
{
    "name": "bryanszendel1", 
    "room_type": "ROOM2", 
    "description": "DEFAULT DESCRIPTION", 
    "players": ["bryanszendel1"], 
    "error_msg": ""
}
"""
@csrf_exempt
@api_view(["GET"])
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'room_id': room.id, 'room_type':room.room_type, 'description':room.description, 'players':players}, safe=True)


"""
POST /api/adv/move/
REQUEST:
{
    "direction":"u" || "d" || "l" || "r"
}
RETURNS:
{
    "name": "bryanszendel1", 
    "room_type": "ROOM1", 
    "description": "DEFAULT DESCRIPTION", 
    "players": ["bryanszendel1", "bryanszendel"], 
    "error_msg": ""
}
"""
# @csrf_exempt
@api_view(["POST"])
def move(request):
    dirs={"u": "up", "d": "down", "r": "right", "l": "left"}
    reverse_dirs = {"u": "down", "d": "up", "r": "left", "l": "right"}
    player = request.user.player
    player_id = player.id
    player_uuid = player.uuid
    data = json.loads(request.body)
    direction = data['direction']
    room = player.room()
    nextRoomID = None
    if direction == "u":
        nextRoomID = room.room_up
    elif direction == "d":
        nextRoomID = room.room_down
    elif direction == "r":
        nextRoomID = room.room_right
    elif direction == "l":
        nextRoomID = room.room_left
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.location=nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name':player.user.username, 'room_id': nextRoom.id, 'room_type':nextRoom.room_type, 'description':nextRoom.description, 'players':players, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name':player.user.username, 'room_id': room.id, 'room_type':room.room_type, 'description':room.description, 'players':players, 'error_msg':"You cannot move that way."}, safe=True)


@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)
