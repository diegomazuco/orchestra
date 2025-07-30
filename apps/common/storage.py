from django.core.files.storage import FileSystemStorage

class OriginalFilenameStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        # Retorna o nome original do arquivo, sem modificações.
        # Isso significa que arquivos com o mesmo nome serão sobrescritos.
        return name
