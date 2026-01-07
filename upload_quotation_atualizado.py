import pandas as pd
import mysql.connector
from mysql.connector import Error
from pathlib import Path
from datetime import datetime

# ============================================================
# CONFIGURAÇÕES DO BANCO DE DADOS - PREENCHA AQUI
# ============================================================
DB_CONFIG = {
    'host': 'localhost',
    'database': 'donaldson',  # Nome do banco de dados
    'user': 'root',           # Usuário do MySQL
    'password': '',           # Senha do MySQL
    'port': 3306
}
# ============================================================

def conectar_banco():
    """Estabelece conexão com o banco de dados MySQL."""
    try:
        conexao = mysql.connector.connect(**DB_CONFIG)
        if conexao.is_connected():
            print("✅ Conectado ao MySQL com sucesso!")
            return conexao
    except Error as e:
        print(f"❌ Erro ao conectar ao MySQL: {e}")
        return None

def limpar_valor(valor):
    """Limpa e converte valores para inserção no banco."""
    if pd.isna(valor) or valor == '' or valor is None:
        return None
    return str(valor).strip()

def converter_decimal(valor):
    """Converte valor para decimal, tratando vírgulas e valores vazios."""
    if pd.isna(valor) or valor == '' or valor is None:
        return None
    try:
        # Substitui vírgula por ponto
        valor_str = str(valor).replace(',', '.').strip()
        if valor_str == '':
            return None
        return float(valor_str)
    except (ValueError, TypeError):
        return None

def main():
    print("=" * 70)
    print("UPLOAD DO QUOTATION_BASECALC_ATUALIZADO PARA O BANCO DE DADOS")
    print("=" * 70)
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Carregar o CSV (do mesmo diretório do script)
    base_dir = Path(__file__).parent
    arquivo_csv = base_dir / "Quotation_baseCalc_ATUALIZADO.csv"
    
    print(f"\n📂 Carregando: {arquivo_csv}")
    
    if not arquivo_csv.exists():
        print(f"❌ Arquivo não encontrado: {arquivo_csv}")
        return
    
    df = pd.read_csv(arquivo_csv, sep=';', dtype=str)
    df = df.fillna('')
    
    print(f"   Total de registros no CSV: {len(df)}")
    
    # 2. Conectar ao banco
    print(f"\n🔌 Conectando ao banco de dados...")
    conexao = conectar_banco()
    
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # 3. Perguntar se deseja limpar a tabela
        print("\n" + "!" * 70)
        print("⚠️  ATENÇÃO: TODOS OS DADOS DA TABELA 'quotations' SERÃO APAGADOS!")
        print("!" * 70)
        print("\nEste processo irá:")
        print("   1. APAGAR todos os registros existentes na tabela 'quotations'")
        print("   2. INSERIR os novos registros do arquivo CSV")
        print(f"\n   Total de registros a serem inseridos: {len(df)}")
        print("\n" + "!" * 70)
        resposta = input("\n❓ Deseja prosseguir? Digite Y para SIM ou N para NÃO: ").strip().upper()
        
        if resposta != 'Y':
            print("\n❌ Operação cancelada pelo usuário.")
            return
        
        # 4. Limpar tabela existente
        print("\n🗑️  Limpando tabela 'quotations'...")
        cursor.execute("TRUNCATE TABLE quotations")
        conexao.commit()
        print("   Tabela limpa com sucesso!")
        
        # 5. Inserir novos registros
        print(f"\n📤 Inserindo {len(df)} registros...")
        
        sql_insert = """
            INSERT INTO quotations 
            (microsiga_pn, oracle_pn, pt_description, ncm, ipi, pis, cofins, 
             fator_18, fator_12, fator_7, fator_4, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        
        registros_inseridos = 0
        registros_erro = 0
        erros = []
        
        for idx, row in df.iterrows():
            try:
                valores = (
                    limpar_valor(row['MicrosigaPN']),
                    limpar_valor(row['OraclePN']),
                    limpar_valor(row['PT Description']),
                    limpar_valor(row['NCM']),
                    converter_decimal(row['IPI']),
                    converter_decimal(row['PIS']),
                    converter_decimal(row['COFINS']),
                    converter_decimal(row['Fator 18']),
                    converter_decimal(row['Fator 12']),
                    converter_decimal(row['Fator 7']),
                    converter_decimal(row['Fator 4'])
                )
                
                cursor.execute(sql_insert, valores)
                registros_inseridos += 1
                
                # Mostrar progresso a cada 1000 registros
                if registros_inseridos % 1000 == 0:
                    print(f"   Inseridos: {registros_inseridos} registros...")
                    conexao.commit()
                    
            except Error as e:
                registros_erro += 1
                erros.append({
                    'linha': idx + 2,  # +2 porque o índice começa em 0 e tem o header
                    'ncm': row['NCM'],
                    'erro': str(e)
                })
        
        # Commit final
        conexao.commit()
        
        # 6. Relatório final
        print("\n" + "=" * 70)
        print("RELATÓRIO FINAL")
        print("=" * 70)
        print(f"✅ Registros inseridos com sucesso: {registros_inseridos}")
        print(f"❌ Registros com erro: {registros_erro}")
        
        if erros:
            print("\n⚠️  Primeiros 10 erros:")
            for erro in erros[:10]:
                print(f"   Linha {erro['linha']}, NCM {erro['ncm']}: {erro['erro']}")
        
        # 7. Verificar total na tabela
        cursor.execute("SELECT COUNT(*) FROM quotations")
        total_tabela = cursor.fetchone()[0]
        print(f"\n📊 Total de registros na tabela 'quotations': {total_tabela}")
        
    except Error as e:
        print(f"\n❌ Erro durante a operação: {e}")
        conexao.rollback()
        
    finally:
        cursor.close()
        conexao.close()
        print("\n🔌 Conexão com o banco fechada.")
    
    print("\n" + "=" * 70)
    print("UPLOAD CONCLUÍDO")
    print(f"Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()
