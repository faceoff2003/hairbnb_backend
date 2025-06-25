# management/commands/fill_tblrole.py
from django.core.management.base import BaseCommand
from hairbnb.models import TblRole


class Command(BaseCommand):
    help = 'Remplit la table TblRole'

    def handle(self, *args, **options):
        roles = ['admin', 'user', 'coiffeuse']

        for role_nom in roles:
            role, created = TblRole.objects.get_or_create(nom=role_nom)
            if created:
                self.stdout.write(f'✓ Rôle créé: {role_nom}')
            else:
                self.stdout.write(f'→ Rôle existant: {role_nom}')

        self.stdout.write(self.style.SUCCESS(f'✅ {TblRole.objects.count()} rôles en base'))