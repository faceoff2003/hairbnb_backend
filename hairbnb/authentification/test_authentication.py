"""
Tests complets pour le système d'authentification
Couvre les décorateurs, Firebase services, et vues protégées
"""

from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from unittest.mock import Mock, patch, MagicMock
from datetime import date
import json

from hairbnb.models import (
    TblUser, TblLocalite, TblRue, TblAdresse, TblRole, TblSexe, TblType,
    TblCoiffeuse, TblSalon, TblCoiffeuseSalon, TblClient
)
from decorators.decorators import (
    firebase_authenticated, is_owner, is_owner_coiffeuse
)
from firebase_auth_services.firebase import verify_firebase_token


class AuthenticationSetupMixin:
    """Mixin pour setup commun aux tests d'authentification"""
    
    def setUp(self):
        """Configuration initiale pour tous les tests d'authentification"""
        self.factory = RequestFactory()
        
        # Créer les données de base
        self.localite = TblLocalite.objects.create(
            commune='Bruxelles',
            code_postal='1000'
        )
        
        self.rue = TblRue.objects.create(
            nom_rue='Rue de la Paix',
            localite=self.localite
        )
        
        self.adresse = TblAdresse.objects.create(
            numero='123',
            rue=self.rue
        )
        
        # Créer les rôles et types
        self.role_user = TblRole.objects.create(nom='user')
        self.role_coiffeuse = TblRole.objects.create(nom='coiffeuse')
        self.sexe = TblSexe.objects.create(libelle='Femme')
        self.type_client = TblType.objects.create(libelle='client')
        self.type_coiffeuse = TblType.objects.create(libelle='coiffeuse')
        
        # Créer un utilisateur client
        self.user_client = TblUser.objects.create(
            uuid='firebase-uid-client-123',
            nom='Dupont',
            prenom='Marie',
            email='marie.dupont@example.com',
            numero_telephone='+32123456789',
            date_naissance=date(1990, 5, 15),
            adresse=self.adresse,
            role=self.role_user,
            sexe_ref=self.sexe,
            type_ref=self.type_client
        )
        
        # Créer un utilisateur coiffeuse
        self.user_coiffeuse = TblUser.objects.create(
            uuid='firebase-uid-coiffeuse-123',
            nom='Martin',
            prenom='Sophie',
            email='sophie.martin@example.com',
            numero_telephone='+32123456788',
            date_naissance=date(1985, 3, 20),
            adresse=self.adresse,
            role=self.role_coiffeuse,
            sexe_ref=self.sexe,
            type_ref=self.type_coiffeuse
        )
        
        # Créer un utilisateur coiffeuse non-propriétaire
        self.user_coiffeuse_employe = TblUser.objects.create(
            uuid='firebase-uid-coiffeuse-employe-123',
            nom='Leroy',
            prenom='Claire',
            email='claire.leroy@example.com',
            numero_telephone='+32123456787',
            date_naissance=date(1990, 8, 10),
            adresse=self.adresse,
            role=self.role_coiffeuse,
            sexe_ref=self.sexe,
            type_ref=self.type_coiffeuse
        )
        
        # Créer les objets coiffeuse
        self.coiffeuse = TblCoiffeuse.objects.create(
            idTblUser=self.user_coiffeuse,
            nom_commercial='Salon Sophie'
        )
        
        self.coiffeuse_employe = TblCoiffeuse.objects.create(
            idTblUser=self.user_coiffeuse_employe,
            nom_commercial='Salon Claire'
        )
        
        # Créer un client
        self.client_obj = TblClient.objects.create(idTblUser=self.user_client)
        
        # Créer un salon
        self.salon = TblSalon.objects.create(
            nom_salon='Salon Belle Coupe',
            slogan='La beauté à votre service',
            adresse=self.adresse,
            position='50.8503,4.3517'
        )
        
        # Lier la coiffeuse au salon comme propriétaire
        self.coiffeuse_salon = TblCoiffeuseSalon.objects.create(
            coiffeuse=self.coiffeuse,
            salon=self.salon,
            est_proprietaire=True
        )
        
        # Lier la coiffeuse employée au salon (sans être propriétaire)
        self.coiffeuse_employe_salon = TblCoiffeuseSalon.objects.create(
            coiffeuse=self.coiffeuse_employe,
            salon=self.salon,
            est_proprietaire=False
        )


