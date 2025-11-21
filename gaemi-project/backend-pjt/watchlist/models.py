from django.db import models
from django.conf import settings  # AUTH_USER_MODEL을 가져오기 위해
from stocks.models import StockMaster

class Watchlist(models.Model):
    watchlist_id = models.BigAutoField(primary_key=True) 
    # user와 1:N
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist') # related_name: 역참조 이름을 지정하는 옵션, 즉 ForeignKey가 연결된 반대쪽 모델에서 이 관계를 어떻게 부를지

    # StockMaster와 1:N관계
    stock = models.ForeignKey(StockMaster, on_delete=models.CASCADE, related_name='watched_by')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_watchlist'
        # 한 유저가 같은 종목을 중복 추가하지 못하게 막기
        constraints = [
            models.UniqueConstraint(fields=['user', 'stock'], name='unique_user_stock')
        ]