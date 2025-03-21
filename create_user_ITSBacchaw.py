import json
import logging
import mysql.connector
import psycopg2
from mysql.connector import errorcode
from psycopg2 import sql

# Configure logging
log_filename = "/backup/logs/ITSBacchaw_creation_2025-03-21.log"
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# Load database credentials
with open('/root/jsonfiles/ti-dba-prod-01.json') as f:
    db_credentials = json.load(f)

mysql_user = db_credentials['mysql']['user']
mysql_password = db_credentials['mysql']['password']
pgsql_user = db_credentials['pgsql']['user']
pgsql_password = db_credentials['pgsql']['password']

# Load server lists
def load_server_list(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines()]

mysql_servers = load_server_list('/backup/configs/MYSQL_servers_list.conf')
pgsql_servers = load_server_list('/backup/configs/PGSQL_servers_list.conf')

# User details
new_user = "ITSBacchaw"
new_password = "ITSBacchaw"

# Create user in MySQL
def create_mysql_user(server):
    try:
        conn = mysql.connector.connect(
            host=server,
            user=mysql_user,
            password=mysql_password
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE USER '{new_user}'@'%' IDENTIFIED BY '{new_password}';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO '{new_user}'@'%' WITH GRANT OPTION;")
        conn.commit()
        logging.info(f"MySQL user '{new_user}' created on {server}")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logging.error(f"Access denied for server {server}")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logging.error(f"Database does not exist on server {server}")
        else:
            logging.error(err)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Create user in PostgreSQL
def create_pgsql_user(server):
    try:
        conn = psycopg2.connect(
            host=server,
            user=pgsql_user,
            password=pgsql_password
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s;").format(sql.Identifier(new_user)), [new_password])
        cursor.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {};").format(sql.Identifier('postgres'), sql.Identifier(new_user)))
        conn.commit()
        logging.info(f"PostgreSQL user '{new_user}' created on {server}")
    except Exception as e:
        logging.error(f"Error creating PostgreSQL user on server {server}: {e}")
    finally:
        cursor.close()
        conn.close()

# Process all servers
for server in mysql_servers:
    create_mysql_user(server)

for server in pgsql_servers:
    create_pgsql_user(server)

logging.info("User creation process completed.")