class FirebaseAuthenticatedDecoratorTestCase(AuthenticationSetupMixin, TestCase):
    """Tests pour le décorateur firebase_authenticated"""
    
    def setUp(self):
        super().setUp()
        
        # Créer une vue de test décorée
        @api_view(['GET'])
        @firebase_authenticated
        def test_protected_view(request):
            return Response({'message': 'success', 'user_id': request.user.idTblUser})
        
        self.test_view = test_protected_view
    
    def test_firebase_authenticated_with_valid_user(self):
        """Test du décorateur avec un utilisateur authentifié valide"""
        request = self.factory.get('/test/')
        request.user = self.user_client
        
        response = self.test_view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'success')
        self.assertEqual(response.data['user_id'], self.user_client.idTblUser)
    
    def test_firebase_authenticated_with_no_user(self):
        """Test du décorateur sans utilisateur"""
        request = self.factory.get('/test/')
        request.user = None
        
        response = self.test_view(request)
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentification requise')
    
    def test_firebase_authenticated_with_user_without_uuid(self):
        """Test du décorateur avec un utilisateur sans uuid"""
        request = self.factory.get('/test/')
        
        # Créer un mock user sans attribut uuid
        mock_user = Mock()
        del mock_user.uuid  # Supprimer l'attribut uuid
        request.user = mock_user
        
        response = self.test_view(request)
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentification requise')
    
    def test_firebase_authenticated_with_anonymous_user(self):
        """Test du décorateur avec un utilisateur anonyme"""
        from django.contrib.auth.models import AnonymousUser
        
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        
        response = self.test_view(request)
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentification requise')
    
    def test_firebase_authenticated_preserves_function_metadata(self):
        """Test que le décorateur préserve les métadonnées de la fonction"""
        @firebase_authenticated
        def test_function():
            """Test docstring"""
            return "test"
        
        self.assertEqual(test_function.__name__, 'test_function')
        self.assertEqual(test_function.__doc__, 'Test docstring')


class IsOwnerDecoratorTestCase(AuthenticationSetupMixin, TestCase):
    """Tests pour le décorateur is_owner"""
    
    def setUp(self):
        super().setUp()
        
        # Créer des vues de test décorées
        @api_view(['GET'])
        @is_owner(param_name='idTblUser', use_uuid=False)
        def test_owner_view_by_id(request, idTblUser=None):
            return Response({'message': 'success', 'user_id': idTblUser})
        
        @api_view(['GET'])
        @is_owner(param_name='uuid', use_uuid=True)
        def test_owner_view_by_uuid(request, uuid=None):
            return Response({'message': 'success', 'uuid': uuid})
        
        @api_view(['POST'])
        @is_owner(param_name='idTblUser', use_uuid=False)
        def test_owner_view_post(request):
            return Response({'message': 'success'})
        
        self.test_view_by_id = test_owner_view_by_id
        self.test_view_by_uuid = test_owner_view_by_uuid
        self.test_view_post = test_owner_view_post
    
    def test_is_owner_valid_by_id_in_kwargs(self):
        """Test du décorateur is_owner avec ID valide dans kwargs"""
        request = self.factory.get('/test/')
        request.user = self.user_client
        
        response = self.test_view_by_id(request, idTblUser=self.user_client.idTblUser)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'success')
        self.assertEqual(response.data['user_id'], self.user_client.idTblUser)
    
    def test_is_owner_valid_by_uuid_in_kwargs(self):
        """Test du décorateur is_owner avec UUID valide dans kwargs"""
        request = self.factory.get('/test/')
        request.user = self.user_client
        
        response = self.test_view_by_uuid(request, uuid=self.user_client.uuid)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'success')
        self.assertEqual(response.data['uuid'], self.user_client.uuid)
    
    def test_is_owner_invalid_id_forbidden(self):
        """Test du décorateur is_owner avec ID différent (403)"""
        request = self.factory.get('/test/')
        request.user = self.user_client
        
        # Utiliser l'ID d'un autre utilisateur
        response = self.test_view_by_id(request, idTblUser=self.user_coiffeuse.idTblUser)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'Accès interdit (non propriétaire).')
    
    def test_is_owner_invalid_uuid_forbidden(self):
        """Test du décorateur is_owner avec UUID différent (403)"""
        request = self.factory.get('/test/')
        request.user = self.user_client
        
        # Utiliser l'UUID d'un autre utilisateur
        response = self.test_view_by_uuid(request, uuid=self.user_coiffeuse.uuid)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'Accès interdit (non propriétaire).')
    
    def test_is_owner_unauthenticated_user(self):
        """Test du décorateur is_owner avec utilisateur non authentifié"""
        request = self.factory.get('/test/')
        request.user = None
        
        response = self.test_view_by_id(request, idTblUser=self.user_client.idTblUser)
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Utilisateur non authentifié.')
    
    def test_is_owner_missing_parameter(self):
        """Test du décorateur is_owner avec paramètre manquant"""
        request = self.factory.get('/test/')
        request.user = self.user_client
        
        response = self.test_view_by_id(request)  # Pas de idTblUser
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], "Paramètre 'idTblUser' manquant.")
    
    def test_is_owner_parameter_in_post_data(self):
        """Test du décorateur is_owner avec paramètre dans request.data"""
        request = self.factory.post('/test/', {'idTblUser': self.user_client.idTblUser})
        request.user = self.user_client
        request.data = {'idTblUser': self.user_client.idTblUser}
        
        response = self.test_view_post(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'success')
    
    def test_is_owner_parameter_in_query_params(self):
        """Test du décorateur is_owner avec paramètre dans query_params"""
        request = self.factory.get(f'/test/?idTblUser={self.user_client.idTblUser}')
        request.user = self.user_client
        request.query_params = {'idTblUser': str(self.user_client.idTblUser)}
        
        response = self.test_view_by_id(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'success')


