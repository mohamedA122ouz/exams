from django.apps import AppConfig


class WebSocketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web_socket'
    
    def ready(self):
        # We import inside the method to avoid "Apps aren't loaded yet" errors
        from core.models.Exams_models import ProfileSettings
        
        try:
            # This runs once when the server process starts
            count = ProfileSettings.objects.filter(socketID__isnull=False).update(socketID=None)
            if count > 0:
                print(f"--- Cleaned up {count} zombie socket IDs ---")
        except Exception as e:
            # Handle cases where the table might not exist yet (e.g., during first migration)
            pass
