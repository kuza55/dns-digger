CREATE DATABASE digger;
\c digger

CREATE TABLE domains (
    id serial PRIMARY KEY NOT NULL,
    domain text NOT NULL,
    active boolean NOT NULL DEFAULT FALSE,
    UNIQUE (domain)
);

CREATE TABLE sources (
    domain_id integer NOT NULL REFERENCES domains(id),
    source text NOT NULL,
    label text NOT NULL,
    info text,
    log_date date NOT NULL,
    UNIQUE (domain_id, source, log_date)
);

CREATE TABLE records (
    domain_id integer NOT NULL REFERENCES domains(id),
    resolver inet NOT NULL,
    log_date date NOT NULL,
    section text NOT NULL,
    type text NOT NULL,
    name_id integer NOT NULL,
    rdata text NOT NULL,
    ttl integer NOT NULL
);

CREATE TABLE summaries (
    domain_id integer NOT NULL REFERENCES domains(id),
    resolver inet NOT NULL,
    log_date date NOT NULL,
    queries integer NOT NULL,
    errors integer NOT NULL,
    rcodezero integer NOT NULL,
    nonempty integer NOT NULL
);
