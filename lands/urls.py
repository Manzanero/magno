from django.urls import path

from . import views

urlpatterns = [
    path('create', views.create_land, name='create_land'),
    path('<str:land_name>', views.land_view, name='land'),
    path('<str:land_name>/info', views.get_land, name='get_land'),
    path('<str:land_name>/delete', views.delete_land, name='delete_land'),
    path('<str:land_name>/realms/create', views.create_realm, name='create_realm'),
    path('<str:land_name>/realms/<str:realm_name>/info', views.get_realm, name='get_realm'),
    path('<str:land_name>/realms/<str:realm_name>/join', views.join_realm, name='join_realm'),
    path('<str:land_name>/realms/<str:realm_name>/leave', views.leave_realm, name='leave_realm'),
    path('<str:land_name>/realms/<str:realm_name>/properties', views.get_realm_properties, name='get_realm_properties'),
    path('<str:land_name>/realms/<str:realm_name>/properties/<str:property_name>', views.set_realm_properties, name='set_realm_properties'),
    path('<str:land_name>/realms/<str:realm_name>/delete', views.delete_realm, name='delete_realm'),
    path('<str:land_name>/realms/<str:realm_name>/publish', views.publish_messages, name='send_messages'),
    path('<str:land_name>/realms/<str:realm_name>/receive', views.receive_messages, name='receive_messages'),
    path('<str:land_name>/realms/<str:realm_name>/clean', views.clean_messages, name='clean_messages'),
]