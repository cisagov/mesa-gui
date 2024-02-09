import os
from django.apps import AppConfig


class MesaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mesa'

    @staticmethod
    def _ensure_mesajob_directory_exists():
        import os
        import pathlib
        import shutil
        from .models import MesaJob

        # Ensure the MesaJob directory exists
        job_directory = MesaJob.get_job_directory()
        if not os.path.exists(job_directory):
            pathlib.Path(job_directory).mkdir(parents=True, exist_ok=True)

    def ready(self):
        MesaConfig._ensure_mesajob_directory_exists()
