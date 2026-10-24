#!/usr/bin/env python3
"""Gera de forma determinística o Genie Agent Farol · Diretoria."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "resources/farol.geniespace.json"
GOLD = "lakehouse_vertice.gold"
SILVER = "lakehouse_vertice.silver"


def cli() -> str:
    if encontrado := shutil.which("databricks"):
        return encontrado
    base = os.environ.get("LOCALAPPDATA")
    if base:
        candidatos = sorted((Path(base) / "Microsoft/WinGet/Packages").glob("Databricks.DatabricksCLI_*/databricks.exe"), reverse=True)
        if candidatos:
            return str(candidatos[0])
    raise SystemExit("Databricks CLI não encontrado")


def existe(tabela: str, profile: str) -> bool:
    resultado = subprocess.run(
        [cli(), "tables", "exists", tabela, "--profile", profile, "--output", "json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    return resultado.returncode == 0 and json.loads(resultado.stdout).get("table_exists") is True


def ident(prefixo: str, numero: int) -> str:
    return f"{prefixo}{numero:0{32 - len(prefixo)}d}"


def colunas(*configs: dict) -> list[dict]:
    return sorted(configs, key=lambda item: item["column_name"])


def montar(incluir_score: bool) -> dict:
    tabelas = [
        {"identifier": f"{GOLD}.fato_projeto_semana", "column_configs": colunas(
            {"column_name": "projeto_id", "description": ["Código único do projeto."], "synonyms": ["código"], "enable_entity_matching": True},
            {"column_name": "semana", "description": ["Sexta-feira de referência; PV, EV e AC são acumulados até esta semana."]},
        )},
        {"identifier": f"{GOLD}.projeto_situacao_atual", "column_configs": colunas(
            {"column_name": "cliente", "enable_format_assistance": True, "enable_entity_matching": True},
            {"column_name": "ferramenta", "description": ["Valor categórico em minúsculas, incluindo excel."], "enable_format_assistance": True},
            {"column_name": "projeto", "description": ["Código e nome no formato PRJ-000 · Nome; use esta coluna quando a pergunta pedir quais ou qual projeto."], "synonyms": ["projeto completo"]},
            {"column_name": "projeto_id", "synonyms": ["código do projeto"], "enable_entity_matching": True},
            {"column_name": "situacao", "synonyms": ["risco", "saúde"], "enable_format_assistance": True},
        )},
        {"identifier": f"{GOLD}.status_estruturado", "column_configs": colunas(
            {"column_name": "causa_bloqueio", "synonyms": ["causa", "motivo do atraso"], "enable_format_assistance": True},
            {"column_name": "projeto_id", "enable_entity_matching": True},
        )},
        {"identifier": f"{GOLD}.utilizacao_pessoa_semana", "column_configs": colunas(
            {"column_name": "colaborador_id", "synonyms": ["pessoa", "colaborador"], "enable_entity_matching": True},
            {"column_name": "papel", "enable_format_assistance": True},
        )},
        {"identifier": f"{SILVER}.entregas_fornecedor", "column_configs": colunas(
            {"column_name": "fornecedor", "enable_format_assistance": True, "enable_entity_matching": True},
            {"column_name": "em_atraso", "description": ["Verdadeiro quando a entrega venceu e ainda não foi concluída."]},
        )},
    ]
    if incluir_score:
        tabelas.append({"identifier": f"{GOLD}.score_estouro_30d", "column_configs": colunas(
            {"column_name": "faixa_risco", "enable_format_assistance": True},
            {"column_name": "projeto_id", "enable_entity_matching": True},
        )})

    exemplos = [
        ("Quais projetos estão atrasados, e de quais clientes?", f"SELECT projeto_id, nome_projeto, cliente, ferramenta, situacao, ROUND(spi, 2) AS spi, ROUND(cpi, 2) AS cpi, atraso_projetado_dias FROM {GOLD}.projeto_situacao_atual WHERE status = 'em_andamento' AND situacao IN ('crítico', 'atenção') ORDER BY least(spi, cpi)"),
        ("Quanto esse atraso vai me custar?", f"SELECT MEASURE(estouro_previsto) AS estouro_previsto, MEASURE(projetos_em_risco) AS projetos_em_risco, MEASURE(margem_projetada) AS margem_projetada FROM {GOLD}.mv_projetos"),
        ("Tenho gente parada enquanto outro projeto pede gente?", f"SELECT colaborador_id, nome, papel, projeto_id, projeto, ROUND(SUM(horas_apontadas) / SUM(horas_disponiveis), 3) AS utilizacao, SUM(horas_ociosas) AS horas_ociosas, SUM(custo_ocioso) AS custo_ocioso FROM {GOLD}.utilizacao_pessoa_semana WHERE semana > DATE'2026-07-24' GROUP BY ALL HAVING SUM(horas_apontadas) / SUM(horas_disponiveis) < 0.2 ORDER BY utilizacao"),
        ("Por que o projeto PRJ-011 atrasou?", f"SELECT s.causa_bloqueio, COUNT(*) AS semanas, SUM(coalesce(s.dias_impacto, 0)) AS dias_de_impacto, MAX(p.spi) AS spi_do_projeto FROM {GOLD}.status_estruturado s JOIN {GOLD}.projeto_situacao_atual p ON p.projeto_id = s.projeto_id WHERE s.projeto_id = 'PRJ-011' AND s.data_status >= DATE'2026-07-18' AND s.causa_bloqueio NOT IN ('sem_bloqueio', 'nao_reportado') GROUP BY s.causa_bloqueio ORDER BY semanas DESC"),
        ("Qual fornecedor mais atrasa?", f"SELECT fornecedor, COUNT(*) AS entregas, ROUND(AVG(prazo_real_dias / prazo_prometido_dias), 2) AS fator_atraso, COUNT_IF(em_atraso) AS em_atraso_hoje FROM {SILVER}.entregas_fornecedor GROUP BY fornecedor ORDER BY fator_atraso DESC LIMIT 1"),
        ("Quais projetos de e-commerce em andamento ficam travados pelo change freeze da Black Friday?", f"SELECT projeto FROM {GOLD}.projeto_situacao_atual WHERE status = 'em_andamento' AND (lower(tipo_projeto) LIKE '%commerce%' OR lower(tipo_projeto) LIKE '%checkout%' OR lower(tipo_projeto) LIKE '%marketplace%')"),
        ("O que vai dar errado no próximo mês, e o que eu faço agora?", f"SELECT 'entrega de fornecedor atrasada' AS risco, e.projeto_id, p.projeto, concat(e.fornecedor, ': ', e.item, ' (', CAST(datediff(DATE'2026-10-16', e.data_prometida) AS STRING), ' dias de atraso)') AS detalhe, 'cobrar o fornecedor' AS o_que_fazer FROM {SILVER}.entregas_fornecedor e JOIN {GOLD}.projeto_situacao_atual p ON p.projeto_id = e.projeto_id WHERE e.em_atraso UNION ALL SELECT 'change freeze da Black Friday', projeto_id, projeto, 'deploy travado de 01/11/2026 a 10/01/2027', 'antecipar deploys até 31/10' FROM {GOLD}.projeto_situacao_atual WHERE status = 'em_andamento' AND (lower(tipo_projeto) LIKE '%commerce%' OR lower(tipo_projeto) LIKE '%checkout%' OR lower(tipo_projeto) LIKE '%marketplace%')"),
        ("Quais clientes têm projetos críticos?", f"SELECT cliente, COUNT(*) AS projetos_criticos FROM {GOLD}.projeto_situacao_atual WHERE status = 'em_andamento' AND situacao = 'crítico' GROUP BY cliente ORDER BY projetos_criticos DESC"),
        ("Qual projeto em andamento tem o maior estouro previsto?", f"SELECT projeto FROM {GOLD}.projeto_situacao_atual WHERE status = 'em_andamento' ORDER BY estouro_previsto DESC LIMIT 1"),
        ("Quais projetos estão com farol verde mas atrasados (SPI abaixo de 0,9)?", f"SELECT projeto FROM {GOLD}.projeto_situacao_atual WHERE melancia"),
        ("Quais são os códigos dos projetos críticos?", f"SELECT projeto FROM {GOLD}.projeto_situacao_atual WHERE status = 'em_andamento' AND situacao = 'crítico'"),
        ("Qual projeto em andamento tem o maior atraso projetado em dias?", f"SELECT projeto FROM {GOLD}.projeto_situacao_atual WHERE status = 'em_andamento' ORDER BY atraso_projetado_dias DESC LIMIT 1"),
        ("Quantos projetos em andamento são gerenciados no Excel?", f"SELECT COUNT(*) FROM {GOLD}.projeto_situacao_atual WHERE status = 'em_andamento' AND ferramenta = 'excel'"),
    ]
    instrucoes = [
        "## PURPOSE\n- Atenda o dono e a diretoria da Vértice com respostas executivas em português sobre projetos, pessoas e fornecedores.",
        "## DISAMBIGUATION\n- HOJE é 16/10/2026. Últimos 90 dias começam em 18/07/2026, últimas 12 semanas após 24/07/2026 e próximo mês termina em 15/11/2026.\n- Use mv_projetos para totais atuais e projeto_situacao_atual para rankings. Quando a resposta pedir projetos, selecione a coluna projeto, que já combina código e nome.\n- Valores de ferramenta são minúsculos, inclusive excel.\n- Em fato_projeto_semana, PV, EV e AC são acumulados e nunca devem ser somados entre semanas.\n- Para explicar atraso, use status_estruturado nos últimos 90 dias, exclua sem_bloqueio e nao_reportado e, se a causa for falta_sre, procure SREs com utilização agregada abaixo de 20%.\n- Fornecedor mais atrasado usa a média de prazo_real_dias dividido por prazo_prometido_dias.\n- Change freeze sempre inclui os três padrões tipo_projeto: commerce, checkout e marketplace.",
        "## DATA QUALITY NOTES\n- Farol do gerente é declarado, farol calculado deriva do SPI e melancia significa farol declarado verde com SPI abaixo de 0,9.",
        "## CONSTRAINTS\n- Para perguntas sobre clientes, devolva cada cliente uma vez. Para perguntas no singular, devolva uma linha.",
        "## Instructions you must follow when providing summaries\n- Mostre projeto_id, nome e cliente ao citar projetos. Formate valores em R$ e índices com duas casas. Termine com uma recomendação curta quando houver decisão.",
    ]
    if incluir_score:
        instrucoes[1] += "\n- Risco futuro usa a fotografia mais recente de score_estouro_30d e prioriza projetos hoje ok com faixa alto ou medio."
        exemplos.append(("Qual a chance de o PRJ-024 estourar?", f"SELECT s.projeto_id, p.projeto, p.cliente, ROUND(s.prob_estouro_30d, 2) AS prob_estouro_30d, s.faixa_risco, s.principais_fatores FROM {GOLD}.score_estouro_30d s JOIN {GOLD}.projeto_situacao_atual p ON p.projeto_id = s.projeto_id WHERE s.projeto_id = 'PRJ-024' AND s.data_referencia = (SELECT MAX(data_referencia) FROM {GOLD}.score_estouro_30d)"))

    return {
        "version": 2,
        "config": {"sample_questions": [
            {"id": ident("b1", i), "question": [q]} for i, q in enumerate([
                "Quais projetos estão atrasados, e de quais clientes?",
                "Quanto esse atraso vai me custar?",
                "Tenho gente parada enquanto outro projeto pede gente?",
                "O que vai dar errado no próximo mês, e o que eu faço agora?",
            ], 1)
        ]},
        "data_sources": {
            "tables": sorted(tabelas, key=lambda item: item["identifier"]),
            "metric_views": [{"identifier": f"{GOLD}.mv_projetos"}],
        },
        "instructions": {
            "text_instructions": [{"id": ident("c1", 1), "content": instrucoes}],
            "example_question_sqls": sorted([
                {"id": ident("d1", i), "question": [q], "sql": [sql]} for i, (q, sql) in enumerate(exemplos, 1)
            ], key=lambda item: item["id"]),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="DEFAULT")
    args = parser.parse_args()
    score = existe(f"{GOLD}.score_estouro_30d", args.profile)
    SAIDA.write_text(json.dumps(montar(score), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ok: {SAIDA.relative_to(ROOT)} · score: {'incluído' if score else 'ausente'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
