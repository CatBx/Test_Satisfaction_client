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
        id_avis integer not null,
        id_resto integer not null,
        auteur varchar(100) not null,
        nb_notes integer,
        note integer not null,
        avis varchar(50000),
        date_avis varchar(100),
        date_exp TIMESTAMP,
        reply varchar(50000),
        date_reply TIMESTAMP,
CONSTRAINT pk_id_avis PRIMARY KEY(id_avis),
CONSTRAINT fk_id_resto FOREIGN KEY(id_resto) REFERENCES restaurants(id_resto)
);

\q
