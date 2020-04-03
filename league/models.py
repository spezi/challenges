from django.db import models

# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=50)
   
    def __str__(self):
        return self.name

class League(models.Model):
    name = models.CharField(max_length=128)
    member = models.ManyToManyField(
        Player,
        through='LeagueMembership',
        through_fields=('league','player'),
    )
    
    def __str__(self):
        return self.name

class Games(models.Model):
    name = models.CharField(max_length=128)
    player_quantity = models.IntegerField()
    members = models.ManyToManyField(
        Player,
        through='GameMembership',
        through_fields=('game', 'player'),
    )
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    legs = models.IntegerField(null=True)
    done = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class Game(models.Model):
    games = models.ForeignKey(Games, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    def __str__(self):
        return self.name

class Leg(models.Model):
    number = models.IntegerField(null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    winner = models.ForeignKey(Player, null=True, on_delete=models.CASCADE)
    last_thrown = models.IntegerField(null=True)
    
class ThrowSet(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    leg = models.ForeignKey(Leg, on_delete=models.CASCADE)

class Dart(models.Model):
    throwset = models.ForeignKey(ThrowSet, on_delete=models.CASCADE)
    points = models.IntegerField(null=True)
    count = models.IntegerField(null=True)
    double = models.BooleanField(default=False)
    tripple = models.BooleanField(default=False)

class Points(models.Model):
    points = models.IntegerField(null=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Games, on_delete=models.CASCADE)

class LegPoints(models.Model):
    points = models.IntegerField(null=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    leg = models.ForeignKey(Leg, on_delete=models.CASCADE)

class GameMembership(models.Model):
    game = models.ForeignKey(Games, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

class LeagueMembership(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)






