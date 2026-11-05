import json
from datetime import date
from functools import wraps
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from catalog.models import Author, Book, Category, Copy, Publisher
from .models import Loan, Reader, Reservation

def error(message, status=400):
    return JsonResponse({'error': message}, status=status)

def protected(*permissions):
    def decorator(fn):
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated: return error('Entre para continuar.', 401)
            if not request.user.is_staff or not request.user.has_perms(permissions): return error('Seu perfil não permite esta operação.', 403)
            try:
                return fn(request, *args, **kwargs)
            except (ValueError, TypeError, KeyError, json.JSONDecodeError): return error('Verifique os campos informados.')
            except ValidationError as exc: return error(' '.join(exc.messages))
            except ProtectedError: return error('Este registro possui vínculos e não pode ser excluído.')
            except IntegrityError: return error('Registro duplicado ou operação em conflito. Atualize a página.')
        return wrapper
    return decorator

@require_http_methods(['GET'])
def session_view(request):
    return JsonResponse({'csrf': get_token(request), 'user': {'name': request.user.get_full_name() or request.user.username, 'staff': request.user.is_staff} if request.user.is_authenticated else None})

@require_http_methods(['POST'])
def login_view(request):
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict): return error('Dados inválidos.')
    except (ValueError, TypeError): return error('Dados inválidos.')
    user = authenticate(request, username=data.get('username', ''), password=data.get('password', ''))
    if user is None or not user.is_staff: return error('Usuário ou senha inválidos, ou acesso administrativo não permitido.', 401)
    login(request, user)
    return JsonResponse({'name': user.get_full_name() or user.username, 'csrf': get_token(request)})

@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    return JsonResponse({'ok': True})

def book_json(book):
    copies = list(book.copies.all())
    active_ids = set(Loan.objects.filter(copy__in=copies, returned_at__isnull=True).values_list('copy_id', flat=True))
    return {'id': book.pk, 'title': book.title, 'author': ', '.join(a.name for a in book.authors.all()), 'category': book.category.name, 'publisher': book.publisher.name, 'year': book.year, 'isbn': book.isbn, 'copies': [{'id': c.pk, 'code': c.code, 'shelf': c.shelf, 'available': c.status == 'available' and c.pk not in active_ids} for c in copies]}

@require_http_methods(['GET'])
@protected('catalog.view_book', 'catalog.view_copy', 'catalog.view_author', 'catalog.view_category', 'catalog.view_publisher', 'circulation.view_reader', 'circulation.view_loan', 'circulation.view_reservation')
def dashboard(request):
    today = timezone.localdate()
    return JsonResponse({'today': today.isoformat(), 'books': [book_json(b) for b in Book.objects.select_related('category', 'publisher').prefetch_related('authors', 'copies')], 'readers': list(Reader.objects.values('id', 'name', 'email', 'registration', 'active')), 'loans': [{'id': l.pk, 'bookId': l.copy.book_id, 'copyId': l.copy_id, 'book': l.copy.book.title, 'readerId': l.reader_id, 'reader': l.reader.name, 'borrowed': l.borrowed_at.isoformat(), 'due': l.due_at.isoformat(), 'returned': l.returned_at.isoformat() if l.returned_at else None} for l in Loan.objects.select_related('copy__book', 'reader')], 'reservations': [{'id': r.pk, 'book': r.book.title, 'reader': r.reader.name, 'created': r.created_at.date().isoformat(), 'status': r.status} for r in Reservation.objects.select_related('book', 'reader')]})

def save_book(data, instance=None):
    required = ['title', 'isbn', 'author', 'category', 'publisher', 'year']
    if any(not str(data.get(k, '')).strip() for k in required): raise ValidationError('Preencha todos os campos obrigatórios.')
    isbn = str(data['isbn']).replace('-', '').replace(' ', '')
    if len(isbn) != 13 or not isbn.isdigit(): raise ValidationError('Informe um ISBN com 13 dígitos.')
    category, _ = Category.objects.get_or_create(name=data['category'].strip())
    publisher, _ = Publisher.objects.get_or_create(name=data['publisher'].strip())
    book = instance or Book()
    book.title, book.isbn, book.year = data['title'].strip(), isbn, int(data['year'])
    book.category, book.publisher = category, publisher
    book.full_clean()
    book.save()
    names = [n.strip() for n in data['author'].split(',') if n.strip()]
    if not names: raise ValidationError('Informe pelo menos um autor.')
    authors = []
    for name in names:
        author, _ = Author.objects.get_or_create(name=name)
        author.full_clean()
        authors.append(author)
    book.authors.set(authors)
    if instance is None:
        count = int(data.get('quantity', 1))
        if count < 1 or count > 50: raise ValidationError('Cadastre de 1 a 50 exemplares por vez.')
        for i in range(count): Copy.objects.create(book=book, code=f'FOL-{book.pk:04d}-{i+1:02d}', shelf=data.get('shelf', 'A-01').strip() or 'A-01')
    return book

@require_http_methods(['POST'])
@protected('catalog.add_book')
@transaction.atomic
def books(request):
    book = save_book(json.loads(request.body))
    return JsonResponse({'id': book.pk}, status=201)

@require_http_methods(['PUT', 'DELETE'])
@protected('catalog.view_book')
@transaction.atomic
def book_detail(request, pk):
    permission = 'catalog.delete_book' if request.method == 'DELETE' else 'catalog.change_book'
    if not request.user.has_perm(permission): return error('Seu perfil não permite esta operação.', 403)
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'DELETE':
        if Loan.objects.filter(copy__book=book).exists() or book.reservations.exists(): return error('Há histórico de circulação vinculado a este livro.')
        book.copies.all().delete()
        book.delete()
    else: save_book(json.loads(request.body), book)
    return JsonResponse({'ok': True})

@require_http_methods(['POST'])
@protected('circulation.add_reader')
def readers(request):
    data = json.loads(request.body)
    reader = Reader(name=data['name'].strip(), email=data['email'].strip(), registration=data['registration'].strip())
    reader.full_clean()
    reader.save()
    return JsonResponse({'id': reader.pk}, status=201)

@require_http_methods(['POST'])
@protected('circulation.add_loan')
@transaction.atomic
def loans(request):
    data = json.loads(request.body)
    copy = get_object_or_404(Copy.objects.select_for_update(), pk=int(data['copyId']))
    loan = Loan(copy=copy, reader=get_object_or_404(Reader, pk=int(data['readerId'])), issued_by=request.user, borrowed_at=timezone.localdate(), due_at=date.fromisoformat(data['due']))
    loan.full_clean()
    loan.save()
    return JsonResponse({'id': loan.pk}, status=201)

@require_http_methods(['POST'])
@protected('circulation.change_loan')
@transaction.atomic
def return_loan(request, pk):
    loan = get_object_or_404(Loan.objects.select_for_update(), pk=pk)
    if loan.returned_at: return error('Este empréstimo já foi devolvido.')
    loan.returned_at = timezone.localdate()
    loan.full_clean()
    loan.save(update_fields=['returned_at'])
    return JsonResponse({'ok': True})

@require_http_methods(['POST'])
@protected('circulation.add_reservation')
def reservations(request):
    data = json.loads(request.body)
    reader = get_object_or_404(Reader, pk=int(data['readerId']))
    if not reader.active: return error('Leitor inativo não pode reservar.')
    reservation = Reservation(book=get_object_or_404(Book, pk=int(data['bookId'])), reader=reader)
    reservation.full_clean()
    reservation.save()
    return JsonResponse({'id': reservation.pk}, status=201)
