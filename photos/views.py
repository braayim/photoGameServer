from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from . import models
from . import serializers


@csrf_exempt
@api_view(['POST'])
def game_request(request, format=None):
    action = request.data.get('action')
    data = request.data

    if not action:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if action == 'LOGIN':
        return login(data=data)
    elif action == 'REGISTER_USER':
        return register_user(data)
    elif action == 'SAVE_PICTURE':
        return save_picture(data=data)
    elif action == 'VOTE_PICTURE':
        return vote_picture(data)
    elif action == 'GET_PICTURES':
        return get_pictures(data=data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


def login(data):
    try:
        user = models.User.objects.get(username=data.get('username'))
    except models.User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = serializers.UserSerializer(user)
    return Response(serializer.data)


def register_user(data):
    serializer = serializers.UserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def save_picture(data):
    picture_serializer = serializers.PictureSerializer(data=data)
    if picture_serializer.is_valid():
        picture_serializer.save()
        image = {}
        image['picture_details'] = picture_serializer.data.get('id');
        image['base64Image'] = data.get('base64Image')
        image_serializer = serializers.ImageSerializer(data=image)
        if image_serializer.is_valid():
            image_serializer.save()
        return Response(picture_serializer.data, status=status.HTTP_201_CREATED)
    return Response(picture_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
Voting logic
"""


def vote_picture(data):
    picture_id = data.get('picture_id')
    user_id = data.get('user_id')
    in_vote_type = data.get('vote_type')

    # Getting picture details obj to provide us with the voting ledger standing
    picture_obj = models.Picture.objects.get(id=picture_id)
    serialized_pic = serializers.PictureSerializer(picture_obj).data

    # If the the picture is own by the voting user return error. Owner can't vote for selt
    picture_owner = serialized_pic.get('owner', 0)
    if picture_owner == user_id:
        return Response(status.HTTP_404_NOT_FOUND)

    # Voting ledger up_votes and down_votes account as per now
    up_votes_count = serialized_pic.get('up_votes_account', 0)
    down_votes_count = serialized_pic.get('down_votes_account', 0)
    new_up_votes_count = 0
    new_down_votes_count = 0

    # If User already voted for this picture and rectifying the vote
    try:
        vote = models.VotingHistory.objects.get(picture_id=picture_id, user_id=user_id)
        serialized_vote = serializers.VotesSerializer(vote).data
        vote_type = serialized_vote.get('vote_type')
        if vote_type == in_vote_type:
            return Response(status.HTTP_404_NOT_FOUND)
        if in_vote_type ==0:
            new_up_votes_count = up_votes_count-1
            new_down_votes_count = down_votes_count+1
        elif in_vote_type == 1:
            new_up_votes_count = up_votes_count+1
            new_down_votes_count = down_votes_count-1

        setattr(vote, 'up_votes_balance_before', up_votes_count)
        setattr(vote, 'up_votes_balance_after', new_up_votes_count)
        setattr(vote, 'down_votes_balance_before', down_votes_count)
        setattr(vote, 'down_votes_balance_after', new_down_votes_count)
        vote.save()
    # If user if voting this picture for the first time
    except models.VotingHistory.DoesNotExist:
        if in_vote_type ==0:
            new_down_votes_count = down_votes_count+1
        elif in_vote_type == 1:
            new_up_votes_count = up_votes_count+1

        data['up_votes_balance_before'] = up_votes_count
        data['down_votes_balance_before'] = down_votes_count
        data['up_votes_balance_after'] = new_up_votes_count
        data['down_votes_balance_after'] = new_down_votes_count

        vote_serializer = serializers.VotesSerializer(data=data)
        if vote_serializer.is_valid():
            vote_serializer.save()

    # Update the picture details that serve as our voting general ledger
    setattr(picture_obj, 'down_votes_account', new_down_votes_count)
    setattr(picture_obj, 'up_votes_account', new_up_votes_count)
    picture_obj.save()
    return Response(serializers.PictureSerializer(picture_obj).data)


def get_pictures(data):
    return Response(data)
