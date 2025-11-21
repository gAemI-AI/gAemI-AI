# backend-pjt/stocks/admin.py
from django.contrib import admin
from .models import StockMaster

@admin.register(StockMaster)
class StockMasterAdmin(admin.ModelAdmin):
    list_display = ('stock_id', 'stock_name', 'market_type')
    search_fields = ('stock_name', 'stock_id')