# services/image_utils.py

import uuid
import os
from datetime import datetime


def generate_unique_filename(original_filename, prefix=""):
    """
    Génère un nom de fichier unique

    Args:
        original_filename: nom original du fichier
        prefix: préfixe optionnel (ex: 'profile_', 'salon_')

    Returns:
        str: nouveau nom unique
    """
    # Récupère l'extension du fichier original
    _, extension = os.path.splitext(original_filename)

    # Génère un UUID unique (32 caractères)
    unique_id = uuid.uuid4().hex

    # Combine tout
    new_filename = f"{prefix}{unique_id}{extension}"

    return new_filename


def generate_timestamped_filename(original_filename, prefix=""):
    """
    Génère un nom avec timestamp + UUID court

    Args:
        original_filename: nom original
        prefix: préfixe optionnel

    Returns:
        str: nom avec timestamp
    """
    # Extension du fichier
    _, extension = os.path.splitext(original_filename)

    # Timestamp actuel (YYYYMMDD_HHMMSS)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # UUID court (8 premiers caractères)
    short_uuid = uuid.uuid4().hex[:8]

    # Combine : prefix_20241225_143022_a1b2c3d4.jpg
    new_filename = f"{prefix}{timestamp}_{short_uuid}{extension}"

    return new_filename


# Fonctions pour upload_to dans les modèles Django

def upload_profile_photo(instance, filename):
    """Fonction pour photo_profil avec nom unique"""
    new_filename = generate_unique_filename(filename, "profile_")
    return f"photos/profils/{new_filename}"


def upload_salon_logo(instance, filename):
    """Fonction pour logo_salon avec nom unique"""
    new_filename = generate_unique_filename(filename, "logo_")
    return f"photos/logos/{new_filename}"


def upload_salon_image(instance, filename):
    """Fonction pour images de salon avec nom unique"""
    new_filename = generate_unique_filename(filename, "salon_")
    return f"photos/salon/{new_filename}"


# Version avec timestamp si tu préfères
def upload_salon_image_timestamped(instance, filename):
    """Fonction avec timestamp pour images salon"""
    new_filename = generate_timestamped_filename(filename, "salon_")
    return f"photos/salon/{new_filename}"