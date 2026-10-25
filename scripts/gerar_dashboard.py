#!/usr/bin/env python3
"""Gera o dashboard AI/BI do Projeto Farol a partir de uma definição versionada."""
from __future__ import annotations

import json
from pathlib import Path

SAIDA = Path(__file__).resolve().parents[1] / "resources" / "dashboard-portfolio.lvdash.json"
BRL = {"type": "number-currency", "currencyCode": "BRL", "abbreviation": "compact", "decimalPlaces": {"type": "max", "places": 1}}
BRL0 = {**BRL, "decimalPlaces": {"type": "max", "places": 0}}
PCT = {"type": "number-percent", "decimalPlaces": {"type": "max", "places": 1}}
NUM2 = {"type": "number-plain", "decimalPlaces": {"type": "max", "places": 2}}
CORES = [{"value": "crítico", "color": "#FF5F46"}, {"value": "atenção", "color": "#F6C344"}, {"value": "ok", "color": "#22C2F4"}]

DATASETS = {
    "ds_kpis": ("KPIs da carteira em andamento", """SELECT SUM(valor_contrato) AS carteira,
       SUM(ev) / SUM(pv) AS spi,
       SUM(ev) / SUM(ac) AS cpi,
       SUM(estouro_previsto) AS estouro_previsto,
       (SUM(valor_contrato) - SUM(eac)) / SUM(valor_contrato) AS margem_projetada,
       COUNT_IF(situacao IN ('atenção', 'crítico')) AS projetos_em_risco,
       COUNT_IF(situacao = 'crítico') AS projetos_criticos,
       COUNT_IF(melancia) AS projetos_melancia
FROM projeto_situacao_atual
WHERE status = 'em_andamento'"""),
    "ds_estouro": ("Maiores estouros previstos", """SELECT projeto, cliente, ferramenta, situacao, estouro_previsto
FROM projeto_situacao_atual
WHERE status = 'em_andamento' AND estouro_previsto > 0
ORDER BY estouro_previsto DESC
LIMIT 12"""),
    "ds_projetos": ("Projetos em andamento hoje", """SELECT projeto_id, projeto, cliente, segmento, ferramenta, situacao, spi, cpi,
       estouro_previsto, margem_projetada, atraso_projetado_dias, termino_projetado,
       farol_do_gerente, farol_calculado,
       CASE WHEN melancia THEN 'sim' ELSE '' END AS melancia, valor_contrato
FROM projeto_situacao_atual
WHERE status = 'em_andamento'"""),
    "ds_evolucao": ("Evolução semanal da carteira", """SELECT semana, SUM(ev) / SUM(pv) AS spi, SUM(ev) / SUM(ac) AS cpi,
       SUM(horas_ociosas) AS horas_ociosas
FROM fato_projeto_semana
WHERE semana >= DATE'2025-03-07'
GROUP BY semana
ORDER BY semana"""),
    "ds_pessoas": ("Pessoas nas últimas 12 semanas", """SELECT colaborador_id, nome, papel, senioridade, projeto_id, projeto,
       SUM(horas_apontadas) / SUM(horas_disponiveis) AS utilizacao,
       SUM(horas_ociosas) AS horas_ociosas, SUM(custo_ocioso) AS custo_ocioso,
       MIN(spi_do_projeto) AS spi_do_projeto
FROM utilizacao_pessoa_semana
WHERE semana > DATE'2026-07-24'
GROUP BY ALL
ORDER BY utilizacao"""),
    "ds_pessoas_top": ("Pessoas mais paradas (top 15)", """SELECT concat(nome, ' · ', papel, ' · ', projeto_id) AS pessoa,
       SUM(custo_ocioso) AS custo_ocioso
FROM utilizacao_pessoa_semana
WHERE semana > DATE'2026-07-24'
GROUP BY 1
ORDER BY 2 DESC
LIMIT 15"""),
    "ds_bloqueios": ("Causas de bloqueio nos últimos 90 dias", """SELECT s.projeto_id, p.projeto, s.causa_bloqueio, COUNT(*) AS semanas,
       SUM(coalesce(s.dias_impacto, 0)) AS dias_impacto
FROM status_estruturado s JOIN projeto_situacao_atual p USING (projeto_id)
WHERE s.data_status >= DATE'2026-07-18'
  AND s.causa_bloqueio NOT IN ('sem_bloqueio', 'nao_reportado')
  AND p.status = 'em_andamento'
GROUP BY ALL"""),
    "ds_fornecedores": ("Desempenho de fornecedor", """SELECT fornecedor, COUNT(*) AS entregas,
       COUNT(DISTINCT fornecedor_como_veio) AS grafias_no_cadastro,
       AVG(prazo_real_dias / prazo_prometido_dias) AS fator_atraso,
       AVG(CASE WHEN data_entrega <= data_prometida THEN 1.0 ELSE 0.0 END)
         FILTER (WHERE data_entrega IS NOT NULL) AS pct_no_prazo,
       COUNT_IF(em_atraso) AS entregas_em_atraso
FROM lakehouse_vertice.silver.entregas_fornecedor
GROUP BY fornecedor
ORDER BY fator_atraso DESC"""),
    "ds_atrasadas": ("Entregas em atraso hoje", """SELECT projeto_id, fornecedor, item, valor, data_prometida,
       datediff(DATE'2026-10-16', data_prometida) AS dias_de_atraso
FROM lakehouse_vertice.silver.entregas_fornecedor
WHERE em_atraso
ORDER BY dias_de_atraso DESC"""),
}


