from django.contrib import admin
from .models import Author, Book, Category, Copy, Publisher

class CopyInline(admin.TabularInline):
    model = Copy
    extra = 0

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'isbn', 'category', 'publisher', 'year']
    list_filter = ['category', 'publisher', 'year', 'authors']
    search_fields = ['title', 'isbn', 'authors__name']
    filter_horizontal = ['authors']
    inlines = [CopyInline]
    date_hierarchy = 'created_at'

@admin.register(Copy)
class CopyAdmin(admin.ModelAdmin):
    list_display = ['code', 'book', 'shelf', 'status']
    list_filter = ['status', 'book__category', 'shelf']
    search_fields = ['code', 'book__title']
    autocomplete_fields = ['book']

@admin.register(Author, Category, Publisher)
class NamedAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']
