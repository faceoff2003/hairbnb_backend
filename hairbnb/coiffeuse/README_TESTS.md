# Tests Coiffeuse - Guide d'utilisation

## Fichiers de tests créés

### `test_coiffeuse.py`
Tests complets pour le module Coiffeuse couvrant :
- **Views** : `get_coiffeuses_info`
- **Business Logic** : `MinimalCoiffeuseData`
- **Intégration** et **Edge Cases**

## Structure des tests

### 1. **MinimalCoiffeuseDataTestCase**
Tests pour la classe de logique métier :
- ✅ Création des données minimales pour coiffeuse propriétaire
- ✅ Création des données pour coiffeuse employée
- ✅ Gestion des coiffeuses sans salon
- ✅ Gestion des photos de profil (présentes/absentes)
- ✅ Méthode `to_dict()`
- ✅ Salons avec logos

### 2. **CoiffeuseViewsTestCase**
Tests pour la vue API `get_coiffeuses_info` :
- ✅ Récupération réussie avec UUIDs valides
- ✅ Correspondances partielles (mix UUIDs valides/invalides)
- ✅ Aucun UUID fourni (erreur 400)
- ✅ Clé 'uuids' manquante
- ✅ JSON invalide (erreur 400)
- ✅ Tous les UUIDs invalides (réponse vide)
- ✅ Méthodes HTTP non autorisées (405)
- ✅ Détails complets des salons
- ✅ Gestion d'erreurs base de données (500)

### 3. **CoiffeuseIntegrationTestCase**
Tests d'intégration end-to-end :
- ✅ Workflow complet récupération multiple coiffeuses
- ✅ Recherche et vérification informations salon
- ✅ Gestion correspondances partielles
- ✅ Cohérence données API ↔ Base de données

### 4. **CoiffeuseEdgeCasesTestCase**
Tests des cas particuliers :
- ✅ Valeurs None dans les champs optionnels
- ✅ Salons sans logo
- ✅ Body de requête vide
- ✅ Données malformées
- ✅ Relations coiffeuse-salon supprimées
- ✅ UUIDs dupliqués

### 5. **CoiffeusePerformanceTestCase**
Tests de performance :
- ✅ Traitement de 20+ coiffeuses
- ✅ Coiffeuse avec 10+ salons
- ✅ Temps de réponse optimisés

### 6. **CoiffeuseLoggingTestCase**
Tests du système de logging :
- ✅ Logs en cas de succès
- ✅ Logs en cas d'erreur

## Comment exécuter les tests

### Tous les tests Coiffeuse
```bash
python manage.py test hairbnb.coiffeuse.test_coiffeuse
```

### Tests spécifiques par classe
```bash
# Tests de la business logic
python manage.py test hairbnb.coiffeuse.test_coiffeuse.MinimalCoiffeuseDataTestCase

# Tests des vues
python manage.py test hairbnb.coiffeuse.test_coiffeuse.CoiffeuseViewsTestCase

# Tests d'intégration
python manage.py test hairbnb.coiffeuse.test_coiffeuse.CoiffeuseIntegrationTestCase

# Tests des cas particuliers
python manage.py test hairbnb.coiffeuse.test_coiffeuse.CoiffeuseEdgeCasesTestCase

# Tests de performance
python manage.py test hairbnb.coiffeuse.test_coiffeuse.CoiffeusePerformanceTestCase
```

### Test spécifique
```bash
python manage.py test hairbnb.coiffeuse.test_coiffeuse.CoiffeuseViewsTestCase.test_get_coiffeuses_info_success
```

### Avec plus de détails
```bash
python manage.py test hairbnb.coiffeuse.test_coiffeuse --verbosity=2
```

### Avec couverture de code
```bash
coverage run --source='.' manage.py test hairbnb.coiffeuse.test_coiffeuse
coverage report
coverage html
```

## API testée

### Endpoint principal : `get_coiffeuses_info`

**URL:** `/coiffeuse/get_coiffeuses_info/`  
**Méthode:** POST  
**Content-Type:** application/json

**Requête:**
```json
{
  "uuids": [
    "coiffeuse-uuid-001",
    "coiffeuse-uuid-002",
    "coiffeuse-uuid-003"
  ]
}
```

**Réponse réussie (200):**
```json
{
  "status": "success",
  "coiffeuses": [
    {
      "idTblUser": 1,
      "uuid": "coiffeuse-uuid-001",
      "nom": "Martin",
      "prenom": "Sophie",
      "photo_profil": "/media/photos/profils/sophie.jpg",
      "nom_commercial": "Salon Sophie",
      "salon": null,
      "autres_salons": [
        {
          "idTblSalon": 1,
          "nom_salon": "Salon Belle Coupe",
          "est_proprietaire": true
        },
        {
          "idTblSalon": 3,
          "nom_salon": "Salon Tendance",
          "est_proprietaire": false
        }
      ]
    }
  ]
}
```

