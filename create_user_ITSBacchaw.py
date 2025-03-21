import json
import logging

# Configure logging
log_filename = "/backup/logs/ITSBacchaw_creation_2025-03-21.log"
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# Load database credentials
with open('/root/jsonfiles/ti-dba-prod-01.json') as f:
    db_credentials = json.load(f)

# Load server lists
def load_server_list(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines()]

mysql_servers = load_server_list('/backup/configs/MYSQL_servers_list.conf')
pgsql_servers = load_server_list('/backup/configs/PGSQL_servers_list.conf')

# User details
new_user = "ITSBacchaw"
new_password = "ITSBacchaw"

# Simulate creating user on MySQL instances
def create_mysql_user(server):
    logging.info(f"Simulating MySQL user '{new_user}' creation on {server}")
    # Here we would add actual code to create the user if we were connecting to the instance

# Simulate creating user on PostgreSQL instances
def create_pgsql_user(server):
    logging.info(f"Simulating PostgreSQL user '{new_user}' creation on {server}")
    # Here we would add actual code to create the user if we were connecting to the instance

# Process all servers
for server in mysql_servers:
    create_mysql_user(server)

for server in pgsql_servers:
    create_pgsql_user(server)

logging.info("User creation simulation process completed.")
