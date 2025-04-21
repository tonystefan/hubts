from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from django.http import HttpResponse
import csv
import datetime

from .models import Route, Vehicle, FuelPrice, Carpool, CarpoolParticipant
from .forms import (
    RouteForm, VehicleForm, FuelPriceForm, CarpoolForm, 
    CarpoolParticipantForm, CarpoolSearchForm
)
from core.models import User, AppPermission

def has_caronas_permission(user, required_role='viewer'):
    """Check if user has permission to access caronas app with specified role."""
    if user.is_superuser:
        return True
    
    role_levels = {
        'viewer': 0,
        'editor': 1,
        'manager': 2,
        'admin': 3
    }
    
    required_level = role_levels.get(required_role, 0)
    
    try:
        permission = AppPermission.objects.get(user=user, app='caronas_app')
        user_level = role_levels.get(permission.role, 0)
        return user_level >= required_level
    except AppPermission.DoesNotExist:
        return False

@login_required
def index(request):
    """Dashboard for the caronas app."""
    if not has_caronas_permission(request.user):
        messages.error(request, "Você não tem permissão para acessar o aplicativo de Caronas.")
        return redirect('dashboard:index')
    
    # Get recent carpools
    recent_carpools = Carpool.objects.all().order_by('-date')[:5]
    
    # Get user's carpools (as driver or participant)
    user_carpools = Carpool.objects.filter(
        Q(driver=request.user) | Q(participants__user=request.user)
    ).distinct().order_by('-date')[:5]
    
    # Calculate user balance
    balance = calculate_user_balance(request.user)
    
    # Get statistics
    total_carpools = Carpool.objects.count()
    total_routes = Route.objects.count()
    total_vehicles = Vehicle.objects.count()
    
    # Calculate total distance and savings
    carpools = Carpool.objects.all()
    total_distance = sum(carpool.total_distance for carpool in carpools)
    total_cost = sum(carpool.fuel_cost for carpool in carpools)
    
    context = {
        'recent_carpools': recent_carpools,
        'user_carpools': user_carpools,
        'balance': balance,
        'total_carpools': total_carpools,
        'total_routes': total_routes,
        'total_vehicles': total_vehicles,
        'total_distance': total_distance,
        'total_cost': total_cost,
        'current_fuel_price': FuelPrice.get_current_price(),
    }
    
    return render(request, 'caronas_app/index.html', context)

# Route views
@login_required
def route_list(request):
    """List all routes."""
    if not has_caronas_permission(request.user):
        messages.error(request, "Você não tem permissão para acessar o aplicativo de Caronas.")
        return redirect('dashboard:index')
    
    routes = Route.objects.all()
    return render(request, 'caronas_app/route_list.html', {'routes': routes})

@login_required
def route_create(request):
    """Create a new route."""
    if not has_caronas_permission(request.user, 'editor'):
        messages.error(request, "Você não tem permissão para criar rotas.")
        return redirect('caronas_app:route_list')
    
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Rota criada com sucesso!")
            return redirect('caronas_app:route_list')
    else:
        form = RouteForm()
    
    return render(request, 'caronas_app/route_form.html', {'form': form, 'title': 'Nova Rota'})

@login_required
def route_update(request, pk):
    """Update an existing route."""
    if not has_caronas_permission(request.user, 'editor'):
        messages.error(request, "Você não tem permissão para editar rotas.")
        return redirect('caronas_app:route_list')
    
    route = get_object_or_404(Route, pk=pk)
    
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, "Rota atualizada com sucesso!")
            return redirect('caronas_app:route_list')
    else:
        form = RouteForm(instance=route)
    
    return render(request, 'caronas_app/route_form.html', {'form': form, 'title': 'Editar Rota'})

@login_required
def route_delete(request, pk):
    """Delete a route."""
    if not has_caronas_permission(request.user, 'manager'):
        messages.error(request, "Você não tem permissão para excluir rotas.")
        return redirect('caronas_app:route_list')
    
    route = get_object_or_404(Route, pk=pk)
    
    if request.method == 'POST':
        # Check if route is used in any carpool
        if route.carpools.exists():
            messages.error(request, "Esta rota não pode ser excluída porque está sendo usada em caronas.")
            return redirect('caronas_app:route_list')
        
        route.delete()
        messages.success(request, "Rota excluída com sucesso!")
        return redirect('caronas_app:route_list')
    
    return render(request, 'caronas_app/route_confirm_delete.html', {'route': route})

