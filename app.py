from flask import Flask, send_file, send_from_directory, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error, pooling
import logging

app = Flask(__name__)
CORS(app)

# Конфигурация MySQL
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'MessiTop_10',
    'auth_plugin': 'mysql_native_password'
}

def setup_database():
    """Создаем базу данных и таблицы если они не существуют"""
    try:
        # Подключаемся без указания базы данных
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Создаем базу данных если нет
        cursor.execute("CREATE DATABASE IF NOT EXISTS search_service")
        cursor.execute("USE search_service")
        
        # Создаем таблицы
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS places (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(50) NOT NULL,
                rating FLOAT,
                description TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bloggers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(50) NOT NULL,
                followers INT
            )
        """)
        
        conn.commit()
        logging.info("Database and tables created successfully")
        
    except Error as e:
        logging.error(f"Database setup failed: {e}")
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_connection_pool():
    """Создаем пул соединений с проверкой базы данных"""
    try:
        # Сначала убедимся что база существует
        setup_database()
        
        # Теперь подключаемся с указанием базы данных
        config_with_db = {**MYSQL_CONFIG, 'database': 'search_service'}
        pool = pooling.MySQLConnectionPool(
            pool_name="my_pool",
            pool_size=5,
            **config_with_db
        )
        logging.info("MySQL connection pool created successfully")
        return pool
    except Error as e:
        logging.error(f"Error creating connection pool: {e}")
        return None

# Инициализация пула соединений
connection_pool = create_connection_pool()

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/')
def home():
    return send_file('project.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    logging.info(f"Search query: {query}")
    
    if not query:
        return jsonify({"error": "Empty query"}), 400
    
    if not connection_pool:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Ищем в обеих таблицах
        cursor.execute("""
            (SELECT 'place' as result_type, name, type, rating as score 
             FROM places WHERE name LIKE %s OR type LIKE %s LIMIT 10)
            UNION ALL
            (SELECT 'blogger' as result_type, name, type, followers as score 
             FROM bloggers WHERE name LIKE %s OR type LIKE %s LIMIT 10)
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
        
        results = cursor.fetchall()
        
        return jsonify({
            "query": query,
            "results": results if results else []
        })
        
    except Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    # Проверка подключения
    if connection_pool:
        try:
            conn = connection_pool.get_connection()
            conn.close()
            logging.info("Database connection test successful")
            app.run(host='127.0.0.1', port=5000, debug=False)
        except Error as e:
            logging.error(f"Database connection test failed: {e}")
    else:
        logging.error("Server not started due to database connection issues")