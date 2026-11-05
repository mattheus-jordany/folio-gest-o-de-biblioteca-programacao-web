from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Author(models.Model):
    name = models.CharField('nome', max_length=150, unique=True)
    class Meta:
        verbose_name = 'autor'
        verbose_name_plural = 'autores'
        ordering = ['name']
    def __str__(self): return self.name

class Category(models.Model):
    name = models.CharField('nome', max_length=100, unique=True)
    class Meta:
        verbose_name = 'categoria'
        ordering = ['name']
    def __str__(self): return self.name

class Publisher(models.Model):
    name = models.CharField('nome', max_length=150, unique=True)
    class Meta:
        verbose_name = 'editora'
        ordering = ['name']
    def __str__(self): return self.name

class Book(models.Model):
    title = models.CharField('título', max_length=200)
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    authors = models.ManyToManyField(Author, verbose_name='autores', related_name='books')
    category = models.ForeignKey(Category, verbose_name='categoria', on_delete=models.PROTECT, related_name='books')
    publisher = models.ForeignKey(Publisher, verbose_name='editora', on_delete=models.PROTECT, related_name='books')
    year = models.PositiveIntegerField('ano', validators=[MinValueValidator(1450), MaxValueValidator(2100)])
    created_at = models.DateTimeField('cadastrado em', auto_now_add=True)
    class Meta:
        verbose_name = 'livro'
        ordering = ['title']
    def __str__(self): return self.title

class Copy(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Disponível'
        MAINTENANCE = 'maintenance', 'Manutenção'
        LOST = 'lost', 'Extraviado'
    book = models.ForeignKey(Book, verbose_name='livro', on_delete=models.PROTECT, related_name='copies')
    code = models.CharField('tombo', max_length=30, unique=True)
    shelf = models.CharField('localização', max_length=60)
    status = models.CharField('condição', max_length=15, choices=Status.choices, default=Status.AVAILABLE)
    class Meta:
        verbose_name = 'exemplar'
        verbose_name_plural = 'exemplares'
    def __str__(self): return f'{self.code} · {self.book.title}'
