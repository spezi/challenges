from django import forms
from .models import *

class AddLeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

class LeagueModesForm(forms.ModelForm):
    class Meta:
        model = Modes
        fields = ['points', 'checkin', 'checkout', 'winmod', 'legs']
        widgets = {
            'points': forms.Select(attrs={'class': 'form-control'}),
            'checkin': forms.Select(attrs={'class': 'form-control'}),
            'checkout': forms.Select(attrs={'class': 'form-control'}),
            'winmod': forms.Select(attrs={'class': 'form-control'}),
            'legs': forms.NumberInput(
                attrs={'class': 'form-control'}
                ),
        }

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

class RemovePlayerToLeagueForm(forms.Form):

    name = forms.ModelChoiceField(
            queryset=Player.objects.none(), 
            empty_label="...", 
            to_field_name="name",
            widget = StyledSelect,
        )
    
    def __init__(self, league, *args, **kwargs):
        super(RemovePlayerToLeagueForm, self).__init__(*args, **kwargs)
        self.fields['name'].queryset = Player.objects.filter(league=league)
        