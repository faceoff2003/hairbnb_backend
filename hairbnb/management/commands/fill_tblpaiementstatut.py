# management/commands/fill_tblpaiementstatut.py
from django.core.management.base import BaseCommand
from hairbnb.models import TblPaiementStatut


class Command(BaseCommand):
    help = 'Remplit la table TblPaiementStatut'

    def handle(self, *args, **options):
        statuts = [
            ('en_attente', 'En attente'),
            ('paye', 'Payé'),
            ('rembourse', 'Remboursé'),
            ('annule', 'Annulé'),
            ('echec', 'Échec')
        ]

        for code, libelle in statuts:
            statut, created = TblPaiementStatut.objects.get_or_create(
                code=code,
                defaults={'libelle': libelle}
            )
            if created:
                self.stdout.write(f'✓ Statut créé: {libelle}')
            else:
                self.stdout.write(f'→ Statut existant: {libelle}')

        self.stdout.write(self.style.SUCCESS(f'✅ {TblPaiementStatut.objects.count()} statuts en base'))