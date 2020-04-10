from django.db import models
from django.conf import settings

# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=50)
   
    def __str__(self):
        return self.name

class Modes(models.Model):

    POINTS =[(301, 301),(401, 401),(501, 501),(601, 601),(701, 701),(801, 801)]
    CHECKIN = [('SI', 'Single In'), ('DI', 'Double In')]
    CHECKOUT = [('SO', 'Single Out'), ('DO', 'Double Out')]
    WINMOD = [('FW', 'First Player Winn'),]

    name = models.CharField(max_length=128)
    points = models.IntegerField(
       choices=POINTS,
       default=501,
    )
    checkin = models.CharField(
       max_length=32,
       choices=CHECKIN,
       default='SI',
    )
    checkout = models.CharField(
       max_length=32,
       choices=CHECKOUT,
       default='DO',
    )
    winmod = models.CharField(
       max_length=32,
       choices=WINMOD,
       default='DO',
    )
    legs = models.IntegerField(null=True)

    def __str__(self):
        return self.name

class Game(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(
        Player,
        through='GameMembership',
        through_fields=('game', 'player'),
    )
    def __str__(self):
        return self.name

class GameMembership(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

class Leg(models.Model):
    number = models.IntegerField(null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    winner = models.IntegerField(blank=True, null=True)

class Points(models.Model): #fliegt evtl raus
    points = models.IntegerField(null=True, default=501)
    leg = models.ForeignKey(Leg, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, blank=True, null=True, on_delete=models.CASCADE)

class Dart(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    leg = models.ForeignKey(Leg, on_delete=models.CASCADE)
    double = models.BooleanField(default=False)
    tripple = models.BooleanField(default=False)
    points = models.IntegerField(null=True)
    points_calc = models.IntegerField(null=True)
    overthrowed = models.BooleanField(default=False) 

class League(models.Model):
    name = models.CharField(max_length=128)
    mode = models.ForeignKey(Modes, blank=True, null=True,on_delete=models.CASCADE)
    member = models.ManyToManyField(
        Player,
        through='LeagueMembership',
        through_fields=('league','player'),
    )

    def __str__(self):
        return self.name

class LeagueMembership(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

class LeagueGames(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)