drop database clients;
create database clients;
\c clients;

create table restaurants(
        id_resto integer,
        nom varchar(100),
        contact varchar(100),
        nb_avis integer,
        score numeric(5,3),
CONSTRAINT pk_id_resto PRIMARY KEY(id_resto)
);

create table avis(
        id_avis SERIAL,
        id_resto integer,
        auteur varchar(100),
        nb_notes integer,
        note integer,
        avis varchar(50000),
        date_avis TIMESTAMP,
        date_exp TIMESTAMP,
        reply varchar(50000),
        date_reply TIMESTAMP,
CONSTRAINT pk_id_avis PRIMARY KEY(id_avis),
CONSTRAINT fk_id_resto FOREIGN KEY(id_resto) REFERENCES restaurants(id_resto)
);

\q