# Vehicle views
@login_required
def vehicle_list(request):
    """List all vehicles."""
    if not has_caronas_permission(request.user):
        messages.error(request, "Você não tem permissão para acessar o aplicativo de Caronas.")
        return redirect('dashboard:index')
    
    # Regular users see only their vehicles, admins see all
    if has_caronas_permission(request.user, 'admin'):
        vehicles = Vehicle.objects.all()
    else:
        vehicles = Vehicle.objects.filter(owner=request.user)
    
    return render(request, 'caronas_app/vehicle_list.html', {'vehicles': vehicles})

@login_required
def vehicle_create(request):
    """Create a new vehicle."""
    if not has_caronas_permission(request.user, 'viewer'):
        messages.error(request, "Você não tem permissão para criar veículos.")
        return redirect('caronas_app:vehicle_list')
    
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            vehicle.save()
            messages.success(request, "Veículo criado com sucesso!")
            return redirect('caronas_app:vehicle_list')
    else:
        form = VehicleForm()
    
    return render(request, 'caronas_app/vehicle_form.html', {'form': form, 'title': 'Novo Veículo'})

@login_required
def vehicle_update(request, pk):
    """Update an existing vehicle."""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    
    # Check if user is owner or admin
    if vehicle.owner != request.user and not has_caronas_permission(request.user, 'admin'):
        messages.error(request, "Você não tem permissão para editar este veículo.")
        return redirect('caronas_app:vehicle_list')
    
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, "Veículo atualizado com sucesso!")
            return redirect('caronas_app:vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)
    
    return render(request, 'caronas_app/vehicle_form.html', {'form': form, 'title': 'Editar Veículo'})

@login_required
def vehicle_delete(request, pk):
    """Delete a vehicle."""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    
    # Check if user is owner or admin
    if vehicle.owner != request.user and not has_caronas_permission(request.user, 'admin'):
        messages.error(request, "Você não tem permissão para excluir este veículo.")
        return redirect('caronas_app:vehicle_list')
    
    if request.method == 'POST':
        # Check if vehicle is used in any carpool
        if vehicle.carpools.exists():
            messages.error(request, "Este veículo não pode ser excluído porque está sendo usado em caronas.")
            return redirect('caronas_app:vehicle_list')
        
        vehicle.delete()
        messages.success(request, "Veículo excluído com sucesso!")
        return redirect('caronas_app:vehicle_list')
    
    return render(request, 'caronas_app/vehicle_confirm_delete.html', {'vehicle': vehicle})

# Fuel Price views
@login_required
def fuel_price_list(request):
    """List all fuel prices."""
    if not has_caronas_permission(request.user):
        messages.error(request, "Você não tem permissão para acessar o aplicativo de Caronas.")
        return redirect('dashboard:index')
    
    fuel_prices = FuelPrice.objects.all().order_by('-effective_date')
    return render(request, 'caronas_app/fuel_price_list.html', {'fuel_prices': fuel_prices})

@login_required
def fuel_price_create(request):
    """Create a new fuel price."""
    if not has_caronas_permission(request.user, 'editor'):
        messages.error(request, "Você não tem permissão para criar preços de combustível.")
        return redirect('caronas_app:fuel_price_list')
    
    if request.method == 'POST':
        form = FuelPriceForm(request.POST)
        if form.is_valid():
            fuel_price = form.save(commit=False)
            fuel_price.created_by = request.user
            fuel_price.save()
            messages.success(request, "Preço de combustível criado com sucesso!")
            return redirect('caronas_app:fuel_price_list')
    else:
        form = FuelPriceForm(initial={'effective_date': timezone.now().date()})
    
    return render(request, 'caronas_app/fuel_price_form.html', {'form': form, 'title': 'Novo Preço de Combustível'})

@login_required
def fuel_price_update(request, pk):
    """Update an existing fuel price."""
    if not has_caronas_permission(request.user, 'editor'):
        messages.error(request, "Você não tem permissão para editar preços de combustível.")
        return redirect('caronas_app:fuel_price_list')
    
    fuel_price = get_object_or_404(FuelPrice, pk=pk)
    
    if request.method == 'POST':
        form = FuelPriceForm(request.POST, instance=fuel_price)
        if form.is_valid():
            form.save()
            messages.success(request, "Preço de combustível atualizado com sucesso!")
            return redirect('caronas_app:fuel_price_list')
    else:
        form = FuelPriceForm(instance=fuel_price)
    
    return render(request, 'caronas_app/fuel_price_form.html', {'form': form, 'title': 'Editar Preço de Combustível'})

@login_required
def fuel_price_delete(request, pk):
    """Delete a fuel price."""
    if not has_caronas_permission(request.user, 'manager'):
        messages.error(request, "Você não tem permissão para excluir preços de combustível.")
        return redirect('caronas_app:fuel_price_list')
    
    fuel_price = get_object_or_404(FuelPrice, pk=pk)
    
    if request.method == 'POST':
        fuel_price.delete()
        messages.success(request, "Preço de combustível excluído com sucesso!")
        return redirect('caronas_app:fuel_price_list')
    
    return render(request, 'caronas_app/fuel_price_confirm_delete.html', {'fuel_price': fuel_price})

# Carpool views
@login_required
def carpool_list(request):
    """List all carpools with search functionality."""
    if not has_caronas_permission(request.user):
        messages.error(request, "Você não tem permissão para acessar o aplicativo de Caronas.")
        return redirect('dashboard:index')
    
    form = CarpoolSearchForm(request.GET)
    carpools = Carpool.objects.all()
    
    if form.is_valid():
        if form.cleaned_data.get('start_date'):
            carpools = carpools.filter(date__gte=form.cleaned_data['start_date'])
        
        if form.cleaned_data.get('end_date'):
            carpools = carpools.filter(date__lte=form.cleaned_data['end_date'])
        
        if form.cleaned_data.get('route'):
            carpools = carpools.filter(route=form.cleaned_data['route'])
        
        if form.cleaned_data.get('driver'):
            carpools = carpools.filter(driver=form.cleaned_data['driver'])
        
        if form.cleaned_data.get('participant'):
            carpools = carpools.filter(participants__user=form.cleaned_data['participant'])
    
    carpools = carpools.order_by('-date', '-created_at')
    
    return render(request, 'caronas_app/carpool_list.html', {
        'carpools': carpools,
        'form': form
    })

@login_required
def carpool_create(request):
    """Create a new carpool."""
    if not has_caronas_permission(request.user, 'editor'):
        messages.error(request, "Você não tem permissão para criar caronas.")
        return redirect('caronas_app:carpool_list')
    
    if request.method == 'POST':
        form = CarpoolForm(request.POST, user=request.user)
        if form.is_valid():
            carpool = form.save(commit=False)
            carpool.created_by = request.user
            carpool.save()
            
            # Add participants
            participants = form.cleaned_data.get('participants', [])
            for participant in participants:
                CarpoolParticipant.objects.create(carpool=carpool, user=participant)
            
            messages.success(request, "Carona criada com sucesso!")
            return redirect('caronas_app:carpool_detail', pk=carpool.pk)
    else:
        form = CarpoolForm(user=request.user)
    
    return render(request, 'caronas_app/carpool_form.html', {'form': form, 'title': 'Nova Carona'})

@login_required
def carpool_detail(request, pk):
    """View carpool details."""
    if not has_caronas_permission(request.user):
        messages.error(request, "Você não tem permissão para acessar o aplicativo de Caronas.")
        return redirect('dashboard:index')
    
    carpool = get_object_or_404(Carpool, pk=pk)
    participants = carpool.participants.all()
    
    # Calculate cost per person
    cost_per_person = carpool.cost_per_person
    
    return render(request, 'caronas_app/carpool_detail.html', {
        'carpool': carpool,
        'participants': participants,
        'cost_per_person': cost_per_person
    })

@login_required
def carpool_update(request, pk):
    """Update an existing carpool."""
    if not has_caronas_permission(request.user, 'editor'):
        messages.error(request, "Você não tem permissão para editar caronas.")
        return redirect('caronas_app:carpool_list')
    
    carpool = get_object_or_404(Carpool, pk=pk)
    
    # Only driver, creator or admin can edit
    if carpool.driver != request.user and carpool.created_by != request.user and not has_caronas_permission(request.user, 'admin'):
        messages.error(request, "Você não tem permissão para editar esta carona.")
        return redirect('caronas_app:carpool_detail', pk=carpool.pk)
    
    if request.method == 'POST':
        form = CarpoolForm(request.POST, instance=carpool, user=request.user)
        if form.is_valid():
            carpool = form.save()
            
            # Update participants
            carpool.participants.all().delete()
            participants = form.cleaned_data.get('participants', [])
            for participant in participants:
                CarpoolParticipant.objects.create(carpool=carpool, user=participant)
            
            messages.success(request, "Carona atualizada com sucesso!")
            return redirect('caronas_app:carpool_detail', pk=carpool.pk)
    else:
        form = CarpoolForm(instance=carpool, user=request.user)
    
    return render(request, 'caronas_app/carpool_form.html', {'form': form, 'title': 'Editar Carona'})

@login_required
def carpool_delete(request, pk):
    """Delete a carpool."""
    if not has_caronas_permission(request.user, 'manager'):
        messages.error(request, "Você não tem permissão para excluir caronas.")
        return redirect('caronas_app:carpool_list')
    
    carpool = get_object_or_404(Carpool, pk=pk)
    
    # Only driver, creator or admin can delete
    if carpool.driver != request.user and carpool.created_by != request.user and not has_caronas_permission(request.user, 'admin'):
        messages.error(request, "Você não tem permissão para excluir esta carona.")
        return redirect('caronas_app:carpool_detail', pk=carpool.pk)
    
    if request.method == 'POST':
        carpool.delete()
        messages.success(request, "Carona excluída com sucesso!")
        return redirect('caronas_app:carpool_list')
    
    return render(request, 'caronas_app/carpool_confirm_delete.html', {'carpool': carpool})

@login_required
def carpool_participants(request, pk):
    """Manage carpool participants."""
    if not has_caronas_permission(request.user, 'editor'):
        messages.error(request, "Você não tem permissão para gerenciar participantes.")
        return redirect('caronas_app:carpool_detail', pk=pk)
    
    carpool = get_object_or_404(Carpool, pk=pk)
    
    # Only driver, creator or admin can manage participants
    if carpool.driver != request.user and carpool.created_by != request.user and not has_caronas_permission(request.user, 'admin'):
        messages.error(request, "Você não tem permissão para gerenciar participantes desta carona.")
        return redirect('caronas_app:carpool_detail', pk=carpool.pk)
    
    participants = carpool.participants.all()
    
    return render(request, 'caronas_app/carpool_participants.html', {
        'carpool': carpool,
        'participants': participants,
        'cost_per_person': carpool.cost_per_person
    })

@login_required
def participant_mark_paid(request, carpool_pk, pk):
    """Mark a participant as paid."""
    if not has_caronas_permission(request.user, 'editor'):
        messages.error(request, "Você não tem permissão para marcar pagamentos.")
        return redirect('caronas_app:carpool_detail', pk=carpool_pk)
    
    carpool = get_object_or_404(Carpool, pk=carpool_pk)
    participant = get_object_or_404(CarpoolParticipant, pk=pk, carpool=carpool)
    
    # Only driver, creator or admin can mark as paid
    if carpool.driver != request.user and carpool.created_by != request.user and not has_caronas_permission(request.user, 'admin'):
        messages.error(request, "Você não tem permissão para marcar pagamentos desta carona.")
        return redirect('caronas_app:carpool_detail', pk=carpool_pk)
    
    if request.method == 'POST':
        form = CarpoolParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, "Status de pagamento atualizado com sucesso!")
            return redirect('caronas_app:carpool_participants', pk=carpool_pk)
    else:
        form = CarpoolParticipantForm(instance=participant)
    
    return render(request, 'caronas_app/participant_form.html', {
        'form': form,
        'carpool': carpool,
        'participant': participant
    })

