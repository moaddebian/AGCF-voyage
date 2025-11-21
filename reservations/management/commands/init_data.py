"""
Commande Django pour initialiser des données de test
Usage: python manage.py init_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta
from reservations.models import Gare, Train, CarteReduction, OffrePromotion


class Command(BaseCommand):
    help = 'Initialise des données de test pour l\'application'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Création des données de test...'))
        
        # Création des gares ONCF marocaines (basées sur les gares officielles)
        gares_data = [
            {'nom': 'Casa-Voyageurs', 'ville': 'Casablanca', 'code': 'CASA-V', 'adresse': 'Boulevard Mohammed V, Casablanca 20000'},
            {'nom': 'Casa-Port', 'ville': 'Casablanca', 'code': 'CASA-P', 'adresse': 'Boulevard des Almohades, Casablanca 20000'},
            {'nom': 'Rabat-Ville', 'ville': 'Rabat', 'code': 'RABAT-V', 'adresse': 'Avenue Mohammed V, Rabat 10000'},
            {'nom': 'Rabat-Agdal', 'ville': 'Rabat', 'code': 'RABAT-A', 'adresse': 'Quartier Agdal, Rabat 10000'},
            {'nom': 'Fès-Ville', 'ville': 'Fès', 'code': 'FES-V', 'adresse': 'Boulevard Allal Ben Abdellah, Fès 30000'},
            {'nom': 'Marrakech', 'ville': 'Marrakech', 'code': 'MARRAK', 'adresse': 'Avenue Hassan II, Marrakech 40000'},
            {'nom': 'Tanger-Ville', 'ville': 'Tanger', 'code': 'TANGER', 'adresse': 'Place de la Gare, Tanger 90000'},
            {'nom': 'Meknès-Ville', 'ville': 'Meknès', 'code': 'MEKNES', 'adresse': 'Avenue Hassan II, Meknès 50000'},
            {'nom': 'Oujda', 'ville': 'Oujda', 'code': 'OUJDA', 'adresse': 'Boulevard Zerktouni, Oujda 60000'},
            {'nom': 'Kénitra', 'ville': 'Kénitra', 'code': 'KENITRA', 'adresse': 'Avenue Mohammed V, Kénitra 14000'},
            {'nom': 'Salé', 'ville': 'Salé', 'code': 'SALE', 'adresse': 'Avenue Hassan II, Salé 11000'},
            {'nom': 'Tétouan', 'ville': 'Tétouan', 'code': 'TETOUAN', 'adresse': 'Boulevard Mohammed V, Tétouan 93000'},
            {'nom': 'Taza', 'ville': 'Taza', 'code': 'TAZA', 'adresse': 'Avenue Hassan II, Taza 35000'},
            {'nom': 'Nador', 'ville': 'Nador', 'code': 'NADOR', 'adresse': 'Boulevard Zerktouni, Nador 62000'},
        ]
        
        gares = {}
        for gare_data in gares_data:
            gare, created = Gare.objects.get_or_create(
                code=gare_data['code'],
                defaults=gare_data
            )
            gares[gare_data['code']] = gare
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Gare créée: {gare}'))
        
        # Création des trains ONCF (Al Boraq - TGV marocain, trains classiques)
        # Données basées sur les informations publiques de l'ONCF
        trains_data = [
            # Al Boraq : Casablanca - Tanger (ligne à grande vitesse)
            {
                'numero': 'ALB-1001',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'TANGER',
                'heure_depart': time(6, 10),
                'heure_arrivee': time(8, 25),
                'duree': timedelta(hours=2, minutes=15),
                'classe': '1',
                'prix_base': 140.00,
                'places_disponibles': 120
            },
            {
                'numero': 'ALB-1002',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'TANGER',
                'heure_depart': time(8, 10),
                'heure_arrivee': time(10, 25),
                'duree': timedelta(hours=2, minutes=15),
                'classe': '2',
                'prix_base': 95.00,
                'places_disponibles': 200
            },
            {
                'numero': 'ALB-1003',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'TANGER',
                'heure_depart': time(14, 10),
                'heure_arrivee': time(16, 25),
                'duree': timedelta(hours=2, minutes=15),
                'classe': '1',
                'prix_base': 140.00,
                'places_disponibles': 130
            },
            {
                'numero': 'ALB-1004',
                'gare_depart': 'TANGER',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(9, 0),
                'heure_arrivee': time(11, 15),
                'duree': timedelta(hours=2, minutes=15),
                'classe': '2',
                'prix_base': 95.00,
                'places_disponibles': 200
            },
            # Al Boraq : Casablanca - Rabat
            {
                'numero': 'ALB-2001',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'RABAT-V',
                'heure_depart': time(6, 0),
                'heure_arrivee': time(6, 50),
                'duree': timedelta(hours=0, minutes=50),
                'classe': '1',
                'prix_base': 65.00,
                'places_disponibles': 150
            },
            {
                'numero': 'ALB-2002',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'RABAT-V',
                'heure_depart': time(8, 0),
                'heure_arrivee': time(8, 50),
                'duree': timedelta(hours=0, minutes=50),
                'classe': '2',
                'prix_base': 45.00,
                'places_disponibles': 220
            },
            {
                'numero': 'ALB-2003',
                'gare_depart': 'RABAT-V',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(7, 30),
                'heure_arrivee': time(8, 20),
                'duree': timedelta(hours=0, minutes=50),
                'classe': '2',
                'prix_base': 45.00,
                'places_disponibles': 220
            },
            # Trains classiques : Casablanca - Fès
            {
                'numero': 'TRN-3001',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'FES-V',
                'heure_depart': time(7, 0),
                'heure_arrivee': time(10, 15),
                'duree': timedelta(hours=3, minutes=15),
                'classe': '1',
                'prix_base': 95.00,
                'places_disponibles': 100
            },
            {
                'numero': 'TRN-3002',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'FES-V',
                'heure_depart': time(14, 30),
                'heure_arrivee': time(17, 45),
                'duree': timedelta(hours=3, minutes=15),
                'classe': '2',
                'prix_base': 75.00,
                'places_disponibles': 180
            },
            {
                'numero': 'TRN-3003',
                'gare_depart': 'FES-V',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(8, 0),
                'heure_arrivee': time(11, 15),
                'duree': timedelta(hours=3, minutes=15),
                'classe': '2',
                'prix_base': 75.00,
                'places_disponibles': 180
            },
            # Trains classiques : Casablanca - Marrakech
            {
                'numero': 'TRN-4001',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'MARRAK',
                'heure_depart': time(8, 0),
                'heure_arrivee': time(11, 30),
                'duree': timedelta(hours=3, minutes=30),
                'classe': '1',
                'prix_base': 120.00,
                'places_disponibles': 110
            },
            {
                'numero': 'TRN-4002',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'MARRAK',
                'heure_depart': time(15, 0),
                'heure_arrivee': time(18, 30),
                'duree': timedelta(hours=3, minutes=30),
                'classe': '2',
                'prix_base': 90.00,
                'places_disponibles': 200
            },
            {
                'numero': 'TRN-4003',
                'gare_depart': 'MARRAK',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(9, 0),
                'heure_arrivee': time(12, 30),
                'duree': timedelta(hours=3, minutes=30),
                'classe': '2',
                'prix_base': 90.00,
                'places_disponibles': 200
            },
            # Trains classiques : Fès - Meknès
            {
                'numero': 'TRN-5001',
                'gare_depart': 'FES-V',
                'gare_arrivee': 'MEKNES',
                'heure_depart': time(10, 0),
                'heure_arrivee': time(10, 45),
                'duree': timedelta(hours=0, minutes=45),
                'classe': '2',
                'prix_base': 25.00,
                'places_disponibles': 250
            },
            {
                'numero': 'TRN-5002',
                'gare_depart': 'MEKNES',
                'gare_arrivee': 'FES-V',
                'heure_depart': time(11, 30),
                'heure_arrivee': time(12, 15),
                'duree': timedelta(hours=0, minutes=45),
                'classe': '2',
                'prix_base': 25.00,
                'places_disponibles': 250
            },
            # Trains classiques : Casablanca - Oujda
            {
                'numero': 'TRN-6001',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'OUJDA',
                'heure_depart': time(6, 30),
                'heure_arrivee': time(13, 45),
                'duree': timedelta(hours=7, minutes=15),
                'classe': '1',
                'prix_base': 150.00,
                'places_disponibles': 80
            },
            {
                'numero': 'TRN-6002',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'OUJDA',
                'heure_depart': time(14, 0),
                'heure_arrivee': time(21, 15),
                'duree': timedelta(hours=7, minutes=15),
                'classe': '2',
                'prix_base': 120.00,
                'places_disponibles': 180
            },
            {
                'numero': 'TRN-6003',
                'gare_depart': 'OUJDA',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(7, 0),
                'heure_arrivee': time(14, 15),
                'duree': timedelta(hours=7, minutes=15),
                'classe': '2',
                'prix_base': 120.00,
                'places_disponibles': 180
            },
            # Trains classiques : Casablanca - Kénitra
            {
                'numero': 'TRN-7001',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'KENITRA',
                'heure_depart': time(9, 0),
                'heure_arrivee': time(10, 15),
                'duree': timedelta(hours=1, minutes=15),
                'classe': '2',
                'prix_base': 35.00,
                'places_disponibles': 240
            },
            {
                'numero': 'TRN-7002',
                'gare_depart': 'KENITRA',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(11, 0),
                'heure_arrivee': time(12, 15),
                'duree': timedelta(hours=1, minutes=15),
                'classe': '2',
                'prix_base': 35.00,
                'places_disponibles': 240
            },
            # Trains classiques : Rabat - Salé
            {
                'numero': 'TRN-8001',
                'gare_depart': 'RABAT-V',
                'gare_arrivee': 'SALE',
                'heure_depart': time(8, 30),
                'heure_arrivee': time(8, 50),
                'duree': timedelta(hours=0, minutes=20),
                'classe': '2',
                'prix_base': 15.00,
                'places_disponibles': 300
            },
            {
                'numero': 'TRN-8002',
                'gare_depart': 'SALE',
                'gare_arrivee': 'RABAT-V',
                'heure_depart': time(9, 15),
                'heure_arrivee': time(9, 35),
                'duree': timedelta(hours=0, minutes=20),
                'classe': '2',
                'prix_base': 15.00,
                'places_disponibles': 300
            },
            # Trains classiques : Fès - Taza
            {
                'numero': 'TRN-9001',
                'gare_depart': 'FES-V',
                'gare_arrivee': 'TAZA',
                'heure_depart': time(11, 0),
                'heure_arrivee': time(12, 30),
                'duree': timedelta(hours=1, minutes=30),
                'classe': '2',
                'prix_base': 40.00,
                'places_disponibles': 200
            },
            {
                'numero': 'TRN-9002',
                'gare_depart': 'TAZA',
                'gare_arrivee': 'FES-V',
                'heure_depart': time(13, 30),
                'heure_arrivee': time(15, 0),
                'duree': timedelta(hours=1, minutes=30),
                'classe': '2',
                'prix_base': 40.00,
                'places_disponibles': 200
            },
            # Trains supplémentaires pour plus de variété
            # Al Boraq supplémentaires
            {
                'numero': 'ALB-2004',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'RABAT-V',
                'heure_depart': time(10, 0),
                'heure_arrivee': time(10, 50),
                'duree': timedelta(hours=0, minutes=50),
                'classe': '1',
                'prix_base': 65.00,
                'places_disponibles': 140
            },
            {
                'numero': 'ALB-2005',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'RABAT-V',
                'heure_depart': time(12, 0),
                'heure_arrivee': time(12, 50),
                'duree': timedelta(hours=0, minutes=50),
                'classe': '2',
                'prix_base': 45.00,
                'places_disponibles': 210
            },
            {
                'numero': 'ALB-2006',
                'gare_depart': 'RABAT-V',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(9, 0),
                'heure_arrivee': time(9, 50),
                'duree': timedelta(hours=0, minutes=50),
                'classe': '2',
                'prix_base': 45.00,
                'places_disponibles': 210
            },
            {
                'numero': 'ALB-2007',
                'gare_depart': 'RABAT-V',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(11, 0),
                'heure_arrivee': time(11, 50),
                'duree': timedelta(hours=0, minutes=50),
                'classe': '1',
                'prix_base': 65.00,
                'places_disponibles': 140
            },
            {
                'numero': 'ALB-1005',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'TANGER',
                'heure_depart': time(10, 10),
                'heure_arrivee': time(12, 25),
                'duree': timedelta(hours=2, minutes=15),
                'classe': '2',
                'prix_base': 95.00,
                'places_disponibles': 190
            },
            {
                'numero': 'ALB-1006',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'TANGER',
                'heure_depart': time(16, 10),
                'heure_arrivee': time(18, 25),
                'duree': timedelta(hours=2, minutes=15),
                'classe': '1',
                'prix_base': 140.00,
                'places_disponibles': 125
            },
            {
                'numero': 'ALB-1007',
                'gare_depart': 'TANGER',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(11, 0),
                'heure_arrivee': time(13, 15),
                'duree': timedelta(hours=2, minutes=15),
                'classe': '1',
                'prix_base': 140.00,
                'places_disponibles': 125
            },
            {
                'numero': 'ALB-1008',
                'gare_depart': 'TANGER',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(17, 0),
                'heure_arrivee': time(19, 15),
                'duree': timedelta(hours=2, minutes=15),
                'classe': '2',
                'prix_base': 95.00,
                'places_disponibles': 190
            },
            # Trains classiques supplémentaires
            {
                'numero': 'TRN-3004',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'FES-V',
                'heure_depart': time(10, 0),
                'heure_arrivee': time(13, 15),
                'duree': timedelta(hours=3, minutes=15),
                'classe': '2',
                'prix_base': 75.00,
                'places_disponibles': 170
            },
            {
                'numero': 'TRN-3005',
                'gare_depart': 'FES-V',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(14, 0),
                'heure_arrivee': time(17, 15),
                'duree': timedelta(hours=3, minutes=15),
                'classe': '1',
                'prix_base': 95.00,
                'places_disponibles': 110
            },
            {
                'numero': 'TRN-4004',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'MARRAK',
                'heure_depart': time(11, 0),
                'heure_arrivee': time(14, 30),
                'duree': timedelta(hours=3, minutes=30),
                'classe': '2',
                'prix_base': 90.00,
                'places_disponibles': 190
            },
            {
                'numero': 'TRN-4005',
                'gare_depart': 'MARRAK',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(6, 0),
                'heure_arrivee': time(9, 30),
                'duree': timedelta(hours=3, minutes=30),
                'classe': '2',
                'prix_base': 90.00,
                'places_disponibles': 190
            },
            {
                'numero': 'TRN-4006',
                'gare_depart': 'MARRAK',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(14, 0),
                'heure_arrivee': time(17, 30),
                'duree': timedelta(hours=3, minutes=30),
                'classe': '1',
                'prix_base': 120.00,
                'places_disponibles': 105
            },
            {
                'numero': 'TRN-6004',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'OUJDA',
                'heure_depart': time(10, 30),
                'heure_arrivee': time(17, 45),
                'duree': timedelta(hours=7, minutes=15),
                'classe': '2',
                'prix_base': 120.00,
                'places_disponibles': 170
            },
            {
                'numero': 'TRN-6005',
                'gare_depart': 'OUJDA',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(8, 0),
                'heure_arrivee': time(15, 15),
                'duree': timedelta(hours=7, minutes=15),
                'classe': '2',
                'prix_base': 120.00,
                'places_disponibles': 170
            },
            # Trains entre autres gares
            {
                'numero': 'TRN-7003',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'KENITRA',
                'heure_depart': time(13, 0),
                'heure_arrivee': time(14, 15),
                'duree': timedelta(hours=1, minutes=15),
                'classe': '2',
                'prix_base': 35.00,
                'places_disponibles': 230
            },
            {
                'numero': 'TRN-7004',
                'gare_depart': 'KENITRA',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(15, 0),
                'heure_arrivee': time(16, 15),
                'duree': timedelta(hours=1, minutes=15),
                'classe': '2',
                'prix_base': 35.00,
                'places_disponibles': 230
            },
            {
                'numero': 'TRN-8003',
                'gare_depart': 'RABAT-V',
                'gare_arrivee': 'SALE',
                'heure_depart': time(10, 30),
                'heure_arrivee': time(10, 50),
                'duree': timedelta(hours=0, minutes=20),
                'classe': '2',
                'prix_base': 15.00,
                'places_disponibles': 290
            },
            {
                'numero': 'TRN-8004',
                'gare_depart': 'SALE',
                'gare_arrivee': 'RABAT-V',
                'heure_depart': time(11, 15),
                'heure_arrivee': time(11, 35),
                'duree': timedelta(hours=0, minutes=20),
                'classe': '2',
                'prix_base': 15.00,
                'places_disponibles': 290
            },
            {
                'numero': 'TRN-5003',
                'gare_depart': 'FES-V',
                'gare_arrivee': 'MEKNES',
                'heure_depart': time(14, 0),
                'heure_arrivee': time(14, 45),
                'duree': timedelta(hours=0, minutes=45),
                'classe': '2',
                'prix_base': 25.00,
                'places_disponibles': 240
            },
            {
                'numero': 'TRN-5004',
                'gare_depart': 'MEKNES',
                'gare_arrivee': 'FES-V',
                'heure_depart': time(15, 30),
                'heure_arrivee': time(16, 15),
                'duree': timedelta(hours=0, minutes=45),
                'classe': '2',
                'prix_base': 25.00,
                'places_disponibles': 240
            },
            {
                'numero': 'TRN-9003',
                'gare_depart': 'FES-V',
                'gare_arrivee': 'TAZA',
                'heure_depart': time(15, 0),
                'heure_arrivee': time(16, 30),
                'duree': timedelta(hours=1, minutes=30),
                'classe': '2',
                'prix_base': 40.00,
                'places_disponibles': 190
            },
            {
                'numero': 'TRN-9004',
                'gare_depart': 'TAZA',
                'gare_arrivee': 'FES-V',
                'heure_depart': time(17, 30),
                'heure_arrivee': time(19, 0),
                'duree': timedelta(hours=1, minutes=30),
                'classe': '2',
                'prix_base': 40.00,
                'places_disponibles': 190
            },
            # Trains avec Casa-Port
            {
                'numero': 'TRN-1001',
                'gare_depart': 'CASA-P',
                'gare_arrivee': 'RABAT-V',
                'heure_depart': time(7, 0),
                'heure_arrivee': time(7, 55),
                'duree': timedelta(hours=0, minutes=55),
                'classe': '2',
                'prix_base': 45.00,
                'places_disponibles': 200
            },
            {
                'numero': 'TRN-1002',
                'gare_depart': 'RABAT-V',
                'gare_arrivee': 'CASA-P',
                'heure_depart': time(8, 30),
                'heure_arrivee': time(9, 25),
                'duree': timedelta(hours=0, minutes=55),
                'classe': '2',
                'prix_base': 45.00,
                'places_disponibles': 200
            },
            {
                'numero': 'TRN-1003',
                'gare_depart': 'CASA-P',
                'gare_arrivee': 'MARRAK',
                'heure_depart': time(9, 0),
                'heure_arrivee': time(12, 35),
                'duree': timedelta(hours=3, minutes=35),
                'classe': '2',
                'prix_base': 90.00,
                'places_disponibles': 180
            },
            # Trains avec Rabat-Agdal
            {
                'numero': 'TRN-1101',
                'gare_depart': 'RABAT-A',
                'gare_arrivee': 'CASA-V',
                'heure_depart': time(8, 0),
                'heure_arrivee': time(8, 55),
                'duree': timedelta(hours=0, minutes=55),
                'classe': '2',
                'prix_base': 45.00,
                'places_disponibles': 200
            },
            {
                'numero': 'TRN-1102',
                'gare_depart': 'CASA-V',
                'gare_arrivee': 'RABAT-A',
                'heure_depart': time(13, 0),
                'heure_arrivee': time(13, 55),
                'duree': timedelta(hours=0, minutes=55),
                'classe': '2',
                'prix_base': 45.00,
                'places_disponibles': 200
            },
        ]
        
        for train_data in trains_data:
            train_data['gare_depart'] = gares[train_data['gare_depart']]
            train_data['gare_arrivee'] = gares[train_data['gare_arrivee']]
            
            train, created = Train.objects.get_or_create(
                numero=train_data['numero'],
                defaults=train_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Train créé: {train}'))
        
        # Création des cartes de réduction
        cartes_data = [
            {
                'type_carte': 'jeune',
                'nom': 'Carte Jeune',
                'reduction_pourcentage': 30.00,
                'description': 'Réduction de 30% pour les moins de 27 ans'
            },
            {
                'type_carte': 'senior',
                'nom': 'Carte Senior',
                'reduction_pourcentage': 25.00,
                'description': 'Réduction de 25% pour les plus de 60 ans'
            },
            {
                'type_carte': 'famille',
                'nom': 'Carte Famille',
                'reduction_pourcentage': 20.00,
                'description': 'Réduction de 20% pour les familles nombreuses'
            },
            {
                'type_carte': 'weekend',
                'nom': 'Carte Weekend',
                'reduction_pourcentage': 15.00,
                'description': 'Réduction de 15% pour les voyages en weekend'
            },
        ]
        
        for carte_data in cartes_data:
            carte, created = CarteReduction.objects.get_or_create(
                type_carte=carte_data['type_carte'],
                defaults=carte_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Carte créée: {carte}'))
        
        # Création des offres promotionnelles
        offres_data = [
            {
                'titre': 'Offre Été 2024',
                'description': 'Profitez de 20% de réduction sur tous vos trajets cet été !',
                'reduction_pourcentage': 20.00,
                'date_debut': date.today(),
                'date_fin': date.today() + timedelta(days=90),
                'actif': True
            },
            {
                'titre': 'Promotion Première Classe',
                'description': 'Voyagez en première classe avec 15% de réduction supplémentaire.',
                'reduction_pourcentage': 15.00,
                'date_debut': date.today(),
                'date_fin': date.today() + timedelta(days=60),
                'actif': True
            },
            {
                'titre': 'Offre Weekend',
                'description': 'Réservez votre billet pour le weekend et économisez 25% !',
                'reduction_pourcentage': 25.00,
                'date_debut': date.today(),
                'date_fin': date.today() + timedelta(days=120),
                'actif': True
            },
        ]
        
        for offre_data in offres_data:
            offre, created = OffrePromotion.objects.get_or_create(
                titre=offre_data['titre'],
                defaults=offre_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Offre créée: {offre}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Données de test créées avec succès !'))

