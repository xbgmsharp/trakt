# Trakt.tv tools

## Purpose

 * Import Movies or TVShows IDs from CSV file format into Trakt.tv.
 * Import Ratings of Movies or TVShows IDs from CSV file format into Trakt.tv.

## Requirements

You must use Python 3.x.

Refer to [README.md](README.md#requirements) for details.

## Configuration

Refer to [README.md](README.md#configuration) for details.

## Usage
### Import usage

```text
usage: import_trakt.py [-h] [-v] [-c CONFIG] -i [INPUT]
                       [-f {imdb,tmdb,tvdb,tvrage,trakt}]
                       [-t {movies,shows,episodes}]
                       [-l {watchlist,collection,history,ratings}] [-s [SEEN]] [-C]
                       [-w]
                       [-r]
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
  -w, --watched_at      import watched_at date from CSV, it's must be UTC
                        datetime, default False
  -r, --rated_at        import rated_at date from CSV, it's must be UTC
                        datetime, default False
  -f {imdb,tmdb,tvdb,tvrage,trakt}, --format {imdb,tmdb,tvdb,tvrage,trakt}
                        allow to overwrite default ID type format, default
                        imdb
  -t {movies,shows,episodes}, --type {movies,shows,episodes}
                        allow to overwrite type, default movies
  -l {watchlist,collection,history,ratings}, --list {watchlist,collection,history,ratings}
                        allow to overwrite default list, default watchlist
  -s [SEEN], --seen [SEEN]
                        mark as seen, default False. Use specific time if
                        provided, fallback time: "2016-01-01T00:00:00.000Z"
  -C, --clean           empty list prior to import, default False
  -V, --verbose         print additional verbose information, default True

Read a list of ID from 'imdb', 'tmdb', 'tvdb' or 'tvrage' or 'trakt'. Import
them into a list in Trakt.tv, mark as seen if need.
```

## Examples

### Sample import usage

Import all movies with imdb id from file ``movies_favorites.csv`` into watchlist:

	$ ./import_trakt.py -c config.ini -f imdb -t movies -i movies_favorites.csv -l watchlist

Import all tvshows with imdb id from file ``tvshows_favorites.csv`` into watchlist:

	$ ./import_trakt.py -c config.ini -f imdb -i  tvshows_favorites.csv -l watchlist -t shows

Import all movies with imdb id from file ``movies_views.csv`` into history and mark as seen:

	$ ./import_trakt.py -c config.ini -f imdb -i movies_views.csv -l history -t movies -s

Import all movies with imdb id from file ``movies_views.csv`` into history and mark as watched using watched_at date in CSV

	$ ./import_trakt.py -c config.ini -f imdb -i movies_views.csv -l history -t movies -w

Import all ratings of movies with imdb id from file ``movies_rated.csv`` using rated_at date in CSV and rating (0-10) in CSV as rating

	$ ./import_trakt.py -c config.ini -f imdb -i movies_views.csv -l ratings -t movies -r

Import all ratings of TVShows with imdb id from file ``shows_rated.csv`` using rated_at date in CSV and rating (0-10) in CSV as rating

	$ ./import_trakt.py -c config.ini -f imdb -i movies_views.csv -l ratings -t shows -r

Import all episodes with tvshows imdbid from file ``episodes_views.csv`` into history and mark as seen on 1 January 2014

	$ ./import_trakt.py -c config.ini -f imdb -i episodes_views.csv -l history -t episodes -s 2014-01-01T00:00:00.000Z

Import all episodes with tvshows imdbid from file ``episodes_views.csv`` into history and mark as watched using watched_at date in CSV

	$ ./import_trakt.py -c config.ini -f imdb -i episodes_views.csv -l history -t episodes -w

#### Movies to add watchlist
Header line as format must be one 'imdb' or 'tmdb' or 'tvdb' or 'tvrage' or 'trakt'
If the ID is not available in the specified format, the system will automatically search Trakt.tv's database using the value in the 'title' field to find the correct ID
Other columns are ignored
```
imdb,title
tt22239XX,
tt11712XX,
tt12728XX,
,The Matrix
,Inception
```

#### TVShows to add to watchlist
Header line as format must be one 'imdb' or 'tmdb' or 'tvdb' or 'tvrage' or 'trakt'
If the ID is not available in the specified format, the system will automatically search Trakt.tv's database using the value in the 'title' field to find the correct ID
Other columns are ignored
```
imdb,title
tt04606XX,
tt12365XX,
,Breaking Bad
,The Wire
```

#### Episodes as views to history
Header line as format 'imdb' or 'tmdb' or 'tvdb' or 'tvrage' or 'trakt'.
One 'imdb' or 'tmdb' or 'tvdb' or 'tvrage' or 'trakt' with season and episode
```
imdb
tt04606XX,3,4
```

## Support

To get support, please create new [issue](https://github.com/xbgmsharp/trakt/issues)

## Licence

This script is free software:  you can redistribute it and/or  modify  it under  the  terms  of the  GNU  General  Public License  as published by the Free Software Foundation.

This program is distributed in the hope  that it will be  useful, but WITHOUT ANY WARRANTY; without even the  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

See <http://www.gnu.org/licenses/gpl.html>.
