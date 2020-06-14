-- Revert monitor-db:checks from pg

BEGIN;

	DROP TABLE monitor.checks;

COMMIT;
