(function($) {
    'use strict';
    
    function initCalculDuree() {
        // Trouver les champs d'heure de départ et d'arrivée
        const heureDepartField = $('#id_heure_depart');
        const heureArriveeField = $('#id_heure_arrivee');
        const dureeField = $('#id_duree');
        
        // Vérifier que les champs existent
        if (!heureDepartField.length || !heureArriveeField.length || !dureeField.length) {
            return false;
        }
        
        // Si les événements sont déjà attachés, ne pas les réattacher
        if (heureDepartField.data('duree-auto-initialized')) {
            return true;
        }
        
        // Marquer comme initialisé
        heureDepartField.data('duree-auto-initialized', true);
        heureArriveeField.data('duree-auto-initialized', true);
        
        // Fonction pour parser une heure (format HH:MM:SS ou HH:MM)
        function parserHeure(heureStr) {
            if (!heureStr) return null;
            const parties = heureStr.split(':');
            if (parties.length < 2) return null;
            return {
                heures: parseInt(parties[0]) || 0,
                minutes: parseInt(parties[1]) || 0,
                secondes: parseInt(parties[2]) || 0
            };
        }
        
        // Fonction pour calculer la durée
        function calculerDuree() {
            const heureDepart = heureDepartField.val();
            const heureArrivee = heureArriveeField.val();
            
            if (!heureDepart || !heureArrivee) {
                return;
            }
            
            try {
                const dep = parserHeure(heureDepart);
                const arr = parserHeure(heureArrivee);
                
                if (!dep || !arr) {
                    return;
                }
                
                // Convertir en minutes depuis minuit
                const minutesDepart = dep.heures * 60 + dep.minutes;
                const minutesArrivee = arr.heures * 60 + arr.minutes;
                
                // Calculer la différence
                let differenceMinutes = minutesArrivee - minutesDepart;
                
                // Gérer le cas où l'arrivée est le lendemain (ex: départ 23:00, arrivée 01:00)
                if (differenceMinutes < 0) {
                    differenceMinutes += 24 * 60; // Ajouter 24 heures
                }
                
                // Convertir en format DurationField
                const heures = Math.floor(differenceMinutes / 60);
                const minutes = differenceMinutes % 60;
                
                // Format Django DurationField: "DD HH:MM:SS" ou "HH:MM:SS"
                let dureeFormatee;
                if (heures >= 24) {
                    const jours = Math.floor(heures / 24);
                    const heuresRestantes = heures % 24;
                    dureeFormatee = `${jours} ${String(heuresRestantes).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:00`;
                } else {
                    dureeFormatee = `${String(heures).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:00`;
                }
                
                // Mettre à jour le champ durée
                dureeField.val(dureeFormatee);
                
                // Retirer l'erreur de validation si elle existe
                dureeField.removeClass('error');
                const errorList = dureeField.closest('.form-row, .field-duree, tr, .form-group').find('.errorlist');
                if (errorList.length) {
                    errorList.hide();
                }
                
                // Afficher un message de confirmation visuel
                let helpText = dureeField.siblings('.help-duree-auto');
                if (helpText.length === 0) {
                    // Chercher dans le parent
                    const dureeRow = dureeField.closest('.form-row, .field-duree, tr, .form-group');
                    helpText = dureeRow.find('.help-duree-auto');
                    if (helpText.length === 0) {
                        helpText = $('<p class="help help-duree-auto" style="color: #28a745; font-weight: bold; margin-top: 5px;"></p>');
                        dureeField.after(helpText);
                    }
                }
                
                const message = '✓ Durée calculée automatiquement: ' + heures + 'h' + String(minutes).padStart(2, '0');
                helpText.html(message);
                helpText.css('color', '#28a745');
                helpText.show();
            } catch (e) {
                console.error('Erreur lors du calcul de la durée:', e);
            }
        }
        
        // Écouter les changements sur les champs d'heure
        heureDepartField.on('change blur input', calculerDuree);
        heureArriveeField.on('change blur input', calculerDuree);
        
        // Calculer aussi lors de la saisie en temps réel (déclenché à chaque frappe)
        heureDepartField.on('keyup', function() {
            if (heureArriveeField.val()) {
                calculerDuree();
            }
        });
        
        heureArriveeField.on('keyup', function() {
            if (heureDepartField.val()) {
                calculerDuree();
            }
        });
        
        // Calculer automatiquement si les deux champs sont déjà remplis au chargement
        if (heureDepartField.val() && heureArriveeField.val()) {
            calculerDuree();
        }
        
        return true;
    }
    
    // Initialiser au chargement du document
    $(document).ready(function() {
        // Essayer plusieurs fois avec des délais différents pour s'assurer que le DOM est chargé
        let attempts = 0;
        const maxAttempts = 10;
        
        function tryInit() {
            attempts++;
            if (initCalculDuree() || attempts >= maxAttempts) {
                return;
            }
            setTimeout(tryInit, 200);
        }
        
        tryInit();
    });
    
    // Réinitialiser si le DOM change (pour les formulaires dynamiques)
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).on('formset:added', function() {
            setTimeout(initCalculDuree, 100);
        });
    }
})(django.jQuery || jQuery);

