import json
import time

from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404
from django.utils.datetime_safe import datetime
from django.views.decorators.http import require_http_methods

from lands.models import Realm, Message, Land, RealmProperty
from utils.decorators import api_response
from utils.time_ops import to_datetime_iso


def land(request, land_name):
    return render(request, 'lands/index.html', {'land_name': land_name, 'base_url': settings.BASE_URL})


@require_http_methods(["PUT"])
@api_response
def create_land(request):
    data = json.loads(request.body.decode('utf-8'))
    land_info = data['info']
    land_name = data['name']
    Land.objects.create(name=land_name, info=json.dumps(land_info))

    return {
        'message': f'Land (name={land_name}) created',
    }


@require_http_methods(["POST"])
@api_response
def upload_land(request):
    data = json.loads(request.body.decode('utf-8'))
    land_info = data['info']
    land_name = data['name']
    Land.objects.create(name=land_name, info=json.dumps(land_info))

    return {
        'message': f'Land (name={land_name}) uploaded',
    }


@require_http_methods(["GET"])
@api_response
def get_land(request, land_name):
    land = get_object_or_404(Land, name=land_name)
    realms = land.realms.all()

    return {
        'message': f'Land (name={land_name}) loaded',
        'name': land.name,
        'info': json.loads(land.info),
        'realms': [x.name for x in realms],
    }


@require_http_methods(["DELETE"])
@api_response
def delete_land(request, land_name):
    land = get_object_or_404(Land, name=land_name)
    land.delete()

    return {
        'message': f'Land (name={land_name}) deleted',
    }


@require_http_methods(["PUT"])
@api_response
def create_realm(request, land_name):
    land = get_object_or_404(Land, name=land_name)
    data = json.loads(request.body.decode('utf-8'))
    realm_name = data['name']
    realm_info = data.get('info', {})
    try:
        Realm.objects.create(land=land, name=realm_name, info=json.dumps(realm_info), host=request.user)
        message = f'Realm (name={realm_name}) created'
        created = True
        exists = True
    except IntegrityError:
        message = f'Realm (name={realm_name}) already exist'
        created = False
        exists = True

    return {
        'message': message,
        'created': created,
        'exists': exists,
    }


@require_http_methods(["GET"])
@api_response
def get_realm(request, land_name, realm_name):
    land = get_object_or_404(Land, name=land_name)
    realm = get_object_or_404(Realm, land=land, name=realm_name)

    return {
        'message': f'Realm (name={realm_name}) loaded',
        'name': realm.name,
        'info': json.loads(realm.info),
        'land': land.name,
    }


@require_http_methods(["GET"])
@api_response
def join_realm(request, land_name, realm_name):
    land = get_object_or_404(Land, name=land_name)
    realm = get_object_or_404(Realm, land=land, name=realm_name)
    player = request.user
    realm.players.add(player)

    return {
        'message': f'Realm (name={realm_name}) joined',
        'players': [x.username for x in realm.players.all()],
        'host': realm.host.username,
    }


@require_http_methods(["GET"])
@api_response
def leave_realm(request, land_name, realm_name):
    land = get_object_or_404(Land, name=land_name)
    realm = get_object_or_404(Realm, land=land, name=realm_name)
    player = request.user
    realm.players.remove(player)

    return {
        'message': f'Realm (name={realm_name}) joined',
        'players': [x.username for x in realm.players.all()],
        'host': realm.host.username,
    }


@require_http_methods(["GET"])
@api_response
def get_realm_properties(request, land_name, realm_name):
    land = get_object_or_404(Land, name=land_name)
    realm = get_object_or_404(Realm, land=land, name=realm_name)
    players = request.GET.get('player')
    if players:
        users = User.objects.filter(username__in=players.split(','))
    else:
        users = []

    properties = request.GET.get('name')
    if users:
        if properties:
            realm_properties = realm.realm_properties.filter(player__in=users, name__in=properties.split(','))
        else:
            realm_properties = realm.realm_properties.filter(player__in=users)
    else:
        if properties:
            realm_properties = realm.realm_properties.filter(name__in=properties.split(','))
        else:
            realm_properties = realm.realm_properties.filter()

    return {
        'message': f'Realm Properties (len={len(realm_properties)}) get',
        'properties': [{
            'player': x.player.username if x.player else '',
            'name': x.name,
            'value': x.value,
        } for x in realm_properties],
    }


