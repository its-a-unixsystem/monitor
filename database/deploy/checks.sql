-- Deploy monitor-db:checks to pg
-- requires: appschema

BEGIN;

CREATE TABLE monitor.checks (
    name      varchar(255) NOT NULL,
    host      varchar(255) NOT NULL,
    checktime timestamp NOT NULL,
    response_time integer,
    regex_hits integer,
    regex varchar(255),
    return_code smallint
);
create index idx_name on monitor.checks (name);
create index idx_checktime on monitor.checks (checktime);

COMMIT;
