# management/commands/fill_tblmethodepaiement.py
from django.core.management.base import BaseCommand
from hairbnb.models import TblMethodePaiement


class Command(BaseCommand):
    help = 'Remplit la table TblMethodePaiement'

    def handle(self, *args, **options):
        methodes = [
            ('card', 'Carte Bancaire'),
            ('apple_pay', 'Apple Pay'),
            ('google_pay', 'Google Pay'),
            ('paypal', 'PayPal'),
            ('bancontact', 'Bancontact'),
            ('especes', 'Espèces')
        ]

        for code, libelle in methodes:
            methode, created = TblMethodePaiement.objects.get_or_create(
                code=code,
                defaults={'libelle': libelle}
            )
            if created:
                self.stdout.write(f'✓ Méthode créée: {libelle}')
            else:
                self.stdout.write(f'→ Méthode existante: {libelle}')

        self.stdout.write(self.style.SUCCESS(f'✅ {TblMethodePaiement.objects.count()} méthodes en base'))