class IsOwnerCoiffeuseDecoratorTestCase(AuthenticationSetupMixin, TestCase):
    """Tests pour le décorateur is_owner_coiffeuse"""
    
    def setUp(self):
        super().setUp()
        
        # Créer une vue de test décorée
        @api_view(['GET'])
        @is_owner_coiffeuse
        def test_coiffeuse_owner_view(request):
            return Response({'message': 'success', 'salon_id': 'accessible'})
        
        self.test_view = test_coiffeuse_owner_view
    
    def test_is_owner_coiffeuse_valid_owner(self):
        """Test du décorateur avec une coiffeuse propriétaire valide"""
        request = self.factory.get('/test/')
        request.user = self.user_coiffeuse
        
        response = self.test_view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'success')
        self.assertEqual(response.data['salon_id'], 'accessible')
    
    def test_is_owner_coiffeuse_not_coiffeuse_type(self):
        """Test du décorateur avec un utilisateur qui n'est pas coiffeuse"""
        request = self.factory.get('/test/')
        request.user = self.user_client  # Client, pas coiffeuse
        
        response = self.test_view(request)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data['error'], 
            'Accès non autorisé. Ce service est réservé aux coiffeuses.'
        )
    
    def test_is_owner_coiffeuse_employe_not_owner(self):
        """Test du décorateur avec une coiffeuse employée (non propriétaire)"""
        request = self.factory.get('/test/')
        request.user = self.user_coiffeuse_employe  # Employée, pas propriétaire
        
        response = self.test_view(request)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data['error'], 
            'Cette fonctionnalité est réservée aux propriétaires de salon.'
        )
    
    def test_is_owner_coiffeuse_no_coiffeuse_profile(self):
        """Test du décorateur avec un utilisateur type coiffeuse sans profil coiffeuse"""
        # Créer un utilisateur avec type coiffeuse mais sans objet TblCoiffeuse
        user_without_profile = TblUser.objects.create(
            uuid='no-profile-uuid',
            nom='SansProfile',
            prenom='User',
            email='sansprofile@example.com',
            numero_telephone='+32123456786',
            date_naissance=date(1990, 1, 1),
            adresse=self.adresse,
            role=self.role_coiffeuse,
            sexe_ref=self.sexe,
            type_ref=self.type_coiffeuse
        )
        
        request = self.factory.get('/test/')
        request.user = user_without_profile
        
        response = self.test_view(request)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Profil coiffeuse introuvable.')
    
    def test_is_owner_coiffeuse_case_insensitive_type(self):
        """Test du décorateur avec type 'Coiffeuse' (majuscule)"""
        # Créer un type avec majuscule
        type_coiffeuse_maj = TblType.objects.create(libelle='Coiffeuse')
        
        user_maj = TblUser.objects.create(
            uuid='coiffeuse-maj-uuid',
            nom='Majuscule',
            prenom='Coiffeuse',
            email='maj@example.com',
            numero_telephone='+32123456785',
            date_naissance=date(1990, 1, 1),
            adresse=self.adresse,
            role=self.role_coiffeuse,
            sexe_ref=self.sexe,
            type_ref=type_coiffeuse_maj
        )
        
        coiffeuse_maj = TblCoiffeuse.objects.create(
            idTblUser=user_maj,
            nom_commercial='Salon Maj'
        )
        
        # Créer une relation propriétaire
        TblCoiffeuseSalon.objects.create(
            coiffeuse=coiffeuse_maj,
            salon=self.salon,
            est_proprietaire=True
        )
        
        request = self.factory.get('/test/')
        request.user = user_maj
        
        response = self.test_view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'success')
    
    def test_is_owner_coiffeuse_user_without_type_ref(self):
        """Test du décorateur avec un utilisateur sans type_ref"""
        request = self.factory.get('/test/')
        
        # Mock un utilisateur sans type_ref
        mock_user = Mock()
        mock_user.type_ref = None
        request.user = mock_user
        
        response = self.test_view(request)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data['error'], 
            'Accès non autorisé. Ce service est réservé aux coiffeuses.'
        )


