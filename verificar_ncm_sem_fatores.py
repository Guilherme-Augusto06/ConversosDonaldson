#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar NCMs sem fatores no Quotation_baseCalc_ATUALIZADO.csv
Gera um Excel com os NCMs que não possuem os fatores 4, 7, 12 e 18 preenchidos.
"""

import pandas as pd
from pathlib import Path

def main():
    # Caminhos dos arquivos
    base_dir = Path(__file__).parent.parent
    arquivo_entrada = base_dir / "Quotation_baseCalc_ATUALIZADO.csv"
    arquivo_saida = base_dir / "NCMs_sem_fatores.xlsx"
    
    print("=" * 60)
    print("VERIFICAÇÃO DE NCMs SEM FATORES")
    print("=" * 60)
    
    # 1. Carregar o arquivo atualizado
    print(f"\n📂 Carregando: {arquivo_entrada}")
    df = pd.read_csv(arquivo_entrada, sep=';', dtype=str)
    df = df.fillna('')
    
    print(f"   Total de linhas: {len(df)}")
    
    # 2. Verificar quais NCMs não têm todos os fatores preenchidos
    print("\n🔍 Verificando NCMs sem fatores...")
    
    colunas_fatores = ['Fator 18', 'Fator 12', 'Fator 7', 'Fator 4']
    
    # Filtrar linhas onde QUALQUER fator está vazio
    mask_sem_fatores = (
        (df['Fator 18'].str.strip() == '') |
        (df['Fator 12'].str.strip() == '') |
        (df['Fator 7'].str.strip() == '') |
        (df['Fator 4'].str.strip() == '')
    )
    
    ncms_sem_fatores = df[mask_sem_fatores][['OraclePN', 'PT Description', 'NCM']].copy()
    
    print(f"\n📊 Resultado:")
    print(f"   NCMs COM todos os fatores: {len(df) - len(ncms_sem_fatores)}")
    print(f"   NCMs SEM algum fator: {len(ncms_sem_fatores)}")
    
    # 3. Gerar Excel
    if len(ncms_sem_fatores) > 0:
        ncms_sem_fatores.to_excel(arquivo_saida, index=False, sheet_name='NCMs_sem_fatores')
        print(f"\n✅ Excel gerado: {arquivo_saida}")
        
        # Mostrar alguns exemplos
        print(f"\n📋 Primeiros 10 NCMs sem fatores:")
        print("-" * 60)
        for _, row in ncms_sem_fatores.head(10).iterrows():
            print(f"   NCM: {row['NCM']} | OraclePN: {row['OraclePN']}")
    else:
        print("\n✅ Todos os NCMs possuem os fatores preenchidos!")
    
    print("\n" + "=" * 60)
    print("VERIFICAÇÃO CONCLUÍDA")
    print("=" * 60)

if __name__ == "__main__":
    main()
