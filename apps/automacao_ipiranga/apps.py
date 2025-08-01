from django.apps import AppConfig


class AutomacaoIpirangaConfig(AppConfig):
    """Configuração da aplicação de Automação Ipiranga."""

    default_auto_field = "django.db.models.BigAutoField"  # type: ignore
    name = "apps.automacao_ipiranga"

    def ready(self):
        """Configurações a serem executadas quando a aplicação estiver pronta."""
        pass
