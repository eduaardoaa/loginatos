#Conxão com o banco
import calendar
from datetime import datetime
from matplotlib.dates import relativedelta
import pandas as pd
import pyodbc

dados_empresa = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=aquidaba.infonet.com.br;'
    'DATABASE=dbproinfo;'
    'UID=leituraVendas;'
    'PWD=KRphDP65BM;'
    'Connection Timeout=30'
)

def obter_conexao():
    """Estabelece e retorna uma conexão com o banco de dados."""
    try:
        return pyodbc.connect(dados_empresa)
    except pyodbc.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def obter_nmfilial():
    """Executa a consulta e retorna os nomes das filiais."""
    conn = obter_conexao()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT(nmfilial) FROM tbVendasDashboard ORDER BY nmfilial;')
        nmfilial = [row.nmfilial for row in cursor]  
        return nmfilial
    except pyodbc.Error as e:
        print(f"Erro ao executar a consulta: {e}")
        return []
    finally:
        conn.close()

def obter_vendas_ano_anterior(filial):
    """Executa a consulta para obter o total de vendas do mesmo período do ano anterior para a filial especificada."""
    conn = obter_conexao()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        consulta = '''
        SELECT SUM(vlVenda) AS total_vendas_ano_anterior
        FROM tbVendasDashboard
        WHERE YEAR(dtVenda) = YEAR(GETDATE()) - 1  -- Ano anterior (2024)
          AND MONTH(dtVenda) = MONTH(GETDATE())    -- Mesmo mês (março)
          AND nmFilial = ?                        -- Filtro pela filial
        '''
        cursor.execute(consulta, (filial,))
        resultado = cursor.fetchone()  # Pega o primeiro resultado
        if resultado:
            return resultado.total_vendas_ano_anterior
        else:
            return 0  # Caso não haja vendas
    except pyodbc.Error as e:
        print(f"Erro ao executar a consulta: {e}")
        return None
    finally:
        conn.close()

def obter_meta_mes(filial):
    """Obtém a meta de vendas (vendas do mês anterior + 5%) para uma filial específica."""
    conn = obter_conexao()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        consulta = '''
        SELECT SUM(vlVenda) * 1.05 AS meta_mes
        FROM tbVendasDashboard
        WHERE YEAR(dtVenda) = YEAR(GETDATE()) - 1
          AND MONTH(dtVenda) = MONTH(GETDATE())
          AND nmFilial = ?
        '''
        cursor.execute(consulta, (filial,))
        resultado = cursor.fetchone()
        return resultado.meta_mes if resultado else 0
    except pyodbc.Error as e:
        print(f"Erro: {e}")
        return None
    finally:
        conn.close()

def obter_previsao_vendas(filial):
    """Calcula a previsão de vendas do mês corrente para uma filial específica."""
    conn = obter_conexao()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        consulta = '''
        SELECT 
            CAST(
                (SUM(vlVenda) / DAY(GETDATE())) * 
                DAY(DATEADD(DAY, -DAY(GETDATE()), DATEADD(MONTH, 1, GETDATE())))
            AS DECIMAL(10,2)) AS previsao_vendas
        FROM tbVendasDashboard
        WHERE YEAR(dtVenda) = YEAR(GETDATE())  
          AND MONTH(dtVenda) = MONTH(GETDATE())    
          AND DAY(dtVenda) <= DAY(GETDATE())       
          AND nmFilial = ?
        '''
        cursor.execute(consulta, (filial,))
        resultado = cursor.fetchone()
        return resultado.previsao_vendas if resultado else 0
    except pyodbc.Error as e:
        print(f"Erro: {e}")
        return None
    finally:
        conn.close()
       
def acumulo_vendas_periodo_ano_anterior(filial):
    """Obtém as vendas do mesmo período do ano anterior para uma filial específica."""
    conn = obter_conexao()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        consulta = '''
        SELECT 
            SUM(vlVenda) AS acumulo_vendas_ano_anterior
        FROM tbVendasDashboard
        WHERE YEAR(dtVenda) = YEAR(GETDATE()) - 1  
          AND MONTH(dtVenda) = MONTH(GETDATE())    
          AND DAY(dtVenda) BETWEEN 1 AND DAY(GETDATE()) 
          AND nmFilial = ?
        '''
        cursor.execute(consulta, (filial,))
        resultado = cursor.fetchone()
        return resultado.acumulo_vendas_ano_anterior if resultado else 0
    except pyodbc.Error as e:
        print(f"Erro: {e}")
        return None
    finally:
        conn.close()

