# trakt.tv import/export tools

Python scripts that use the [Trakt API](https://trakt.docs.apiary.io/) to export movie and episodes from trakt lists to a csv file, and import them back to any Trakt account. 

## Installation 

You must use Python 3.x.

To install requirements: 

```console
$ pip install -r requirements.txt
```

## Usage

### Setup

* Create an [Trakt.tv application](https://trakt.tv/oauth/applications) to have your own ``client_id`` and ``client_secret``, https://trakt.tv/oauth/applications.
You only need to fill up the ``Name`` with a ``Description`` and ``Redirect uri`` to `urn:ietf:wg:oauth:2.0:oob`, leave the rest empty and click on ``SAVE APP``.
* Run the script to create a default config file ``config.ini``
```
$ python export_trakt.py
```
* Edit the config file ``config.ini``. You **must** specify 
	* ``client_id``
	* ``client_secret``
	* ``username``
	* any other settings appropriate to your environment, eg: URL, proxy, etc...
* Run the script to authenticate against Trakt.tv API using the PIN method.
```
$ python export_trakt.py
```
* In the CLI, you will be prompted to open a link into a browser and paste the pincode back to the script. You should only need to do this once.

### Import 

For help, run 
```console
$ python import_trakt.py -h
```
#### Import movies from csv file to history with csv ``watched_at`` time 
The following command will import all movies in  ``m.csv`` to the default history list in Trakt with the ``watched_at`` and the  ``trakt``  id columns specified in ``m.csv``. 
```console
$ python import_trakt.py -c config.ini -f trakt -i m.csv -l history -t movies -w
```
#### Import episodes from csv file to history with custom ``watched_at`` time 
The following command will import all episodes in ``e.csv`` to the default history list in Trakt with the ``trakt`` id columns specified in ``e.csv``, with a ``watched_at`` date set to ``2014-01-01T00:00:00.000Z``. 
```console
$ python import_trakt.py -c config.ini -f trakt -i e.csv -l history -t episodes -s 2014-01-01T00:00:00.000Z
```
#### Import movies from csv file to user list 
The following command will import all movies in  ``m.csv`` to a custom user list using the ``trakt`` id columns specified in ``m.csv``. 
```console
$ python import_trakt.py -c config.ini -f trakt -i m_f.csv -t movies -u
```

The user will have to provide the id of the user list they want to import to. 
```console
Found 2 user list(s)

id       | name
21358741 | test2
21369802 | test

Type in the id matching with the name of the list you want to import item(s) to.
Input: 
```

### Export

For help, run 
```console
$ python export_trakt.py -h
```
#### Export movies from history list to csv
The following command will export all movies in Trakt's default history list to ``m.csv``.
```console
$ python export_trakt.py -c config.ini -t movies -o m.csv -l history
```
#### Export episodes from history list to csv
The following command will export all episodes in Trakt's default history list to ``e.csv``.
```console
$ python export_trakt.py -c config.ini -t episodes -o e.csv -l history
```
#### Export user list to csv 
The following command will export all movies from a custom user list to ``test2.csv``. 
```console
$ python export_trakt.py -c config.ini -t movies -o test2.csv -u
```

The user will have to provide the id of the user list they want to export, or ``all`` for all user lists. This will export them in to csv files with the name of the user list.  
```console
Found 2 user list(s)

id       | name
21358741 | test2
21369802 | test

Type in the id matching with the name of the list you want to export, or 'all' for all lists.
Input:
```

## Export data from Kodi

Export Movies or TVShows IDs from Kodi into CSV file format.
[Export data from Kodi](KODI.md)

## Export data from CouchPotato

Export Movies IDs from CouchPotato into CSV file format.
[Export data from CouchPotato](CouchPotato.md)

## Support

To get support, please create new [issue](https://github.com/xbgmsharp/trakt/issues)

## Contribution
I'm happy to accept Pull Requests! 

## License

This script is free software:  you can redistribute it and/or  modify  it under  the  terms  of the  GNU  General  Public License  as published by the Free Software Foundation.

This program is distributed in the hope  that it will be  useful, but WITHOUT ANY WARRANTY; without even the  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

See <http://www.gnu.org/licenses/gpl.html>.
