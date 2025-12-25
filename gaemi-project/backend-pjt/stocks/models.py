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


class WeeklyReport(models.Model):
    """
    주간 리포트 저장용 모델
    - 매주 토요일 배치 작업(Spark)을 통해 생성됨
    - 한 종목당 한 주에 하나의 리포트만 존재
    """
    stock = models.ForeignKey(
        'StockMaster', 
        on_delete=models.CASCADE, 
        related_name='weekly_reports',
        help_text="리포트 대상 종목"
    )
    
    # 기간 정보
    start_date = models.DateField(help_text="해당 주차 시작일 (월요일)")
    end_date = models.DateField(help_text="해당 주차 종료일 (금요일)")
    
    # 수치 데이터 (Spark가 계산해서 넣어줌)
    weekly_return = models.FloatField(help_text="주간 수익률 (%)")
    weekly_high = models.IntegerField(help_text="주간 최고가")
    weekly_low = models.IntegerField(help_text="주간 최저가")
    start_price = models.IntegerField(help_text="주초 시가")
    end_price = models.IntegerField(help_text="주말 종가")
    
    # AI 분석 내용 (OpenAI가 작성)
    summary_text = models.TextField(help_text="AI가 요약한 주간 흐름")
    
    # 생성 일시
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'weekly_reports'
        ordering = ['-start_date'] # 최신순 정렬
        # 한 종목에 대해 같은 시작일(주차)의 리포트는 유일해야 함
        unique_together = ('stock', 'start_date')

    def __str__(self):
        return f"[{self.start_date}] {self.stock.stock_name} 리포트"