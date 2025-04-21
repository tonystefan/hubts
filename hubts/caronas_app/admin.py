from django.contrib import admin
from .models import Route, Vehicle, FuelPrice, Carpool, CarpoolParticipant

class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'distance_km', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('model', 'plate', 'owner', 'fuel_efficiency', 'capacity', 'is_active')
    list_filter = ('is_active', 'owner')
    search_fields = ('model', 'plate', 'owner__email', 'owner__first_name', 'owner__last_name')

class FuelPriceAdmin(admin.ModelAdmin):
    list_display = ('price', 'effective_date', 'created_by')
    list_filter = ('effective_date',)
    search_fields = ('price', 'created_by__email')
    date_hierarchy = 'effective_date'

class CarpoolParticipantInline(admin.TabularInline):
    model = CarpoolParticipant
    extra = 1
    autocomplete_fields = ['user']

class CarpoolAdmin(admin.ModelAdmin):
    list_display = ('date', 'route', 'vehicle', 'driver', 'direction', 'fuel_price', 'total_distance', 'fuel_cost')
    list_filter = ('date', 'direction', 'route', 'driver')
    search_fields = ('route__name', 'driver__email', 'driver__first_name', 'driver__last_name', 'notes')
    date_hierarchy = 'date'
    inlines = [CarpoolParticipantInline]
    autocomplete_fields = ['driver', 'vehicle', 'route']
    
    def total_distance(self, obj):
        return f"{obj.total_distance} km"
    total_distance.short_description = "Distância Total"
    
    def fuel_cost(self, obj):
        return f"R$ {obj.fuel_cost}"
    fuel_cost.short_description = "Custo de Combustível"

class CarpoolParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'carpool', 'has_paid', 'payment_date')
    list_filter = ('has_paid', 'payment_date', 'carpool__date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'carpool__route__name')
    autocomplete_fields = ['user', 'carpool']

admin.site.register(Route, RouteAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(FuelPrice, FuelPriceAdmin)
admin.site.register(Carpool, CarpoolAdmin)
admin.site.register(CarpoolParticipant, CarpoolParticipantAdmin)
