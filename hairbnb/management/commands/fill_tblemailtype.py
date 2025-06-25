# management/commands/fill_tblemailtype.py
from django.core.management.base import BaseCommand
from hairbnb.models import TblEmailType


class Command(BaseCommand):
    help = 'Remplit la table TblEmailType'

    def handle(self, *args, **options):
        types_email = [
            ('confirmation_rdv', 'Confirmation de rendez-vous'),
            ('rappel_rdv', 'Rappel de rendez-vous'),
            ('annulation_rdv', 'Annulation de rendez-vous'),
            ('modification_rdv', 'Modification de rendez-vous'),
            ('paiement_confirme', 'Confirmation de paiement'),
            ('bienvenue', 'Email de bienvenue'),
            ('promotion', 'Promotion / Offre spéciale'),
            ('newsletter', 'Newsletter')
        ]

        for code, libelle in types_email:
            email_type, created = TblEmailType.objects.get_or_create(
                code=code,
                defaults={'libelle': libelle}
            )
            if created:
                self.stdout.write(f'✓ Type créé: {libelle}')
            else:
                self.stdout.write(f'→ Type existant: {libelle}')

        self.stdout.write(self.style.SUCCESS(f'✅ {TblEmailType.objects.count()} types en base'))