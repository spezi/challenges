from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View, TemplateView
from .models import *
from .forms import *
from django.http import JsonResponse
from .tables import LeagueTable
from .helper import Statistic, LegFake, LegFactory


import json


#from rest_framework.views import APIView
#from rest_framework.response import Response
#from rest_framework import authentication, permissions
#from django.contrib.auth.models import User

# Create your views here.

class IndexView(TemplateView):
	template_name = 'index.html'
	add_league_form = AddLeagueForm()
	add_league_mod_form = LeagueModesForm()

	def get_context_data(self, *args, **kwargs):
		context = super(IndexView, self).get_context_data(*args, **kwargs)
		print(self.add_league_form)
		context['leagues'] = League.objects.all()
		context['addleagueform'] = self.add_league_form 
		context['addleaguemodform'] = self.add_league_mod_form 
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
		
		league_games = self.get_or_create_games()

		tabledata =''
		statistic = Statistic()
		statistic.league=self.league 
		statistic.league_members=self.league_members
		statistic.league_games = league_games 
		tabledata = statistic.gen_league_table()
		#print("tabledata")
		#print(tabledata)

		league_table = LeagueTable(tabledata)
		league_table.order_by = "-points"

		# auch remis grün darstellen
		for game in league_games:
			legwinns = 0 
			game_legs = Leg.objects.filter(game=game)
			for leg in game_legs:
				if leg.winner: legwinns += 1
			if legwinns == self.league.mode.legs:
				game.winner = True

		context['league'] = self.league 
		context['games'] = league_games
		context['table'] = league_table
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
			
			self.players = set()
		
			leg = LegFake()
			leg.id = int(i)
			leg.number = int(i) 
			leg.game = self.game
			leg.players = self.players
			leg.winner = None 
			leg.blocked = True
			prepare_legs.append(leg)
			
		
			for player in players:
				that_player = player.player
				self.players.add(that_player)
				print(self.players)

		print(prepare_legs)
		
		legfactory = LegFactory()
		legfactory.players = self.players
		legfactory.game = self.game
		out_legs = legfactory.get_or_build_legs(prepare_legs)


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
	throw = {}
	current_dart_of_set = 0
	game = {}

	def check_game_win(self, game_id):
		self.game = Game.objects.get(pk=game_id)
		neededwinns = self.current_league.mode.legs / 2 + 1
		game_legs = Leg.objects.filter(game=self.game)
		winnerset = set()
		winnerlist = []
		for leg in game_legs:
			print('get winners:')
			winnerlist.append(leg.winner)
			if leg.winner: winnerset.add(leg.winner)
		print(winnerset)
		for winner in winnerset:
			count = winnerlist.count(winner)
			print('count winns: ' + str(count))
			if count >= neededwinns:
				self.game.winner = winner
				self.game.save()
				return True
		return False # wenn nicht dann könnte link fürs nächste Leg angezeigt werden

	def scoring(self):
		init_points = self.current_league.mode.points
		points = init_points
		out_points = points

		for index, dart in enumerate(self.current_player_darts):
			if dart.count and not dart.overthrowed:
				points = points - dart.points_calc
		
		out_points = points
		return out_points
		
	def get_player_throwed(self):
		#print(len(self.current_player_darts))
		first = ''
		second = ''
		third = ''

		self.current_player_darts = Dart.objects.filter(player=self.current_player, leg=self.current_leg)

		throwed = len(self.current_player_darts) % 3 # 0 1 2 
		print("throwed darts: " + str(len(self.current_player_darts)))
		print("throwed module: " + str(throwed))
		if self.current_player_points != self.current_league.mode.points: # damit am start nicht alle schon geworfen sind
			if throwed == 1:
				first = 'thrown'
				self.current_dart_of_set = 1
			if throwed == 2:
				first = 'thrown'
				second = 'thrown'
				self.current_dart_of_set = 2
			if throwed == 0:
				first = 'thrown'
				second = 'thrown'
				third = 'thrown'
				self.current_dart_of_set = 3
		throwed_darts = {'first': first,'second': second, 'third':third}
		return throwed_darts

	def checkin_dart(self, points_calc):
		print('###')
		print(self.throw)
		print(self.overthrowed)
		print('###')
		try:
			save_dart = Dart(
				player= self.current_player, 
				leg= self.current_leg, 
				double= self.throw['double'],
				tripple= self.throw['tripple'],
				points= self.throw['points'],
				points_calc= points_calc,
				overthrowed= self.overthrowed,
				count= True,
				)
			save_dart.save()
			ret = True
		except Exception as e:
			print(str(e))
			ret = False

		# noch mal danach abfragen
		self.throwed = self.get_player_throwed()
		print('self.throwed nach dart speichern')
		print(self.throwed)
		return ret

	def fill_dart_set(self):
		ret = False
		print("fill dart set")
		print(self.current_player)
		print(self.throwed)
		fillcount = 0
		if not self.throwed['second']:
			fillcount += 1
		if not self.throwed['third']:
			fillcount += 1
		#print(fillcount)
		for i in range(fillcount):
			try:
				save_dart = Dart(
					player= self.current_player, 
					leg= self.current_leg, 
					double= False,
					tripple= False,
					points= 0,
					points_calc= 0,
					overthrowed= self.overthrowed,
					count= False,
					)
				save_dart.save()
				ret = True
			except Exception as e:
				print(str(e))
				ret = False
		
		# noch mal danach abfragen
		self.throwed = self.get_player_throwed()
		print('self.throwed nach dart speichern')
		print(self.throwed)

		return ret
	def set_overthrowed_for_all_in_set(self):
		print("overthrowed for whole set")
		print(self.throwed)
		last_darts = []
		if self.throwed['second']:
			last_darts = Dart.objects.filter(player=self.current_player, leg=self.current_leg).order_by('-id')[:2]
		if self.throwed['third']:
			last_darts = Dart.objects.filter(player=self.current_player, leg=self.current_leg).order_by('-id')[:3]
		print(last_darts)
		for dart in last_darts:
			dart.overthrowed = True
			dart.save()
		return True

	def score_dart(self):
		point_before = self.current_player_points
		points = point_before
		self.overthrowed = False

		#calc throw points
		throw_points = self.throw['points']
		if self.throw['double']:
				throw_points = self.throw['points'] * 2
			
		if self.throw['tripple']:
			throw_points = self.throw['points'] * 3
		
		#spiellogic
		points = point_before - throw_points
		
		if points == 0:
			if self.throw['double']:
				print("wir haben einen Sieger!!")
				self.win = True
				self.current_leg.winner = self.current_player.id
				self.current_leg.save()
			else:
				print("kein double out !!")
				self.overthrowed = True
		elif points < 2:
			self.overthrowed = True
		else:
			self.current_player_points = points

		dart_checkin =  self.checkin_dart(throw_points)

		if self.overthrowed:
			setforall = self.set_overthrowed_for_all_in_set()
			if setforall: 
				self.fill_dart_set()
				points = self.scoring() #auf punkte for dem set berechnen
				

		if dart_checkin:
			response = {
					'player': self.throw["player"], 
					'points': points, 
					'throwed': self.throwed, 
					'success': True, 
					'overthrowed': self.overthrowed,
					'win': self.win,
					}
		else:
			response = {'success': False, 'score_dart': False}

		
		return response

	def post(self, request, *args, **kwargs):
		
		print("da kam was geflogen")
		self.throw = json.loads(request.body)
		print(self.throw)

		self.current_league = League.objects.get(pk=kwargs['league_id']) # um den modus zu bekommen
		self.current_leg = Leg.objects.get(pk=kwargs['leg_id'])

		if self.throw['what'] == 'throw':
			self.current_player = Player.objects.get(pk=self.throw['player'])
			self.current_player_darts = Dart.objects.filter(player=self.current_player, leg=self.current_leg)
			self.current_player_points = self.scoring()
			self.throwed = self.get_player_throwed()
			response= {'success': False }

			try:
				response = self.score_dart()
			except Exception as e:
				print(str(e))
				response = {'success': False }

			self.check_game_win(kwargs['game_id'])
			return JsonResponse(response)

		elif self.throw['what'] == 'undo':
			print(self.current_leg.id)
			try:
				lastdart = Dart.objects.filter(leg=self.current_leg).last()
				lastdart.delete()
				print('gibts schon nen winner??')
				print(self.current_leg.winner)
				if self.current_leg.winner: 
					self.current_leg.winner = None
					self.current_leg.save()
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
			
			self.current_player_points = self.scoring()
			
			self.throwed = self.get_player_throwed()

			if self.throwed['third'] == 'thrown':
				self.throwed['first'] = ''
				self.throwed['second'] = ''
				self.throwed['third'] = ''
			else:
				activeplayer = self.current_player.id	

			playerdata = {
				'id': player.id,
				'name': player.name,
				'points': self.current_player_points,
				'darts': len(self.current_player_darts),
				'throwed': self.throwed
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

		#anfänger auswählbar machen
		current_leg_darts = Dart.objects.filter(leg=self.current_leg)
		print('current leg darts' + str(len(current_leg_darts)))
		if len(current_leg_darts) == 0:
			activeplayer = 'none'
		
		self.check_game_win(game_id)

		context = super(LegView, self).get_context_data(*args, **kwargs)
		context['root'] = league_id
		context['game'] = self.game
		context['leg'] = self.current_leg
		context['players'] = self.players
		context['activeplayer'] = activeplayer
		context['range'] = range(21)
		return context