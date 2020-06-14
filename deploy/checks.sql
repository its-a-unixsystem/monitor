-- Deploy monitor-db:checks to pg
-- requires: appschema

BEGIN;

CREATE TABLE monitor.checks (
    name      varchar(255) NOT NULL,
    host      varchar(255) NOT NULL,
    checktime timestamp NOT NULL,
    regex_hits integer,
    regex varchar(255),
    return_code smallint
);
COMMIT;
