"""
Vue d'analyse des revenus et du volume de passagers pour l'admin Django
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate, TruncDay, TruncMonth, TruncYear
from datetime import datetime, timedelta, date
from decimal import Decimal
from .models import Reservation


class AnalyticsAdminView:
    """Vue d'analyse pour l'admin"""
    
    @staticmethod
    def analytics_view(request):
        """Vue principale d'analyse"""
        # Paramètres de période
        period = request.GET.get('period', '30')  # 7, 30, 90, 365, all
        chart_type = request.GET.get('chart_type', 'daily')  # daily, weekly, monthly
        
        # Calculer les dates
        end_date = date.today()
        if period == '7':
            start_date = end_date - timedelta(days=7)
        elif period == '30':
            start_date = end_date - timedelta(days=30)
        elif period == '90':
            start_date = end_date - timedelta(days=90)
        elif period == '365':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = None
        
        # Filtrer les réservations confirmées et payées
        reservations = Reservation.objects.filter(
            statut__in=['confirmee', 'utilisee']
        )
        
        if start_date:
            reservations = reservations.filter(date_reservation__date__gte=start_date)
        
        # ========== ANALYSE DES REVENUS ==========
        revenue_data = []
        revenue_labels = []
        
        if chart_type == 'daily':
            # Revenus par jour
            revenue_by_day = reservations.extra(
                select={'day': 'DATE(date_reservation)'}
            ).values('day').annotate(
                total_revenue=Sum('prix_total'),
                count=Count('id')
            ).order_by('day')
            
            for item in revenue_by_day:
                if item['day']:
                    day_date = item['day'] if isinstance(item['day'], date) else datetime.strptime(str(item['day']), '%Y-%m-%d').date()
                    revenue_labels.append(day_date.strftime('%d/%m/%Y'))
                    revenue_data.append(float(item['total_revenue'] or 0))
        
        elif chart_type == 'weekly':
            # Revenus par semaine (simplifié - par jour pour MySQL)
            revenue_by_week = reservations.extra(
                select={'week': 'DATE(date_reservation)'}
            ).values('week').annotate(
                total_revenue=Sum('prix_total'),
                count=Count('id')
            ).order_by('week')
            
            # Grouper par semaine manuellement
            week_data = {}
            for item in revenue_by_week:
                if item['week']:
                    week_date = item['week'] if isinstance(item['week'], date) else datetime.strptime(str(item['week']), '%Y-%m-%d').date()
                    week_num = week_date.isocalendar()[1]
                    week_key = f"{week_date.year}-W{week_num:02d}"
                    if week_key not in week_data:
                        week_data[week_key] = {'date': week_date, 'revenue': 0}
                    week_data[week_key]['revenue'] += float(item['total_revenue'] or 0)
            
            for week_key in sorted(week_data.keys()):
                revenue_labels.append(f"Sem. {week_data[week_key]['date'].strftime('%d/%m')}")
                revenue_data.append(week_data[week_key]['revenue'])
        
        elif chart_type == 'monthly':
            # Revenus par mois
            revenue_by_month = reservations.extra(
                select={'month': "DATE_FORMAT(date_reservation, '%%Y-%%m-01')"}
            ).values('month').annotate(
                total_revenue=Sum('prix_total'),
                count=Count('id')
            ).order_by('month')
            
            for item in revenue_by_month:
                if item['month']:
                    month_date = datetime.strptime(str(item['month']), '%Y-%m-%d').date()
                    revenue_labels.append(month_date.strftime('%b %Y'))
                    revenue_data.append(float(item['total_revenue'] or 0))
        
        # Statistiques globales des revenus
        total_revenue = reservations.aggregate(
            total=Sum('prix_total')
        )['total'] or Decimal('0.00')
        
        avg_daily_revenue = total_revenue / max((end_date - start_date).days, 1) if start_date else total_revenue
        
        # ========== ANALYSE DU VOLUME DE PASSAGERS ==========
        passenger_data = []
        passenger_labels = []
        
        if chart_type == 'daily':
            # Passagers par jour
            passengers_by_day = reservations.extra(
                select={'day': 'DATE(date_reservation)'}
            ).values('day').annotate(
                total_passengers=Sum('nombre_places'),
                count=Count('id')
            ).order_by('day')
            
            for item in passengers_by_day:
                if item['day']:
                    day_date = item['day'] if isinstance(item['day'], date) else datetime.strptime(str(item['day']), '%Y-%m-%d').date()
                    passenger_labels.append(day_date.strftime('%d/%m/%Y'))
                    passenger_data.append(int(item['total_passengers'] or 0))
        
        elif chart_type == 'weekly':
            # Passagers par semaine
            passengers_by_week = reservations.extra(
                select={'week': 'DATE(date_reservation)'}
            ).values('week').annotate(
                total_passengers=Sum('nombre_places'),
                count=Count('id')
            ).order_by('week')
            
            # Grouper par semaine manuellement
            week_data = {}
            for item in passengers_by_week:
                if item['week']:
                    week_date = item['week'] if isinstance(item['week'], date) else datetime.strptime(str(item['week']), '%Y-%m-%d').date()
                    week_num = week_date.isocalendar()[1]
                    week_key = f"{week_date.year}-W{week_num:02d}"
                    if week_key not in week_data:
                        week_data[week_key] = {'date': week_date, 'passengers': 0}
                    week_data[week_key]['passengers'] += int(item['total_passengers'] or 0)
            
            for week_key in sorted(week_data.keys()):
                passenger_labels.append(f"Sem. {week_data[week_key]['date'].strftime('%d/%m')}")
                passenger_data.append(week_data[week_key]['passengers'])
        
        elif chart_type == 'monthly':
            # Passagers par mois
            passengers_by_month = reservations.extra(
                select={'month': "DATE_FORMAT(date_reservation, '%%Y-%%m-01')"}
            ).values('month').annotate(
                total_passengers=Sum('nombre_places'),
                count=Count('id')
            ).order_by('month')
            
            for item in passengers_by_month:
                if item['month']:
                    month_date = datetime.strptime(str(item['month']), '%Y-%m-%d').date()
                    passenger_labels.append(month_date.strftime('%b %Y'))
                    passenger_data.append(int(item['total_passengers'] or 0))
        
        # Statistiques globales des passagers
        total_passengers = reservations.aggregate(
            total=Sum('nombre_places')
        )['total'] or 0
        
        total_reservations = reservations.count()
        avg_passengers_per_reservation = total_passengers / max(total_reservations, 1)
        
        # ========== PRÉDICTIONS IA (simple) ==========
        # Prédiction basée sur la tendance moyenne
        if len(revenue_data) > 0:
            recent_avg = sum(revenue_data[-7:]) / min(len(revenue_data), 7)
            predicted_revenue = recent_avg * 7  # Prédiction pour les 7 prochains jours
        else:
            predicted_revenue = 0
        
        if len(passenger_data) > 0:
            recent_avg_passengers = sum(passenger_data[-7:]) / min(len(passenger_data), 7)
            predicted_passengers = int(recent_avg_passengers * 7)
        else:
            predicted_passengers = 0
        
        # Tendance (croissance/décroissance)
        if len(revenue_data) >= 2:
            recent_trend = revenue_data[-1] - revenue_data[-2]
            trend_percentage = (recent_trend / revenue_data[-2] * 100) if revenue_data[-2] > 0 else 0
        else:
            trend_percentage = 0
        
        import json
        context = {
            'revenue_labels': json.dumps(revenue_labels),
            'revenue_data': json.dumps(revenue_data),
            'passenger_labels': json.dumps(passenger_labels),
            'passenger_data': json.dumps(passenger_data),
            'total_revenue': float(total_revenue),
            'avg_daily_revenue': float(avg_daily_revenue),
            'total_passengers': total_passengers,
            'total_reservations': total_reservations,
            'avg_passengers_per_reservation': float(avg_passengers_per_reservation),
            'predicted_revenue': float(predicted_revenue),
            'predicted_passengers': predicted_passengers,
            'trend_percentage': round(trend_percentage, 2),
            'period': period,
            'chart_type': chart_type,
            'start_date': start_date,
            'end_date': end_date,
        }
        
        return render(request, 'admin/analytics.html', context)


