from django.contrib import admin
from django.utils import timezone
from .models import Loan, Reader, Reservation

class LoanStatusFilter(admin.SimpleListFilter):
    title = 'situação do empréstimo'
    parameter_name = 'situation'
    def lookups(self, request, model_admin):
        return [('active', 'Em aberto'), ('overdue', 'Em atraso'), ('returned', 'Devolvido')]
    def queryset(self, request, queryset):
        if self.value() == 'active': return queryset.filter(returned_at__isnull=True, due_at__gte=timezone.localdate())
        if self.value() == 'overdue': return queryset.filter(returned_at__isnull=True, due_at__lt=timezone.localdate())
        if self.value() == 'returned': return queryset.filter(returned_at__isnull=False)
        return queryset

@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ['name', 'registration', 'email', 'active']
    list_filter = ['active']
    search_fields = ['name', 'email', 'registration']

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['reader', 'copy', 'borrowed_at', 'due_at', 'returned_at', 'issued_by']
    list_filter = [LoanStatusFilter, 'borrowed_at', 'due_at', 'copy__book__category']
    search_fields = ['reader__name', 'reader__registration', 'copy__code', 'copy__book__title']
    autocomplete_fields = ['reader', 'copy']
    date_hierarchy = 'borrowed_at'

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['book', 'reader', 'created_at', 'status']
    list_filter = ['status', 'created_at', 'book__category']
    search_fields = ['book__title', 'reader__name']
    autocomplete_fields = ['book', 'reader']
