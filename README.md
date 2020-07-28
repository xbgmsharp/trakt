# Trakt.tv import/export tools

## Purpose

 * Import Movies or TVShows IDs from CSV file format into Trakt.tv.
 * Export Movies or TVShows IDs from Trakt.tv list into CSV file format.
 * Create trakt.tv custom list from TDMB discover with filter.

## Requirements

You must use Python 3.x.

### On Ubuntu/Debian Linux system

Ensure you are running Python 3
```
$ python -V
Python 3.5
```

Install need module dependencies

```
$ apt-get install python3-dateutil python3-simplejson python3-requests python3-openssl jq
```

### On Windows system

 Download the installer: https://www.python.org/downloads/windows/

 Ensure you are running Python 3
```
<python dir>>python.exe -V
Python 3.5
```

 Install need module dependencies

```
<python dir>\Scripts\pip3.exe install requests simplejson
```

### On macOS system

 Download the installer: https://www.python.org/downloads/mac-osx/

Append to PATH in ZSH

```shell
$ path=('/Library/Frameworks/Python.framework/Versions/3.8/bin' $path)
```

Ensure you are running Python 3

```shell
$ python3 -V
Python 3.8.5
```

Run Install Certificates.command

```shell
$ pip3 install certifi
```

Open a new Terminal session so that certificates will be available

Install need module dependencies

```shell
$ pip3 install python-dateutil
$ pip3 install simplejson
$ pip3 install requests
$ pip3 install pyopenssl
$ pip3 install jq
```

## Usage

* Create an [Trakt.tv application](https://trakt.tv/oauth/applications) to have your own ``client_id`` and ``client_secret``, https://trakt.tv/oauth/applications.
You only need to fill up the ``Name`` with a ``Description`` and ``Redirect uri`` to `urn:ietf:wg:oauth:2.0:oob`, leave the rest empty and click on ``SAVE APP``.

* Run the script to create a default config file ``config.ini``

```
$ python export_trakt.py
```

* Edit the config file ``config.ini`` and specify the ``client_id`` and ``client_secret`` as well as any other settings appropriate to your enviromenent, eg: URL, proxy, etc...
Refer to ``Configuration details`` section for more information.

```
$ vim config.ini
```

* Run the script to authenticate against Trakt.tv API using the PIN method and it will generate you an ``oauth_token``.
You will be prompted to open a link into a browser and paste the pincode back to the script. 
Make sure you save the generated ``oauth_token`` into the config file ``config.ini`` for later use.

```
$ python export_trakt.py
```

## Import 

[Import CSV into trakt.tv](import.md)

## Export

[Export data from trakt.tv into CSV](export.md)

## Sync

[Create trakt.tv list from TDMB discover with filter](sync.md)

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

## Licence

This script is free software:  you can redistribute it and/or  modify  it under  the  terms  of the  GNU  General  Public License  as published by the Free Software Foundation.

This program is distributed in the hope  that it will be  useful, but WITHOUT ANY WARRANTY; without even the  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

See <http://www.gnu.org/licenses/gpl.html>.
