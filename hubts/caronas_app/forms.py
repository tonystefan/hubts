from django import forms
from .models import Route, Vehicle, FuelPrice, Carpool, CarpoolParticipant
from core.models import User

class RouteForm(forms.ModelForm):
    """Form for creating and updating routes."""
    class Meta:
        model = Route
        fields = ['name', 'distance_km', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class VehicleForm(forms.ModelForm):
    """Form for creating and updating vehicles."""
    class Meta:
        model = Vehicle
        fields = ['model', 'plate', 'fuel_efficiency', 'capacity', 'is_active']

class FuelPriceForm(forms.ModelForm):
    """Form for creating and updating fuel prices."""
    class Meta:
        model = FuelPrice
        fields = ['price', 'effective_date']
        widgets = {
            'effective_date': forms.DateInput(attrs={'type': 'date'}),
        }

class CarpoolForm(forms.ModelForm):
    """Form for creating and updating carpools."""
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Participantes"
    )
    
    class Meta:
        model = Carpool
        fields = ['date', 'route', 'vehicle', 'driver', 'direction', 'fuel_price', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter vehicles by owner if user is provided
        if user:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(owner=user, is_active=True)
            
            # Set initial fuel price
            if not self.instance.pk:  # Only for new instances
                self.fields['fuel_price'].initial = FuelPrice.get_current_price()
        
        # For existing carpools, initialize participants field
        if self.instance.pk:
            self.fields['participants'].initial = User.objects.filter(
                carpool_participations__carpool=self.instance
            )

class CarpoolParticipantForm(forms.ModelForm):
    """Form for updating carpool participant payment status."""
    class Meta:
        model = CarpoolParticipant
        fields = ['has_paid', 'payment_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

class CarpoolSearchForm(forms.Form):
    """Form for searching carpools."""
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Data Inicial"
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Data Final"
    )
    route = forms.ModelChoiceField(
        queryset=Route.objects.filter(is_active=True),
        required=False,
        label="Rota"
    )
    driver = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Motorista"
    )
    participant = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Participante"
    )
