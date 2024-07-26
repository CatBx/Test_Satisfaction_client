#nb restaurants
select count(1) from restaurants;
#nb avis
select count(1) from avis;
#nb avis et moyenne des notes des avis récupérés par restaurants à comparer avec la moyenne indiquée sur le site
select r.nom,r.nb_avis,r.score,count(1),avg(a.note) from restaurants r left join avis a on a.id_resto=r.id_resto group by r.id_resto order by 
4 desc limit 10;

