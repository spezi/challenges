
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

class LegFake(object):
    id = int()
    number = int()
    game = object()
    winner = int()
    blocked = bool()

class LegFactory():

    def get_or_build_legs(self, prepare_legs):
        out_legs = []
        last_leg = {}
        print("prepare_legs:" + str(len(prepare_legs)))
        for idx, this_lag in enumerate(prepare_legs, start=1):
            if idx == 1 and this_lag.blocked:
                leg, created = Leg.objects.get_or_create(
						number=idx,
						game=self.game,
					)
                this_lag = leg
                this_lag.blocked = False
                last_leg = this_lag
            
            print("last leg winner")
            if this_lag.blocked and last_leg.winner and not self.game.winner:
                leg, created = Leg.objects.get_or_create(
                    number=idx,
                    game=self.game,
                    )
                this_lag = leg
                this_lag.blocked = False
                last_leg = this_lag
            else:
                try:
                    leg = Leg.objects.get(
                        number=idx,
                        game=self.game,
                    )
                    this_lag = leg
                    this_lag.blocked = False
                except:
                    pass
            if not this_lag.blocked:
                this_lag.playerdata = []
                for this_player in self.players:
                    out_player = {}
                    this_player.darts = Dart.objects.filter(player=this_player, leg=this_lag, count=True)
                    out_player["id"] = this_player.id
                    out_player["name"] = this_player.name
                    out_player["darts"] = this_player.darts
                    this_lag.playerdata.append(out_player)
            else:
                print(idx)
			#print(this_lag.playerdata)
            out_legs.append(this_lag)
            
        return out_legs

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

