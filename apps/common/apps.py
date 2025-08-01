from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Configuração da aplicação Common."""

    default_auto_field = "django.db.models.BigAutoField"  # type: ignore
    name = "apps.common"
