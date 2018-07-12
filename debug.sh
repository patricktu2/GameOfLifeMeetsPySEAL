# Copies the content of the consoles from the client and the server in the files
# log_server and log_client. The log files serve for debugging purposes

sudo docker cp gameOfLife:/SEAL/log_client  log_client
sudo docker cp gameOfLife:/SEAL/log_server log_server