def dataset(nome: str) -> dict:
    titulo, sql = DATASETS[nome]
    return {"name": nome, "displayName": titulo, "queryLines": [linha + "\n" for linha in sql.splitlines()]}


def pos(x: int, y: int, width: int, height: int) -> dict:
    return {"x": x, "y": y, "width": width, "height": height}


def texto(nome: str, markdown: str, position: dict) -> dict:
    return {"widget": {"name": nome, "textbox_spec": markdown}, "position": position}


def widget(nome: str, ds: str, campos: list[tuple[str, str]], spec: dict, position: dict, disaggregated: bool = False) -> dict:
    return {"widget": {"name": nome, "queries": [{"name": "main_query", "query": {
        "datasetName": ds,
        "fields": [{"name": nome_campo, "expression": expressao} for nome_campo, expressao in campos],
        "disaggregated": disaggregated,
    }}], "spec": spec}, "position": position}


def kpi(nome: str, campo: str, titulo: str, formato: dict, position: dict) -> dict:
    return widget(nome, "ds_kpis", [(campo, f"`{campo}`")], {"version": 2, "widgetType": "counter",
        "encodings": {"value": {"fieldName": campo, "displayName": titulo, "format": formato}},
        "frame": {"showTitle": True, "title": titulo}}, position, True)


def filtro(nome: str, ds: str, campo: str, titulo: str, position: dict) -> dict:
    query_name = f"{nome}_query"
    return {"widget": {"name": nome, "queries": [{"name": query_name, "query": {
        "datasetName": ds,
        "fields": [{"name": campo, "expression": f"`{campo}`"}],
        "disaggregated": False,
    }}], "spec": {
        "version": 2,
        "widgetType": "filter-multi-select",
        "encodings": {"fields": [{"fieldName": campo, "displayName": titulo, "queryName": query_name}]},
        "frame": {"showTitle": True, "title": titulo},
    }}, "position": position}


def barra(nome: str, ds: str, dimensao: str, medida: str, expressao: str, titulo: str, formato: dict, position: dict, cor: str | None = None) -> dict:
    campos = [(dimensao, f"`{dimensao}`"), (medida, expressao)]
    encodings = {
        "y": {"fieldName": dimensao, "scale": {"type": "categorical", "sort": {"by": "x-reversed"}}, "displayName": dimensao},
        "x": {"fieldName": medida, "scale": {"type": "quantitative"}, "displayName": titulo, "format": formato},
    }
    if cor:
        campos.append((cor, f"`{cor}`"))
        encodings["color"] = {"fieldName": cor, "scale": {"type": "categorical", "mappings": CORES}, "displayName": cor}
    return widget(nome, ds, campos, {"version": 3, "widgetType": "bar", "encodings": encodings,
        "frame": {"showTitle": True, "title": titulo}}, position)


def tabela(nome: str, ds: str, colunas: list[tuple], titulo: str, position: dict) -> dict:
    encodings = []
    for coluna in colunas:
        item = {"fieldName": coluna[0], "displayName": coluna[1]}
        if len(coluna) == 3:
            item["format"] = coluna[2]
        encodings.append(item)
    return widget(nome, ds, [(c[0], f"`{c[0]}`") for c in colunas], {"version": 2, "widgetType": "table",
        "encodings": {"columns": encodings}, "frame": {"showTitle": True, "title": titulo}}, position, True)


