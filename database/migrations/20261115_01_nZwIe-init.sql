-- init
-- depends 

CREATE TABLE localisations (
  id serial CONSTRAINT localisations_pk PRIMARY KEY,
  geo_point point NOT NULL,
  ville text,
  code_postale text,
  region text,
  departement text,
  pays text
);

CREATE TABLE aleas (
  id serial CONSTRAINT aleas_pk PRIMARY KEY,
  nom text NOT NULL,
  commentaire text
);

CREATE TABLE initiatives (
  id serial CONSTRAINT initiatives_pk PRIMARY KEY,
  titre text,
  type_initiative text,
  liens text,
  images text,
  description text,
  alea_id integer REFERENCES aleas,
  type_porteur_initiative text,
  nom_porteur text,
  localisation integer REFERENCES localisations
);

CREATE TABLE sources (
  id serial CONSTRAINT sources_pk PRIMARY KEY,
  nom text NOT NULL,
  type text
);

CREATE TABLE tasks (
  id serial CONSTRAINT tasks_pk PRIMARY KEY,
  source_id integer NOT NULL UNIQUE,
  nom text NOT NULL,
  next_run timestamp,
  last_run timestamp,
  locked boolean
);

CREATE TABLE tasks_jobs (
  id bigserial CONSTRAINT tasks_jobs_pk PRIMARY KEY,
  task_id integer NOT NULL REFERENCES tasks,
  status text,
  job_timeout integer,
  ttl integer
);

CREATE TABLE tasks_jobs_summaries (
  id bigserial CONSTRAINT tasks_jobs_summaries_pk PRIMARY KEY,
  job_id bigint NOT NULL REFERENCES tasks_jobs UNIQUE,
  message text
);
