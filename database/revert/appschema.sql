-- Revert monitor-db:appschema from pg

BEGIN;

DROP SCHEMA monitor;

COMMIT;
