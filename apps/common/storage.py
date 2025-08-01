from django.core.files.storage import FileSystemStorage


class OriginalFilenameStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        # Retorna o nome original do arquivo, sem modificações.
        # ATENÇÃO: Isso significa que arquivos com o mesmo nome serão sobrescritos.
        # Este comportamento é intencional para permitir a substituição de certificados existentes.
        return name
