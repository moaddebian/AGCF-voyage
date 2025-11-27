# Diagrammes UML - AGCF Voyages

## Diagramme de cas d'utilisation
```mermaid
%% Diagramme des principaux acteurs
usecaseDiagram
  actor Voyageur
  actor Operateur as "Opérateur AGCF"
  actor SystemePaiement as "Système de paiement"

  Voyageur --> (Rechercher un trajet)
  Voyageur --> (Réserver un billet)
  Voyageur --> (Payer et recevoir le billet)
  Voyageur --> (Gérer réservation)
  Voyageur --> (Consulter retards)

  Operateur --> (Planifier maintenance)
  Operateur --> (Signaler un retard)
  Operateur --> (Superviser tableaux de bord)

  (Réserver un billet) --> (Payer et recevoir le billet)
  (Payer et recevoir le billet) --> SystemePaiement
  (Gérer réservation) --> (Changer d'horaire)
  (Gérer réservation) --> (Annuler réservation)
  (Consulter retards) <-- (Signaler un retard)
```

## Diagramme de classes (simplifié)
```mermaid
classDiagram
    class User {
        username
        email
        password
    }
    class ProfilUtilisateur {
        telephone
        adresse
        date_naissance
    }
    class Gare {
        nom
        ville
        code
    }
    class Train {
        numero
        heure_depart
        heure_arrivee
        places_disponibles
        est_en_maintenance()
    }
    class Reservation {
        code_reservation
        date_voyage
        statut
        prix_total
    }
    class Passager {
        nom
        prenom
        date_naissance
    }
    class RetardTrain {
        date_voyage
        minutes_retard
        statut
    }
    class MaintenanceTrain {
        type_maintenance
        date_debut
        date_fin
        statut
    }
    class CarteReductionUtilisateur {
        numero_carte
        date_expiration
    }

    User "1" -- "1" ProfilUtilisateur
    User "1" -- "*" Reservation
    Reservation "1" -- "*" Passager
    Reservation "*" -- "1" Train
    Train "*" -- "*" RetardTrain
    Train "*" -- "*" MaintenanceTrain
    User "1" -- "*" CarteReductionUtilisateur
    Gare "1" <-- "*" Train : gare_depart/gare_arrivee
```

## Diagramme de séquence – Paiement et génération du billet
```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant V as Vue Paiement
    participant S as Django
    participant M as Modèles
    participant PDF as Service PDF/Email

    U->>V: Soumet formulaire de paiement
    V->>S: POST /paiement (données)
    S->>M: Vérifie réservation + stocke paiement
    M-->>S: Réservation confirmée
    S->>PDF: generer_billet_pdf(reservation)
    PDF-->>S: PDF prêt
    S->>PDF: envoyer_billet_email(reservation, pdf)
    PDF-->>S: Email envoyé
    S-->>V: Redirect confirmation + message succès
    V-->>U: Affiche confirmation et déclenche téléchargement
```

> Ces diagrammes peuvent être visualisés avec n'importe quel moteur Mermaid (GitHub, VS Code, etc.).

