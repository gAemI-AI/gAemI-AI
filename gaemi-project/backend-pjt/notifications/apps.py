from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    def ready(self):
        """Django 앱 시작 시 Kafka Bridge 초기화"""
        try:
            from .kafka_bridge import kafka_bridge
            kafka_bridge.start_all_consumers()
        except Exception as e:
            print(f"⚠️  Kafka Bridge 초기화 실패: {e}")