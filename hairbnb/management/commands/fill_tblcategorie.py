# management/commands/fill_tblcategorie.py
from django.core.management.base import BaseCommand
from hairbnb.models import TblCategorie


class Command(BaseCommand):
    help = 'Remplit la table TblCategorie'

    def handle(self, *args, **options):
        categories = [
            'Coupe',
            'Coloration',
            'Brushing',
            'Permanente',
            'Défrisage',
            'Extensions',
            'Soins',
            'Mèches',
            'Balayage',
            'Lissage',
            'Bouclage',
            'Coiffure mariée',
            'Coiffure événement',
            'Shampooing',
            'Massage crânien',
            'Tresses',
            'Chignons',
            'Coupe enfant',
            'Coupe homme',
            'Barbe',
            'Vente produits'
        ]

        for cat_nom in categories:
            categorie, created = TblCategorie.objects.get_or_create(intitule_categorie=cat_nom)
            if created:
                self.stdout.write(f'✓ Catégorie créée: {cat_nom}')
            else:
                self.stdout.write(f'→ Catégorie existante: {cat_nom}')

        self.stdout.write(self.style.SUCCESS(f'✅ {TblCategorie.objects.count()} catégories en base'))