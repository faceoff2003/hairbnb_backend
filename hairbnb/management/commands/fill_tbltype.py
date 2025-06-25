# management/commands/fill_tbltype.py
from django.core.management.base import BaseCommand
from hairbnb.models import TblType


class Command(BaseCommand):
    help = 'Remplit la table TblType'

    def handle(self, *args, **options):
        types = ['Client', 'Coiffeuse']

        for type_libelle in types:
            type_obj, created = TblType.objects.get_or_create(libelle=type_libelle)
            if created:
                self.stdout.write(f'✓ Type créé: {type_libelle}')
            else:
                self.stdout.write(f'→ Type existant: {type_libelle}')

        self.stdout.write(self.style.SUCCESS(f'✅ {TblType.objects.count()} types en base'))