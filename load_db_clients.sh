sudo -u postgres psql</home/ubuntu/projet/source/Test_Satisfaction_client/create_db_clients.sql
sudo -u postgres psql clients <<EOF
COPY restaurants(id_resto,nom,contact,nb_avis,score) FROM '/home/ubuntu/projet/output/restaurants.csv' DELIMITER '#' CSV HEADER;
COPY avis(id_avis,id_resto, auteur, nb_notes, note, avis,date_avis,date_exp,reply,date_reply) FROM '/home/ubuntu/projet/output/restaurants_avis.csv' DELIMITER '#' CSV HEADER;
EOF
exit

