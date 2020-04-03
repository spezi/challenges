from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View, TemplateView
from .models import League, Games, Game, GameMembership, LeagueMembership, Points, Player, Leg, LegPoints, ThrowSet, Dart
from .forms import AddPlayerForm, AddPlayerToLeagueForm
from django.http import JsonResponse
from .tables import LeagueTable
from .helper import Statistic

import json


#from rest_framework.views import APIView
#from rest_framework.response import Response
#from rest_framework import authentication, permissions
#from django.contrib.auth.models import User

# Create your views here.


def save_to_game(request, league_id, game_id):
    data = [{'name': 'Peter', 'email': 'peter@example.org'},
            {'name': 'Julia', 'email': 'julia@example.org'}]
    return JsonResponse(data, safe=False)

def save_to_leg(request, leg_id):
    data = [{'name': 'Peter', 'email': 'peter@example.org'},
            {'name': 'Julia', 'email': 'julia@example.org'}]
    return JsonResponse(data, safe=False)

def add_player(request):
	#print(request)
	#print(league_id)
	data = [{'league_id': 1, 'player': 1}]
	if request.method == 'POST':
		print("yes got a post")
		return JsonResponse(data, safe=False)

def build_counter():
	counter = {"range" : 20,}
	return counter

#Frickl Frickl
def get_game_data(games):
	games_out = []
	try:
		for game in games:
			#print("output:")
			#print(game.name)
			game.players = GameMembership.objects.filter(game=game.id)
			games_out.append(game)
			for player in game.players:
				print('player.player.name')
	except:
		games.players = GameMembership.objects.filter(game=games.id)
		games.points = Points.objects.filter(game=games.id)
		#print("points")
		#print(games.points)
		games_out.append(games)

		#for player in games.players:
		#	print(player.player.name)

	return games_out

class IndexView(TemplateView):
	template_name = 'index.html'

	def get_context_data(self, *args, **kwargs):
		context = super(IndexView, self).get_context_data(*args, **kwargs)
		context['title'] = 'welcome'
		context['leagues'] = League.objects.all()
		return context

class Counter(TemplateView):
	template_name = 'counter.html'

	def get_context_data(self, *args, **kwargs):
		context = super(Counter, self).get_context_data(*args, **kwargs)
		context['name'] = 'Gryffindor'
		return context

