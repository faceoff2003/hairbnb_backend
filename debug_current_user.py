#!/usr/bin/env python3
"""
Script de diagnostic pour déboguer le problème avec get_current_user
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hairbnb_backend.settings')
django.setup()

from hairbnb.models import TblUser, TblCoiffeuse
from hairbnb.currentUser.CurrentUser_serializerOld import CurrentUserSerializer, TblCoiffeuseSerializer

def debug_user_ahmad():
    """Diagnostic pour l'utilisateur Ahmad Bihiri"""
    print("🔍 === DIAGNOSTIC DEBUG AHMAD BIHIRI ===")
    
    try:
        # 1. Récupérer l'utilisateur par ID
        user = TblUser.objects.get(idTblUser=10)
        print(f"✅ Utilisateur trouvé: {user}")
        print(f"✅ user.type_ref: {user.type_ref}")
        print(f"✅ user.role: {user.role}")
        
        # 2. Vérifier la relation coiffeuse
        print(f"✅ hasattr(user, 'coiffeuse'): {hasattr(user, 'coiffeuse')}")
        
        if hasattr(user, 'coiffeuse'):
            coiffeuse_obj = user.coiffeuse
            print(f"✅ coiffeuse_obj: {coiffeuse_obj}")
            print(f"✅ Type de coiffeuse_obj: {type(coiffeuse_obj)}")
            
            # 3. Tester la sérialisation de la coiffeuse séparément
            print("\n🔍 === TEST SERIALIZATION COIFFEUSE ===")
            try:
                serializer = TblCoiffeuseSerializer(coiffeuse_obj)
                print(f"✅ TblCoiffeuseSerializer créé avec succès")
                
                # Tester chaque méthode individuellement
                print("\n🔍 === TEST get_salons ===")
                salons = serializer.get_salons(coiffeuse_obj)
                print(f"✅ get_salons: {salons}")
                
                print("\n🔍 === TEST get_salon_principal ===")
                salon_principal = serializer.get_salon_principal(coiffeuse_obj)
                print(f"✅ get_salon_principal: {salon_principal}")
                
                print("\n🔍 === TEST get_est_proprietaire ===")
                est_proprietaire = serializer.get_est_proprietaire(coiffeuse_obj)
                print(f"✅ get_est_proprietaire: {est_proprietaire}")
                
                print("\n🔍 === TEST .data complet ===")
                data = serializer.data
                print(f"✅ Serializer.data: {data}")
                
            except Exception as e:
                print(f"❌ ERREUR dans TblCoiffeuseSerializer: {str(e)}")
                import traceback
                print(f"❌ Traceback: {traceback.format_exc()}")
                
        # 4. Tester la sérialisation complète
        print("\n🔍 === TEST SERIALIZATION COMPLÈTE ===")
        try:
            serializer = CurrentUserSerializer(user)
            print(f"✅ CurrentUserSerializer créé avec succès")
            
            # Tester get_coiffeuse_data directement
            print("\n🔍 === TEST get_coiffeuse_data ===")
            coiffeuse_data = serializer.get_coiffeuse_data(user)
            print(f"✅ get_coiffeuse_data: {coiffeuse_data}")
            
            # Tester le .data complet
            print("\n🔍 === TEST .data complet ===")
            data = serializer.data
            print(f"✅ CurrentUserSerializer.data: {data}")
            
        except Exception as e:
            print(f"❌ ERREUR dans CurrentUserSerializer: {str(e)}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            
    except TblUser.DoesNotExist:
        print("❌ Utilisateur avec ID 10 non trouvé")
    except Exception as e:
        print(f"❌ ERREUR générale: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

def debug_coiffeuse_relations():
    """Diagnostic des relations coiffeuse"""
    print("\n🔍 === DIAGNOSTIC RELATIONS COIFFEUSE ===")
    
    try:
        from hairbnb.models import TblCoiffeuseSalon
        
        user = TblUser.objects.get(idTblUser=10)
        if hasattr(user, 'coiffeuse'):
            coiffeuse = user.coiffeuse
            
            # Vérifier les relations salon
            print(f"✅ Coiffeuse: {coiffeuse}")
            
            # Relations TblCoiffeuseSalon
            salon_relations = TblCoiffeuseSalon.objects.filter(coiffeuse=coiffeuse)
            print(f"✅ Nombre de relations salon: {salon_relations.count()}")
            
            for relation in salon_relations:
                print(f"  - Salon: {relation.salon}")
                print(f"  - Est propriétaire: {relation.est_proprietaire}")
                print(f"  - Nom salon: {relation.salon.nom_salon}")
                
                # Vérifier l'adresse du salon
                if relation.salon.adresse:
                    print(f"  - Adresse salon: {relation.salon.adresse}")
                else:
                    print(f"  - ⚠️ Pas d'adresse pour ce salon")
                
                # Vérifier le logo
                if relation.salon.logo_salon:
                    print(f"  - Logo salon: {relation.salon.logo_salon}")
                    try:
                        url = relation.salon.logo_salon.url
                        print(f"  - URL logo: {url}")
                    except Exception as e:
                        print(f"  - ❌ Erreur URL logo: {e}")
                else:
                    print(f"  - ⚠️ Pas de logo pour ce salon")
                    
    except Exception as e:
        print(f"❌ ERREUR dans debug_coiffeuse_relations: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    print("🚀 Début du diagnostic...")
    debug_user_ahmad()
    debug_coiffeuse_relations()
    print("🏁 Fin du diagnostic")
