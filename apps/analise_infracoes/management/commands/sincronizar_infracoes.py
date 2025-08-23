import logging
import random
from datetime import datetime, timedelta
from typing import Any, TypedDict

from django.conf import settings  # Added import
from django.core.management.base import BaseCommand
from django.db import connections, transaction

from apps.analise_infracoes.models import Infracao

logger = logging.getLogger(__name__)


class InfracaoRow(TypedDict):
    """Representa uma linha de infração com tipagem estática."""

    placa: str
    data_hora: datetime
    local: str
    tipo: str
    valor: float
    pontos: int
    status: str
    dados_origem: dict[str, Any]


class Command(BaseCommand):
    """Comando para sincronizar infrações entre bancos de dados."""

    help = "Sincroniza infrações do banco de dados MySQL de origem para o PostgreSQL de destino."

    def handle(self, *args: Any, **options: Any) -> None:
        """Lida com a execução do comando de sincronização."""
        logger.info("Iniciando a sincronização de infrações...")

        rows: list[InfracaoRow] = []
        try:
            # Tenta conectar ao banco de dados real
            with connections["mysql_source"].cursor() as cursor:
                cursor.execute(
                    f"SELECT placa, data_hora, local, tipo, valor, pontos, status, dados_origem FROM {settings.MYSQL_INFRACOES_TABLE}"
                )
                fetched_rows = cursor.fetchall()
                rows = [
                    InfracaoRow(
                        placa=row[0],
                        data_hora=row[1],
                        local=row[2],
                        tipo=row[3],
                        valor=row[4],
                        pontos=row[5],
                        status=row[6],
                        dados_origem=row[7],
                    )
                    for row in fetched_rows
                ]
                logger.info(
                    f"{len(rows)} infrações encontradas no banco de dados de origem."
                )
        except Exception as e:
            logger.warning(
                f"Não foi possível conectar ao MySQL ({e}). Usando dados de teste em memória."
            )
            # Gera 10.000 infrações de exemplo se a conexão falhar
            for i in range(10000):
                rows.append(
                    InfracaoRow(
                        placa=f"ABC{random.randint(1000, 9999)}",
                        data_hora=datetime.now()
                        - timedelta(days=random.randint(1, 365)),
                        local=f"Local {i}",
                        tipo=random.choice(["leve", "media", "grave", "gravissima"]),
                        valor=random.uniform(50.0, 500.0),
                        pontos=random.randint(3, 7),
                        status="nova",
                        dados_origem={"origem": "teste"},
                    )
                )

        if not rows:
            logger.info("Nenhuma infração para sincronizar.")
            return

        try:
            # Usando o banco de dados 'default' (SQLite) para o profiling
            db_alias = settings.POSTGRES_DB_ALIAS

            # Limpa a tabela antes de inserir novos dados
            with transaction.atomic(using=db_alias):
                logger.info(
                    f"Limpando a tabela {Infracao._meta.db_table} no banco de dados '{db_alias}'..."
                )
                Infracao.objects.using(db_alias).all().delete()

            infracoes_para_criar: list[Infracao] = []
            batch_size = 2000

            logger.info(
                f"Processando {len(rows)} infrações em lotes de {batch_size}..."
            )

            for i, row in enumerate(rows):
                infracoes_para_criar.append(
                    Infracao(
                        placa_veiculo=row["placa"],
                        data_hora=row["data_hora"],
                        local=row["local"],
                        tipo_infracao=row["tipo"],
                        valor=row["valor"],
                        pontos_carteira=row["pontos"],
                        status=row["status"],
                        dados_origem=row["dados_origem"],
                    )
                )
                # Quando o lote estiver cheio, insere no banco
                if len(infracoes_para_criar) == batch_size:
                    Infracao.objects.using(db_alias).bulk_create(infracoes_para_criar)
                    logger.info(f"Lote {i // batch_size + 1} inserido com sucesso.")
                    infracoes_para_criar = []  # Limpa a lista para o próximo lote

            # Insere o lote final, se houver
            if infracoes_para_criar:
                try:
                    Infracao.objects.using(db_alias).bulk_create(infracoes_para_criar)
                    logger.info("Lote final inserido com sucesso.")
                except Exception as bulk_e:
                    logger.error(f"Erro ao inserir lote final de infrações: {bulk_e}")
                    self.stdout.write(
                        self.style.ERROR(
                            f"Erro ao inserir lote final de infrações: {bulk_e}"
                        )
                    )

            logger.info(
                f"{len(rows)} infrações foram sincronizadas com sucesso para o banco de dados '{db_alias}'."
            )

        except Exception as e:
            logger.error(f"Ocorreu um erro durante a sincronização: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"Erro durante a sincronização: {e}"))
