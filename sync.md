# Trakt.tv tools

## Purpose

 * Create trakt.tv custom list from TDMB discover with filter.

## Requirements

You must use Python 3.x.

Refer to [README.md](README.md#requirements) for details.

## Configuration

Refer to [README.md](README.md#configuration) for details.

### Configuration sample
```text
[TMDB]
apikey = xxxxxxxxxxxxxxxxxxxxxxxxx
filter = {'vote_average.gte': 6, 'year': 2015, 'with_genres': 35}
[TRAKT]
(...)
[SETTINGS]
(...)
```

### Configuration details

The Movie Database API:
 * ``apikey``: Uniq ID to identify your application, https://www.themoviedb.org/documentation/api
 * ``filter``: Filter for discover process, filter list http://docs.themoviedb.apiary.io/#reference/discover/

## Usage
#### Sync usage
```text
usage: sync_tmdb_trakt.py [-h] [-v] [-c CONFIG] [-t {movies,shows}] [-l LIST] [-s [SEEN]] [-C] [-d] [--skipwatched] [-V]

This program sync TMDB discovery into a Trakt.tv list.

options:
  -h, --help            show this help message and exit
  -v                    show program's version number and exit
  -c CONFIG, --config CONFIG
                        allow to overwrite default config filename, default config.ini
  -t {movies,shows}, --type {movies,shows}
                        allow to overwrite type, default movies
  -l LIST, --list LIST  specify a trakt.tv user list via is slug name
  -s [SEEN], --seen [SEEN]
                        mark as seen, default False. Use specific time if provided, falback time: "2016-01-01T00:00:00.000Z"
  -C, --clean           empty trakt.tv list prior to import, default False
  -d, --dryrun          do not update the account, default False
  --skipwatched         skip watched items from trakt.tv, default True
  -V, --verbose         print additional verbose information, default True

Discover movie using TMDB filter (year, genre, vote average). Import them into a list in Trakt.tv, mark as seen if need.
```

## Examples
#### Sample sync usage

Get all TMDB movies from filter and import them into trakt.tv in list comedy
  $ ./sync_tmdb_trakt.py -c /tmp/config.ini -l comedy

## Support

To get support, please create new [issue](https://github.com/xbgmsharp/trakt/issues)

## Licence

This script is free software:  you can redistribute it and/or  modify  it under  the  terms  of the  GNU  General  Public License  as published by the Free Software Foundation.

This program is distributed in the hope  that it will be  useful, but WITHOUT ANY WARRANTY; without even the  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

See <http://www.gnu.org/licenses/gpl.html>.