**Réponses d'erreur:**
- **400** : Aucun UUID fourni ou JSON invalide
- **405** : Méthode non autorisée (seul POST accepté)
- **500** : Erreur interne du serveur

## Fonctionnalités testées

### ✅ **Business Logic (MinimalCoiffeuseData)**
- Construction automatique des données coiffeuse
- Récupération des relations salon (propriétaire/employée)
- Gestion des champs optionnels (photo, nom commercial)
- Conversion en dictionnaire
- Performance avec volumes importants

### ✅ **Views (get_coiffeuses_info)**
- Validation des données d'entrée
- Filtrage par UUIDs
- Gestion des erreurs (JSON, validation, BDD)
- Logging approprié
- Restrictions de méthodes HTTP
- Réponses conformes au format API

### ✅ **Intégration**
- Cohérence données API ↔ Base de données
- Workflows end-to-end complets
- Gestion correspondances partielles
- Performance avec données réelles

### ✅ **Edge Cases**
- Données manquantes ou None
- Relations cassées
- Requêtes malformées
- UUIDs invalides/dupliqués
- Erreurs de base de données

## Structure des données de test

Les tests utilisent :
- **3 coiffeuses** avec profils différents
- **3 salons** avec caractéristiques variées
- **Relations multiples** coiffeuse ↔ salon
- **Rôles propriétaire/employée** mixtes

### Coiffeuses de test :
1. **Sophie Martin** - Propriétaire de "Salon Belle Coupe", employée de "Salon Tendance"
2. **Marie Dubois** - Propriétaire de "Salon Moderne"  
3. **Claire Leroy** - Employée de "Salon Belle Coupe"

### Scénarios couverts :
- Coiffeuse avec **multiple salons** (propriétaire + employée)
- Coiffeuse avec **un seul salon** (propriétaire uniquement)
- Coiffeuse **employée uniquement** (sans propriété)
- Coiffeuse **sans salon** (indépendante)

## Mocks et fixtures

- **APITestCase** pour tests d'API REST
- **Logging désactivé** pendant les tests (clarté)
- **Mock de base de données** pour erreurs simulées
- **Setup réutilisable** via `CoiffeuseSetupMixin`
- **Données cohérentes** entre tous les tests

## Métriques de couverture attendues

- **Business Logic** : ~98% (toute la logique couverte)
- **Views** : ~95% (tous les chemins d'exécution)
- **Intégration** : ~90% (workflows principaux)
- **Edge Cases** : ~85% (cas particuliers)

## Optimisations de performance

### Tests de performance inclus :
1. **Volume élevé** : 20+ coiffeuses simultanées
2. **Relations multiples** : 10+ salons par coiffeuse
3. **Temps de réponse** : < 1 seconde pour 20 coiffeuses
4. **Optimisation requêtes** : Prévention N+1

### Seuils de performance :
- ⚡ **< 100ms** pour 1-5 coiffeuses
- ⚡ **< 500ms** pour 5-20 coiffeuses  
- ⚡ **< 1s** pour 20+ coiffeuses

## Logging et debugging

Les tests vérifient :
- ✅ **Logs d'information** (UUIDs reçus, résultats trouvés)
- ✅ **Logs d'erreur** (JSON invalide, erreurs BDD)
- ✅ **Stack traces** pour erreurs internes
- ✅ **Désactivation logs** pendant tests (performance)

## Prochaines étapes possibles

1. **Tests de charge** avec 100+ coiffeuses
2. **Tests de sécurité** (injection, validation)
3. **Tests avec cache** Redis/Memcached
4. **Tests de concurrence** (accès simultanés)
5. **Tests avec données réelles** (fixtures complètes)

## Remarques importantes

### Limitations actuelles :
- **Serializers vide** : Pas de tests serializers (fichier vide)
- **Pas d'authentification** : Endpoint public pour l'instant
- **Logging mockée** : Tests logging nécessitent mocks

### Points d'attention :
- **Performance** : Surveiller les requêtes N+1
- **Mémoire** : Attention aux volumes de données
- **Cohérence** : Synchronisation coiffeuse ↔ salon

### Bonnes pratiques :
- **Setup centralisé** via Mixin
- **Tests isolés** (pas d'effets de bord)
- **Assertions explicites** (messages d'erreur clairs)
- **Couverture complète** (success + error paths)

## Intégration CI/CD

### Commandes pour CI :
```bash
# Tests rapides (sans performance)
python manage.py test hairbnb.coiffeuse.test_coiffeuse --exclude-tag=performance

# Tests complets avec coverage
coverage run --source='hairbnb.coiffeuse' manage.py test hairbnb.coiffeuse.test_coiffeuse
coverage report --fail-under=90

# Tests de performance uniquement
python manage.py test hairbnb.coiffeuse.test_coiffeuse.CoiffeusePerformanceTestCase
```

### Métriques CI attendues :
- ✅ **Tous les tests passent** (0 échecs)
- ✅ **Coverage > 90%** (couverture élevée)
- ✅ **Performance < seuils** (temps de réponse)
- ✅ **0 erreurs lint** (qualité code)
