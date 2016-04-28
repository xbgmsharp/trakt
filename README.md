# Trakt import/export tools

## Purpose
Import CSV file format Movies or TVShows IDs into Trakt.tv.

Export Movies or TVShows IDs from Trakt.tv list into CSV file format.

## Usage

#### Import
```text
usage: import_trakt.py [-h] [-v] [-c CONFIG] [-i [INPUT]]
                       [-f {imdb,tmdb,tvdb,tvrage}]
                       [-t {movies,shows,episodes}]
                       [-l {watchlist,collection,history}] [-s [SEEN]] [-V]

This program import Movies or TVShows IDs into Trakt.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -c CONFIG, --config CONFIG
                        allow to overwrite default config filename, default
                        config.ini
  -i [INPUT], --input [INPUT]
                        allow to overwrite default input filename, default
                        None
  -f {imdb,tmdb,tvdb,tvrage}, --format {imdb,tmdb,tvdb,tvrage}
                        allow to overwrite default ID type format, default
                        imdb
  -t {movies,shows,episodes}, --type {movies,shows,episodes}
                        allow to overwrite type, default movies
  -l {watchlist,collection,history}, --list {watchlist,collection,history}
                        allow to overwrite default list, default watchlist
  -s [SEEN], --seen [SEEN]
                        mark as seen, default False. Use specific time if
                        provided, falback time: "2016-01-01T00:00:00.000Z"
  -V, --verbose         print additional verbose information, default True

Read a list of ID from 'imdb', 'tmdb', 'tvdb' or 'tvrage'. Import them into a
list in track, mark as seen if need.
```

#### Export
```text
usage: export_trackt.py [-h] [-v] [-c CONFIG] [-o [OUTPUT]]
                        [-t {movies,shows,episodes}]
                        [-l {watchlist,collection,history}] [-V]

This program export Movies or TVShows IDs from Trakt list.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -c CONFIG, --config CONFIG
                        allow to overwrite default config filename, default
                        config.ini
  -o [OUTPUT], --output [OUTPUT]
                        allow to overwrite default output filename, default
                        None
  -t {movies,shows,episodes}, --type {movies,shows,episodes}
                        allow to overwrite type, default movies
  -l {watchlist,collection,history}, --list {watchlist,collection,history}
                        allow to overwrite default list, default history
  -V, --verbose         print additional verbose information, default True

Read a list from Trakt API. Export them into a CSV file.
```

## Sample import usage

Import all movies with imdb id from file ``movies_favorites.csv`` into watchlist:

        $ ./import_trakt.py -c config.ini -f imdb -t movies -i movies_favorites.csv -l watchlist

Import all tvshows with imdb id from file ``tvshows_favorites.csv`` into watchlist:

        $ ./import_trakt.py -c config.ini -f imdb -i  tvshows_favorites.csv -l watchlist -t shows

Import all movies with imdb id from file ``movies_views.csv`` into history and mark as seen:

        $ ./import_trakt.py -c config.ini -f imdb -i movies_views.csv -l history -t movies -s

Import all episodes with tvshows imdbid from file ``episodes_views.csv`` into history and mark as seen:

        $ ./import_trakt.py -c config.ini -f imdb -i episodes_views.csv -l history -t episodes -s

## Sample export usage

Export all movies from wathclist:

	$ ./export_trakt.py -c config.ini -t movies -o export_movies_wathclist.csv -l watchlist

Export all tvshows from the history list:

	$ ./export_trakt.py -c config.ini -t shows -o export_tvshows_history.csv -l history


#### Movies to add watchlist
One 'imdb' or 'tmdb' or 'tvdb' or 'tvrage' by line
```
tt22239XX
tt11712XX
tt12728XX
```

#### TVShows to add to watchlist
one 'imdb' or 'tmdb' or 'tvdb' or 'tvrage' by line
```
tt04606XX
tt12365XX
```

#### Episodes as views to history
One 'imdb' or 'tmdb' or 'tvdb' or 'tvrage with season and episode
```
tt04606XX,3,4
```

## Export data from Kodi

#### Favourites - To put in watchlist

Export your favourites movies ``movies_favourites.csv``

        $ sqlite3 plugin.video.genesis/favourites.db "select id from movies;" -csv > movies_favourites.csv

Export your favourites tvshows ``tvshows_favourites.csv``

        $ sqlite3 plugin.video.genesis/favourites.db "select id from tvshows;" -csv > tvshows_favourites.csv

From the sqlite promt
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

        $ sqlite3 script.module.metahandler/meta_cache/video_cache.db "SELECT imdb_id FROM movie_meta WHERE overlay=7;" -csv > movies_views.csv

Export your views episodes ``episodes_views.csv``

        $ sqlite3 script.module.metahandler/meta_cache/video_cache.db "SELECT imdb_id,season,episode FROM episode_meta WHERE overlay=7;" -csv > episodes_views.csv

From the sqlite promt
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

## Requirements

#### On Ubuntu/Debian Linux system

        apt-get install python-dateutil python-simplejson python-requests python-openssl jq

#### On Windows on Python 2.7

 Download the installer: https://www.python.org/ftp/python/2.7.11/python-2.7.11.msi

 Install need module dependecies

        C:\Python2.7\Scripts\easy_install-2.7.exe simplejson requests

## Support

To get support, please create new [issue](https://github.com/xbgmsharp/import_csv_trakt/issues)

## Licence

This script is free software:  you can redistribute it and/or  modify  it under  the  terms  of the  GNU  General  Public License  as published by the Free Software Foundation.

This program is distributed in the hope  that it will be  useful, but WITHOUT ANY WARRANTY; without even the  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

See <http://www.gnu.org/licenses/gpl.html>.