def obter_acumulo_meta_ano_anterior(filial):
    """Obtém o acúmulo de meta (vendas do mês anterior + 5%) para uma filial específica, com base no mesmo período do ano anterior."""
    conn = obter_conexao()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        consulta = '''
        SELECT SUM(vlVenda) * 1.05 AS acumulo_meta_ano_anterior
        FROM tbVendasDashboard
        WHERE YEAR(dtVenda) = YEAR(GETDATE()) - 1  
          AND MONTH(dtVenda) = MONTH(GETDATE())    
          AND DAY(dtVenda) BETWEEN 1 AND DAY(GETDATE()) 
          AND nmFilial = ?
        '''
        cursor.execute(consulta, (filial,))
        resultado = cursor.fetchone()
        return resultado.acumulo_meta_ano_anterior if resultado else 0
    except pyodbc.Error as e:
        print(f"Erro: {e}")
        return None
    finally:
        conn.close()

def obter_acumulo_de_vendas(filial):
    """Obtém o acúmulo de vendas do mês atual para uma filial específica."""
    conn = obter_conexao()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        consulta = '''
        SELECT SUM(vlVenda) AS acumulo_de_vendas
        FROM tbVendasDashboard
        WHERE YEAR(dtVenda) = YEAR(GETDATE())  -- Ano atual
          AND MONTH(dtVenda) = MONTH(GETDATE())  -- Mês atual
          AND nmFilial = ?  -- Filial específica
        '''
        cursor.execute(consulta, (filial,))
        resultado = cursor.fetchone()
        return resultado.acumulo_de_vendas if resultado else 0
    except pyodbc.Error as e:
        print(f"Erro: {e}")
        return None
    finally:
        conn.close()

def obter_ultima_venda_com_valor(filial):
    """Obtém a última venda com valor do mês atual ou, se não houver, dos meses anteriores para uma filial específica."""
    conn = obter_conexao()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        consulta = '''
        SELECT TOP 1
            vlVenda,
            dtVenda,
            nmFilial
        FROM tbVendasDashboard
        WHERE YEAR(dtVenda) = YEAR(GETDATE())  -- Ano atual
          AND MONTH(dtVenda) <= MONTH(GETDATE())  -- Meses anteriores e o mês atual
          AND nmFilial = ?  -- Filial específica
          AND vlVenda IS NOT NULL  -- Garantir que a venda tenha um valor
        ORDER BY dtVenda DESC;  -- Ordena pela data de venda mais recente
        '''
        cursor.execute(consulta, (filial,))
        resultado = cursor.fetchone()
        
        if resultado and resultado.vlVenda is not None:
            return resultado.vlVenda  # Retorna o valor da última venda com valor
        else:
            return 0  # Retorna 0 se não houver vendas com valor para o mês atual ou anteriores
    except pyodbc.Error as e:
        print(f"Erro: {e}")
        return None
    finally:
        conn.close()

def obter_percentual_de_crescimento_atual(filial):
    """Obtém o percentual de diferença entre as vendas do mês atual e o mesmo período do ano anterior, com 2 casas decimais."""
    conn = obter_conexao()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        consulta = '''
        WITH vendas_mes_atual AS (
            SELECT SUM(vlVenda) AS vendas_atual
            FROM tbVendasDashboard
            WHERE YEAR(dtVenda) = YEAR(GETDATE())
              AND MONTH(dtVenda) = MONTH(GETDATE())
              AND DAY(dtVenda) <= DAY(GETDATE())  -- Até o dia atual
              AND nmFilial = ?  -- Filial específica
        ),
        vendas_mes_ano_anterior AS (
            SELECT SUM(vlVenda) AS vendas_ano_anterior
            FROM tbVendasDashboard
            WHERE YEAR(dtVenda) = YEAR(GETDATE()) - 1  -- Ano passado
              AND MONTH(dtVenda) = MONTH(GETDATE())
              AND DAY(dtVenda) <= DAY(GETDATE())  -- Mesmo intervalo de dias do ano passado
              AND nmFilial = ?  -- Filial específica
        )
        SELECT 
            CASE 
                WHEN vendas_ano_anterior > 0 THEN 
                    ROUND(((vendas_atual - vendas_ano_anterior) / vendas_ano_anterior) * 100, 2)  -- Limita a 2 casas decimais
                ELSE 0  -- Evitar divisão por zero
            END AS percentual_diferenca
        FROM vendas_mes_atual, vendas_mes_ano_anterior;
        '''
        cursor.execute(consulta, (filial, filial))
        resultado = cursor.fetchone()
        
        if resultado:
            percentual_diferenca = resultado[0]
            return round(percentual_diferenca, 2)  
        else:
            return 0  
    except pyodbc.Error as e:
        print(f"Erro: {e}")
        return None
    finally:
        conn.close()

