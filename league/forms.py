from django import forms
from .models import Player

class AddPlayerForm(forms.Form):
    name = forms.CharField(label='Add Player', max_length=100)

class StyledSelect(forms.Select):
    template_name = 'styledselect.html'

class AddPlayerToLeagueForm(forms.Form):
    name = forms.ModelChoiceField(
        queryset=Player.objects.all(), 
        empty_label="...", 
        to_field_name="name",
        widget = StyledSelect,
    )