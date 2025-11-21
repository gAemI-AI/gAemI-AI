# backend-pjt/watchlist/admin.py
from django.contrib import admin
from .models import Watchlist

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('watchlist_id', 'user_id', 'stock', 'created_at')
    list_filter = ('user',)