CREATE CATALOG IF NOT EXISTS lakehouse_vertice;

CREATE SCHEMA IF NOT EXISTS lakehouse_vertice.bronze
COMMENT 'Dados brutos do Projeto Vértice, preservados como chegaram das fontes.';

CREATE SCHEMA IF NOT EXISTS lakehouse_vertice.silver
COMMENT 'Dados limpos, tipados e integrados do Projeto Vértice.';

CREATE SCHEMA IF NOT EXISTS lakehouse_vertice.gold
COMMENT 'Indicadores e produtos analíticos do Projeto Vértice.';

CREATE VOLUME IF NOT EXISTS lakehouse_vertice.bronze.raw
COMMENT 'Arquivos brutos copiados do Supabase Storage.';
