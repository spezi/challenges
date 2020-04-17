
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

class Statistic(object):
    league =  {}
    league_members = []
    league_games = []    
    league_legs = [] # not used iterate by game
    league_states = {}

    def collect_league_states(self):
        
        # erstmal spieler sammeln
        for member in self.league_members:
            self.league_states[member.player.id] = {
                'name': member.player.name,
                'games': 0,
                'winn': 0,
                'loose': 0,
                'remis': 0,
                'winlegs': 0,
                'looselegs': 0,
                'diff': 0,
                'points': 0,
                }
        
        #games daten sammeln und anreichern
        for game in self.league_games:
            
            game_player = Player.objects.filter(game=game)
            game_legs = Leg.objects.filter(game=game)
            
            legwins = 0
            for leg in game_legs:
                for player in game_player:
                    if leg.winner:
                    #leg gewinne zählen
                        if player.id == leg.winner:
                            self.league_states[player.id]['winlegs'] +=1
                            legwins += 1
                        #verlorene legs zählen 
                        else:
                            self.league_states[player.id]['looselegs'] +=1
            
            for player in game_player:
                #zu player games addieren wenn game zuende
                if game.winner:
                    if player.id == game.winner: 
                        self.league_states[player.id]['winn'] += 1
                    else:
                        self.league_states[player.id]['loose'] += 1
                else:
                    if self.league.mode.legs == legwins:
                        self.league_states[player.id]['remis'] += 1
        


    def gen_league_table(self):
        print("table will be generated")
        self.collect_league_states()
        player_data_rows = []
        
        for player_id, player_dict in self.league_states.items():
            
            #count games points and leg diff
            player_dict['games'] = player_dict['winn'] + player_dict['loose'] + player_dict['remis']
            player_dict['points'] = player_dict['winn'] * 2 + player_dict['remis']
            player_dict['diff'] = player_dict['winlegs'] - player_dict['looselegs']

            player_data_rows.append(player_dict)
        
        return player_data_rows

