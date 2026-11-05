from datetime import timedelta
from getpass import getpass
from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from catalog.models import Author, Book, Category, Copy, Publisher
from circulation.models import Loan, Reader, Reservation

class Command(BaseCommand):
    help = 'Cria dados para apresentação e um administrador com senha informada pelo terminal.'
    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin')
    @transaction.atomic
    def handle(self, *args, **options):
        username = options['username']
        admin = User.objects.filter(username=username).first()
        if admin and not admin.is_superuser: raise CommandError('O usuário já existe e não é administrador.')
        if not admin:
            password = getpass('Senha do administrador (mínimo 10 caracteres): ')
            if len(password) < 10: raise CommandError('Use pelo menos 10 caracteres.')
            admin = User.objects.create_superuser(username, '', password, first_name='Administrador')
        librarian, _ = Group.objects.get_or_create(name='Bibliotecários')
        librarian.permissions.set(Permission.objects.filter(content_type__app_label__in=['catalog', 'circulation']).exclude(codename__startswith='delete_'))
        observer, _ = Group.objects.get_or_create(name='Consulta')
        observer.permissions.set(Permission.objects.filter(content_type__app_label__in=['catalog', 'circulation'], codename__startswith='view_'))
        records = [('Dom Casmurro', 'Machado de Assis', 'Literatura brasileira', 'Companhia das Letras', 1899, '9788535914849'), ('A hora da estrela', 'Clarice Lispector', 'Literatura brasileira', 'Rocco', 1977, '9788532529626'), ('O pequeno príncipe', 'Antoine de Saint-Exupéry', 'Literatura estrangeira', 'Agir', 1943, '9788522005239'), ('Clean Code', 'Robert C. Martin', 'Tecnologia', 'Alta Books', 2008, '9788576082675'), ('Sapiens', 'Yuval Noah Harari', 'História', 'Companhia das Letras', 2011, '9788525432186'), ('1984', 'George Orwell', 'Literatura estrangeira', 'Companhia das Letras', 1949, '9788535914848'), ('Torto arado', 'Itamar Vieira Junior', 'Literatura brasileira', 'Todavia', 2019, '9786580309313'), ('O universo numa casca de noz', 'Stephen Hawking', 'Ciência', 'Intrínseca', 2001, '9788580578889')]
        copies = []
        for i, (title, author, category, publisher, year, isbn) in enumerate(records):
            cat, _ = Category.objects.get_or_create(name=category)
            pub, _ = Publisher.objects.get_or_create(name=publisher)
            book, _ = Book.objects.get_or_create(isbn=isbn, defaults={'title': title, 'category': cat, 'publisher': pub, 'year': year})
            book.authors.add(Author.objects.get_or_create(name=author)[0])
            for n in range(1, 4):
                copy, _ = Copy.objects.get_or_create(code=f'FOL-{i+1:04d}-{n:02d}', defaults={'book': book, 'shelf': f'{chr(65+i//3)}-{i+1:02d}'})
                if n == 1: copies.append(copy)
        readers = []
        for i, name in enumerate(['Ana Carolina Silva', 'Pedro Henrique Santos', 'Mariana Oliveira', 'Lucas Ferreira', 'Beatriz Costa', 'Rafael Almeida']):
            reader, _ = Reader.objects.get_or_create(registration=f'2026{i+1:04d}', defaults={'name': name, 'email': f'leitor{i+1}@example.com'})
            readers.append(reader)
        today = timezone.localdate()
        for i in range(5):
            if not Loan.objects.filter(copy=copies[i]).exists():
                Loan.objects.create(copy=copies[i], reader=readers[i], borrowed_at=today-timedelta(days=10+i), issued_by=admin, due_at=today+timedelta(days=i-2))
        Reservation.objects.get_or_create(book=copies[5].book, reader=readers[0], status='waiting')
        self.stdout.write(self.style.SUCCESS('Dados preparados. Entre com o administrador informado.'))
