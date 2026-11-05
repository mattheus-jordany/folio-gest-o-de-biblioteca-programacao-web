from datetime import timedelta
from io import StringIO
from unittest.mock import patch
from django.contrib.auth.models import Permission, User
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.utils import timezone
from catalog.models import Author, Book, Category, Copy, Publisher
from .models import Loan, Reader, Reservation

class CirculationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('testadmin', '', 'test-password-only')
        self.reader = Reader.objects.create(name='Ana', email='ana@example.com', registration='01')
        self.book = Book.objects.create(title='Livro de teste', isbn='9781234567890', year=2026, category=Category.objects.create(name='Teste'), publisher=Publisher.objects.create(name='Editora'))
        self.book.authors.add(Author.objects.create(name='Autor'))
        self.copy = Copy.objects.create(book=self.book, code='TEST-01', shelf='A1')
        self.today = timezone.localdate()
        self.client.force_login(self.admin)
    def post(self, url, data):
        return self.client.post(url, data, content_type='application/json')
    def create_loan(self):
        return Loan.objects.create(copy=self.copy, reader=self.reader, issued_by=self.admin, borrowed_at=self.today, due_at=self.today+timedelta(days=7))
    def test_api_and_admin_require_authentication(self):
        self.client.logout()
        self.assertEqual(self.client.get('/api/dashboard/').status_code, 401)
        self.assertEqual(self.client.get('/admin/').status_code, 302)
    def test_reader_cannot_access_staff_dashboard(self):
        user = User.objects.create_user('reader', password='test-password-only')
        self.client.force_login(user)
        self.assertEqual(self.client.get('/api/dashboard/').status_code, 403)
    def test_read_only_staff_cannot_mutate(self):
        user = User.objects.create_user('observer', password='test-password-only', is_staff=True)
        user.user_permissions.add(Permission.objects.get(codename='view_book'))
        self.client.force_login(user)
        self.assertEqual(self.post('/api/books/', {}).status_code, 403)
    def test_book_permission_does_not_expose_reader_data(self):
        user = User.objects.create_user('catalog-only', is_staff=True)
        user.user_permissions.add(Permission.objects.get(codename='view_book'))
        self.client.force_login(user)
        self.assertEqual(self.client.get('/api/dashboard/').status_code, 403)
    def test_consulta_profile_can_read_but_not_write(self):
        user = User.objects.create_user('consulta', is_staff=True)
        user.user_permissions.set(Permission.objects.filter(content_type__app_label__in=['catalog', 'circulation'], codename__startswith='view_'))
        self.client.force_login(user)
        self.assertEqual(self.client.get('/api/dashboard/').status_code, 200)
        self.assertEqual(self.post('/api/readers/', {'name': 'Bloqueado'}).status_code, 403)
    def test_duplicate_active_loan_is_rejected(self):
        self.create_loan()
        result = self.post('/api/loans/', {'copyId': self.copy.pk, 'readerId': self.reader.pk, 'due': str(self.today+timedelta(days=4))})
        self.assertEqual(result.status_code, 400)
        self.assertEqual(Loan.objects.count(), 1)
    def test_return_releases_copy_and_allows_new_loan(self):
        loan = self.create_loan()
        self.assertEqual(self.post(f'/api/loans/{loan.pk}/return/', {}).status_code, 200)
        self.assertEqual(self.post(f'/api/loans/{loan.pk}/return/', {}).status_code, 400)
        payload = self.client.get('/api/dashboard/').json()
        self.assertTrue(payload['books'][0]['copies'][0]['available'])
        result = self.post('/api/loans/', {'copyId': self.copy.pk, 'readerId': self.reader.pk, 'due': str(self.today+timedelta(days=4))})
        self.assertEqual(result.status_code, 201)
    def test_invalid_book_rolls_back_related_records(self):
        result = self.post('/api/books/', {'title': 'Inválido', 'isbn': '9781234567891', 'author': 'Novo autor', 'category': 'Nova categoria', 'publisher': 'Nova editora', 'year': 100, 'quantity': 1})
        self.assertEqual(result.status_code, 400)
        self.assertFalse(Category.objects.filter(name='Nova categoria').exists())
    def test_book_requires_an_author(self):
        result = self.post('/api/books/', {'title': 'Sem autor', 'isbn': '9781234567891', 'author': ', ,', 'category': 'Teste', 'publisher': 'Editora', 'year': 2026})
        self.assertEqual(result.status_code, 400)
        self.assertFalse(Book.objects.filter(isbn='9781234567891').exists())
    def test_history_prevents_delete(self):
        self.create_loan()
        self.assertEqual(self.client.delete(f'/api/books/{self.book.pk}/').status_code, 400)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())
    def test_reservation_unique_while_waiting(self):
        data = {'bookId': self.book.pk, 'readerId': self.reader.pk}
        self.assertEqual(self.post('/api/reservations/', data).status_code, 201)
        self.assertEqual(self.post('/api/reservations/', data).status_code, 400)
        self.assertEqual(Reservation.objects.count(), 1)
    def test_database_rejects_invalid_due_date(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Loan.objects.create(copy=self.copy, reader=self.reader, issued_by=self.admin, borrowed_at=self.today, due_at=self.today-timedelta(days=1))
    def test_csrf_required_on_login(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/api/login/', {'username': 'testadmin', 'password': 'test-password-only'}, content_type='application/json').status_code, 403)
        token = client.get('/api/session/').json()['csrf']
        response = client.post('/api/login/', {'username': 'testadmin', 'password': 'test-password-only'}, content_type='application/json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client.get('/api/dashboard/').status_code, 200)
    def test_login_rejects_non_object_json(self):
        self.assertEqual(self.post('/api/login/', ['invalid']).status_code, 400)
    def test_seed_can_run_again_on_another_day(self):
        call_command('seed_demo', username='testadmin', stdout=StringIO())
        counts = (Book.objects.count(), Copy.objects.count(), Reader.objects.count(), Loan.objects.count(), Reservation.objects.count())
        with patch('circulation.management.commands.seed_demo.timezone.localdate', return_value=self.today+timedelta(days=1)):
            call_command('seed_demo', username='testadmin', stdout=StringIO())
        self.assertEqual(counts, (Book.objects.count(), Copy.objects.count(), Reader.objects.count(), Loan.objects.count(), Reservation.objects.count()))
    def test_jazzmin_admin_and_custom_filters_render(self):
        self.create_loan()
        self.assertContains(self.client.get('/admin/'), 'jazzmin')
        response = self.client.get('/admin/circulation/loan/?situation=active')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Em atraso')
        self.assertContains(response, 'TEST-01')
