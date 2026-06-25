# Importa o framework Flask para criar a aplicação web e ferramentas para gerenciar requisições e JSON
from flask import Flask, request, jsonify
# Importa a biblioteca do Flask-CORS para permitir que o front-end acesse esta API de outra origem
from flask_cors import CORS
# Importa a biblioteca nativa do Python para trabalhar com o banco de dados SQLite
import sqlite3

# Inicializa a aplicação Flask
app = Flask(__name__)
# Ativa o CORS na aplicação para evitar erros de bloqueio no navegador ao integrar com o front-end
CORS(app)

# Função para conectar ao banco de dados e garantir que a tabela exista
def init_db():
    # Abre uma conexão com o arquivo de banco de dados 'database.db' (ele será criado se não existir)
    conn = sqlite3.connect('database.db')
    # Cria um cursor, objeto que permite executar comandos SQL no banco de dados
    cursor = conn.cursor()
    # Executa o comando SQL para criar a tabela 'historico' caso ela ainda não tenha sido criada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peso REAL NOT NULL,
            altura REAL NOT NULL,
            imc REAL NOT NULL,
            classificacao TEXT NOT NULL
        )
    ''')
    # Salva (commita) as alterações feitas no banco de dados
    conn.commit()
    # Fecha a conexão com o banco de dados para liberar memória e evitar travamentos
    conn.close()

# Define uma rota HTTP POST no endereço '/calcular' para receber os dados do formulário
@app.route('/calcular', methods=['POST'])
def calcular_imc():
    # Recupera os dados enviados pelo front-end no formato JSON
    data = request.get_json()
    
    try:
        # Extrai os valores e converte explicitamente para float (número decimal)
        peso = float(data.get('peso', 0))
        # Extrai o valor da altura convertido para float (número decimal)
        altura = float(data.get('altura', 0))
        
        # Validação de segurança: se o peso ou altura forem zero ou menores, evita o erro de divisão por zero
        if peso <= 0 or altura <= 0:
            # Retorna um JSON de erro caso os valores inseridos sejam inválidos
            return jsonify({'erro': 'Valores inválidos. Peso e altura devem ser maiores que zero.'}), 400
            
        # Executa a fórmula matemática do IMC: peso dividido pela altura elevada ao quadrado
        imc = peso / (altura ** 2)
        # Arredonda o resultado do IMC para duas casas decimais
        imc = round(imc, 2)
        
        # Lógica corrigida sem "buracos" entre as faixas de peso para determinar a categoria
        if imc < 18.5:
            # Define como abaixo do peso se menor que 18.5
            classificacao = 'Abaixo do peso'
        elif imc < 25.0:
            # Define como peso normal se estiver entre 18.5 e 24.99
            classificacao = 'Peso normal'
        elif imc < 30.0:
            # Define como sobrepeso se estiver entre 25.0 e 29.99
            classificacao = 'Sobrepeso'
        else:
            # Define como obesidade se for maior ou igual a 30.0
            classificacao = 'Obesidade'
            
        # Abre uma nova conexão com o banco de dados para salvar o novo registro
        conn = sqlite3.connect('database.db')
        # Cria um cursor para rodar o comando SQL
        cursor = conn.cursor()
        # Executa o comando SQL para inserir os dados de peso, altura, imc e classificação na tabela
        cursor.execute('''
            INSERT INTO historico (peso, altura, imc, classificacao) 
            VALUES (?, ?, ?, ?)
        ''', (peso, altura, imc, classificacao))
        # Confirma a inserção dos dados no banco de dados
        conn.commit()
        # Fecha a conexão com o banco de dados
        conn.close()
        
        # Retorna uma resposta de sucesso para o front-end com os dados calculados
        return jsonify({
            'imc': imc,
            'classificacao': classificacao
        })

    # Bloco que captura erros caso o front-end envie dados que não possam virar números
    except (ValueError, TypeError):
        # Retorna um JSON informando o erro de formato de dados ao front-end
        return jsonify({'erro': 'Dados enviados estão em formato incorreto.'}), 400

# Garante que o código abaixo só rode se este arquivo for executado diretamente pelo terminal
if __name__ == '__main__':
    # Chama a função de inicialização do banco de dados criada no início do código
    init_db()
    # Inicia o servidor web do Flask no modo de depuração (debug) ativo na porta padrão 5000
    app.run(debug=True, port=5000)