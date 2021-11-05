# Trakt.tv tools

## Purpose

 * Export Movies or TVShows IDs from Trakt.tv list into CSV file format.

## Requirements

You must use Python 3.x.

Refer to [README.md](README.md#requirements) for details.

## Configuration

Refer to [README.md](README.md#configuration) for details.

## Usage
### Export usage

```text
usage: export_trakt.py [-h] [-v] [-c CONFIG] [-o [OUTPUT]]
                       [-t {movies,shows,episodes}]
                       [-l {watchlist,collection,history}] [-u USERLIST] [-C]
                       [-D] [-V]

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
  -u USERLIST, --userlist USERLIST
                        allow to export a user custom list, default None
  -C, --clean           empty list after export, default False
  -D, --duplicate       remove duplicate from list after export, default False
  -V, --verbose         print additional verbose information, default True

Read a list from Trakt API. Export them into a CSV file.
```

## Examples
### Sample export usage

Export all movies from watchlist:

	$ ./export_trakt.py -c config.ini -t movies -o export_movies_watchlist.csv -l watchlist

Export all tvshows from the history list:

	$ ./export_trakt.py -c config.ini -t shows -o export_shows_history.csv -l history

Export all episodes from the history list:

	$ ./export_trakt.py -c config.ini -t episodes -o export_episodes_history.csv -l history

Export all shows from the history list and remove duplicate:

	$ ./export_trakt.py -c config.ini -t shows -o export_shows_history.csv -l history -D

Export all movies from a user list:

	$ ./export_trakt.py -c config.ini -t movies -u <username> -o export_movies_<username>.csv

## Support

To get support, please create new [issue](https://github.com/xbgmsharp/trakt/issues)

## Licence

This script is free software:  you can redistribute it and/or  modify  it under  the  terms  of the  GNU  General  Public License  as published by the Free Software Foundation.

This program is distributed in the hope  that it will be  useful, but WITHOUT ANY WARRANTY; without even the  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

See <http://www.gnu.org/licenses/gpl.html>.
