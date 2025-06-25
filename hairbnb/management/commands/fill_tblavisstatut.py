# management/commands/fill_tblavisstatut.py
from django.core.management.base import BaseCommand
from hairbnb.models import TblAvisStatut


class Command(BaseCommand):
    help = 'Remplit la table TblAvisStatut'

    def handle(self, *args, **options):
        statuts = [
            ('visible', 'Visible', 'Avis visible publiquement'),
            ('masque', 'Masqué', 'Avis masqué par le salon'),
            ('supprime', 'Supprimé', 'Avis supprimé définitivement'),
            ('en_attente', 'En attente', 'Avis en attente de modération')
        ]

        for code, libelle, description in statuts:
            statut, created = TblAvisStatut.objects.get_or_create(
                code=code,
                defaults={'libelle': libelle, 'description': description}
            )
            if created:
                self.stdout.write(f'✓ Statut créé: {libelle}')
            else:
                self.stdout.write(f'→ Statut existant: {libelle}')

        self.stdout.write(self.style.SUCCESS(f'✅ {TblAvisStatut.objects.count()} statuts en base'))