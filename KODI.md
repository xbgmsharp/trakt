# Kodi export

## Purpose

 * Export Movies or TVShows IDs from Kodi into CSV file format.

## Export data from Kodi

#### Favourites - To put in watchlist

Export your favourites movies ``movies_favourites.csv``

```
$ sqlite3 plugin.video.genesis/favourites.db "select id from movies;" -csv > movies_favourites.csv
```

Export your favourites tvshows ``tvshows_favourites.csv``

```
$ sqlite3 plugin.video.genesis/favourites.db "select id from tvshows;" -csv > tvshows_favourites.csv
```

From the sqlite prompt
```sql
sqlite> .schema
CREATE TABLE tvshows (id TEXT, items TEXT, UNIQUE(id));
CREATE TABLE movies (id TEXT, items TEXT, UNIQUE(id));
sqlite> select id from movies;
tt15027XX
...
sqlite> select id from tvshows;
tt04606XX
...
sqlite>
```

#### Meta - Views - To put in history list

Export your views movies into ``movies_views.csv``

```
$ sqlite3 script.module.metahandler/meta_cache/video_cache.db "SELECT imdb_id FROM movie_meta WHERE overlay=7;" -csv > movies_views.csv
```

Export your views episodes ``episodes_views.csv``

```
$ sqlite3 script.module.metahandler/meta_cache/video_cache.db "SELECT imdb_id,season,episode FROM episode_meta WHERE overlay=7;" -csv > episodes_views.csv
```

From the sqlite prompt
```sql
sqlite> SELECT count(imdb_id) FROM movie_meta WHERE overlay=7;
XX
sqlite> SELECT count(imdb_id) FROM episode_meta WHERE overlay=7;
XXX
sqlite> SELECT count(imdb_id) FROM season_meta WHERE overlay=7;
XX
sqlite> SELECT count(imdb_id) FROM tvshow_meta WHERE overlay=7;
XX
```
