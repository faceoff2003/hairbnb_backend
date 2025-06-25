# management/commands/fill_tblsexe.py
from django.core.management.base import BaseCommand
from hairbnb.models import TblSexe


class Command(BaseCommand):
    help = 'Remplit la table TblSexe'

    def handle(self, *args, **options):
        sexes = ['Homme', 'Femme', 'Autre']

        for sexe_libelle in sexes:
            sexe, created = TblSexe.objects.get_or_create(libelle=sexe_libelle)
            if created:
                self.stdout.write(f'✓ Sexe créé: {sexe_libelle}')
            else:
                self.stdout.write(f'→ Sexe existant: {sexe_libelle}')

        self.stdout.write(self.style.SUCCESS(f'✅ {TblSexe.objects.count()} enregistrements en base'))