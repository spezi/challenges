from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View, TemplateView
from .models import *
from .forms import *
from django.http import JsonResponse
from .tables import LeagueTable
from .helper import Statistic


import json


#from rest_framework.views import APIView
#from rest_framework.response import Response
#from rest_framework import authentication, permissions
#from django.contrib.auth.models import User

# Create your views here.

class IndexView(TemplateView):
	template_name = 'index.html'

	def get_context_data(self, *args, **kwargs):
		context = super(IndexView, self).get_context_data(*args, **kwargs)
		context['leagues'] = League.objects.all()
		context['title'] = 'welcome'
		return context

class LeagueView(TemplateView):
	template_name = 'league.html'
	league_id = 0
	league_members = [] 

	def get_or_create_games(self):
		
		print(len(self.league_members))
		#get league player
		league_player_id_list = []
		for league_member in self.league_members:
			print(league_member.player)
			league_player_id_list.append(league_member.player.id)

		#prepare matches
		pre_game_list = []

		for challenger in league_player_id_list:
			for i in range(0,len(league_player_id_list)):
  				if league_player_id_list[i] != challenger:
					  #print("player " + str(challenger) + " <-> player " + str(league_player_id_list[i]))
					  pre_game_list.append(sorted([challenger, league_player_id_list[i]]))

		# magic to avoid doubles
		jeder_gegen_jeden_list = [] 
		[jeder_gegen_jeden_list.append(x) for x in pre_game_list if x not in jeder_gegen_jeden_list] 
		
		print("nötige begegnungen:")
		print(jeder_gegen_jeden_list)

		#check games created
		league_games = LeagueGames.objects.filter(league=self.league_id)
		#print(league_games)
		for league_game in league_games:
			game_members = GameMembership.objects.filter(game=league_game.game)
			comparelist = []
			for member in game_members:
				comparelist.append(member.player.id)
			#print(sorted(comparelist))
			if sorted(comparelist) in jeder_gegen_jeden_list:
				#print("gibts schon")
				jeder_gegen_jeden_list.remove(sorted(comparelist))

		#create rest if necessary
		for players in jeder_gegen_jeden_list:
			player_one = Player.objects.get(pk=players[0])
			player_two = Player.objects.get(pk=players[1])
		
			new_game_name = player_one.name + " <-> " + player_two.name  
			new_game = Game(name=new_game_name)
			new_game.save()
			new_game.members.add(player_one)
			new_game.members.add(player_two)
			new_game.save
			
			league_games_add = LeagueGames(league=self.league, game=new_game)
			league_games_add.save()
		
		# output
		games_out = []
		league_games = LeagueGames.objects.filter(league=self.league_id)
		for league_game in league_games:
			that_league_game = Game.objects.get(pk=league_game.id)
			games_out.append(that_league_game)
		print(games_out)
		return games_out

	def add_player(self, name, league_id):
		
		try:
			playerobj = Player.objects.get(name=name)
		except:
			return False

		print("player gefunden")
		inleague = {}

		try:
			inleague = LeagueMembership.objects.get(league=self.league.id, player=playerobj)
		except:
			league_member = LeagueMembership(league=self.league, player=playerobj)
			league_member.save()
			return True
		
		return False

	def post(self, request, *args, **kwargs):
		print("get post")
		
		form = AddPlayerForm(request.POST)

		if form.is_valid():
			name = form.cleaned_data['name']
			league_id = kwargs['league_id']
			self.league = League.objects.get(pk=league_id) 
			player_added = self.add_player(name, league_id)
			if player_added:
				return self.get(request, *args, **kwargs)
			else:
				return HttpResponse("Player konnte nicht hinzugefügt werden")

	def get_context_data(self, *args, league_id, **kwargs):
		context = super(LeagueView, self).get_context_data(*args, **kwargs)
		self.league_id = league_id
		self.league = League.objects.get(pk=league_id)
		self.league_members = LeagueMembership.objects.filter(league=league_id)
		#print(self.league_members)
		
		statistic = Statistic()
		tabledata = statistic.calc_league_player_tabledata(self.league, self.league_members)

		context['league'] = self.league 
		context['games'] = self.get_or_create_games()
		context['table'] = LeagueTable(tabledata)
		context['add_user_form'] = AddPlayerToLeagueForm()
		return context

class GameView(TemplateView):
	template_name = 'game.html'
	players = set()


	def get_context_data(self, *args, game_id, **kwargs):
		context = super(GameView, self).get_context_data(*args, **kwargs)
		
		
		self.game = Game.objects.get(pk=game_id)
		league = LeagueGames.objects.get(game=self.game)
		self.league = league.league
		
		print(self.league.mode.legs)
		players = GameMembership.objects.filter(game=self.game)
		
		prepare_legs = []
		for i in range(1,self.league.mode.legs + 1):
			leg, created = Leg.objects.get_or_create(
						number=i,
						game=self.game,
					)
			prepare_legs.append(leg)
			# get players leg state
			#print(players)
			for player in players:
				that_player = player.player
				#that_player.legdarts = Dart.objects.filter(player=that_player, leg=leg)
				#print(that_player.legdarts)
				#if that_player not in self.players: self.players.append(that_player)
				self.players.add(that_player)

		print(prepare_legs)
		
		out_players = []
		out_legs = []
		for this_lag in prepare_legs:
			this_lag.playerdata = []
			for this_player in self.players:
				this_player.darts = Dart.objects.filter(player=this_player, leg=this_lag)
				print(len(this_player.darts))
				this_lag.playerdata.append(this_player)
				
			out_legs.append(this_lag)
		
		#print(out_legs[0].playerdata[0].darts)
		
		context['game'] = self.game
		context['players'] = self.players
		context['league'] = self.league
		context['legs'] = out_legs
		return context

class LegView(TemplateView):
	template_name = 'leg.html'

	def get_context_data(self, *args, game_id, leg_id, **kwargs):
		context = super(LegView, self).get_context_data(*args, **kwargs)
		return context