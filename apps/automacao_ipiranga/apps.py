from django.apps import AppConfig

import apps.automacao_ipiranga.signals  # type: ignore


class AutomacaoIpirangaConfig(AppConfig):
    """Configuração da aplicação de Automação Ipiranga."""

    default_auto_field = "django.db.models.BigAutoField"  # type: ignore
    name = "apps.automacao_ipiranga"

    def ready(self) -> None:
        """Configurações a serem executadas quando a aplicação estiver pronta."""
        print("AutomacaoIpirangaConfig ready() called")
