# management/commands/fill_tblemailstatus.py
from django.core.management.base import BaseCommand
from hairbnb.models import TblEmailStatus


class Command(BaseCommand):
    help = 'Remplit la table TblEmailStatus'

    def handle(self, *args, **options):
        statuts = [
            ('en_attente', 'En attente d\'envoi'),
            ('envoye', 'Envoyé'),
            ('echec', 'Échec d\'envoi'),
            ('lu', 'Lu par le destinataire')
        ]

        for code, libelle in statuts:
            statut, created = TblEmailStatus.objects.get_or_create(
                code=code,
                defaults={'libelle': libelle}
            )
            if created:
                self.stdout.write(f'✓ Statut créé: {libelle}')
            else:
                self.stdout.write(f'→ Statut existant: {libelle}')

        self.stdout.write(self.style.SUCCESS(f'✅ {TblEmailStatus.objects.count()} statuts en base'))