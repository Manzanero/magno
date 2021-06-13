from django.contrib import admin

from .models import WorldProperty, Land, LandProperty, Realm, RealmProperty, Message


class WorldPropertyAdmin(admin.ModelAdmin):
    pass


admin.site.register(WorldProperty, WorldPropertyAdmin)


class LandPropertyInline(admin.StackedInline):
    model = LandProperty
    extra = 1


class LandAdmin(admin.ModelAdmin):
    inlines = [LandPropertyInline]
    list_display = ['name']


admin.site.register(Land, LandAdmin)


class RealmPropertyInline(admin.StackedInline):
    model = RealmProperty
    extra = 1


class RealmAdmin(admin.ModelAdmin):
    inlines = [RealmPropertyInline]
    list_display = ['name', 'land_name']

    @staticmethod
    def land_name(obj):
        return obj.land.name


admin.site.register(Realm, RealmAdmin)


class MessageAdmin(admin.ModelAdmin):
    pass


admin.site.register(Message, MessageAdmin)