def montar() -> dict:
    portfolio = [
        texto("titulo-portfolio", "# Projeto Farol · Portfólio\n\n**Onde agir agora para proteger prazo, custo e margem?** Fotografia executiva validada em **16/10/2026**.", pos(0, 0, 12, 2)),
        filtro("filtro-cliente", "ds_projetos", "cliente", "Cliente", pos(0, 2, 4, 2)),
        filtro("filtro-situacao", "ds_projetos", "situacao", "Situação", pos(4, 2, 4, 2)),
        filtro("filtro-ferramenta", "ds_projetos", "ferramenta", "Ferramenta", pos(8, 2, 4, 2)),
        kpi("kpi-carteira", "carteira", "Carteira em andamento", BRL0, pos(0, 4, 3, 4)),
        kpi("kpi-estouro", "estouro_previsto", "Estouro previsto", BRL0, pos(3, 4, 3, 4)),
        kpi("kpi-spi", "spi", "SPI da carteira", NUM2, pos(6, 4, 3, 4)),
        kpi("kpi-cpi", "cpi", "CPI da carteira", NUM2, pos(9, 4, 3, 4)),
        kpi("kpi-risco", "projetos_em_risco", "Projetos em risco", {"type": "number-plain"}, pos(0, 8, 3, 4)),
        kpi("kpi-criticos", "projetos_criticos", "Projetos críticos", {"type": "number-plain"}, pos(3, 8, 3, 4)),
        kpi("kpi-melancia", "projetos_melancia", "Falsos verdes", {"type": "number-plain"}, pos(6, 8, 3, 4)),
        kpi("kpi-margem", "margem_projetada", "Margem projetada", PCT, pos(9, 8, 3, 4)),
        barra("estouro-projeto", "ds_estouro", "projeto", "sum(estouro_previsto)", "SUM(`estouro_previsto`)", "Onde está concentrado o estouro previsto?", BRL, pos(0, 12, 7, 8), "situacao"),
        widget("spi-cpi", "ds_projetos", [("spi", "`spi`"), ("cpi", "`cpi`"), ("situacao", "`situacao`"), ("projeto", "`projeto`")],
            {"version": 3, "widgetType": "scatter", "encodings": {
                "x": {"fieldName": "spi", "scale": {"type": "quantitative"}, "displayName": "SPI (prazo)"},
                "y": {"fieldName": "cpi", "scale": {"type": "quantitative"}, "displayName": "CPI (custo)"},
                "color": {"fieldName": "situacao", "scale": {"type": "categorical", "mappings": CORES}, "displayName": "Situação"}},
             "annotations": [
                 {"type": "vertical-line", "encodings": {"x": {"dataValue": "0.9", "dataType": "DOUBLE"}, "label": {"value": "Limite de prazo"}, "color": {"value": "#F6C344"}}},
                 {"type": "horizontal-line", "encodings": {"y": {"dataValue": "0.9", "dataType": "DOUBLE"}, "label": {"value": "Limite de custo"}, "color": {"value": "#F6C344"}}},
             ],
             "frame": {"showTitle": True, "title": "Quais projetos combinam risco de prazo e custo?"}}, pos(7, 12, 5, 8), True),
        widget("evolucao", "ds_evolucao", [("semana", "`semana`"), ("spi", "`spi`"), ("cpi", "`cpi`")],
            {"version": 3, "widgetType": "line", "encodings": {
                "x": {"fieldName": "semana", "scale": {"type": "temporal"}, "displayName": "Semana"},
                "y": {"scale": {"type": "quantitative"}, "fields": [{"fieldName": "spi", "displayName": "SPI"}, {"fieldName": "cpi", "displayName": "CPI"}]}},
             "annotations": [{"type": "horizontal-line", "encodings": {"y": {"dataValue": "0.9", "dataType": "DOUBLE"}, "label": {"value": "Limite de atenção"}, "color": {"value": "#F6C344"}}}],
             "frame": {"showTitle": True, "title": "A carteira está melhorando ou piorando?"}}, pos(0, 20, 12, 6), True),
        tabela("tabela-projetos", "ds_projetos", [("projeto", "Projeto"), ("cliente", "Cliente"), ("situacao", "Situação"), ("spi", "SPI", NUM2), ("cpi", "CPI", NUM2), ("farol_do_gerente", "Farol informado"), ("farol_calculado", "Farol calculado"), ("melancia", "Falso verde"), ("estouro_previsto", "Estouro previsto", BRL), ("atraso_projetado_dias", "Atraso projetado (dias)")], "Fila executiva de projetos em andamento", pos(0, 26, 12, 9)),
    ]
    pessoas = [
        texto("titulo-pessoas", "# Capacidade e bloqueios\n\n**Onde existe capacidade ociosa e quais projetos precisam de ajuda?** Janela móvel das últimas 12 semanas.", pos(0, 0, 12, 2)),
        filtro("filtro-papel", "ds_pessoas", "papel", "Papel", pos(0, 2, 4, 2)),
        filtro("filtro-projeto-pessoas", "ds_pessoas", "projeto", "Projeto", pos(4, 2, 8, 2)),
        barra("pessoas-ociosas", "ds_pessoas_top", "pessoa", "sum(custo_ocioso)", "SUM(`custo_ocioso`)", "Quem concentra o maior custo de capacidade ociosa?", BRL, pos(0, 4, 6, 8)),
        tabela("tabela-pessoas", "ds_pessoas", [("nome", "Pessoa"), ("papel", "Papel"), ("projeto", "Projeto"), ("utilizacao", "Utilização", PCT), ("horas_ociosas", "Horas ociosas"), ("custo_ocioso", "Custo ocioso", BRL)], "Capacidade disponível por pessoa", pos(6, 4, 6, 8)),
        widget("bloqueios", "ds_bloqueios", [("projeto", "`projeto`"), ("causa_bloqueio", "`causa_bloqueio`"), ("sum(semanas)", "SUM(`semanas`)")],
            {"version": 3, "widgetType": "bar", "encodings": {
                "y": {"fieldName": "projeto", "scale": {"type": "categorical", "sort": {"by": "x-reversed"}}, "displayName": "Projeto"},
                "x": {"fieldName": "sum(semanas)", "scale": {"type": "quantitative"}, "displayName": "Semanas com bloqueio"},
                "color": {"fieldName": "causa_bloqueio", "scale": {"type": "categorical"}, "displayName": "Causa"}},
             "frame": {"showTitle": True, "title": "O que mais bloqueou os projetos nos últimos 90 dias?"}}, pos(0, 12, 12, 9)),
    ]
    fornecedores = [
        texto("titulo-fornecedores", "# Fornecedores\n\n**Quem está colocando o portfólio em risco?** Cumprimento de prazo e entregas vencidas na data de referência.", pos(0, 0, 12, 2)),
        barra("fornecedores-prazo", "ds_fornecedores", "fornecedor", "avg(pct_no_prazo)", "AVG(`pct_no_prazo`)", "Quem entrega no prazo?", PCT, pos(0, 2, 5, 7)),
        tabela("tabela-fornecedores", "ds_fornecedores", [("fornecedor", "Fornecedor"), ("entregas", "Entregas"), ("fator_atraso", "Real ÷ prometido", NUM2), ("pct_no_prazo", "No prazo", PCT), ("entregas_em_atraso", "Em atraso")], "Comparativo de desempenho", pos(5, 2, 7, 7)),
        tabela("tabela-atrasadas", "ds_atrasadas", [("projeto_id", "Projeto"), ("fornecedor", "Fornecedor"), ("item", "Item"), ("valor", "Valor", BRL), ("data_prometida", "Prometida para"), ("dias_de_atraso", "Dias de atraso")], "Entregas que exigem ação imediata", pos(0, 9, 12, 7)),
    ]
    pagina = lambda nome, titulo, layout: {"name": nome, "displayName": titulo, "pageType": "PAGE_TYPE_CANVAS", "layoutVersion": "GRID_V1", "layout": layout}
    return {
        "datasets": [dataset(nome) for nome in DATASETS],
        "pages": [pagina("portfolio", "Portfólio", portfolio), pagina("pessoas", "Pessoas", pessoas), pagina("fornecedores", "Fornecedores", fornecedores)],
        "uiSettings": {"theme": {
            "canvasBackgroundColor": {"light": "#F3F6FA", "dark": "#10141B"},
            "widgetBackgroundColor": {"light": "#FFFFFF", "dark": "#181E27"},
            "widgetBorderColor": {"light": "#FFFFFF", "dark": "#181E27"},
            "fontColor": {"light": "#172033", "dark": "#F4F7FB"},
            "selectionColor": {"light": "#0059DB", "dark": "#22C2F4"},
            "visualizationColors": ["#0059DB", "#22C2F4", "#F6C344", "#FF5F46", "#9B6BDB", "#3ECF8E", "#6E7180"],
            "widgetHeaderAlignment": "LEFT", "widgetCornerRadius": 12,
        }},
    }


if __name__ == "__main__":
    SAIDA.write_text(json.dumps(montar(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ok: {SAIDA}")