def obter_percentual_crescimento_meta(filial):
    """Obtém o percentual de diferença entre as vendas do mês atual e a meta (vendas do mesmo período do ano passado +5%)."""
    conn = obter_conexao()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        consulta = '''
        WITH VendasAnoAnterior AS (
            SELECT 
                SUM(vlVenda) * 1.05 AS meta_ano_anterior  -- Acrescenta 5% ao total do mesmo período do ano anterior
            FROM tbVendasDashboard
            WHERE YEAR(dtVenda) = YEAR(GETDATE()) - 1  -- Ano passado
              AND MONTH(dtVenda) = MONTH(GETDATE())  -- Mesmo mês
              AND DAY(dtVenda) BETWEEN 1 AND DAY(GETDATE())  -- Mesmo período (1º dia até o dia atual)
              AND nmFilial = ?  -- Filial específica
        ),
        VendasAnoAtual AS (
            SELECT 
                SUM(vlVenda) AS total_ano_atual  
            FROM tbVendasDashboard
            WHERE YEAR(dtVenda) = YEAR(GETDATE())  -- Ano atual
              AND MONTH(dtVenda) = MONTH(GETDATE())  -- Mesmo mês
              AND DAY(dtVenda) BETWEEN 1 AND DAY(GETDATE())  -- Mesmo período (1º dia até o dia atual)
              AND nmFilial = ?  -- Filial específica
        )
        SELECT 
            CAST(
                ROUND(
                    ((VA.total_ano_atual - VAA.meta_ano_anterior) / NULLIF(VA.total_ano_atual, 0)) * 100, 
                    2
                ) AS DECIMAL(10,2)
            ) AS percentual_diferenca
        FROM VendasAnoAnterior VAA, VendasAnoAtual VA;
        '''
        cursor.execute(consulta, (filial, filial))
        resultado = cursor.fetchone()
        
        if resultado and resultado[0] is not None:
            return resultado[0]  
        else:
            return 0  
        
    except pyodbc.Error as e:
        print(f"Erro: {e}")
        return None
    finally:
        conn.close()

def obter_vendas_por_mes_e_filial(mes_referencia, filial_selecionada):
    nomes_para_numeros = {
        "Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04",
        "Maio": "05", "Junho": "06", "Julho": "07", "Agosto": "08",
        "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"
    }

    if not (mes_referencia and filial_selecionada):
        return []

    ano_atual = datetime.now().year
    resultados_totais = []

    conn = obter_conexao()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()

        for mes_nome in mes_referencia:
            mes_num = int(nomes_para_numeros[mes_nome])
            ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]

            data_inicio = f"{ano_atual}-{mes_num:02d}-01"
            data_fim = f"{ano_atual}-{mes_num:02d}-{ultimo_dia}"

            query = """
                SELECT vlVenda, dtVenda, ? as mes_nome
                FROM tbVendasDashboard
                WHERE dtVenda BETWEEN ? AND ?
                AND nmFilial = ?
                ORDER BY dtVenda
            """
            cursor.execute(query, (mes_nome, data_inicio, data_fim, filial_selecionada))
            resultados_totais.extend(cursor.fetchall())

        return resultados_totais

    except pyodbc.Error as e:
        print(f"Erro: {e}")
        return []
    finally:
        conn.close()
    

def obter_vendas_anual_e_filial(filial_selecionada):
    """Retorna um dicionário com o total de vendas dos últimos 12 meses para uma filial específica."""
    conn = obter_conexao()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()

        # Gera os 13 últimos meses a partir do mês atual
        meses = []
        hoje = datetime.today().replace(day=1)
        for i in range(13):
            mes_ref = hoje - relativedelta(months=i)
            ano = mes_ref.year
            mes = mes_ref.month
            meses.append((ano, mes))

        # Cria um dicionário para armazenar os resultados
        vendas_por_mes = {}

        for ano, mes in meses:
            # Pega o último dia do mês de forma precisa
            ultimo_dia = calendar.monthrange(ano, mes)[1]
            data_inicio = f"{ano}-{mes:02d}-01"
            data_fim = f"{ano}-{mes:02d}-{ultimo_dia}"

            consulta = '''
                SELECT SUM(vlVenda) as total
                FROM tbVendasDashboard
                WHERE dtVenda BETWEEN ? AND ?
                  AND nmFilial = ?
            '''
            cursor.execute(consulta, (data_inicio, data_fim, filial_selecionada))
            resultado = cursor.fetchone()
            chave = f"{mes:02d}/{ano}"
            vendas_por_mes[chave] = resultado.total if resultado and resultado.total else 0

        # Ordena por data decrescente (mais recente primeiro)
        vendas_ordenadas = dict(sorted(vendas_por_mes.items(), key=lambda x: datetime.strptime(x[0], "%m/%Y"), reverse=True))
        
        return vendas_ordenadas
    
    except pyodbc.Error as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return {}
    finally:
        conn.close()
    
