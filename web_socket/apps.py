from django.apps import AppConfig
import sys

class WebSocketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web_socket'
    
    def ready(self):
        # if not any(arg in sys.argv for arg in ['runserver', 'daphne', 'gunicorn']):
        #     return

        from django.db.backends.signals import connection_created
        def clean_zombie_sockets(**kwargs):
            connection_created.disconnect(clean_zombie_sockets)
            from core.models.Exams_models import ProfileSettings
            try:
                count = ProfileSettings.objects.filter(socketID__isnull=False).update(socketID=None)
                if count > 0:
                    print(f"--- Database: {count} Zombie Socket IDs Cleared Safely ---")
            except Exception:
                pass
        # 4. ربط الوظيفة بالـ Signal
        connection_created.connect(clean_zombie_sockets)
