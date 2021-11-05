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

```

## Examples
#### Sample sync usage

## Support

To get support, please create new [issue](https://github.com/xbgmsharp/trakt/issues)

## Licence

This script is free software:  you can redistribute it and/or  modify  it under  the  terms  of the  GNU  General  Public License  as published by the Free Software Foundation.

This program is distributed in the hope  that it will be  useful, but WITHOUT ANY WARRANTY; without even the  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

See <http://www.gnu.org/licenses/gpl.html>.
