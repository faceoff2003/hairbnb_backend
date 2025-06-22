# firebase.py

import firebase_admin
from firebase_admin import credentials, auth
import os

# 👇 Utilise ton fichier .json téléchargé depuis Firebase Console
FIREBASE_CREDENTIAL_PATH = os.path.join(os.path.dirname(__file__), 'firebase_credentials.json')

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIAL_PATH)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://hairbnb-7eeb9-default-rtdb.europe-west1.firebasedatabase.app/'
    })


# firebase.py (suite)

def verify_firebase_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token  # contient 'uid', 'email', etc.
    except Exception as e:
        print(f"❌ Erreur de vérification Firebase: {e}")
        return None
