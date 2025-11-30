"""
Patch pour corriger le problème de compatibilité Python 3.14.0 avec Django
Problème: 'super' object has no attribute 'dicts' dans django/template/context.py
"""
import django.template.context as context_module
import copy

# Sauvegarder la méthode originale si elle existe
if hasattr(context_module.Context, '_copy_'):
    _original_copy = context_module.Context._copy_
else:
    _original_copy = None

def _patched_copy(self):
    """Version corrigée de _copy_ compatible avec Python 3.14.0"""
    # Créer une nouvelle instance du contexte
    new_context = self.__class__()
    
    # Copier les dictionnaires du contexte
    if hasattr(self, 'dicts'):
        # Si dicts existe, le copier
        new_context.dicts = [copy.copy(d) if hasattr(d, 'copy') else d for d in self.dicts]
    elif hasattr(self, '_dict'):
        # Sinon utiliser _dict
        new_context._dict = copy.copy(self._dict) if hasattr(self._dict, 'copy') else self._dict
    
    # Copier les autres attributs importants
    for attr in ['autoescape', 'current_app', 'use_l10n', 'use_tz']:
        if hasattr(self, attr):
            try:
                setattr(new_context, attr, getattr(self, attr))
            except (AttributeError, TypeError):
                pass
    
    return new_context

# Appliquer le patch
context_module.Context._copy_ = _patched_copy

