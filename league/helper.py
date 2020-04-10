
from .models import *

class LeaguePlayer(object):
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
       
    def calc_league_player_tabledata(self, league):
        
        player_data_rows = []
        #print(league)
        league_player = Player.objects.filter(league=league)
        league_games = LeagueGames.objects.filter(league=league)
        league_legs = []
        for game in league_games:
            game_legs = Leg.objects.filter(game=game.game)
            for leg in game_legs:
                league_legs.append(leg)
                #league_player.append()
        

        for player in league_player:
            
            player.legwin = 0
            player.points = 0
            player.looselegs = 0

            for leg in league_legs:
                #print(leg)
                if leg.winner == player.id:
                    player.legwin += 1
                    player.points += 2

            player_row = {
                        'player': player.name,
                        'games': LeaguePlayer.games,
                        'winn': LeaguePlayer.winn,
                        'loose': LeaguePlayer.loose,
                        'remis': LeaguePlayer.remis,
                        'winlegs': player.legwin,
                        'looselegs': player.looselegs,
                        'diff': player.legwin - player.looselegs,
                        'points': player.points,
                    }

            player_data_rows.append(player_row)



        return player_data_rows

