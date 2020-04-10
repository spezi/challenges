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
		
		#print(len(self.league_members))
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
		
		#print("nötige begegnungen:")
		#print(jeder_gegen_jeden_list)

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
		#print(games_out)
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
		tabledata = statistic.calc_league_player_tabledata(self.league)
		#print("tabledata")
		#print(tabledata)

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
		print(len(players))

		prepare_legs = []
		for i in range(1,self.league.mode.legs + 1):
			#clear players
			self.players = set()
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
				print(self.players)

		print(prepare_legs)
		
		out_legs = []
		
		for this_lag in prepare_legs:
			this_lag.playerdata = []
			for this_player in self.players:
				out_player = {}
				this_player.darts = Dart.objects.filter(player=this_player, leg=this_lag)
				out_player["id"] = this_player.id
				out_player["name"] = this_player.name
				out_player["darts"] = this_player.darts
				this_lag.playerdata.append(out_player)

			#print(this_lag.playerdata)
			out_legs.append(this_lag)
				
		
		context['game'] = self.game
		context['players'] = self.players
		context['league'] = self.league
		context['legs'] = out_legs
		return context

class LegView(TemplateView):
	template_name = 'leg.html'
	players = []
	overthrowed = False
	win = False 

	def checkin(self):
		print(self.throw)

		try:
			save_dart = Dart(
				player= self.current_player, 
				leg= self.current_leg, 
				double= self.throw['double'],
				tripple= self.throw['tripple'],
				points= self.throw['points'],
				points_calc= self.throw['points'],
				)
			save_dart.save()

			if save_dart.double: save_dart.points_calc = save_dart.points_calc * 2
			if save_dart.tripple: save_dart.points_calc = save_dart.points_calc * 3
			save_dart.save()
			#print(save_dart)
			return True
		except Exception as e:
			print(str(e))
			return False
		#player_points = Points.objects.get(player=self.throw['player'], leg=self.throw['leg']) 
		#print(player_points.points)

	def scoring(self):
		init_points = self.current_league.mode.points
		points = init_points
		out_points = points
		self.overthrowed = False

		for index, dart in enumerate(self.current_player_darts):
			#print(dart.points_calc)
			if not dart.overthrowed:
				points = points - dart.points_calc
			#print(self.current_player.name)
			#print(points)
			if points == 0:
				if dart.double:
					print("wir haben einen Sieger!!")
					self.win = True
					self.current_leg.winner = self.current_player.id
					self.current_leg.save()
				else:
					print("kein double out !!")
					points = points + dart.points_calc
					
			elif points < 2:
				print('überworfen')
				thatround = self.get_player_throwed()
				print(thatround)
				
				#überworfene taggen und zur not die davor auch 
				#um punkte vor der runde wieder herzustellen 
				if thatround['first']:
					dart.overthrowed = True
					dart.save()
					self.overthrowed = True
				if thatround['second']:
					dart2 = self.current_player_darts[index-1]
					dart2.overthrowed = True
					dart2.save()
					self.overthrowed = True
				if thatround['third']:
					dart3 = self.current_player_darts[index-2]
					dart3.overthrowed = True
					dart3.save()
					self.overthrowed = True
				
		for dart_out in self.current_player_darts:			
			if not dart_out.overthrowed:
				out_points = out_points - dart_out.points_calc 
		
		return out_points
		

	def get_player_throwed(self):
		#print(len(self.current_player_darts))
		
		first = ''
		second = ''
		third = ''

		self.current_player_darts = Dart.objects.filter(player=self.current_player, leg=self.current_leg)

		throwed = len(self.current_player_darts) % 3 # 0 1 2 
		if throwed == 1:
			first = 'thrown'
		if throwed == 2:
			first = 'thrown'
			second = 'thrown'
		if throwed == 0:
			first = 'thrown'
			second = 'thrown'
			third = 'thrown'
		throwed_darts = {'first': first,'second': second, 'third':third}
		return throwed_darts

	def build_player_response(self):
		points = self.scoring()
		throwed = self.get_player_throwed()
		response = {
			'player': self.throw["player"], 
			'points': points, 
			'throwed': throwed, 
			'success': True, 
			'overthrowed': self.overthrowed,
			'win': self.win,
			}
		return response

	def post(self, request, *args, **kwargs):
		print("da kam was geflogen")
		#print(kwargs)
		
		self.throw = json.loads(request.body)
		#print(self.throw)

		self.current_league = League.objects.get(pk=kwargs['league_id']) # um den modus zu bekommen
		self.current_leg = Leg.objects.get(pk=kwargs['leg_id'])

		if self.throw['what'] == 'throw':
			self.current_player = Player.objects.get(pk=self.throw['player'])
			self.current_player_darts = Dart.objects.filter(player=self.current_player, leg=self.current_leg)
			
			try:
				if self.throw["player"]:
					if self.checkin(): 
						#return JsonResponse({'success': True })
						response = self.build_player_response()
						print(response)
						return JsonResponse(response) 
					else:
						return JsonResponse({'success': False, 'reason': 'checkin false' })
			except:
				return JsonResponse({'success': False })
		elif self.throw['what'] == 'undo':
			print(self.current_leg.id)
			try:
				lastdart = Dart.objects.filter(leg=self.current_leg).last()
				lastdart.delete()
				return JsonResponse({'success': True })
			except:
				return JsonResponse({'success': False })

	def get_context_data(self, *args, league_id, game_id, leg_id, **kwargs):

		self.game = Game.objects.get(pk=game_id)
		self.current_league = League.objects.get(pk=league_id)
		self.current_leg = Leg.objects.get(pk=leg_id)

		activeplayer = 'none'
		

		players = Player.objects.filter(game=self.game)

		#spielmodus ausgeben
		print(self.current_league.mode)

		self.players = []
		for player in players:
			#player_points, created = Points.objects.get_or_create(leg=self.leg, player=player, defaults={'point': self.league.mode.points})
			self.current_player = player
			self.current_player_darts = Dart.objects.filter(player=self.current_player, leg=self.current_leg)
			player_points = self.scoring()
			throwed = self.get_player_throwed()
			
			if throwed['third'] == 'thrown':
				throwed['first'] = ''
				throwed['second'] = ''
				throwed['third'] = ''
			else:
				activeplayer = self.current_player.id	

			playerdata = {
				'id': player.id,
				'name': player.name,
				'points': player_points,
				'darts': len(self.current_player_darts),
				'throwed': throwed
				}
			self.players.append(playerdata)
	
		#bei neu laden den richtigen player aktivieren
		lastdart = Dart.objects.filter(leg=self.current_leg).last()
		if activeplayer == 'none' and lastdart:
			#print(len(self.players))
			for i in range(len(self.players)):
				if self.players[i]['id'] == lastdart.player.id:
					j = i + 1
					if i == len(self.players) - 1: 
						 j = 0
					

					activeplayer = self.players[j]['id']


		context = super(LegView, self).get_context_data(*args, **kwargs)
		context['root'] = league_id
		context['game'] = self.game
		context['leg'] = self.current_leg
		context['players'] = self.players
		context['activeplayer'] = activeplayer
		context['range'] = range(21)
		return context