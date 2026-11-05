from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

class Reader(models.Model):
    name = models.CharField('nome', max_length=150)
    email = models.EmailField('e-mail', unique=True)
    registration = models.CharField('matrícula', max_length=30, unique=True)
    active = models.BooleanField('ativo', default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='usuário')
    class Meta:
        verbose_name = 'leitor'
        verbose_name_plural = 'leitores'
        ordering = ['name']
    def __str__(self): return self.name

class Loan(models.Model):
    copy = models.ForeignKey('catalog.Copy', on_delete=models.PROTECT, related_name='loans', verbose_name='exemplar')
    reader = models.ForeignKey(Reader, on_delete=models.PROTECT, related_name='loans', verbose_name='leitor')
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='responsável')
    borrowed_at = models.DateField('retirada')
    due_at = models.DateField('prazo de devolução')
    returned_at = models.DateField('devolvido em', null=True, blank=True)
    class Meta:
        verbose_name = 'empréstimo'
        ordering = ['-borrowed_at', '-pk']
        constraints = [models.UniqueConstraint(fields=['copy'], condition=Q(returned_at__isnull=True), name='one_active_loan_per_copy'), models.CheckConstraint(condition=Q(due_at__gte=models.F('borrowed_at')), name='loan_due_after_borrow'), models.CheckConstraint(condition=Q(returned_at__isnull=True) | Q(returned_at__gte=models.F('borrowed_at')), name='return_after_borrow')]
    def clean(self):
        super().clean()
        if self.copy_id and self.copy.status != 'available' and not self.returned_at:
            raise ValidationError('Exemplar indisponível para empréstimo.')
        if self.reader_id and not self.reader.active and not self.returned_at:
            raise ValidationError('Leitor inativo não pode retirar exemplares.')
    def __str__(self): return f'{self.reader} · {self.copy}'

class Reservation(models.Model):
    class Status(models.TextChoices):
        WAITING = 'waiting', 'Aguardando'
        FULFILLED = 'fulfilled', 'Atendida'
        CANCELLED = 'cancelled', 'Cancelada'
    book = models.ForeignKey('catalog.Book', on_delete=models.PROTECT, related_name='reservations', verbose_name='livro')
    reader = models.ForeignKey(Reader, on_delete=models.PROTECT, related_name='reservations', verbose_name='leitor')
    created_at = models.DateTimeField('solicitada em', auto_now_add=True)
    status = models.CharField('situação', max_length=15, choices=Status.choices, default=Status.WAITING)
    class Meta:
        verbose_name = 'reserva'
        ordering = ['created_at']
        constraints = [models.UniqueConstraint(fields=['book', 'reader'], condition=Q(status='waiting'), name='one_waiting_reservation_per_reader_book')]
    def __str__(self): return f'{self.reader} · {self.book}'