class FirebaseServicesTestCase(TestCase):
    """Tests pour les services Firebase"""
    
    @patch('firebase_auth_services.firebase.auth.verify_id_token')
    def test_verify_firebase_token_success(self, mock_verify):
        """Test de vérification réussie d'un token Firebase"""
        # Mock de la réponse Firebase
        mock_decoded_token = {
            'uid': 'firebase-uid-123',
            'email': 'test@example.com',
            'name': 'Test User'
        }
        mock_verify.return_value = mock_decoded_token
        
        token = 'valid-firebase-token'
        result = verify_firebase_token(token)
        
        self.assertEqual(result, mock_decoded_token)
        self.assertEqual(result['uid'], 'firebase-uid-123')
        self.assertEqual(result['email'], 'test@example.com')
        mock_verify.assert_called_once_with(token)
    
    @patch('firebase_auth_services.firebase.auth.verify_id_token')
    def test_verify_firebase_token_failure(self, mock_verify):
        """Test de vérification échouée d'un token Firebase"""
        # Mock d'une exception Firebase
        mock_verify.side_effect = Exception('Invalid token')
        
        token = 'invalid-firebase-token'
        result = verify_firebase_token(token)
        
        self.assertIsNone(result)
        mock_verify.assert_called_once_with(token)
    
    @patch('firebase_auth_services.firebase.auth.verify_id_token')
    def test_verify_firebase_token_empty_token(self, mock_verify):
        """Test de vérification avec un token vide"""
        mock_verify.side_effect = Exception('Empty token')
        
        token = ''
        result = verify_firebase_token(token)
        
        self.assertIsNone(result)
    
    @patch('firebase_auth_services.firebase.auth.verify_id_token')
    def test_verify_firebase_token_malformed_token(self, mock_verify):
        """Test de vérification avec un token malformé"""
        mock_verify.side_effect = Exception('Malformed token')
        
        token = 'malformed.token.here'
        result = verify_firebase_token(token)
        
        self.assertIsNone(result)


class AuthenticationIntegrationTestCase(AuthenticationSetupMixin, APITestCase):
    """Tests d'intégration pour l'authentification"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
    
    def test_current_user_with_authentication(self):
        """Test de l'endpoint current_user avec authentification"""
        # Simuler l'authentification
        self.client.force_authenticate(user=self.user_client)
        
        with patch('hairbnb.currentUser.currentUser_views.request') as mock_request:
            mock_request.user = self.user_client
            
            url = reverse('get_current_user')
            response = self.client.get(url)
        
        # La vue devrait fonctionner avec un utilisateur authentifié
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
    
    def test_current_user_without_authentication(self):
        """Test de l'endpoint current_user sans authentification"""
        # Ne pas authentifier l'utilisateur
        with patch('hairbnb.currentUser.currentUser_views.request') as mock_request:
            mock_request.user = None
            
            url = reverse('get_current_user')
            response = self.client.get(url)
        
        # La vue devrait retourner une erreur
        self.assertEqual(response.status_code, 404)
    
    def test_coiffeuses_info_endpoint_accessibility(self):
        """Test que l'endpoint get_coiffeuses_info est accessible sans auth"""
        url = reverse('get_coiffeuses_info')
        data = {
            'uuids': ['firebase-uid-coiffeuse-123']
        }
        
        response = self.client.post(url, data, format='json')
        
        # Cet endpoint devrait être accessible sans authentification
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['status'], 'success')


