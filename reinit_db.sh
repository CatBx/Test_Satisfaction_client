#!/bin/bash
# Réinitialisatin du postgres
sudo chmod -R 750 ~/projet/app/pg_data
sudo chmod 644 ~/projet/source/Test_Satisfaction_client/initdb/*.sql
docker-compose down
sudo rm -Rf ~/projet/app/pg_data
docker-compose up -d
sudo chmod -R 750 ~/projet/app/pg_data

# Vérification de la présence des docker postgres et fastapi
sleep 5 
docker ps


