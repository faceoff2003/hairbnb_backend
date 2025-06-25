# management/commands/fill_tblservice.py
from django.core.management.base import BaseCommand
from hairbnb.models import TblService, TblCategorie


class Command(BaseCommand):
    help = 'Remplit la table TblService'

    def handle(self, *args, **options):
        services_data = [
            ('Coupe femme', 'Coupe classique pour femme avec shampoing', 'Coupe'),
            ('Coupe homme', 'Coupe moderne pour homme', 'Coupe'),
            ('Coupe enfant', 'Coupe adaptée aux enfants', 'Coupe'),
            ('Brushing simple', 'Mise en forme avec sèche-cheveux', 'Brushing'),
            ('Brushing bouclé', 'Brushing avec création de boucles', 'Brushing'),
            ('Coloration complète', 'Coloration de toute la chevelure', 'Coloration'),
            ('Retouche racines', 'Coloration des racines uniquement', 'Coloration'),
            ('Mèches classiques', 'Mèches avec papier aluminium', 'Mèches'),
            ('Balayage naturel', 'Technique de balayage pour effet naturel', 'Balayage'),
            ('Permanente', 'Création de boucles permanentes', 'Permanente'),
            ('Défrisage', 'Lissage permanent des cheveux', 'Défrisage'),
            ('Lissage brésilien', 'Traitement lissant à la kératine', 'Lissage'),
            ('Extensions', 'Pose d\'extensions cheveux naturels', 'Extensions'),
            ('Soin hydratant', 'Masque nourrissant pour cheveux secs', 'Soins'),
            ('Soin réparateur', 'Traitement pour cheveux abîmés', 'Soins'),
            ('Chignon simple', 'Chignon classique', 'Chignons'),
            ('Chignon mariée', 'Chignon élaboré pour mariage', 'Coiffure mariée'),
            ('Tresses africaines', 'Tressage style africain', 'Tresses'),
            ('Shampooing', 'Lavage des cheveux', 'Shampooing'),
            ('Massage crânien', 'Massage relaxant du cuir chevelu', 'Massage crânien'),
        ]

        for nom, description, categorie_nom in services_data:
            try:
                categorie = TblCategorie.objects.get(intitule_categorie=categorie_nom)
                service, created = TblService.objects.get_or_create(
                    intitule_service=nom,
                    defaults={
                        'description': description,
                        'categorie': categorie
                    }
                )
                if created:
                    self.stdout.write(f'✓ Service créé: {nom}')
                else:
                    self.stdout.write(f'→ Service existant: {nom}')
            except TblCategorie.DoesNotExist:
                self.stdout.write(f'✗ Catégorie "{categorie_nom}" introuvable pour {nom}')

        self.stdout.write(self.style.SUCCESS(f'✅ {TblService.objects.count()} services en base'))