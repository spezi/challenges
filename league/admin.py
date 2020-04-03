from django.contrib import admin

from .models import League,Player,Games,Game,Leg,LegPoints,ThrowSet, GameMembership, LeagueMembership, Points

# Register your models here.

admin.site.register(League)
admin.site.register(Player)
admin.site.register(Games)
admin.site.register(Game)
admin.site.register(Leg)
admin.site.register(LegPoints)
admin.site.register(GameMembership)
admin.site.register(LeagueMembership)
admin.site.register(Points)
admin.site.register(ThrowSet)