@require_http_methods(["POST"])
@api_response
def set_realm_properties(request, land_name, realm_name, property_name):
    land = get_object_or_404(Land, name=land_name)
    realm = get_object_or_404(Realm, land=land, name=realm_name)

    data = json.loads(request.body.decode('utf-8'))
    players = data.get('players', [])
    values = data.get('values', [])

    if players:
        users = User.objects.filter(username__in=players)
    else:
        users = []

    if users:
        for user in users:
            RealmProperty.objects.filter(realm=realm, player=user, name=property_name).delete()
            for value in values:
                RealmProperty.objects.create(realm=realm, player=user, name=property_name, value=value)
    else:
        RealmProperty.objects.filter(realm=realm, player__isnull=True, name=property_name).delete()
        for value in values:
            RealmProperty.objects.create(realm=realm, player=None, name=property_name, value=value)

    return {
        'message': f'Realm Property (name={property_name}) set',
    }


@require_http_methods(["DELETE"])
@api_response
def delete_realm(request, land_name, realm_name):
    land = get_object_or_404(Land, name=land_name)
    realm = get_object_or_404(Realm, land=land, name=realm_name)
    realm.delete()

    return {
        'message': f'Realm (name={realm_name}) deleted',
    }


@require_http_methods(["PUT"])
@api_response
def publish_messages(request, land_name, realm_name):
    land = get_object_or_404(Land, name=land_name)
    realm = get_object_or_404(Realm, land=land, name=realm_name)
    body = request.body.decode('utf-8')
    messages = json.loads(body)['messages'] if body else []
    for message in messages:
        topic = message['topic']
        payload = json.dumps(message['payload'])
        Message.objects.create(realm=realm, player=request.user, topic=topic, payload=payload)

    return {
        'message': f'Messages send (len={len(messages)})',
    }


@require_http_methods(["GET"])
@api_response
def receive_messages(request, land_name, realm_name):
    realm = get_object_or_404(Realm, land__name=land_name, name=realm_name)
    from_datetime = request.GET['from'].replace(' ', '+')
    topic = request.GET['topic']
    every = int(request.GET.get('every', 1))
    persistence = int(request.GET.get('persistence', 0))
    messages = Message.objects.filter(realm=realm, created__gt=datetime.fromisoformat(from_datetime), topic=topic)
    date = to_datetime_iso(messages.last().created) if messages else from_datetime
    messages = messages.exclude(player=request.user)

    from_time = time.time()
    while not messages and time.time() - from_time < persistence:
        time.sleep(every)
        messages = Message.objects.filter(realm=realm, created__gt=datetime.fromisoformat(date), topic=topic)
        date = to_datetime_iso(messages.last().created) if messages else date
        messages = messages.exclude(player=request.user)

    return {
        'message': f'Messages received (len={len(messages)})',
        'date': date,
        'messages': [{'topic': x.topic, 'payload': json.loads(x.payload)} for x in messages],
    }


@require_http_methods(["DELETE"])
@api_response
def clean_messages(request, land_name, realm_name):
    realm = get_object_or_404(Realm, land__name=land_name, name=realm_name)
    datetime_iso = request.GET.get('until')
    if datetime_iso:
        messages = Message.objects.filter(realm=realm, created__lt=datetime.fromisoformat(datetime_iso))
    else:
        messages = Message.objects.filter(realm=realm)
    messages_deleted = len(messages)
    messages.delete()

    return {
        'message': f'Messages deleted (len={messages_deleted})',
    }
