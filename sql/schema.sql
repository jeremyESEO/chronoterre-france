PRAGMA foreign_keys = ON;
CREATE TABLE source (
 source_id TEXT PRIMARY KEY, name TEXT NOT NULL, owner TEXT NOT NULL,
 url TEXT NOT NULL, license TEXT NOT NULL
);
CREATE TABLE raw_file (
 raw_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source,
 path TEXT NOT NULL UNIQUE, request_url TEXT NOT NULL, sha256 TEXT NOT NULL CHECK(length(sha256)=64),
 fetched_at TEXT NOT NULL, byte_count INTEGER NOT NULL CHECK(byte_count>0)
);
CREATE TABLE department (
 department_code TEXT PRIMARY KEY, name TEXT NOT NULL, region_code TEXT NOT NULL CHECK(region_code='11'),
 raw_id TEXT NOT NULL REFERENCES raw_file
);
CREATE TABLE city (
 city_code TEXT PRIMARY KEY, name TEXT NOT NULL,
 department_code TEXT NOT NULL REFERENCES department,
 latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),
 longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180),
 raw_id TEXT NOT NULL REFERENCES raw_file
);
CREATE TABLE bibliography (
 reference_id INTEGER PRIMARY KEY, citation TEXT NOT NULL, url TEXT NOT NULL
);
CREATE TABLE taxon (
 taxon_id TEXT PRIMARY KEY, accepted_name TEXT NOT NULL, rank TEXT,
 phylum TEXT, class_name TEXT, family TEXT
);
CREATE TABLE geo_interval (
 interval_id TEXT PRIMARY KEY, early_name TEXT NOT NULL, late_name TEXT,
 max_ma REAL NOT NULL CHECK(max_ma>=0), min_ma REAL NOT NULL CHECK(min_ma>=0 AND min_ma<=max_ma)
);
CREATE TABLE fossil_site (
 site_id INTEGER PRIMARY KEY, name TEXT NOT NULL,
 department_code TEXT NOT NULL REFERENCES department,
 latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),
 longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180),
 environment TEXT, coordinate_basis TEXT, coordinate_precision TEXT,
 geographic_comment TEXT, raw_id TEXT NOT NULL REFERENCES raw_file
);
CREATE TABLE fossil_occurrence (
 occurrence_id INTEGER PRIMARY KEY, site_id INTEGER NOT NULL REFERENCES fossil_site,
 taxon_id TEXT NOT NULL REFERENCES taxon, reference_id INTEGER NOT NULL REFERENCES bibliography,
 interval_id TEXT NOT NULL REFERENCES geo_interval, identified_name TEXT NOT NULL,
 raw_id TEXT NOT NULL REFERENCES raw_file
);
CREATE TABLE climate_model (
 model_id TEXT PRIMARY KEY, name TEXT NOT NULL, institution TEXT NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN ('reanalysis','projection')),
 scenario TEXT NOT NULL
);
CREATE TABLE climate_series (
 series_id TEXT PRIMARY KEY, city_code TEXT NOT NULL REFERENCES city,
 model_id TEXT NOT NULL REFERENCES climate_model,
 kind TEXT NOT NULL CHECK(kind IN ('baseline','future')),
 start_date TEXT NOT NULL, end_date TEXT NOT NULL CHECK(end_date>=start_date),
 grid_latitude REAL NOT NULL, grid_longitude REAL NOT NULL,
 raw_id TEXT NOT NULL REFERENCES raw_file,
 UNIQUE(city_code,model_id,start_date,end_date)
);
CREATE TABLE climate_day (
 series_id TEXT NOT NULL REFERENCES climate_series, date TEXT NOT NULL CHECK(length(date)=10),
 tmean_c REAL NOT NULL CHECK(tmean_c BETWEEN -90 AND 65),
 tmax_c REAL NOT NULL CHECK(tmax_c BETWEEN -90 AND 65),
 tmin_c REAL NOT NULL CHECK(tmin_c BETWEEN -90 AND 65),
 precipitation_mm REAL NOT NULL CHECK(precipitation_mm BETWEEN 0 AND 1500),
 CHECK(tmin_c<=tmean_c AND tmean_c<=tmax_c), PRIMARY KEY(series_id,date)
) WITHOUT ROWID;
CREATE INDEX idx_occurrence_site ON fossil_occurrence(site_id);
CREATE INDEX idx_occurrence_taxon ON fossil_occurrence(taxon_id);
CREATE INDEX idx_site_department ON fossil_site(department_code);
CREATE VIEW v_fossils AS
 SELECT o.occurrence_id,o.site_id,s.name AS site_name,s.department_code,d.name AS department,
 s.latitude,s.longitude,s.environment,s.coordinate_basis,s.coordinate_precision,s.geographic_comment,
 o.taxon_id,t.accepted_name,t.class_name,t.phylum,t.family,o.identified_name,
 i.early_name,i.late_name,i.max_ma,i.min_ma,o.reference_id,b.citation,b.url AS reference_url,o.raw_id
 FROM fossil_occurrence o JOIN fossil_site s USING(site_id)
 JOIN department d USING(department_code) JOIN taxon t USING(taxon_id)
 JOIN geo_interval i USING(interval_id) JOIN bibliography b USING(reference_id);
CREATE VIEW v_climate_annual AS
 SELECT s.series_id,s.city_code,s.model_id,s.kind,CAST(substr(d.date,1,4) AS INTEGER) AS year,
 COUNT(*) AS days,AVG(d.tmean_c) AS mean_c,SUM(d.precipitation_mm) AS rain_mm,
 SUM(CASE WHEN d.tmax_c>=30 THEN 1 ELSE 0 END) AS hot_days,
 SUM(CASE WHEN d.tmin_c>=20 THEN 1 ELSE 0 END) AS tropical_nights,
 SUM(CASE WHEN d.tmin_c<0 THEN 1 ELSE 0 END) AS frost_days
 FROM climate_day d JOIN climate_series s USING(series_id)
 GROUP BY s.series_id,year
 HAVING COUNT(*)=CAST(strftime('%j',substr(d.date,1,4)||'-12-31') AS INTEGER);
