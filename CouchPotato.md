#  CouchPotato export

## Purpose

* Export Movies from CouchPotato into CSV file format.

## Export view (history) movies

Export your views movies into ``movies_views.csv``

```
$ sqlite3 .couchpotato/couchpotato.db "select identifier from library INNER JOIN movie ON library.id=movie.library_id where movie.status_id=10;" > coucouchpotato_movies.csv
```

From the sqlite prompt
```sql
sqlite> .schema movie
CREATE TABLE movie (
	id INTEGER NOT NULL, 
	last_edit INTEGER, 
	library_id INTEGER, 
	status_id INTEGER, 
	profile_id INTEGER, 
	PRIMARY KEY (id), 
	CONSTRAINT movie_library_id_fk FOREIGN KEY(library_id) REFERENCES library (id), 
	CONSTRAINT movie_status_id_fk FOREIGN KEY(status_id) REFERENCES status (id), 
	CONSTRAINT movie_profile_id_fk FOREIGN KEY(profile_id) REFERENCES profile (id)
);
CREATE INDEX ix_movie_last_edit ON movie (last_edit);
CREATE INDEX ix_movie_library_id ON movie (library_id);
CREATE INDEX ix_movie_profile_id ON movie (profile_id);
CREATE INDEX ix_movie_status_id ON movie (status_id);
sqlite> .schema library
CREATE TABLE library (
	id INTEGER NOT NULL, 
	year INTEGER, 
	identifier VARCHAR(20), 
	plot TEXT, 
	tagline TEXT, 
	info TEXT, 
	status_id INTEGER, 
	PRIMARY KEY (id), 
	CONSTRAINT library_status_id_fk FOREIGN KEY(status_id) REFERENCES status (id)
);
CREATE INDEX ix_library_identifier ON library (identifier);
CREATE INDEX ix_library_status_id ON library (status_id);
sqlite> .schema status
CREATE TABLE status (
	id INTEGER NOT NULL, 
	identifier VARCHAR(20), 
	label VARCHAR(20), 
	PRIMARY KEY (id), 
	UNIQUE (identifier)
);
sqlite> select * from status;
1|needs_update|Needs update
2|ignored|Ignored
3|done|Done
4|snatched|Snatched
5|downloaded|Downloaded
6|active|Active
7|wanted|Wanted
8|deleted|Deleted
9|available|Available
10|viewed|Viewed
11|failed|Failed
12|queued|Queued
sqlite> select count(id) from movie where status_id=10;
XXX
sqlite> select count(id) from library INNER JOIN movie ON library.id=movie.library_id where movie.status_id=10;
XXX
```
