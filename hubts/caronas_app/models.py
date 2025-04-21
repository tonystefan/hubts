from django.db import models
from core.models import User

class Route(models.Model):
    """
    Model for carpool routes.
    """
    name = models.CharField(max_length=100, verbose_name="Nome da Rota")
    distance_km = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Distância (km)")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    is_active = models.BooleanField(default=True, verbose_name="Ativa")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rota"
        verbose_name_plural = "Rotas"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.distance_km} km)"

class Vehicle(models.Model):
    """
    Model for vehicles used in carpools.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles', verbose_name="Proprietário")
    model = models.CharField(max_length=100, verbose_name="Modelo")
    plate = models.CharField(max_length=20, verbose_name="Placa")
    fuel_efficiency = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Consumo (km/l)")
    capacity = models.PositiveSmallIntegerField(default=4, verbose_name="Capacidade")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
        ordering = ['owner', 'model']
    
    def __str__(self):
        return f"{self.model} - {self.plate} ({self.owner.get_full_name()})"

class FuelPrice(models.Model):
    """
    Model to track fuel prices over time.
    """
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Preço (R$)")
    effective_date = models.DateField(verbose_name="Data de Vigência")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='fuel_prices', verbose_name="Criado por")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Preço de Combustível"
        verbose_name_plural = "Preços de Combustível"
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"R$ {self.price} (a partir de {self.effective_date})"
    
    @classmethod
    def get_current_price(cls):
        """Get the most recent fuel price."""
        try:
            return cls.objects.order_by('-effective_date').first().price
        except AttributeError:
            return 5.00  # Default price if no prices are set

class Carpool(models.Model):
    """
    Model for carpool events.
    """
    DIRECTION_CHOICES = (
        ('one_way', 'Somente Ida'),
        ('round_trip', 'Ida e Volta'),
    )
    
    date = models.DateField(verbose_name="Data")
    route = models.ForeignKey(Route, on_delete=models.PROTECT, related_name='carpools', verbose_name="Rota")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='carpools', verbose_name="Veículo")
    driver = models.ForeignKey(User, on_delete=models.PROTECT, related_name='driven_carpools', verbose_name="Motorista")
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default='round_trip', verbose_name="Direção")
    fuel_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Preço do Combustível (R$)")
    notes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_carpools', verbose_name="Criado por")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Carona"
        verbose_name_plural = "Caronas"
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"Carona em {self.date} - {self.route.name} ({self.get_direction_display()})"
    
    def save(self, *args, **kwargs):
        # Set fuel price if not provided
        if not self.fuel_price:
            self.fuel_price = FuelPrice.get_current_price()
        super().save(*args, **kwargs)
    
    @property
    def total_distance(self):
        """Calculate total distance based on route and direction."""
        if self.direction == 'round_trip':
            return float(self.route.distance_km) * 2
        return float(self.route.distance_km)
    
    @property
    def fuel_cost(self):
        """Calculate fuel cost for this carpool."""
        fuel_consumed = self.total_distance / float(self.vehicle.fuel_efficiency)
        return round(fuel_consumed * float(self.fuel_price), 2)
    
    @property
    def cost_per_person(self):
        """Calculate cost per person for this carpool."""
        participants_count = self.participants.count() + 1  # +1 for the driver
        if participants_count <= 1:
            return self.fuel_cost
        return round(self.fuel_cost / participants_count, 2)

class CarpoolParticipant(models.Model):
    """
    Model for participants in a carpool.
    """
    carpool = models.ForeignKey(Carpool, on_delete=models.CASCADE, related_name='participants', verbose_name="Carona")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carpool_participations', verbose_name="Participante")
    has_paid = models.BooleanField(default=False, verbose_name="Pagou")
    payment_date = models.DateField(null=True, blank=True, verbose_name="Data de Pagamento")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Participante de Carona"
        verbose_name_plural = "Participantes de Carona"
        unique_together = ('carpool', 'user')
        ordering = ['carpool', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.carpool}"
