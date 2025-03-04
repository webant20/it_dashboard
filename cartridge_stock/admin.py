from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import CartridgeStock, CartridgeAddition, CartridgeIssue

@admin.register(CartridgeStock)
class CartridgeStockAdmin(admin.ModelAdmin):
    list_display = ('material_code', 'description', 'qty', 'add_stock_link', 'issue_stock_link')
    search_fields = ('material_code', 'description')

    def add_stock_link(self, obj):
        url = reverse('admin:cartridge_stock_cartridgeaddition_add')  # Admin add form URL
        return format_html('<a href="{}?cartridge={}">Add Stock</a>', url, obj.pk)

    add_stock_link.short_description = "Add"

    def issue_stock_link(self, obj):
        url = reverse('admin:cartridge_stock_cartridgeissue_add')  # Admin add form URL
        return format_html('<a href="{}?cartridge={}">Issue Stock</a>', url, obj.pk)

    issue_stock_link.short_description = "Issue"

from django.utils.html import format_html
from django.urls import reverse

from django.utils.html import format_html
from django.urls import reverse

@admin.register(CartridgeAddition)
class CartridgeAdditionAdmin(admin.ModelAdmin):
    list_display = ('cartridge', 'added_qty', 'date_added', 'po_number_display')
    search_fields = ('po_number__po_number',)

    def po_number_display(self, obj):
        """Display PO Number as plain text (non-clickable)"""
        return obj.po_number.po_number if obj.po_number else "-"

    po_number_display.short_description = "PO Number"  # Column Header in Admin


@admin.register(CartridgeIssue)
class CartridgeIssueAdmin(admin.ModelAdmin):
    list_display = ('cartridge', 'asset', 'issued_qty', 'date_issued')