# Reports views
@login_required
def reports(request):
    """View reports dashboard."""
    if not has_caronas_permission(request.user):
        messages.error(request, "Você não tem permissão para acessar o aplicativo de Caronas.")
        return redirect('dashboard:index')
    
    # Get all users with carpool activity
    users = User.objects.filter(
        Q(driven_carpools__isnull=False) | Q(carpool_participations__isnull=False)
    ).distinct()
    
    # Calculate balances for each user
    user_balances = []
    for user in users:
        balance = calculate_user_balance(user)
        user_balances.append({
            'user': user,
            'balance': balance
        })
    
    # Sort by balance
    user_balances.sort(key=lambda x: x['balance'])
    
    return render(request, 'caronas_app/reports.html', {
        'user_balances': user_balances
    })

@login_required
def user_report(request, user_id):
    """View detailed report for a specific user."""
    if not has_caronas_permission(request.user):
        messages.error(request, "Você não tem permissão para acessar o aplicativo de Caronas.")
        return redirect('dashboard:index')
    
    user = get_object_or_404(User, pk=user_id)
    
    # Get carpools where user is driver
    driven_carpools = Carpool.objects.filter(driver=user)
    
    # Get carpools where user is participant
    participated_carpools = Carpool.objects.filter(participants__user=user)
    
    # Calculate balance
    balance = calculate_user_balance(user)
    
    return render(request, 'caronas_app/user_report.html', {
        'user': user,
        'driven_carpools': driven_carpools,
        'participated_carpools': participated_carpools,
        'balance': balance
    })