class LeagueView(TemplateView):
	template_name = 'league.html'
	#

	def add_player(self, name, league_id):
		
		try:
			playerobj = Player.objects.get(name=name)
			league = self.get_league(league_id)
		except:
			return False
		
		inleague = {}	
		
		try:
			inleague = LeagueMembership.objects.get(league=league, player=playerobj)
		except:
			league_member = LeagueMembership(league=league, player=playerobj)
			league_member.save()

		#print(inleague)

		#league_member = LeagueMembership(league=league, player=playerobj)
		#league_member.save()

		#print(playerobj)
		#print(league_id)
		return True

	def post(self, request, *args, **kwargs):
		print("get post")
		
		form = AddPlayerForm(request.POST)

		if form.is_valid():
			name = form.cleaned_data['name']
			league_id = kwargs['league_id']
			player_added = self.add_player(name, league_id)
			if player_added:
				return self.get(request, *args, **kwargs)
			else:
				return HttpResponse("Player konnte nicht hinzugefügt werden")

	def get_league(self, league_id):
		try:
			league = League.objects.get(pk=league_id)
		except League.DoesNotExist:
			return HttpResponse("League does not exist")
		return league

	def get_games(self, league_id):
		
		games = Games.objects.filter(league=league_id)
		games_out = get_game_data(games)
		#return games
		
		return games_out 

	def get_or_create_games(self, league_players):

		league_player_id_list = []

		for league_player in league_players:
			league_player_id_list.append(league_player.player.id)

		print(league_player_id_list)

		pre_game_list = []
		
		for challenger in league_player_id_list:
			for i in range(0,len(league_player_id_list)):
  				if league_player_id_list[i] != challenger:
					  #print("player " + str(challenger) + " <-> player " + str(league_player_id_list[i]))
					  pre_game_list.append(sorted([challenger, league_player_id_list[i]]))

		#m = [i for i in l if i[0] == 'a']
		
		# magie zum doppelte rausschmeissen
		jeder_gegen_jeden_list = [] 
		[jeder_gegen_jeden_list.append(x) for x in pre_game_list if x not in jeder_gegen_jeden_list] 

		#print(jeder_gegen_jeden_list)

		tocheckgames = Games.objects.filter(league=self.league_id)
		schon_vorhanden_list = []
		#print(checkgames)
		for checkgame in tocheckgames:
			#print(checkgame.id)
			checkgame_membership = GameMembership.objects.filter(game=checkgame.id)
			#zum gegenprüfen
			checkgame_paar = []
		
			for thatgame in checkgame_membership:
				checkgame_paar.append(thatgame.player.id)

			#
			# das pärchen spiel gibt es schon
			checkgame_paar = sorted(checkgame_paar)
			#print(checkgame_paar)
			schon_vorhanden_list.append(checkgame_paar)
		
		for check_or_create_match in jeder_gegen_jeden_list:
			#print(check_or_create_match)
			#print(schon_vorhanden_list)
			if check_or_create_match not in schon_vorhanden_list:
				
				p1 = Player.objects.get(id=check_or_create_match[0])
				p2 = Player.objects.get(id=check_or_create_match[1])
				
				new_game_name = p1.name + " <-> " + p2.name + " : " + self.league.name
				new_games = Games(name=new_game_name)
				new_games.player_quantity = 2
				new_games.league = self.league
				new_games.save()

				new_game_members_p1 = GameMembership(game=new_games, player=p1)
				new_game_members_p2 = GameMembership(game=new_games, player=p2)
				new_game_members_p1.save()
				new_game_members_p2.save()


		games = Games.objects.filter(league=self.league_id)
		games_out = get_game_data(games)
		#return games
		
		return games_out 

	def get_context_data(self, *args, league_id, **kwargs):
		context = super(LeagueView, self).get_context_data(*args, **kwargs)
		self.league_id = league_id
		league = self.get_league(league_id)
		self.league = league
		#games = self.get_games(league_id)

		league_players = LeagueMembership.objects.filter(league=league_id)
		games = self.get_or_create_games(league_players)

		statistic = Statistic()
		tabledata = statistic.calc_league_player_tabledata(league, league_players)

		#context['players'] = league_players
		context['league'] = league
		context['games'] = games
		context['table'] = LeagueTable(tabledata)
		context['add_user_form'] = AddPlayerToLeagueForm()
		return context

class GameView(TemplateView):
	template_name = 'game.html'
	legs_count = 8

	def get_game(self, game_id):
		try:
			game = Games.objects.get(pk=game_id)
			game.points = Points.objects.filter(game=game.id)
		except Games.DoesNotExist:
			raise Http404("Games does not exist")

		game_data = get_game_data(game)
		print(game_data)
		return game

	def get_context_data(self, *args, game_id, **kwargs):
		context = super(GameView, self).get_context_data(*args, **kwargs)
		games = Games.objects.get(pk=game_id)
		#game = Game.objects.get(pk=games)
		game, created = Game.objects.get_or_create(
					games=games,
				)
		if len(game.name) == 0:
			game.name = games.name
			game.save()

		print("game:")
		print(game.name)

		players = GameMembership.objects.filter(game=games)

		out_legs = []
		for i in range(1,self.legs_count + 1):
			leg, created = Leg.objects.get_or_create(
						number=i,
						game=game,
					)
			# würfe zählen
			leg.player = []
			for player in players:
				sets = ThrowSet.objects.filter(player=player.player, leg=leg)
				leg.player.append({ "name": player.player.name, "sets": len(sets)})
			out_legs.append(leg)


		context['players'] = players
		context['games'] = games
		context['legs'] = out_legs
		
	
		return context

