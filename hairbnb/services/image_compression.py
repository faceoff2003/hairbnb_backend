# services/image_compression.py

import os
from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile


class ImageCompressionService:
    """Service pour compresser les images uploadées"""

    # Configurations par type d'image
    COMPRESSION_SETTINGS = {
        'photo_profil': {
            'max_width': 400,
            'max_height': 400,
            'quality': 85,
            'format': 'JPEG'
        },
        'logo_salon': {
            'max_width': 300,
            'max_height': 300,
            'quality': 90,
            'format': 'PNG'
        },
        'salon_image': {
            'max_width': 800,
            'max_height': 600,
            'quality': 80,
            'format': 'JPEG'
        }
    }

    @classmethod
    def compress_image(cls, image_file, image_type='salon_image'):
        """
        Compresse une image selon le type spécifié

        Args:
            image_file: Fichier image Django
            image_type: Type d'image ('photo_profil', 'logo_salon', 'salon_image')

        Returns:
            ContentFile: Fichier compressé
        """
        # Récupérer les paramètres de compression
        settings_config = cls.COMPRESSION_SETTINGS.get(image_type, cls.COMPRESSION_SETTINGS['salon_image'])

        try:
            # Ouvrir l'image avec PIL
            img = Image.open(image_file)

            # Corriger l'orientation EXIF
            img = ImageOps.exif_transpose(img)

            # Convertir en RGB si nécessaire (pour JPEG)
            if settings_config['format'] == 'JPEG' and img.mode in ('RGBA', 'P'):
                # Créer un fond blanc pour les images transparentes
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif settings_config['format'] == 'PNG' and img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Redimensionner si nécessaire
            img = cls._resize_image(img, settings_config['max_width'], settings_config['max_height'])

            # Sauvegarder dans un buffer
            output = BytesIO()

            # Paramètres de sauvegarde selon le format
            save_kwargs = {'format': settings_config['format']}

            if settings_config['format'] == 'JPEG':
                save_kwargs.update({
                    'quality': settings_config['quality'],
                    'optimize': True,
                    'progressive': True
                })
            elif settings_config['format'] == 'PNG':
                save_kwargs.update({
                    'optimize': True,
                    'compress_level': 6
                })

            img.save(output, **save_kwargs)
            output.seek(0)

            # Générer le nouveau nom de fichier
            original_name = image_file.name
            name_without_ext = os.path.splitext(original_name)[0]
            new_extension = '.jpg' if settings_config['format'] == 'JPEG' else '.png'
            new_name = f"{name_without_ext}_compressed{new_extension}"

            # Retourner le fichier compressé
            return ContentFile(output.getvalue(), name=new_name)

        except Exception as e:
            print(f"Erreur lors de la compression: {e}")
            # En cas d'erreur, retourner le fichier original
            return image_file

    @classmethod
    def _resize_image(cls, img, max_width, max_height):
        """Redimensionne l'image en gardant les proportions"""
        width, height = img.size

        # Calculer le ratio pour garder les proportions
        ratio = min(max_width / width, max_height / height)

        # Si l'image est déjà plus petite, on la garde telle quelle
        if ratio >= 1:
            return img

        # Calculer nouvelles dimensions
        new_width = int(width * ratio)
        new_height = int(height * ratio)

        # Redimensionner avec un algorithme de qualité
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    @classmethod
    def get_file_size_mb(cls, file):
        """Retourne la taille du fichier en MB"""
        return file.size / (1024 * 1024)


# Fonction utilitaire pour les modèles
def compress_uploaded_image(image_file, image_type):
    """
    Fonction helper pour compresser une image uploadée
    À utiliser dans les méthodes save() des modèles
    """
    if image_file and hasattr(image_file, 'file'):
        return ImageCompressionService.compress_image(image_file, image_type)
    return image_file