@login_required
def export_report(request):
    """Export carpool data to CSV."""
    if not has_caronas_permission(request.user, 'editor'):
        messages.error(request, "Você não tem permissão para exportar relatórios.")
        return redirect('caronas_app:reports')
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="caronas_report_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Data', 'Rota', 'Distância', 'Motorista', 'Veículo', 'Direção', 'Preço Combustível', 'Custo Total', 'Participantes', 'Custo por Pessoa'])
    
    carpools = Carpool.objects.all().order_by('-date')
    
    for carpool in carpools:
        participants_count = carpool.participants.count() + 1  # +1 for driver
        writer.writerow([
            carpool.date,
            carpool.route.name,
            carpool.total_distance,
            carpool.driver.get_full_name(),
            f"{carpool.vehicle.model} ({carpool.vehicle.plate})",
            carpool.get_direction_display(),
            carpool.fuel_price,
            carpool.fuel_cost,
            participants_count,
            carpool.cost_per_person
        ])
    
    return response

@login_required
def my_balance(request):
    """View personal balance and transaction history."""
    if not has_caronas_permission(request.user):
        messages.error(request, "Você não tem permissão para acessar o aplicativo de Caronas.")
        return redirect('dashboard:index')
    
    # Get carpools where user is driver
    driven_carpools = Carpool.objects.filter(driver=request.user).order_by('-date')
    
    # Get carpools where user is participant
    participated_carpools = Carpool.objects.filter(participants__user=request.user).order_by('-date')
    
    # Calculate balance
    balance = calculate_user_balance(request.user)
    
    # Calculate statistics
    total_driven = driven_carpools.count()
    total_participated = participated_carpools.count()
    
    # Calculate total distance
    total_driven_distance = sum(carpool.total_distance for carpool in driven_carpools)
    total_participated_distance = sum(carpool.total_distance for carpool in participated_carpools)
    
    return render(request, 'caronas_app/my_balance.html', {
        'driven_carpools': driven_carpools,
        'participated_carpools': participated_carpools,
        'balance': balance,
        'total_driven': total_driven,
        'total_participated': total_participated,
        'total_driven_distance': total_driven_distance,
        'total_participated_distance': total_participated_distance
    })

# Helper functions
def calculate_user_balance(user):
    """Calculate user balance based on driven and participated carpools."""
    # Money earned as driver
    driven_carpools = Carpool.objects.filter(driver=user)
    earned = 0
    for carpool in driven_carpools:
        participants_count = carpool.participants.count()
        if participants_count > 0:
            # Driver doesn't pay, only collects from participants
            earned += carpool.fuel_cost
    
    # Money spent as participant
    participated_carpools = CarpoolParticipant.objects.filter(user=user)
    spent = 0
    for participation in participated_carpools:
        spent += participation.carpool.cost_per_person
    
    return earned - spent
