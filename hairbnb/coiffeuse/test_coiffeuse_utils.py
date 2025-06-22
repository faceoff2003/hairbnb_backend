"""
Tests utilitaires et serializers pour le module Coiffeuse
(À utiliser quand des serializers seront ajoutés)
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import serializers
from datetime import date

from hairbnb.models import (
    TblUser, TblLocalite, TblRue, TblAdresse, TblRole, TblSexe, TblType,
    TblCoiffeuse, TblSalon, TblCoiffeuseSalon
)
from hairbnb.coiffeuse.test_coiffeuse import CoiffeuseSetupMixin


class CoiffeuseTestUtils:
    """Utilitaires pour les tests Coiffeuse"""
    
    @staticmethod
    def create_test_coiffeuse(uuid_suffix="test", nom="Test", prenom="Coiffeuse"):
        """Créer une coiffeuse de test rapidement"""
        # Cette méthode nécessiterait les objets de base (localite, rue, etc.)
        # À implémenter selon les besoins
        pass
    
    @staticmethod
    def create_test_salon(nom_salon="Test Salon"):
        """Créer un salon de test rapidement"""
        pass
    
    @staticmethod
    def assert_coiffeuse_data_structure(test_case, coiffeuse_data):
        """Vérifier la structure standard des données coiffeuse"""
        required_fields = [
            'idTblUser', 'uuid', 'nom', 'prenom', 'photo_profil',
            'nom_commercial', 'salon', 'autres_salons'
        ]
        
        for field in required_fields:
            test_case.assertIn(field, coiffeuse_data, f"Champ manquant: {field}")
        
        # Vérifier le type des champs
        test_case.assertIsInstance(coiffeuse_data['autres_salons'], list)
        test_case.assertIsInstance(coiffeuse_data['idTblUser'], int)
        test_case.assertIsInstance(coiffeuse_data['uuid'], str)
    
    @staticmethod
    def assert_salon_data_structure(test_case, salon_data):
        """Vérifier la structure des données salon dans autres_salons"""
        required_fields = ['idTblSalon', 'nom_salon', 'est_proprietaire']
        
        for field in required_fields:
            test_case.assertIn(field, salon_data, f"Champ salon manquant: {field}")
        
        test_case.assertIsInstance(salon_data['idTblSalon'], int)
        test_case.assertIsInstance(salon_data['nom_salon'], str)
        test_case.assertIsInstance(salon_data['est_proprietaire'], bool)


# Exemple de serializers à tester (quand ils seront implémentés)
class ExampleCoiffeuseSerializer(serializers.ModelSerializer):
    """Exemple de serializer pour les tests futurs"""
    
    class Meta:
        model = TblCoiffeuse
        fields = ['idTblUser', 'nom_commercial']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Ajouter les données utilisateur
        user = instance.idTblUser
        representation.update({
            'uuid': user.uuid,
            'nom': user.nom,
            'prenom': user.prenom,
            'photo_profil': user.photo_profil.url if user.photo_profil else None
        })
        
        return representation


class ExampleCoiffeuseSerializerTestCase(CoiffeuseSetupMixin, TestCase):
    """Tests d'exemple pour les serializers futurs"""
    
    def test_example_serializer_basic(self):
        """Test basique du serializer d'exemple"""
        serializer = ExampleCoiffeuseSerializer(self.coiffeuse1)
        data = serializer.data
        
        # Vérifications de base
        self.assertEqual(data['nom_commercial'], 'Salon Sophie')
        self.assertEqual(data['uuid'], 'coiffeuse-uuid-001')
        self.assertEqual(data['nom'], 'Martin')
        self.assertEqual(data['prenom'], 'Sophie')
    
    def test_example_serializer_liste(self):
        """Test du serializer avec une liste de coiffeuses"""
        coiffeuses = [self.coiffeuse1, self.coiffeuse2, self.coiffeuse3]
        serializer = ExampleCoiffeuseSerializer(coiffeuses, many=True)
        data = serializer.data
        
        self.assertEqual(len(data), 3)
        
        # Vérifier que toutes les coiffeuses sont sérialisées
        noms = [c['nom'] for c in data]
        self.assertIn('Martin', noms)
        self.assertIn('Dubois', noms)
        self.assertIn('Leroy', noms)
    
    def test_example_serializer_validation(self):
        """Test de validation du serializer"""
        # Test avec données valides
        valid_data = {
            'nom_commercial': 'Nouveau Salon'
        }
        
        serializer = ExampleCoiffeuseSerializer(data=valid_data)
        # Note: Ce test nécessiterait un serializer complet avec validation
        # self.assertTrue(serializer.is_valid())
    
    def test_example_serializer_photo_profil_url(self):
        """Test de la conversion URL de la photo de profil"""
        # Simuler une photo de profil
        self.user_coiffeuse1.photo_profil = 'photos/test.jpg'
        self.user_coiffeuse1.save()
        
        serializer = ExampleCoiffeuseSerializer(self.coiffeuse1)
        data = serializer.data
        
        self.assertIsNotNone(data['photo_profil'])
        self.assertIn('photos/test.jpg', data['photo_profil'])


