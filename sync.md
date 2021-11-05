# Trakt.tv tools

## Purpose

 * Create trakt.tv custom list from TDMB discover with filter.

## Requirements

You must use Python 3.x.

Refer to [README.md](README.md#requirements) for details.

## Configuration

Refer to [README.md](README.md#configuration) for details.

## Usage
#### Sync usage
```text
usage: import_trakt.py [-h] [-v] [-c CONFIG] -i [INPUT]
                       [-f {imdb,tmdb,tvdb,tvrage,trakt}]
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
  -f {imdb,tmdb,tvdb,tvrage,trakt}, --format {imdb,tmdb,tvdb,tvrage,trakt}
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

Read a list of ID from 'imdb', 'tmdb', 'tvdb' or 'tvrage' or 'trakt'. Import
them into a list in Trakt.tv, mark as seen if need.
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
#### Sample sync usage

## Support

To get support, please create new [issue](https://github.com/xbgmsharp/trakt/issues)

## Licence

This script is free software:  you can redistribute it and/or  modify  it under  the  terms  of the  GNU  General  Public License  as published by the Free Software Foundation.

This program is distributed in the hope  that it will be  useful, but WITHOUT ANY WARRANTY; without even the  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

See <http://www.gnu.org/licenses/gpl.html>.
