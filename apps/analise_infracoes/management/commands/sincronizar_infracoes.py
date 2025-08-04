import logging

from django.core.management.base import BaseCommand
from django.db import connections

from apps.analise_infracoes.models import Infracao

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando para sincronizar infrações entre bancos de dados."""

    help = "Sincroniza infrações do banco de dados MySQL de origem para o PostgreSQL de destino."

    def handle(self, *args, **options):
        """Lida com a execução do comando de sincronização."""
        logger.info("Iniciando a sincronização de infrações...")

        try:
            with connections["mysql_source"].cursor() as cursor:
                # ATENÇÃO: Substitua pela sua consulta real
                cursor.execute(
                    "SELECT placa, data_hora, local, tipo, valor, pontos, status, dados_origem FROM tbl_infracoes_exemplo"
                )
                rows = cursor.fetchall()
                logger.info(
                    f"{len(rows)} infrações encontradas no banco de dados de origem."
                )

            infracoes_para_criar = []
            for row in rows:
                infracoes_para_criar.append(
                    Infracao(
                        placa_veiculo=row[0],
                        data_hora=row[1],
                        local=row[2],
                        tipo_infracao=row[3],
                        valor=row[4],
                        pontos_carteira=row[5],
                        status=row[6],
                        dados_origem=row[7],
                    )
                )

            # O bulk_create é mais eficiente para inserir múltiplos objetos
            Infracao.objects.using("postgres_db").bulk_create(infracoes_para_criar)

            logger.info(
                f"{len(infracoes_para_criar)} infrações foram sincronizadas com sucesso para o PostgreSQL."
            )

        except Exception as e:
            logger.error(f"Ocorreu um erro durante a sincronização: {e}")
            self.stdout.write(self.style.ERROR(f"Erro durante a sincronização: {e}"))
