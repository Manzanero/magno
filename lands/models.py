from django.contrib.auth.models import User
from django.db import models


class WorldProperty(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    name = models.CharField(max_length=255)
    value = models.TextField()

    class Meta:
        verbose_name_plural = "World Properties"

    def __str__(self):
        return f'{self.player.username} - {self.name}'


class Land(models.Model):
    name = models.SlugField(max_length=255, unique=True)
    info = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class LandProperty(models.Model):
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='land_properties')
    player = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='land_properties')
    name = models.CharField(max_length=255)
    value = models.TextField()

    class Meta:
        verbose_name_plural = "Land Properties"

    def __str__(self):
        return f'{self.land.name} - {self.player.username} - {self.name}'


class Realm(models.Model):
    land = models.ForeignKey(Land, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='realms')
    name = models.SlugField(max_length=255)
    info = models.TextField()
    host = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='hosts')
    players = models.ManyToManyField(User, blank=True, default=None, related_name='plays')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['land', 'name']

    def __str__(self):
        return self.name


class RealmProperty(models.Model):
    realm = models.ForeignKey(Realm, on_delete=models.CASCADE, related_name='realm_properties')
    player = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='realm_properties')
    name = models.CharField(max_length=255)
    value = models.TextField()

    class Meta:
        verbose_name_plural = "Realm Properties"

    def __str__(self):
        return f"{self.realm.land.name} - {self.realm.name} - {self.player.username if self.player else None} - {self.name}"


class Message(models.Model):
    realm = models.ForeignKey(Realm, on_delete=models.CASCADE, related_name='messages')
    player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, default=None, related_name='messages')
    topic = models.SlugField(max_length=255, null=True, blank=True, default=None)
    payload = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.realm.land.name} - {self.realm.name} - {self.player.username if self.player else None} - {self.topic} - {self.created}"
