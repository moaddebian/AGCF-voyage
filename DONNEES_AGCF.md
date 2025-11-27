# Données ONCF - AGCF Voyages

Ce document décrit les données basées sur l'Office National des Chemins de Fer du Maroc (ONCF) intégrées dans l'application.

## ⚠️ Note importante

Ces données sont créées à des fins de démonstration et de test. Elles sont basées sur des informations publiques sur l'ONCF mais ne représentent pas les données officielles en temps réel. Pour des données réelles, veuillez consulter le site officiel [oncf-voyages.ma](https://www.oncf-voyages.ma).

## Gares ONCF intégrées

L'application contient **14 gares marocaines** principales :

### Gares principales

1. **Casa-Voyageurs** (Casablanca) - Gare principale de Casablanca
2. **Casa-Port** (Casablanca) - Gare secondaire de Casablanca
3. **Rabat-Ville** (Rabat) - Gare principale de la capitale
4. **Rabat-Agdal** (Rabat) - Gare du quartier Agdal
5. **Fès-Ville** (Fès) - Gare principale de Fès
6. **Marrakech** (Marrakech) - Gare de Marrakech
7. **Tanger-Ville** (Tanger) - Gare principale de Tanger
8. **Meknès-Ville** (Meknès) - Gare de Meknès
9. **Oujda** (Oujda) - Gare de l'Est du Maroc
10. **Kénitra** (Kénitra) - Gare de Kénitra
11. **Salé** (Salé) - Gare de Salé
12. **Tétouan** (Tétouan) - Gare du Nord
13. **Taza** (Taza) - Gare de Taza
14. **Nador** (Nador) - Gare de Nador

## Types de trains

### Al Boraq (ALB) - Train à Grande Vitesse

Le **Al Boraq** est le TGV marocain qui relie Casablanca à Tanger en environ 2h15.

**Lignes principales :**
- Casablanca ↔ Tanger (via Rabat)
- Casablanca ↔ Rabat

**Caractéristiques :**
- Vitesse maximale : 320 km/h
- Confort moderne
- Deux classes disponibles

### Trains classiques (TRN)

Trains classiques de l'ONCF desservant les principales villes du Maroc.

**Lignes principales :**
- Casablanca ↔ Fès
- Casablanca ↔ Marrakech
- Casablanca ↔ Oujda
- Fès ↔ Meknès
- Fès ↔ Taza
- Rabat ↔ Salé
- Casablanca ↔ Kénitra

## Exemples de trajets

### Al Boraq - Casablanca → Tanger
- **Durée :** 2h15
- **Prix 1ère classe :** 140 MAD
- **Prix 2ème classe :** 95 MAD
- **Horaires :** Plusieurs départs quotidiens

### Train classique - Casablanca → Fès
- **Durée :** 3h15
- **Prix 1ère classe :** 95 MAD
- **Prix 2ème classe :** 75 MAD
- **Horaires :** Plusieurs départs quotidiens

### Train classique - Casablanca → Marrakech
- **Durée :** 3h30
- **Prix 1ère classe :** 120 MAD
- **Prix 2ème classe :** 90 MAD
- **Horaires :** Plusieurs départs quotidiens

## Prix et tarification

Les prix dans l'application sont exprimés en **MAD (Dirhams marocains)** et sont indicatifs. Les prix réels peuvent varier selon :
- La période (haute/basse saison)
- Les promotions en cours
- Le type de train
- La classe choisie

## Horaires

Les horaires dans l'application sont des exemples représentatifs. Les horaires réels de l'ONCF peuvent être consultés sur :
- Site web : [oncf-voyages.ma](https://www.oncf-voyages.ma)
- Application mobile ONCF Voyages
- Gares et points de vente ONCF

## Mise à jour des données

Pour mettre à jour les données avec de nouvelles informations :

```bash
# Supprimer les anciennes données
python manage.py shell -c "from reservations.models import Gare, Train; Gare.objects.all().delete(); Train.objects.all().delete()"

# Recréer les données
python manage.py init_data
```

## Ajout de nouvelles gares

Pour ajouter de nouvelles gares, modifiez le fichier `reservations/management/commands/init_data.py` et ajoutez les gares dans la liste `gares_data`.

## Ajout de nouveaux trains

Pour ajouter de nouveaux trains, modifiez le fichier `reservations/management/commands/init_data.py` et ajoutez les trains dans la liste `trains_data`.

## Ressources officielles ONCF

- Site officiel : [www.oncf.ma](https://www.oncf.ma)
- Réservation en ligne : [oncf-voyages.ma](https://www.oncf-voyages.ma)
- Centre d'appels : 2255 (depuis le Maroc)
- Application mobile : ONCF Voyages (iOS et Android)

## Statistiques des données

- **Total gares :** 14
- **Total trains :** 25
- **Lignes Al Boraq :** 7 trains
- **Lignes classiques :** 18 trains
- **Villes desservies :** 10 villes principales

---

**Note :** Ces données sont à des fins de démonstration uniquement. Pour des informations officielles et à jour, consultez le site de l'ONCF.