def analytics_data_view(request):
    """Vue API pour retourner les données d'analyse en JSON"""
    from django.http import JsonResponse
    import json
    
    # Utiliser la même logique que analytics_view
    period = request.GET.get('period', '30')
    chart_type = request.GET.get('chart_type', 'daily')
    
    # Calculer les dates
    end_date = date.today()
    if period == '7':
        start_date = end_date - timedelta(days=7)
    elif period == '30':
        start_date = end_date - timedelta(days=30)
    elif period == '90':
        start_date = end_date - timedelta(days=90)
    elif period == '365':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = None
    
    # Filtrer les réservations
    reservations = Reservation.objects.filter(
        statut__in=['confirmee', 'utilisee']
    )
    
    if start_date:
        reservations = reservations.filter(date_reservation__date__gte=start_date)
    
    # Calculer les données (simplifié - réutiliser la logique existante)
    revenue_labels = []
    revenue_data = []
    passenger_labels = []
    passenger_data = []
    
    if chart_type == 'daily':
        revenue_by_day = reservations.extra(
            select={'day': 'DATE(date_reservation)'}
        ).values('day').annotate(
            total_revenue=Sum('prix_total'),
            count=Count('id')
        ).order_by('day')
        
        for item in revenue_by_day:
            if item['day']:
                day_date = item['day'] if isinstance(item['day'], date) else datetime.strptime(str(item['day']), '%Y-%m-%d').date()
                revenue_labels.append(day_date.strftime('%d/%m/%Y'))
                revenue_data.append(float(item['total_revenue'] or 0))
        
        passengers_by_day = reservations.extra(
            select={'day': 'DATE(date_reservation)'}
        ).values('day').annotate(
            total_passengers=Sum('nombre_places'),
            count=Count('id')
        ).order_by('day')
        
        for item in passengers_by_day:
            if item['day']:
                day_date = item['day'] if isinstance(item['day'], date) else datetime.strptime(str(item['day']), '%Y-%m-%d').date()
                passenger_labels.append(day_date.strftime('%d/%m/%Y'))
                passenger_data.append(int(item['total_passengers'] or 0))
    
    elif chart_type == 'weekly':
        revenue_by_week = reservations.extra(
            select={'week': 'DATE(date_reservation)'}
        ).values('week').annotate(
            total_revenue=Sum('prix_total'),
            count=Count('id')
        ).order_by('week')
        
        week_data = {}
        for item in revenue_by_week:
            if item['week']:
                week_date = item['week'] if isinstance(item['week'], date) else datetime.strptime(str(item['week']), '%Y-%m-%d').date()
                week_num = week_date.isocalendar()[1]
                week_key = f"{week_date.year}-W{week_num:02d}"
                if week_key not in week_data:
                    week_data[week_key] = {'date': week_date, 'revenue': 0}
                week_data[week_key]['revenue'] += float(item['total_revenue'] or 0)
        
        for week_key in sorted(week_data.keys()):
            revenue_labels.append(f"Sem. {week_data[week_key]['date'].strftime('%d/%m')}")
            revenue_data.append(week_data[week_key]['revenue'])
        
        passengers_by_week = reservations.extra(
            select={'week': 'DATE(date_reservation)'}
        ).values('week').annotate(
            total_passengers=Sum('nombre_places'),
            count=Count('id')
        ).order_by('week')
        
        week_passenger_data = {}
        for item in passengers_by_week:
            if item['week']:
                week_date = item['week'] if isinstance(item['week'], date) else datetime.strptime(str(item['week']), '%Y-%m-%d').date()
                week_num = week_date.isocalendar()[1]
                week_key = f"{week_date.year}-W{week_num:02d}"
                if week_key not in week_passenger_data:
                    week_passenger_data[week_key] = {'date': week_date, 'passengers': 0}
                week_passenger_data[week_key]['passengers'] += int(item['total_passengers'] or 0)
        
        for week_key in sorted(week_passenger_data.keys()):
            passenger_labels.append(f"Sem. {week_passenger_data[week_key]['date'].strftime('%d/%m')}")
            passenger_data.append(week_passenger_data[week_key]['passengers'])
    
    elif chart_type == 'monthly':
        revenue_by_month = reservations.extra(
            select={'month': "DATE_FORMAT(date_reservation, '%%Y-%%m-01')"}
        ).values('month').annotate(
            total_revenue=Sum('prix_total'),
            count=Count('id')
        ).order_by('month')
        
        for item in revenue_by_month:
            if item['month']:
                month_date = datetime.strptime(str(item['month']), '%Y-%m-%d').date()
                revenue_labels.append(month_date.strftime('%b %Y'))
                revenue_data.append(float(item['total_revenue'] or 0))
        
        passengers_by_month = reservations.extra(
            select={'month': "DATE_FORMAT(date_reservation, '%%Y-%%m-01')"}
        ).values('month').annotate(
            total_passengers=Sum('nombre_places'),
            count=Count('id')
        ).order_by('month')
        
        for item in passengers_by_month:
            if item['month']:
                month_date = datetime.strptime(str(item['month']), '%Y-%m-%d').date()
                passenger_labels.append(month_date.strftime('%b %Y'))
                passenger_data.append(int(item['total_passengers'] or 0))
    
    return JsonResponse({
        'revenue_labels': revenue_labels,
        'revenue_data': revenue_data,
        'passenger_labels': passenger_labels,
        'passenger_data': passenger_data,
    })


def get_admin_urls(admin_site=None):
    """Retourne les URLs pour l'admin"""
    if admin_site is None:
        from django.contrib import admin
        admin_site = admin.site
    
    return [
        path('analytics/', admin_site.admin_view(AnalyticsAdminView.analytics_view), name='admin_analytics'),
        path('analytics/data/', admin_site.admin_view(analytics_data_view), name='admin_analytics_data'),
    ]

