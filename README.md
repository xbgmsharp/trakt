# Trakt.tv import/export tools

## Purpose

 * Import Movies or TVShows IDs from CSV file format into Trakt.tv.

 * Export Movies or TVShows IDs from Trakt.tv list into CSV file format.

## Usage
On the first run, it will create a config file ``config.ini``, if it does not exist, 
make sure you edit it and specify the ``client_id`` and ``client_secret`` as well as any other settings appropriate to your enviromenent, eg: AN, proxy, etc...

        $ python import_trakt.py -h

        $ python import_trakt.py

        $ vim config.ini

Create an [Trakt.tv application](https://trakt.tv/oauth/applications) to have your own ``client_id`` and ``client_secret``, https://trakt.tv/oauth/applications

Then you need to authenticate against Trakt.tv API using the PIN and it will generate you an ``oauth_token``. 
Run the script to guide you thought this process to generate your ``oauth_token``.

## Configuration

#### Configuration sample
```text
[SETTINGS]
client_id = xxxxxxxxxxxxxxxxxxxxxxxxx
client_secret = xxxxxxxxxxxxxxxxxxxxxx
oauth_token = xxxxxxxxxxxxxxxxxxxxxxx
baseurl = https://api-v2launch.trakt.tv
proxy = False
proxy_host = https://127.0.0.1
proxy_port = 3128
```

#### Configuration details

 * ``client_id``: Uniq ID to identify your application, https://trakt.tv/oauth/applications
 * ``client_secret``: Uniq ID to identify your application, https://trakt.tv/oauth/applications
 * ``oauth_token``: Uniq ID to identify yourself against your application
 * ``baseurl``: API base URL, depends on the platfrom, eg: Production (https://api-v2launch.trakt.tv) or Staging (https://api-staging.trakt.tv)
 * ``proxy``: True/False setting to enable proxy support
 * ``proxy_host``: Full URI of the proxy
 * ``proxy_port``: Port of the proxy to connect to

## Developer documentation

        $ pydoc `pwd`/import_trakt.py

        $ pydoc `pwd`/export_trakt.py

## Usage 
#### Import usage
```text
usage: import_trakt.py [-h] [-v] [-c CONFIG] -i [INPUT]
                       [-f {imdb,tmdb,tvdb,tvrage}]
                       [-t {movies,shows,episodes}]
                       [-l {watchlist,collection,history}] [-s [SEEN]] [-C]
                       [-V]

This program import Movies or TVShows IDs into Trakt.tv.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -c CONFIG, --config CONFIG
                        allow to overwrite default config filename, default
                        config.ini
  -i [INPUT], --input [INPUT]
                        CSV file to import, default None
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
  -C, --clean           empty list prior to import, default False
  -V, --verbose         print additional verbose information, default True

Read a list of ID from 'imdb', 'tmdb', 'tvdb' or 'tvrage'. Import them into a
list in Trakt.tv, mark as seen if need.
```

#### Export usage
```text
usage: export_trakt.py [-h] [-v] [-c CONFIG] [-o [OUTPUT]]
                       [-t {movies,shows,episodes}]
                       [-l {watchlist,collection,history}] [-C] [-D] [-V]

This program export Movies or TVShows IDs from Trakt.tv list.

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
  -C, --clean           empty list after export, default False
  -D, --duplicate       Remove duplicate from list after export, default False
  -V, --verbose         print additional verbose information, default True

Read a list from Trakt API. Export them into a CSV file.
```

## Examples
#### Sample import usage

Import all movies with imdb id from file ``movies_favorites.csv`` into watchlist:

        $ ./import_trakt.py -c config.ini -f imdb -t movies -i movies_favorites.csv -l watchlist

Import all tvshows with imdb id from file ``tvshows_favorites.csv`` into watchlist:

        $ ./import_trakt.py -c config.ini -f imdb -i  tvshows_favorites.csv -l watchlist -t shows

Import all movies with imdb id from file ``movies_views.csv`` into history and mark as seen:

        $ ./import_trakt.py -c config.ini -f imdb -i movies_views.csv -l history -t movies -s

Import all episodes with tvshows imdbid from file ``episodes_views.csv`` into history and mark as seen on 1 January 2014

        $ ./import_trakt.py -c config.ini -f imdb -i episodes_views.csv -l history -t episodes -s 2014-01-01T00:00:00.000Z

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

#### Sample export usage

Export all movies from wathclist:

        $ ./export_trakt.py -c config.ini -t movies -o export_movies_wathclist.csv -l watchlist

Export all tvshows from the history list:

        $ ./export_trakt.py -c config.ini -t shows -o export_shows_history.csv -l history

Export all episodes from the history list:

        $ ./export_trakt.py -c config.ini -t episodes -o export_episodes_history.csv -l history

## Export data from Kodi

Export Movies or TVShows IDs from Kodi into CSV file format.
[Export data from Kodi](https://github.com/xbgmsharp/trakt/blob/master/KODI.md)

## Export data from CouchPotato

Export Movies IDs from CouchPotato into CSV file format.
[Export data from CouchPotato](https://github.com/xbgmsharp/trakt/blob/master/CouchPotato.md)

## Requirements

#### On Ubuntu/Debian Linux system

        $ apt-get install python-dateutil python-simplejson python-requests python-openssl jq

#### On Windows on Python 2.7

 Download the installer: https://www.python.org/ftp/python/2.7.11/python-2.7.11.msi

 Install need module dependecies

        C:\Python2.7\Scripts\easy_install-2.7.exe simplejson requests

## Support

To get support, please create new [issue](https://github.com/xbgmsharp/trakt/issues)

## Licence

This script is free software:  you can redistribute it and/or  modify  it under  the  terms  of the  GNU  General  Public License  as published by the Free Software Foundation.

This program is distributed in the hope  that it will be  useful, but WITHOUT ANY WARRANTY; without even the  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

See <http://www.gnu.org/licenses/gpl.html>.