class AuthenticationMiddlewareTestCase(AuthenticationSetupMixin, TestCase):
    """Tests pour le middleware d'authentification personnalisé"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
    
    @patch('firebase_auth_services.firebase.verify_firebase_token')
    def test_firebase_token_authentication_success(self, mock_verify):
        """Test d'authentification réussie avec token Firebase"""
        # Mock de la vérification Firebase
        mock_verify.return_value = {
            'uid': self.user_client.uuid,
            'email': self.user_client.email
        }
        
        # Simuler une requête avec token Firebase
        request = self.factory.get('/test/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer valid-firebase-token'
        
        # Ici, on testerait le middleware d'authentification personnalisé
        # si il était implémenté
        
        # Pour l'instant, juste vérifier que le token est validé
        token = 'valid-firebase-token'
        result = verify_firebase_token(token)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['uid'], self.user_client.uuid)
    
    @patch('firebase_auth_services.firebase.verify_firebase_token')
    def test_firebase_token_authentication_failure(self, mock_verify):
        """Test d'authentification échouée avec token Firebase invalide"""
        # Mock d'une vérification échouée
        mock_verify.return_value = None
        
        # Simuler une requête avec token invalide
        request = self.factory.get('/test/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid-firebase-token'
        
        token = 'invalid-firebase-token'
        result = verify_firebase_token(token)
        
        self.assertIsNone(result)


class AuthenticationEdgeCasesTestCase(AuthenticationSetupMixin, TestCase):
    """Tests pour les cas particuliers d'authentification"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
    
    def test_decorator_with_multiple_parameters(self):
        """Test du décorateur is_owner avec plusieurs paramètres possibles"""
        @api_view(['POST'])
        @is_owner(param_name='user_id', use_uuid=False)
        def test_view(request):
            return Response({'message': 'success'})
        
        # Test avec paramètre dans kwargs (priorité 1)
        request = self.factory.post('/test/')
        request.user = self.user_client
        request.data = {'user_id': 999}  # Valeur différente dans data
        request.query_params = {'user_id': 888}  # Valeur différente dans query_params
        
        # kwargs devrait avoir la priorité
        response = test_view(request, user_id=self.user_client.idTblUser)
        
        self.assertEqual(response.status_code, 200)
    
    def test_decorator_parameter_priority_data_over_query(self):
        """Test de la priorité des paramètres : data > query_params"""
        @api_view(['POST'])
        @is_owner(param_name='user_id', use_uuid=False)
        def test_view(request):
            return Response({'message': 'success'})
        
        request = self.factory.post('/test/')
        request.user = self.user_client
        request.data = {'user_id': self.user_client.idTblUser}  # Valeur correcte
        request.query_params = {'user_id': 999}  # Valeur incorrecte
        
        # data devrait avoir la priorité sur query_params
        response = test_view(request)
        
        self.assertEqual(response.status_code, 200)
    
    def test_decorator_with_string_ids(self):
        """Test du décorateur is_owner avec des IDs en string"""
        @api_view(['GET'])
        @is_owner(param_name='user_id', use_uuid=False)
        def test_view(request, user_id=None):
            return Response({'message': 'success'})
        
        request = self.factory.get('/test/')
        request.user = self.user_client
        
        # Passer l'ID comme string (conversion implicite)
        response = test_view(request, user_id=str(self.user_client.idTblUser))
        
        self.assertEqual(response.status_code, 200)
    
    def test_coiffeuse_decorator_with_multiple_salons(self):
        """Test du décorateur is_owner_coiffeuse avec plusieurs salons"""
        # Créer un second salon et lier la coiffeuse comme propriétaire
        salon2 = TblSalon.objects.create(
            nom_salon='Salon Secondaire',
            adresse=self.adresse
        )
        
        TblCoiffeuseSalon.objects.create(
            coiffeuse=self.coiffeuse,
            salon=salon2,
            est_proprietaire=True
        )
        
        @api_view(['GET'])
        @is_owner_coiffeuse
        def test_view(request):
            return Response({'message': 'success'})
        
        request = self.factory.get('/test/')
        request.user = self.user_coiffeuse
        
        # Devrait passer car elle est propriétaire d'au moins un salon
        response = test_view(request)
        
        self.assertEqual(response.status_code, 200)
    
    def test_coiffeuse_decorator_with_no_salon_relation(self):
        """Test du décorateur is_owner_coiffeuse sans relation salon"""
        # Créer une coiffeuse sans aucune relation salon
        user_sans_salon = TblUser.objects.create(
            uuid='sans-salon-uuid',
            nom='SansSalon',
            prenom='Coiffeuse',
            email='sanssalon@example.com',
            numero_telephone='+32123456784',
            date_naissance=date(1990, 1, 1),
            adresse=self.adresse,
            role=self.role_coiffeuse,
            sexe_ref=self.sexe,
            type_ref=self.type_coiffeuse
        )
        
        coiffeuse_sans_salon = TblCoiffeuse.objects.create(
            idTblUser=user_sans_salon,
            nom_commercial='Salon Sans Relation'
        )
        
        @api_view(['GET'])
        @is_owner_coiffeuse
        def test_view(request):
            return Response({'message': 'success'})
        
        request = self.factory.get('/test/')
        request.user = user_sans_salon
        
        response = test_view(request)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data['error'], 
            'Cette fonctionnalité est réservée aux propriétaires de salon.'
        )


class AuthenticationPerformanceTestCase(AuthenticationSetupMixin, TestCase):
    """Tests de performance pour l'authentification"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
    
    def test_decorator_performance_with_many_requests(self):
        """Test de performance des décorateurs avec beaucoup de requêtes"""
        @api_view(['GET'])
        @firebase_authenticated
        @is_owner(param_name='user_id', use_uuid=False)
        def test_view(request, user_id=None):
            return Response({'message': 'success'})
        
        import time
        
        # Mesurer le temps pour 100 requêtes
        start_time = time.time()
        
        for i in range(100):
            request = self.factory.get('/test/')
            request.user = self.user_client
            response = test_view(request, user_id=self.user_client.idTblUser)
            self.assertEqual(response.status_code, 200)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 100 requêtes ne devraient pas prendre plus de 1 seconde
        self.assertLess(total_time, 1.0)
        
        # Temps moyen par requête ne devrait pas dépasser 5ms
        avg_time = total_time / 100
        self.assertLess(avg_time, 0.005)
    
    def test_coiffeuse_decorator_performance(self):
        """Test de performance du décorateur is_owner_coiffeuse"""
        @api_view(['GET'])
        @is_owner_coiffeuse
        def test_view(request):
            return Response({'message': 'success'})
        
        import time
        
        # Mesurer le temps pour 50 requêtes
        start_time = time.time()
        
        for i in range(50):
            request = self.factory.get('/test/')
            request.user = self.user_coiffeuse
            response = test_view(request)
            self.assertEqual(response.status_code, 200)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 50 requêtes avec requêtes DB ne devraient pas prendre plus de 2 secondes
        self.assertLess(total_time, 2.0)


class AuthenticationLoggingTestCase(AuthenticationSetupMixin, TestCase):
    """Tests pour vérifier le logging d'authentification"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
    
    @patch('firebase_auth_services.firebase.print')
    def test_firebase_verification_error_logging(self, mock_print):
        """Test que les erreurs Firebase sont loggées"""
        with patch('firebase_auth_services.firebase.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = Exception('Invalid token format')
            
            token = 'invalid-token'
            result = verify_firebase_token(token)
            
            self.assertIsNone(result)
            
            # Vérifier que l'erreur a été loggée
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            self.assertIn('❌ Erreur de vérification Firebase', call_args)
            self.assertIn('Invalid token format', call_args)


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'rest_framework',
                'hairbnb',
            ],
            REST_FRAMEWORK={
                'DEFAULT_AUTHENTICATION_CLASSES': [],
                'DEFAULT_PERMISSION_CLASSES': [],
            }
        )
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["hairbnb.authentification.test_authentication"])
