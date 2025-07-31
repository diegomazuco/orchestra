from django.apps import AppConfig


class AutomacaoIpirangaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # type: ignore
    name = 'apps.automacao_ipiranga'

    def ready(self):
        pass