class LegView(TemplateView):
	template_name = 'leg.html'
	

	def get_game(self, game_id):
		try:
			game = Games.objects.get(pk=game_id)
			game.points = Points.objects.filter(game=game.id)
		except League.DoesNotExist:
			raise Http404("Games does not exist")

		game_data = get_game_data(game)
		print(game_data)
		return game

	def get_context_data(self, *args, game_id, leg_id, **kwargs):
		context = super(LegView, self).get_context_data(*args, **kwargs)
		games = self.get_game(game_id)
		game = Game.objects.get(games=games)

		
		leg = Leg.objects.get(game=game, id=leg_id)
		throwsets = ThrowSet.objects.filter(leg=leg)

		print("len(throwsets)")
		print(len(throwsets))
		
		player = set()
		playerdata = set()
		playerobjs = set()

		gamemember = GameMembership.objects.filter(game=games)
		for member in gamemember:
			playerobjs.add(member.player)
			 	 
			

		for p in playerobjs :
			legpoints, created = LegPoints.objects.get_or_create(
					player = p,
					game = game,
					leg = leg,
					defaults={'points': 501} 
				)

			####################################
			#spiellogic init der legpoints
			####################################

			playerdata.add(legpoints)

		print("playersens")
		print(player)

		context['player'] = player
		context['playerdata'] = playerdata
		context['leg'] = leg
		context['games'] = games
		#context['game'] = game
		context['range'] = range(21) # für die buttons
		
	
		return context

# Badges 3 x tripple 20 
# oder 3 x bull
# oder 3 x tripple 19


class AddUserView(TemplateView):
	template_name = 'adduserform.html'
	
	def get_context_data(self, *args, league_id, **kwargs):
		context = super(AddUserView, self).get_context_data(*args, **kwargs)		
		context["players"] = Player.objects.all()
		return context

class AjaxApi(View):

	def evaluation(self):
			####################################
			#spiellogic rest
			####################################

		print("na logisch ..")
		print(self.current_darts)
		print(self.legpoints.points)

		double = False
		tripple = False
		checkin = False
			 
		if self.current_darts[0].double or self.current_darts[1].double or self.current_darts[2].double:
				print("da kahm doch a dubble")
				double = True

		if self.current_darts[0].tripple or self.current_darts[1].tripple or self.current_darts[2].tripple:
				print("da kahm doch a tripple")
				tripple = True

		if self.legpoints.points == 501:
			print("erster wurf")
			if not double and not tripple:
				checkin = True
			else:
				return False

		self.legpoints.points = self.legpoints.points - self.current_darts[0].points
		if self.legpoints.points > 1:
			print(self.legpoints.points)
			self.legpoints.points = self.legpoints.points - self.current_darts[1].points
			if self.legpoints.points > 1:
				self.legpoints.points = self.legpoints.points - self.current_darts[2].points

		print(self.legpoints.points)
		if self.legpoints.points > 1:
			checkin = True
		

		if self.legpoints.points == 0 and double:
			print("jewonna!!")
			checkin = True

		if checkin:
			self.checkin_points()
			return True

	def checkin_points(self):
		print("checkin points")
		print(self.legpoints.points)
		try:
			self.legpoints.save()
			return True
		except:
			return False
			

	def save_throw(self, thatrequest):
		#print(thatrequest["leg_id"])
		#print(thatrequest["userid"])

		thatleg = Leg.objects.get(pk=thatrequest["leg_id"])
		thatplayer = Player.objects.get(pk=thatrequest["userid"])

		thatleg.last_thrown = thatplayer.id
		thatleg.save()

		self.legpoints = LegPoints.objects.get(player=thatplayer, leg=thatleg)

		print(self.legpoints.id)

		try:
			newthrowset = ThrowSet(player=thatplayer, leg=thatleg)
			newthrowset.save()

			round_dict = thatrequest["round"]

			dart_one = Dart(
					throwset= newthrowset, 
					points = round_dict["first"],
					double = round_dict["f_double"],
					tripple = round_dict["f_tripple"],
					)
			dart_one.save()
			dart_two = Dart(
					throwset= newthrowset, 
					points = round_dict["second"],
					double = round_dict["s_double"],
					tripple = round_dict["s_tripple"],
					)
			dart_two.save()
			dart_three = Dart(
					throwset= newthrowset, 
					points = round_dict["third"],
					double = round_dict["t_double"],
					tripple = round_dict["t_tripple"],
					)
			dart_three.save()

			self.current_darts = [dart_one,dart_two,dart_three] 
			
			if self.evaluation():
				return True
			else:
				return False
			
		except:
			return False
		
		

	def post(self, request):
		print("Api request:")

		thatrequest = json.loads(request.body)
		#if thatthrow
		if thatrequest["what"] == "throw":
			print("da kam was geflogen")
			if self.save_throw(thatrequest):
				return JsonResponse({'success': True })
			else:
				return JsonResponse({'success': False })