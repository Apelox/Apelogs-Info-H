# # # import mysql.connector
# # # from mysql.connector import Error
# # # from config.settings import DB_CONFIG # Importa as configurações
# # # from datetime import datetime

# # # # Esta classe irá gerenciar a conexão e todas as queries para o banco de dados.
# # # class DatabaseManager:
# # #     def __init__(self):
# # #         """Inicializa o gerenciador e estabelece a conexão."""
# # #         try:
# # #             self.connection = mysql.connector.connect(**DB_CONFIG)
# # #             if self.connection.is_connected():
# # #                 print("Conectado ao banco de dados MySQL com sucesso!")
# # #         except Error as e:
# # #             print(f"Erro ao conectar ao MySQL: {e}")
# # #             self.connection = None

# # #     def _execute_query(self, query, params=None, fetch=None):
# # #         """
# # #         Função auxiliar para executar queries de forma segura.
# # #         'fetch' pode ser 'one' (um resultado), 'all' (todos os resultados), ou None (para INSERT/UPDATE).
# # #         """
# # #         if not self.connection or not self.connection.is_connected():
# # #             print("Não há conexão com o banco de dados.")
# # #             return None
        
# # #         cursor = self.connection.cursor()
# # #         try:
# # #             cursor.execute(query, params or ())
# # #             if fetch == 'one':
# # #                 result = cursor.fetchone()
# # #                 return result
# # #             elif fetch == 'all':
# # #                 result = cursor.fetchall()
# # #                 return result
# # #             else:
# # #                 self.connection.commit() # Salva as alterações (INSERT, UPDATE, DELETE)
# # #                 return cursor.lastrowid # Retorna o ID da última linha inserida
# # #         except Error as e:
# # #             print(f"Erro ao executar a query: {e}")
# # #             return None
# # #         finally:
# # #             cursor.close()

# # #     # --- FUNÇÕES DE USUÁRIO (Substituindo as antigas) ---

# # #     def ensure_user_exists(self, user_id, server_id):
# # #         """Garante que um usuário exista no banco para um servidor específico."""
# # #         # Garante que o servidor existe primeiro
# # #         self._execute_query("INSERT IGNORE INTO CONFIG_SERVIDOR (server_id) VALUES (%s)", (server_id,))
# # #         # Agora, insere o usuário se ele não existir
# # #         self._execute_query(
# # #             "INSERT IGNORE INTO USUARIOS (user_id, server_id) VALUES (%s, %s)",
# # #             (user_id, server_id)
# # #         )

# # #     def get_balance(self, user_id, server_id):
# # #         """Busca o saldo da carteira e do banco de um usuário."""
# # #         self.ensure_user_exists(user_id, server_id)
# # #         query = "SELECT saldo_carteira, saldo_banco FROM USUARIOS WHERE user_id = %s AND server_id = %s"
# # #         result = self._execute_query(query, (user_id, server_id), fetch='one')
# # #         return {'wallet': result[0], 'bank': result[1]} if result else {'wallet': 0, 'bank': 0}

# # #     def add_balance(self, user_id, server_id, amount, target='carteira'):
# # #         """Adiciona ou remove valor do saldo da carteira ou do banco."""
# # #         self.ensure_user_exists(user_id, server_id)
# # #         column = 'saldo_carteira' if target == 'carteira' else 'saldo_banco'
# # #         query = f"UPDATE USUARIOS SET {column} = {column} + %s WHERE user_id = %s AND server_id = %s"
# # #         self._execute_query(query, (amount, user_id, server_id))

# # #     def get_cooldown(self, user_id, server_id, command_name):
# # #         """Busca o timestamp do último uso de um comando."""
# # #         self.ensure_user_exists(user_id, server_id)
# # #         column_map = {'daily': 'ultimo_daily', 'work': 'ultimo_work'}
# # #         column = column_map.get(command_name)
# # #         if not column: return None
        
# # #         query = f"SELECT {column} FROM USUARIOS WHERE user_id = %s AND server_id = %s"
# # #         result = self._execute_query(query, (user_id, server_id), fetch='one')
# # #         return result[0] if result else None

# # #     def update_cooldown(self, user_id, server_id, command_name):
# # #         """Atualiza o timestamp de um comando para o tempo atual."""
# # #         self.ensure_user_exists(user_id, server_id)
# # #         column_map = {'daily': 'ultimo_daily', 'work': 'ultimo_work'}
# # #         column = column_map.get(command_name)
# # #         if not column: return
        
# # #         query = f"UPDATE USUARIOS SET {column} = %s WHERE user_id = %s AND server_id = %s"
# # #         self._execute_query(query, (datetime.now(), user_id, server_id))

# # #     # --- FUNÇÕES GLOBAIS ---
    
# # #     def get_global_data(self, key):
# # #         """Busca um valor da tabela de dados globais."""
# # #         query = "SELECT valor FROM DADOS_GLOBAIS WHERE chave = %s"
# # #         result = self._execute_query(query, (key,), fetch='one')
# # #         return result[0] if result else None
        
# # #     def update_global_data(self, key, value):
# # #         """Atualiza um valor na tabela de dados globais."""
# # #         query = "UPDATE DADOS_GLOBAIS SET valor = %s WHERE chave = %s"
# # #         self._execute_query(query, (value, key))