class CoiffeuseSerializerPerformanceTestCase(CoiffeuseSetupMixin, TestCase):
    """Tests de performance pour les serializers futurs"""
    
    def test_serializer_performance_bulk(self):
        """Test de performance avec sérialisation en masse"""
        # Créer 50 coiffeuses supplémentaires
        coiffeuses = []
        for i in range(50):
            user = TblUser.objects.create(
                uuid=f'perf-uuid-{i:03d}',
                nom=f'PerfNom{i}',
                prenom=f'PerfPrenom{i}',
                email=f'perf{i}@example.com',
                numero_telephone=f'+3212345{i:04d}',
                date_naissance=date(1985, 1, 1),
                adresse=self.adresse,
                role=self.role_coiffeuse,
                sexe_ref=self.sexe,
                type_ref=self.type_coiffeuse
            )
            
            coiffeuse = TblCoiffeuse.objects.create(
                idTblUser=user,
                nom_commercial=f'Salon Perf {i}'
            )
            coiffeuses.append(coiffeuse)
        
        # Mesurer le temps de sérialisation
        import time
        start_time = time.time()
        
        serializer = ExampleCoiffeuseSerializer(coiffeuses, many=True)
        data = serializer.data
        
        end_time = time.time()
        serialization_time = end_time - start_time
        
        # Vérifications
        self.assertEqual(len(data), 50)
        self.assertLess(serialization_time, 0.5)  # Moins de 500ms pour 50 objets


class CoiffeuseAPIResponseTestCase(CoiffeuseSetupMixin, APITestCase):
    """Tests pour vérifier la cohérence des réponses API"""
    
    def test_api_response_structure_consistency(self):
        """Test de cohérence de la structure des réponses API"""
        from django.urls import reverse
        
        url = reverse('get_coiffeuses_info')
        data = {
            'uuids': ['coiffeuse-uuid-001', 'coiffeuse-uuid-002']
        }
        
        response = self.client.post(url, data, format='json')
        response_data = response.json()
        
        # Vérifier la structure de réponse standard
        self.assertIn('status', response_data)
        self.assertIn('coiffeuses', response_data)
        self.assertEqual(response_data['status'], 'success')
        
        # Vérifier chaque coiffeuse
        for coiffeuse_data in response_data['coiffeuses']:
            CoiffeuseTestUtils.assert_coiffeuse_data_structure(self, coiffeuse_data)
            
            # Vérifier chaque salon
            for salon_data in coiffeuse_data['autres_salons']:
                CoiffeuseTestUtils.assert_salon_data_structure(self, salon_data)
    
    def test_api_response_error_structure(self):
        """Test de la structure des réponses d'erreur"""
        from django.urls import reverse
        
        url = reverse('get_coiffeuses_info')
        data = {'uuids': []}  # Aucun UUID
        
        response = self.client.post(url, data, format='json')
        response_data = response.json()
        
        # Structure d'erreur standard
        self.assertIn('status', response_data)
        self.assertIn('message', response_data)
        self.assertEqual(response_data['status'], 'error')
        self.assertIsInstance(response_data['message'], str)
        self.assertNotEqual(response_data['message'], '')


class CoiffeuseDataConsistencyTestCase(CoiffeuseSetupMixin, TestCase):
    """Tests de cohérence des données entre différentes sources"""
    
    def test_consistency_business_logic_vs_direct_query(self):
        """Test de cohérence entre business logic et requête directe"""
        from hairbnb.coiffeuse.coiffeuse_business_logic import MinimalCoiffeuseData
        
        # Données via business logic
        bl_data = MinimalCoiffeuseData(self.coiffeuse1).to_dict()
        
        # Données via requête directe
        coiffeuse_db = TblCoiffeuse.objects.get(idTblUser__uuid='coiffeuse-uuid-001')
        user_db = coiffeuse_db.idTblUser
        salons_db = TblCoiffeuseSalon.objects.filter(coiffeuse=coiffeuse_db)
        
        # Vérifier la cohérence
        self.assertEqual(bl_data['uuid'], user_db.uuid)
        self.assertEqual(bl_data['nom'], user_db.nom)
        self.assertEqual(bl_data['prenom'], user_db.prenom)
        self.assertEqual(bl_data['nom_commercial'], coiffeuse_db.nom_commercial)
        self.assertEqual(len(bl_data['autres_salons']), salons_db.count())
        
        # Vérifier les salons
        for salon_bl in bl_data['autres_salons']:
            salon_db = salons_db.get(salon__idTblSalon=salon_bl['idTblSalon'])
            self.assertEqual(salon_bl['nom_salon'], salon_db.salon.nom_salon)
            self.assertEqual(salon_bl['est_proprietaire'], salon_db.est_proprietaire)
    
    def test_consistency_before_after_modification(self):
        """Test de cohérence avant/après modification"""
        from hairbnb.coiffeuse.coiffeuse_business_logic import MinimalCoiffeuseData
        
        # État initial
        data_before = MinimalCoiffeuseData(self.coiffeuse1).to_dict()
        initial_salon_count = len(data_before['autres_salons'])
        
        # Modification : ajouter un nouveau salon
        nouveau_salon = TblSalon.objects.create(
            nom_salon='Nouveau Salon Test',
            adresse=self.adresse
        )
        
        TblCoiffeuseSalon.objects.create(
            coiffeuse=self.coiffeuse1,
            salon=nouveau_salon,
            est_proprietaire=False
        )
        
        # État après modification
        data_after = MinimalCoiffeuseData(self.coiffeuse1).to_dict()
        
        # Vérifications
        self.assertEqual(len(data_after['autres_salons']), initial_salon_count + 1)
        
        nouveaux_salons = [s for s in data_after['autres_salons'] 
                          if s['nom_salon'] == 'Nouveau Salon Test']
        self.assertEqual(len(nouveaux_salons), 1)
        self.assertFalse(nouveaux_salons[0]['est_proprietaire'])


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
    failures = test_runner.run_tests(["hairbnb.coiffeuse.test_coiffeuse_utils"])
