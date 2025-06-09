#!/usr/bin/env python3
"""
Script de test pour vérifier si le nouvel endpoint salons-list fonctionne correctement.
"""

import os
import sys
import django
import requests

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hairbnb_backend.settings')
django.setup()

from hairbnb.models import TblSalon

def test_local_endpoint():
    """Test l'endpoint en local"""
    try:
        # Vérifier combien de salons sont en base
        salon_count = TblSalon.objects.count()
        print(f"💡 Nombre de salons en base de données : {salon_count}")
        
        if salon_count == 0:
            print("⚠️  Aucun salon trouvé en base. Vous devez d'abord créer des salons.")
            return
        
        # Lister quelques salons pour debug
        print("\n📋 Premiers salons en base :")
        for salon in TblSalon.objects.all()[:3]:
            print(f"  - {salon.nom_salon} (ID: {salon.idTblSalon})")
        
        # Test de l'endpoint avec requests
        url = "http://127.0.0.1:8000/api/salons-list/"
        print(f"\n🔗 Test de l'endpoint : {url}")
        
        response = requests.get(url)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès ! Nombre de salons retournés : {data.get('count', 0)}")
            print(f"📄 Premiers salons : {data.get('salons', [])[:2]}")
        else:
            print(f"❌ Erreur : {response.text}")
            
    except requests.ConnectionError:
        print("❌ Erreur de connexion. Assurez-vous que le serveur Django est lancé.")
    except Exception as e:
        print(f"❌ Erreur inattendue : {str(e)}")

if __name__ == "__main__":
    test_local_endpoint()
