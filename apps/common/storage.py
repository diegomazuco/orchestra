from django.core.files.storage import FileSystemStorage


class OriginalFilenameStorage(FileSystemStorage):
    """Storage personalizado que mantém o nome original do arquivo."""

    def get_available_name(
        self, name: str, max_length: int | None = None
    ) -> str:  # Added type hints
        """Retorna o nome original do arquivo, sem modificações.

        ATENÇÃO: Isso significa que arquivos com o mesmo nome serão sobrescritos.
        Este comportamento é intencional para permitir a substituição de certificados existentes.
        """
        # Retorna o nome original do arquivo, sem modificações.
        # ATENÇÃO: Isso significa que arquivos com o mesmo nome serão sobrescritos.
        # Este comportamento é intencional para permitir a substituição de certificados existentes.
        return name
