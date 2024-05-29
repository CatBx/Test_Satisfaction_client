export DIR=/home/ubuntu/projet/source/Test_Satisfaction_client
echo ${DIR}
sudo -u postgres psql</home/ubuntu/projet/source/Test_Satisfaction_client/create_db_clients.sql
sudo -u postgres psql clients <<EOF
COPY restaurants(id_resto,nom,contact,nb_avis,score) FROM '${DIR}/restaurants.csv' DELIMITER '#' CSV HEADER;
COPY avis(id_resto, auteur, nb_notes, avis,date_avis,date_exp,reply,date_reply) FROM '${DIR}/restaurants_avis.csv' DELIMITER '#' CSV HEADER;
EOF
exit

