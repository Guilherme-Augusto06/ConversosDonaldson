#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para converter dados do item_extract.csv e atualizar o Quotation_baseCalc.csv
Mantendo os NCMs e fatores existentes, apenas atualizando microsiga_pn, oracle_pn e pt_description
"""

import pandas as pd
import os
from datetime import datetime

# Caminhos dos arquivos
BASE_DIR = "/home/guilherme-automata/Área de trabalho/Donaldson"
ITEM_EXTRACT_PATH = os.path.join(BASE_DIR, "item_extract.csv")
QUOTATION_BASE_PATH = os.path.join(BASE_DIR, "Quotation_baseCalc.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "Quotation_baseCalc_ATUALIZADO.csv")

def log(message):
    """Escreve mensagem no console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def main():
    log("=" * 80)
    log("INICIANDO PROCESSO DE CONVERSÃO")
    log("=" * 80)
    
    # 1. Carregar o item_extract.csv (separador ;)
    log(f"Carregando arquivo: {ITEM_EXTRACT_PATH}")
    item_extract = pd.read_csv(ITEM_EXTRACT_PATH, sep=';', dtype=str, low_memory=False)
    log(f"Total de linhas em item_extract: {len(item_extract)}")
    
    # 2. Carregar o Quotation_baseCalc.csv (separador ;)
    log(f"Carregando arquivo: {QUOTATION_BASE_PATH}")
    quotation_base = pd.read_csv(QUOTATION_BASE_PATH, sep=';', dtype=str, low_memory=False)
    log(f"Total de linhas em Quotation_baseCalc: {len(quotation_base)}")
    
    # 3. Mostrar colunas disponíveis
    log("\n--- COLUNAS DO ITEM_EXTRACT ---")
    log(str(item_extract.columns.tolist()))
    
    log("\n--- COLUNAS DO QUOTATION_BASE ---")
    log(str(quotation_base.columns.tolist()))
    
    # 4. Preparar dados do item_extract
    item_extract_clean = item_extract[['COD_ITEM', 'DESCRICAO', 'NCM']].copy()
    item_extract_clean['NCM'] = item_extract_clean['NCM'].astype(str).str.strip().str.lstrip('0')
    item_extract_clean['COD_ITEM'] = item_extract_clean['COD_ITEM'].astype(str).str.strip()
    item_extract_clean['DESCRICAO'] = item_extract_clean['DESCRICAO'].astype(str).str.strip()
    
    # Remover linhas com NCM vazio ou nulo
    item_extract_clean = item_extract_clean[item_extract_clean['NCM'].notna() & (item_extract_clean['NCM'] != '') & (item_extract_clean['NCM'] != 'nan')]
    log(f"\nTotal de linhas em item_extract com NCM válido: {len(item_extract_clean)}")
    
    # 5. Preparar dados do quotation_base
    quotation_base['NCM'] = quotation_base['NCM'].astype(str).str.strip().str.lstrip('0')
    
    # 6. Verificar NCMs únicos
    log("\n--- CRIANDO MAPEAMENTO POR NCM ---")
    
    ncms_item_extract = set(item_extract_clean['NCM'].unique())
    ncms_quotation = set(quotation_base['NCM'].unique())
    
    log(f"NCMs únicos em item_extract: {len(ncms_item_extract)}")
    log(f"NCMs únicos em Quotation_baseCalc: {len(ncms_quotation)}")
    
    # NCMs que existem em ambos
    ncms_match = ncms_item_extract.intersection(ncms_quotation)
    log(f"\n✅ NCMs que BATEM (existem em ambos): {len(ncms_match)}")
    
    # NCMs apenas no item_extract
    ncms_only_item_extract = ncms_item_extract - ncms_quotation
    log(f"⚠️  NCMs apenas no item_extract (não existem no Quotation): {len(ncms_only_item_extract)}")
    
    # NCMs apenas no quotation
    ncms_only_quotation = ncms_quotation - ncms_item_extract
    log(f"⚠️  NCMs apenas no Quotation_baseCalc (não serão atualizados): {len(ncms_only_quotation)}")
    
    # 7. Criar dicionário de mapeamento NCM -> (COD_ITEM, DESCRICAO)
    ncm_mapping = {}
    for ncm in ncms_match:
        items = item_extract_clean[item_extract_clean['NCM'] == ncm]
        if not items.empty:
            first_item = items.iloc[0]
            ncm_mapping[ncm] = {
                'cod_item': first_item['COD_ITEM'],
                'descricao': first_item['DESCRICAO']
            }
    
    log(f"\nMapeamentos criados: {len(ncm_mapping)}")
    
    # 8. Criar o novo DataFrame atualizado
    log("\n--- ATUALIZANDO QUOTATION_BASE ---")
    
    quotation_updated = quotation_base.copy()
    atualizados = 0
    nao_atualizados = 0
    
    for idx, row in quotation_updated.iterrows():
        ncm = row['NCM']
        if ncm in ncm_mapping:
            quotation_updated.at[idx, 'MicrosigaPN'] = ncm_mapping[ncm]['cod_item']
            quotation_updated.at[idx, 'OraclePN'] = ncm_mapping[ncm]['cod_item']
            quotation_updated.at[idx, 'PT Description'] = ncm_mapping[ncm]['descricao']
            atualizados += 1
        else:
            nao_atualizados += 1
    
    log(f"\n✅ Linhas ATUALIZADAS: {atualizados}")
    log(f"⚠️  Linhas NÃO ATUALIZADAS (NCM não encontrado no item_extract): {nao_atualizados}")
    
    # 8.1 Remover linhas com NCMs que existem apenas no Quotation (não existem no item_extract)
    log(f"\n--- REMOVENDO NCMs OBSOLETOS ---")
    linhas_antes = len(quotation_updated)
    quotation_updated = quotation_updated[~quotation_updated['NCM'].isin(ncms_only_quotation)]
    linhas_removidas = linhas_antes - len(quotation_updated)
    log(f"🗑️  Linhas REMOVIDAS (NCMs obsoletos): {linhas_removidas}")
    
    # 8.2 Adicionar linhas para NCMs que existem no item_extract mas não no Quotation
    log(f"\n--- ADICIONANDO NCMs NOVOS ---")
    novas_linhas = []
    for ncm in ncms_only_item_extract:
        rows_ncm = item_extract_clean[item_extract_clean['NCM'] == ncm]
        if not rows_ncm.empty:
            row = rows_ncm.iloc[0]
            novas_linhas.append({
                'MicrosigaPN': row['COD_ITEM'],
                'OraclePN': row['COD_ITEM'],
                'PT Description': row['DESCRICAO'],
                'NCM': ncm,
                'IPI': '',
                'PIS': '',
                'COFINS': '',
                'Fator 18': '',
                'Fator 12': '',
                'Fator 7': '',
                'Fator 4': ''
            })
    
    if novas_linhas:
        novas_linhas_df = pd.DataFrame(novas_linhas)
        quotation_updated = pd.concat([quotation_updated, novas_linhas_df], ignore_index=True)
    
    log(f"➕ Linhas ADICIONADAS (NCMs novos sem fatores): {len(novas_linhas)}")
    
    # 9. Estatísticas detalhadas
    log("\n" + "=" * 80)
    log("RESUMO FINAL")
    log("=" * 80)
    log(f"Total de linhas no Quotation_baseCalc original: {len(quotation_base)}")
    log(f"Total de linhas no Quotation_baseCalc atualizado: {len(quotation_updated)}")
    log(f"Linhas com NCM encontrado e atualizado: {atualizados}")
    log(f"Linhas com NCM NÃO encontrado (mantidas): {nao_atualizados}")
    log(f"Percentual de atualização: {(atualizados/len(quotation_base)*100):.2f}%")
    
    # 10. Mostrar TODOS os NCMs que não bateram
    if ncms_only_quotation:
        log(f"\n--- TODOS OS NCMs DO QUOTATION SEM CORRESPONDÊNCIA ({len(ncms_only_quotation)} NCMs) ---")
        for ncm in sorted(ncms_only_quotation):
            log(f"  NCM: {ncm}")
    
    # 10.1 Gerar Excel com NCMs com erro - NCMs do item_extract que NÃO existem no Quotation_baseCalc
    ncms_erro_path = os.path.join(BASE_DIR, "NCMs_com_erro.xlsx")
    log(f"\n--- TODOS OS NCMs DO ITEM_EXTRACT SEM FATORES ({len(ncms_only_item_extract)} NCMs) ---")
    log(f"   (NCMs do item_extract que NÃO têm fatores no Quotation_baseCalc)")
    
    ncms_erro_data = []
    for ncm in sorted(ncms_only_item_extract):
        rows_ncm = item_extract_clean[item_extract_clean['NCM'] == ncm]
        if not rows_ncm.empty:
            row = rows_ncm.iloc[0]
            log(f"  NCM: {ncm} | COD_ITEM: {row['COD_ITEM']} | Qtd: {len(rows_ncm)}")
            ncms_erro_data.append({
                'NCM': ncm,
                'COD_ITEM': row['COD_ITEM']
            })
    
    log(f"\n--- GERANDO EXCEL DE NCMs COM ERRO ---")
    ncms_erro_df = pd.DataFrame(ncms_erro_data)
    ncms_erro_df.to_excel(ncms_erro_path, index=False, engine='openpyxl')
    log(f"✅ Excel de NCMs com erro salvo em: {ncms_erro_path}")
    log(f"   Total de NCMs com erro: {len(ncms_erro_data)}")
    
    # 11. Salvar o CSV atualizado (separador ;)
    log(f"\n--- SALVANDO ARQUIVO ---")
    log(f"Salvando em: {OUTPUT_PATH}")
    quotation_updated.to_csv(OUTPUT_PATH, sep=';', index=False, encoding='utf-8')
    log("✅ Arquivo salvo com sucesso!")
    
    # 12. Criar um CSV de comparação para conferência (separador ;)
    comparison_path = os.path.join(BASE_DIR, "Comparacao_NCMs.csv")
    log(f"\n--- GERANDO CSV DE COMPARAÇÃO ---")
    
    comparison_data = []
    for idx, row in quotation_base.iterrows():
        ncm = row['NCM']
        original_microsiga = row['MicrosigaPN']
        original_oracle = row['OraclePN']
        original_desc = row['PT Description']
        
        if ncm in ncm_mapping:
            new_cod_item = ncm_mapping[ncm]['cod_item']
            new_desc = ncm_mapping[ncm]['descricao']
            status = "ATUALIZADO"
        else:
            new_cod_item = original_microsiga
            new_desc = original_desc
            status = "MANTIDO"
        
        comparison_data.append({
            'NCM': ncm,
            'Status': status,
            'MicrosigaPN_Original': original_microsiga,
            'MicrosigaPN_Novo': new_cod_item,
            'OraclePN_Original': original_oracle,
            'OraclePN_Novo': new_cod_item,
            'Descricao_Original': original_desc,
            'Descricao_Nova': new_desc
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df.to_csv(comparison_path, sep=';', index=False, encoding='utf-8')
    log(f"✅ CSV de comparação salvo em: {comparison_path}")
    
    log("\n" + "=" * 80)
    log("PROCESSO FINALIZADO COM SUCESSO!")
    log("=" * 80)
    log(f"\nArquivos gerados:")
    log(f"  1. {OUTPUT_PATH} (Quotation atualizado)")
    log(f"  2. {comparison_path} (Comparação para conferência)")
    log(f"  3. {ncms_erro_path} (NCMs sem fatores)")

if __name__ == "__main__":
    main()
