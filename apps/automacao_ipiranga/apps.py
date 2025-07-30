from django.apps import AppConfig


class AutomacaoIpirangaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.automacao_ipiranga'

    def ready(self):
        import apps.automacao_ipiranga.signals
