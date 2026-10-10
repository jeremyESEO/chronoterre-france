-- Cible spatiale complémentaire, NON EXÉCUTÉE ; PostgreSQL avec extension PostGIS requise.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE TABLE ct_version(id text PRIMARY KEY,producer text NOT NULL,retrieved_at timestamptz NOT NULL);
CREATE TABLE ct_zone(id text PRIMARY KEY,version_id text NOT NULL REFERENCES ct_version,kind text NOT NULL,geom geometry(MultiPolygon,4326) NOT NULL CHECK(ST_IsValid(geom)));
CREATE TABLE ct_parcel(id text PRIMARY KEY,version_id text NOT NULL REFERENCES ct_version,geom geometry(MultiPolygon,4326) NOT NULL CHECK(ST_IsValid(geom)));
CREATE INDEX ct_zone_gist ON ct_zone USING gist(geom);
CREATE INDEX ct_parcel_gist ON ct_parcel USING gist(geom);
-- Relations exactes et superficie ellipsoïdale : aucune mesure en degrés.
SELECT p.id parcel_id,z.id zone_id,ST_Area(ST_Intersection(p.geom,z.geom)::geography) area_m2 FROM ct_parcel p JOIN ct_zone z ON ST_Intersects(p.geom,z.geom);
