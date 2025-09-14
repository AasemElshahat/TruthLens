-- MIGRATION SAFETY: Converting varchar('false'/'true') to boolean
-- This uses PostgreSQL's built-in conversion: 'false'::boolean = false, 'true'::boolean = true
-- Safe because original column had varchar(5) constraint with 'false' default
ALTER TABLE "checks" ALTER COLUMN "is_public" SET DATA TYPE boolean USING is_public::boolean;