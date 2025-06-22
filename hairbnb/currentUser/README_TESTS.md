# Tests CurrentUser - Guide d'utilisation

## Fichiers de tests créés

### `test_currentUser.py`
Tests complets pour le module CurrentUser couvrant :
- **Views** : `get_current_user`, `get_user_by_id`
- **Serializers** : `CurrentUserSerializer` et tous les serializers associés
- **Business Logic** : `CurrentUserData`

## Structure des tests

### 1. **CurrentUserSerializerTestCase**
Tests pour tous les serializers :
- `LocaliteSerializer` / `TblLocaliteSerializer`
- `RueSerializer` / `TblRueSerializer`
- `AdresseSerializer` / `TblAdresseSerializer`
- `TblCoiffeuseSerializer`
- `CurrentUserSerializer`

### 2. **CurrentUserViewsTestCase**
Tests pour les vues API :
- `get_current_user` (utilisateur authentifié/anonyme)
- `get_user_by_id` (utilisateur existant/inexistant)
- Tests des méthodes HTTP autorisées
- Tests avec enrichissement des données coiffeuse

### 3. **CurrentUserBusinessLogicTestCase**
Tests pour la logique métier :
- `CurrentUserData` pour clients et coiffeuses
- Gestion des salons multiples
- Cas sans adresse
- Méthode `to_dict()`

### 4. **CurrentUserIntegrationTestCase**
Tests d'intégration :
- Workflow complet coiffeuse
- Workflow complet client
- Cohérence entre différents endpoints

### 5. **CurrentUserEdgeCasesTestCase**
Tests des cas particuliers :
- Serializers sans contexte
- Objets manquants (coiffeuse/client inexistant)
- Types d'utilisateurs inconnus
- IDs invalides

### 6. **CurrentUserPerformanceTestCase**
Tests de performance :
- Serializers avec beaucoup de salons
- Optimisation des requêtes SQL

## Comment exécuter les tests

### Tous les tests CurrentUser
```bash
python manage.py test hairbnb.currentUser.test_currentUser
```

### Tests spécifiques par classe
```bash
# Tests des serializers
python manage.py test hairbnb.currentUser.test_currentUser.CurrentUserSerializerTestCase

# Tests des vues
python manage.py test hairbnb.currentUser.test_currentUser.CurrentUserViewsTestCase

# Tests de la logique métier
python manage.py test hairbnb.currentUser.test_currentUser.CurrentUserBusinessLogicTestCase

# Tests d'intégration
python manage.py test hairbnb.currentUser.test_currentUser.CurrentUserIntegrationTestCase

# Tests des cas particuliers
python manage.py test hairbnb.currentUser.test_currentUser.CurrentUserEdgeCasesTestCase
```

### Test spécifique
```bash
python manage.py test hairbnb.currentUser.test_currentUser.CurrentUserSerializerTestCase.test_current_user_serializer_coiffeuse
```

### Avec plus de détails
```bash
python manage.py test hairbnb.currentUser.test_currentUser --verbosity=2
```

### Avec couverture de code
```bash
# Installer coverage si ce n'est pas fait
pip install coverage

# Exécuter avec coverage
coverage run --source='.' manage.py test hairbnb.currentUser.test_currentUser
coverage report
coverage html  # Génère un rapport HTML
```

## Fonctionnalités testées

### ✅ **Serializers**
- Sérialisation correcte de tous les modèles
- Relations imbriquées (adresse → rue → localité)
- Champs calculés (`salons`, `salon_principal`, `est_proprietaire`)
- Conversion des URLs d'images
- Gestion des contextes de requête

### ✅ **Views**
- Récupération utilisateur authentifié
- Récupération utilisateur par ID
- Gestion des erreurs (404, utilisateur inexistant)
- Enrichissement des données pour les coiffeuses
- Restrictions des méthodes HTTP

### ✅ **Business Logic**
- Construction des données utilisateur
- Données spécifiques par type (client/coiffeuse)
- Gestion des salons multiples
- Cas sans adresse
- Conversion en dictionnaire

### ✅ **Intégration**
- Cohérence entre endpoints
- Workflow complet utilisateur
- Données cohérentes avec la base

### ✅ **Edge Cases**
- Objets manquants
- Relations cassées
- Types inconnus
- Données invalides

### ✅ **Performance**
- Optimisation des requêtes
- Gestion de volumes importants

## Structure des données testées

```json
{
  "status": "success",
  "user": {
    "idTblUser": 1,
    "uuid": "uuid-123",
    "nom": "Martin",
    "prenom": "Sophie",
    "email": "sophie@example.com",
    "type": "coiffeuse",
    "sexe": "Femme",
    "role": "coiffeuse",
    "adresse": {
      "numero": "123",
      "rue": {
        "nom_rue": "Rue de la Paix",
        "localite": {
          "commune": "Bruxelles",
          "code_postal": "1000"
        }
      }
    },
    "coiffeuse": {
      "nom_commercial": "Salon Sophie",
      "est_proprietaire": true,
      "salon_principal": {
        "idTblSalon": 1,
        "nom_salon": "Salon Belle Coupe",
        "numero_tva": "BE0123456789",
        "adresse": { "..." }
      },
      "tous_salons": [
        {
          "idTblSalon": 1,
          "nom_salon": "Salon Belle Coupe",
          "est_proprietaire": true
        }
      ]
    }
  }
}
```

## Mocks et fixtures

Les tests utilisent :
- **APITestCase** pour les tests d'API
- **Mock** pour simuler les requêtes et contextes
- **setUp()** commun via `CurrentUserSetupMixin`
- **force_authenticate()** pour simuler l'authentification
- **patch()** pour mocker les objets externes

## Métriques de couverture attendues

- **Serializers** : ~95% (toutes les méthodes et propriétés)
- **Views** : ~90% (tous les chemins principaux)
- **Business Logic** : ~95% (toute la logique métier)
- **Intégration** : ~85% (workflows principaux)

## Remarques importantes

1. **Base de données** : Les tests utilisent une base SQLite en mémoire
2. **Authentification** : Mockée pour les tests (pas de Firebase réel)
3. **Fichiers** : Les URLs d'images sont mockées
4. **Performance** : Tests inclus pour détecter les régressions N+1

## Prochaines étapes possibles

1. **Tests de load** avec beaucoup d'utilisateurs
2. **Tests de sécurité** (injection, XSS)
3. **Tests de concurrence** 
4. **Tests de cache** si implémenté
5. **Tests avec données réelles** (fixture complète)
