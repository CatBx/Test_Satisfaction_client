delete from avis;
delete from restaurants;
COPY restaurants(id_resto,nom,contact,nb_avis,score) FROM '/app/raw_data/restaurants.csv' DELIMITER '#' CSV HEADER;
COPY avis(id_avis,id_resto, auteur, nb_notes, note, avis,date_avis,date_exp,reply,date_reply) FROM '/app/raw_data/restaurants_avis.csv' DELIMITER '#' CSV HEADER;

