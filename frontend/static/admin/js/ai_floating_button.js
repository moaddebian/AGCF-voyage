// Script pour créer le bouton flottant IA dans l'admin Django
(function() {
    function createAIFloatingButton() {
        // Vérifier si le bouton existe déjà
        if (document.querySelector('.ai-floating-btn')) {
            return;
        }
        
        // Créer le bouton
        const btn = document.createElement('button');
        btn.className = 'ai-floating-btn';
        btn.onclick = openAIModal;
        btn.title = 'Analyse IA des revenus et passagers';
        btn.innerHTML = '<i class="bi bi-robot"></i>';
        document.body.appendChild(btn);
        
        // Créer la modal si elle n'existe pas
        if (!document.getElementById('aiModal')) {
            const modal = document.createElement('div');
            modal.id = 'aiModal';
            modal.className = 'ai-modal';
            modal.innerHTML = `
                <div class="ai-modal-content">
                    <div class="ai-modal-header">
                        <h2>
                            <i class="bi bi-robot"></i>
                            Analyse IA - Revenus & Passagers
                        </h2>
                        <span class="ai-modal-close" onclick="closeAIModal()">&times;</span>
                    </div>
                    <div class="ai-modal-body" id="aiModalBody">
                        <div style="text-align: center; padding: 40px;">
                            <i class="bi bi-hourglass-split" style="font-size: 3rem; color: #667eea;"></i>
                            <p>Chargement de l'analyse...</p>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
    }
    
    // Créer le bouton dès que le DOM est prêt
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createAIFloatingButton);
    } else {
        createAIFloatingButton();
    }
    
    // Réessayer après un court délai au cas où
    setTimeout(createAIFloatingButton, 500);
    setTimeout(createAIFloatingButton, 1000);
    setTimeout(createAIFloatingButton, 2000);
})();

function openAIModal() {
    const modal = document.getElementById('aiModal');
    const modalBody = document.getElementById('aiModalBody');
    
    if (!modal) {
        console.error('Modal not found');
        return;
    }
    
    modal.style.display = 'block';
    
    // Charger le contenu de l'analyse
    fetch('/admin/analytics/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur HTTP: ' + response.status);
            }
            return response.text();
        })
        .then(html => {
            // Extraire le contenu du body de la réponse
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const content = doc.querySelector('.analytics-container');
            
            if (content) {
                // Extraire tous les scripts AVANT de modifier innerHTML
                const scripts = content.querySelectorAll('script');
                const scriptContents = [];
                scripts.forEach(script => {
                    if (script.src) {
                        scriptContents.push({ type: 'src', value: script.src });
                    } else {
                        scriptContents.push({ type: 'inline', value: script.textContent });
                    }
                });
                
                // Insérer le contenu HTML
                modalBody.innerHTML = content.innerHTML;
                
                // Charger Chart.js si nécessaire
                function loadChartJS(callback) {
                    if (typeof Chart !== 'undefined') {
                        callback();
                        return;
                    }
                    
                    const chartScript = document.createElement('script');
                    chartScript.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
                    chartScript.onload = callback;
                    chartScript.onerror = function() {
                        console.error('Erreur lors du chargement de Chart.js');
                    };
                    document.head.appendChild(chartScript);
                }
                
                // Exécuter les scripts après le chargement de Chart.js
                loadChartJS(function() {
                    // Attendre un peu pour que le DOM soit prêt
                    setTimeout(function() {
                        // Exécuter tous les scripts inline dans l'ordre
                        let scriptIndex = 0;
                        function executeNextScript() {
                            if (scriptIndex < scriptContents.length) {
                                const scriptData = scriptContents[scriptIndex];
                                if (scriptData.type === 'inline' && scriptData.value) {
                                    try {
                                        // Créer un script et l'exécuter
                                        const script = document.createElement('script');
                                        script.textContent = scriptData.value;
                                        script.id = 'analytics-script-' + scriptIndex;
                                        document.body.appendChild(script);
                                        
                                        // Passer au script suivant après un court délai
                                        scriptIndex++;
                                        setTimeout(executeNextScript, 50);
                                    } catch (e) {
                                        console.error('Erreur lors de l\'exécution du script:', e);
                                        scriptIndex++;
                                        setTimeout(executeNextScript, 50);
                                    }
                                } else {
                                    scriptIndex++;
                                    setTimeout(executeNextScript, 50);
                                }
                            } else {
                                // Tous les scripts sont exécutés, initialiser les graphiques
                                setTimeout(function() {
                                    if (typeof window.initializeAnalyticsCharts === 'function') {
                                        console.log('Initialisation des graphiques...');
                                        window.initializeAnalyticsCharts();
                                    } else {
                                        console.error('La fonction initializeAnalyticsCharts n\'est pas disponible');
                                        // Réessayer après un délai
                                        setTimeout(function() {
                                            if (typeof window.initializeAnalyticsCharts === 'function') {
                                                window.initializeAnalyticsCharts();
                                            }
                                        }, 500);
                                    }
                                }, 300);
                            }
                        }
                        executeNextScript();
                    }, 200);
                });
            } else {
                modalBody.innerHTML = html;
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            modalBody.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #dc3545;">
                    <i class="bi bi-exclamation-triangle" style="font-size: 3rem;"></i>
                    <p>Erreur lors du chargement de l'analyse. Veuillez réessayer.</p>
                    <p style="font-size: 0.9rem; color: #666;">${error.message}</p>
                </div>
            `;
        });
}

function closeAIModal() {
    const modal = document.getElementById('aiModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Fermer la modal en cliquant en dehors
window.onclick = function(event) {
    const modal = document.getElementById('aiModal');
    if (event.target == modal) {
        closeAIModal();
    }
}

// Fermer avec la touche Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeAIModal();
    }
});

