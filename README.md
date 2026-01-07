# Conversores Donaldson

Scripts Python para conversão e upload de dados do sistema de Quotation da Donaldson.

---

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Acesso ao banco de dados MySQL

---

## 🚀 Instalação

### 1. Instalar as dependências

Abra o terminal na pasta `ConversosDonaldson` e execute:

```bash
pip install -r requirements.txt
```

Ou instale manualmente:

```bash
pip install pandas mysql-connector-python openpyxl
```

---

## 📁 Arquivos do Projeto

| Arquivo | Descrição |
|---------|-----------|
| `conversor_item_extract.py` | Converte dados do `item_extract.csv` para atualizar o `Quotation_baseCalc.csv` |
| `verificar_ncm_sem_fatores.py` | Verifica NCMs sem fatores e gera Excel de pendências |
| `upload_quotation_atualizado.py` | Faz upload do CSV atualizado para o banco de dados MySQL |

---

## 📤 Como Fazer Upload para o Banco de Dados

### 1. Configurar as credenciais do banco

Abra o arquivo `upload_quotation_atualizado.py` e edite as configurações do banco de dados (linhas 17-23):

```python
DB_CONFIG = {
    'host': 'localhost',           # Endereço do servidor MySQL
    'database': 'donaldson',       # Nome do banco de dados
    'user': 'root',                # Usuário do MySQL
    'password': 'SUA_SENHA_AQUI',  # Senha do MySQL
    'port': 3306                   # Porta (padrão: 3306)
}
```

### 2. Colocar o arquivo CSV na pasta

Certifique-se de que o arquivo `Quotation_baseCalc_ATUALIZADO.csv` está na mesma pasta do script (`ConversosDonaldson/`).

### 3. Executar o upload

```bash
python3 upload_quotation_atualizado.py
```

### 4. Confirmar a operação

O script exibirá um aviso informando que **todos os dados da tabela serão apagados**.

Digite `Y` para confirmar ou `N` para cancelar:

```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
⚠️  ATENÇÃO: TODOS OS DADOS DA TABELA 'quotations' SERÃO APAGADOS!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Este processo irá:
   1. APAGAR todos os registros existentes na tabela 'quotations'
   2. INSERIR os novos registros do arquivo CSV

   Total de registros a serem inseridos: XXXX

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

❓ Deseja prosseguir? Digite Y para SIM ou N para NÃO: 
```

---

## 🔍 Verificar NCMs sem Fatores

Para gerar um Excel com os NCMs que não possuem os fatores (4, 7, 12, 18) preenchidos:

```bash
python3 verificar_ncm_sem_fatores.py
```

Será gerado o arquivo `NCMs_sem_fatores.xlsx` com as colunas:
- OraclePN
- PT Description
- NCM

---

## ⚠️ Observações Importantes

1. **Backup**: Faça sempre um backup do banco de dados antes de executar o upload.

2. **Fatores vazios**: Os NCMs adicionados do `item_extract` que não existiam no `Quotation_baseCalc` virão com os fatores em branco. Use o script `verificar_ncm_sem_fatores.py` para identificá-los.

3. **Formato do CSV**: O arquivo CSV deve usar `;` (ponto e vírgula) como separador.

---

## 🛠️ Suporte

Em caso de dúvidas ou problemas, entre em contato com a equipe de desenvolvimento.
