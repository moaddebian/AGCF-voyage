"""
Vue personnalisée pour le dashboard de l'admin avec analyse IA
"""
from django.contrib import admin
from django.template.response import TemplateResponse
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import TruncDate, TruncMonth
from datetime import datetime, timedelta, date
from decimal import Decimal
from .models import Reservation, Train, MaintenanceTrain


def get_dashboard_stats():
    """Calcule les statistiques pour le dashboard"""
    today = date.today()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # Réservations confirmées et utilisées
    reservations = Reservation.objects.filter(
        statut__in=['confirmee', 'utilisee']
    )
    
    # Revenus totaux
    total_revenue = reservations.aggregate(
        total=Sum('prix_total')
    )['total'] or Decimal('0.00')
    
    # Revenus des 30 derniers jours
    revenue_30d = reservations.filter(
        date_reservation__date__gte=last_30_days
    ).aggregate(total=Sum('prix_total'))['total'] or Decimal('0.00')
    
    # Revenus des 7 derniers jours
    revenue_7d = reservations.filter(
        date_reservation__date__gte=last_7_days
    ).aggregate(total=Sum('prix_total'))['total'] or Decimal('0.00')
    
    # Calcul de la croissance
    revenue_prev_7d = reservations.filter(
        date_reservation__date__gte=last_7_days - timedelta(days=7),
        date_reservation__date__lt=last_7_days
    ).aggregate(total=Sum('prix_total'))['total'] or Decimal('0.01')
    
    revenue_growth = ((revenue_7d - revenue_prev_7d) / revenue_prev_7d * 100) if revenue_prev_7d > 0 else 0
    
    # Total passagers
    total_passengers = reservations.aggregate(
        total=Sum('nombre_places')
    )['total'] or 0
    
    # Passagers des 30 derniers jours
    passengers_30d = reservations.filter(
        date_reservation__date__gte=last_30_days
    ).aggregate(total=Sum('nombre_places'))['total'] or 0
    
    # Passagers des 7 derniers jours
    passengers_7d = reservations.filter(
        date_reservation__date__gte=last_7_days
    ).aggregate(total=Sum('nombre_places'))['total'] or 0
    
    # Calcul de la croissance des passagers
    passengers_prev_7d = reservations.filter(
        date_reservation__date__gte=last_7_days - timedelta(days=7),
        date_reservation__date__lt=last_7_days
    ).aggregate(total=Sum('nombre_places'))['total'] or 1
    
    passengers_growth = ((passengers_7d - passengers_prev_7d) / passengers_prev_7d * 100) if passengers_prev_7d > 0 else 0
    
    # Trains actifs
    active_trains = Train.objects.filter(actif=True).count()
    total_trains = Train.objects.count()
    operational_rate = (active_trains / total_trains * 100) if total_trains > 0 else 0
    
    # Maintenances en attente
    pending_maintenance = MaintenanceTrain.objects.filter(
        statut__in=['planifie', 'en_cours']
    ).count()
    
    # Données pour les graphiques (30 derniers jours)
    revenue_data = []
    revenue_labels = []
    passenger_data = []
    passenger_labels = []
    
    for i in range(30):
        day = last_30_days + timedelta(days=i)
        day_reservations = reservations.filter(date_reservation__date=day)
        
        day_revenue = day_reservations.aggregate(
            total=Sum('prix_total')
        )['total'] or Decimal('0.00')
        
        day_passengers = day_reservations.aggregate(
            total=Sum('nombre_places')
        )['total'] or 0
        
        revenue_labels.append(day.strftime('%d/%m'))
        revenue_data.append(float(day_revenue))
        passenger_labels.append(day.strftime('%d/%m'))
        passenger_data.append(int(day_passengers))
    
    # Prédictions IA (basées sur la moyenne des 7 derniers jours)
    avg_daily_revenue = revenue_7d / 7 if revenue_7d > 0 else Decimal('0.00')
    predicted_revenue_7d = avg_daily_revenue * 7
    
    avg_daily_passengers = passengers_7d / 7 if passengers_7d > 0 else 0
    predicted_passengers_7d = int(avg_daily_passengers * 7)
    
    return {
        'total_revenue': float(total_revenue),
        'revenue_30d': float(revenue_30d),
        'revenue_7d': float(revenue_7d),
        'revenue_growth': round(revenue_growth, 1),
        'total_passengers': total_passengers,
        'passengers_30d': passengers_30d,
        'passengers_7d': passengers_7d,
        'passengers_growth': round(passengers_growth, 1),
        'active_trains': active_trains,
        'total_trains': total_trains,
        'operational_rate': round(operational_rate, 1),
        'pending_maintenance': pending_maintenance,
        'revenue_labels': revenue_labels,
        'revenue_data': revenue_data,
        'passenger_labels': passenger_labels,
        'passenger_data': passenger_data,
        'predicted_revenue_7d': float(predicted_revenue_7d),
        'predicted_passengers_7d': predicted_passengers_7d,
    }

