
from .models import *

class LeaguePlayer():
    id = 0
    name = ""
    games = 0
    winn = 0
    loose = 0
    remis = 0
    winlegs = 0
    looselegs = 0 
    diff = 0 
    points = 0

class Statistic():
    
    def calcpoints(pointsobjects):
        
        points = 0
        
        for gamepoints in pointsobjects:
            #print(gamepoints.points)
            points = points + gamepoints.points

        return points
    
    def calc_rows_player_data(self, league_players, games):
        
        playerset = set()
        player_rows = []

        # alle spieler filtern und in ein set
        
        #for game in games:
        #    game.member = GameMembership.objects.filter(game=game.id)
        #    for member in game.member:
        #        #print(member.player.name)
        #        playerset.add(member.player.id)

        for league_player in league_players:
            playerset.add(league_player.player.id)

        #print(playerset) 

        # einzelne player daten ermitteln
        for player_id in playerset:
            #print("player:")
            player = LeaguePlayer()

            #alle punkte des spielers in der league holen
            games.points = Points.objects.filter(player=player_id)
            #print(games.points)
            
            #games zählen
            player.games = len(games.points)
            
            for points in games.points:
                # gewinne zählen
                if points.points == 2:
                    player.winn += 1 
                #remis zählen 
                if points.points == 1:
                    player.remis += 1 
                #remis zählen
                if points.points == 0:
                    player.loose += 1

                #print(points.points)
                player.points = player.points + points.points

            player_row = {
                    'player': Player.objects.get(id=player_id).name,
                    'games': player.games,
                    'winn': player.winn,
                    'loose':player.loose,
                    'remis': player.remis,
                    'winlegs': player.winlegs,
                    'looselegs': player.looselegs,
                    'diff': player.diff,
                    'points': player.points,
                }

            player_rows.append(player_row)

        return player_rows
    
    def calc_league_player_tabledata(self, league, league_players):

        player_data_rows = ""

        #games = Games.objects.filter(league=league.id)
        #player_data_rows = self.calc_rows_player_data(league_players, games)
        
        return player_data_rows

class CheckState():

    def check_throw(self, dart):
        print(dart)