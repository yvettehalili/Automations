import configparser
import logging
import mysql.connector
import psycopg2
from mysql.connector import errorcode
from psycopg2 import sql

# Configure logging
log_filename = "/backup/logs/ITSBacchaw_creation_2025-03-21.log"
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

# Load database credentials
config = configparser.ConfigParser()
config.read('/backup/configs/db_credentials.conf')

try:
    db_user = config['credentials']['DB_USR']
    db_password = config['credentials']['DB_PWD']
except KeyError as e:
    logging.error(f"Missing key in configuration file: {e}")
    exit(1)

# Load server lists
def load_server_list(file_path):
    servers = []
    try:
        config = configparser.ConfigParser()
        config.read(file_path)
        for section in config.sections():
            host = config.get(section, 'host')
            servers.append(host)
    except FileNotFoundError:
        logging.error(f"Server list file not found: {file_path}")
        exit(1)
    except KeyError as e:
        logging.error(f"Missing key in server list file: {e}")
        exit(1)

    return servers

mysql_servers = load_server_list('/backup/configs/MYSQL_servers_list.conf')
pgsql_servers = load_server_list('/backup/configs/PGSQL_servers_list.conf')

# User details
new_user = "ITSBacchaw"
new_password = "ITSBacchaw"

# Create user in MySQL
def create_mysql_user(server):
    logging.debug(f"Connecting to MySQL server: {server}")
    try:
        conn = mysql.connector.connect(
            host=server,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE USER '{new_user}'@'%' IDENTIFIED BY '{new_password}';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO '{new_user}'@'%' WITH GRANT OPTION;")
        conn.commit()
        logging.info(f"MySQL user '{new_user}' created on {server}")
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to MySQL server {server}: {err}")
    finally:
        try:
            if conn.is_connected():
                cursor.close()
                conn.close()
        except NameError:
            pass

# Create user in PostgreSQL
def create_pgsql_user(server):
    logging.debug(f"Connecting to PostgreSQL server: {server}")
    try:
        conn = psycopg2.connect(
            host=server,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s;").format(sql.Identifier(new_user)), [new_password])
        cursor.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {};").format(sql.Identifier('postgres'), sql.Identifier(new_user)))
        conn.commit()
        logging.info(f"PostgreSQL user '{new_user}' created on {server}")
    except Exception as e:
        logging.error(f"Error creating PostgreSQL user on server {server}: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except (NameError, AttributeError):
            pass

# Process all servers
for server in mysql_servers:
    create_mysql_user(server)

for server in pgsql_servers:
    create_pgsql_user(server)

logging.info("User creation process completed.")
