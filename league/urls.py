from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:league_id>/', views.LeagueView.as_view(), name='League'),
    path('<int:league_id>/addplayerform', views.AddUserView.as_view(), name='Add Player'),
    #path('<int:league_id>/addplayer', views.add_player, name='League'),
    path('api', views.AjaxApi.as_view(), name='ajaxapi'),
    path('<int:league_id>/game/<int:game_id>', views.GameView.as_view(), name='Game'),
    path('<int:league_id>/game/<int:game_id>/save', views.save_to_game, name='Save Game'),
    path('<int:league_id>/game/<int:game_id>/leg/<int:leg_id>', views.LegView.as_view(), name='Leg'),
    path('counter', views.Counter.as_view(), name='counter'),
]