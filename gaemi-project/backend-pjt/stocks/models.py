from django.db import models
# stocks/models.py -> 이미 init.sql로 만들어진 stock_master 테이블을 읽기만 함

class StockMaster(models.Model):
    # stock_id는 문자열, PK
    stock_id = models.CharField(primary_key=True, max_length=10)
    stock_name = models.CharField(max_length=100)
    market_type = models.CharField(max_length=10)

    class Meta:
        managed = False # 이 테이블은 생성/삭제 금지
        db_table = 'stock_master' # DB에 이미 있는 테이블 이름과 매핑
        verbose_name = '종목 마스터'
        verbose_name_plural = '종목 마스터 목록'