#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#------------------------------------------------------------------------
# Trakt.tv tools
#
# Copyright 2016-2021 xbgmsharp <xbgmsharp@gmail.com>. All Rights Reserved.
# License:  GNU General Public License version 3 or later; see LICENSE.txt
# Website:  https://trakt.tv, https://github.com/xbgmsharp/trakt
#------------------------------------------------------------------------
#
# Purpose:
# Sync TMDB discovery into a Trakt.tv list
#
# Requirement on Ubuntu/Debian Linux system
# apt-get install python3-dateutil python3-simplejson python3-requests python3-openssl jq
#
# Requirement on Windows on Python 3
# <python dir>\Scripts\pip3.exe install requests simplejson
#

import sys, os
# https://urllib3.readthedocs.org/en/latest/security.html#disabling-warnings
# http://quabr.com/27981545/surpress-insecurerequestwarning-unverified-https-request-is-being-made-in-pytho
# http://docs.python-requests.org/en/v2.4.3/user/advanced/#proxies
try:
        import simplejson as json
        import requests
        requests.packages.urllib3.disable_warnings()
        import tmdbsimple as tmdb
except:
        sys.exit("Please use your favorite mehtod to install the following module requests and simplejson and tmdbsimple to use this script")

import argparse
import configparser
import datetime
import collections
import pprint
import time

pp = pprint.PrettyPrinter(indent=4)

desc="""This program sync TMDB discovery into a Trakt.tv list."""

epilog="""Discover movie using TMDB filter (year, genre, vote average).
Import them into a list in Trakt.tv, mark as seen if need."""

_trakt = {
        'client_id'     :       '', # Auth details for trakt API
        'client_secret' :       '', # Auth details for trakt API
        'access_token'  :       '', # Auth details for trakt API
        'refresh_token' :       '', # Auth details for trakt API
        'username'      :       '', # trakt.tv username
        'baseurl'       :       'https://api-v2launch.trakt.tv' # Sandbox environment https://api-staging.trakt.tv
}

_tmdb = {
        'apikey'     :       '', # Auth details for TMDB API key
        'filter'     :       '', # Auth details for TMDB discover filter
}

_headers = {
        'Accept'            : 'application/json',   # required per API
        'Content-Type'      : 'application/json',   # required per API
        'User-Agent'        : 'Tratk importer',     # User-agent
        'Connection'        : 'Keep-Alive',         # Thanks to urllib3, keep-alive is 100% automatic within a session!
        'trakt-api-version' : '2',                  # required per API
        'trakt-api-key'     : '',                   # required per API
        'Authorization'     : '',                   # required per API
}

_proxy = {
        'proxy' : False,                # True or False, trigger proxy use
        'host'  : 'https://127.0.0.1',  # Host/IP of the proxy
        'port'  : '3128'                # Port of the proxy
}

_proxyDict = {
        "http" : _proxy['host']+':'+_proxy['port'],
        "https" : _proxy['host']+':'+_proxy['port']
}

response_arr = []

def read_config(args):
        """
        Read config file and if provided overwrite default values
        If no config file exist, create one with default values
        """
        work_dir = ''
        if getattr(sys, 'frozen', False):
                work_dir = os.path.dirname(sys.executable)
        elif __file__:
                work_dir = os.path.dirname(__file__)
        _configfile = os.path.join(work_dir, args.config)
        if os.path.exists(args.config):
                _configfile = args.config
        if args.verbose:
                print("Config file: {0}".format(_configfile))
        if os.path.exists(_configfile):
                try:
                        config = configparser.ConfigParser()
                        config.read(_configfile)
                        if config.has_option('TMDB','APIKEY') and len(config.get('TMDB','APIKEY')) != 0:
                                _tmdb['apikey'] = config.get('TMDB','APIKEY')
                        else:
                                print('Error, you must specify a TMDB APIKEY')
                                sys.exit(1)
                        if config.has_option('TMDB','FILTER') and len(config.get('TMDB','FILTER')) != 0:
                                _tmdb['filter'] = config.get('TMDB','FILTER')
                        else:
                                print('Warning, no filter found. default filter will apply')
                        if config.has_option('TRAKT','CLIENT_ID') and len(config.get('TRAKT','CLIENT_ID')) != 0:
                                _trakt['client_id'] = config.get('TRAKT','CLIENT_ID')
                        else:
                                print('Error, you must specify a trakt.tv CLIENT_ID')
                                sys.exit(1)
                        if config.has_option('TRAKT','CLIENT_SECRET') and len(config.get('TRAKT','CLIENT_SECRET')) != 0:
                                _trakt['client_secret'] = config.get('TRAKT','CLIENT_SECRET')
                        else:
                                print('Error, you must specify a trakt.tv CLIENT_SECRET')
                                sys.exit(1)
                        if config.has_option('TRAKT','ACCESS_TOKEN') and len(config.get('TRAKT','ACCESS_TOKEN')) != 0:
                                _trakt['access_token'] = config.get('TRAKT','ACCESS_TOKEN')
                        else:
                                print('Warning, no access token found. Authentification is required')
                        if config.has_option('TRAKT','REFRESH_TOKEN') and len(config.get('TRAKT','REFRESH_TOKEN')) != 0:
                                _trakt['refresh_token'] = config.get('TRAKT','REFRESH_TOKEN')
                        else:
                                print('Warning, no refresh token found. Authentification is required')
                        if config.has_option('TRAKT','BASEURL'):
                                _trakt['baseurl'] = config.get('TRAKT','BASEURL')
                        if config.has_option('SETTINGS','PROXY'):
                                _proxy['proxy'] = config.getboolean('SETTINGS','PROXY')
                        if _proxy['proxy'] and config.has_option('SETTINGS','PROXY_HOST') and config.has_option('SETTINGS','PROXY_PORT'):
                                _proxy['host'] = config.get('SETTINGS','PROXY_HOST')
                                _proxy['port'] = config.get('SETTINGS','PROXY_PORT')
                                _proxyDict['http'] = _proxy['host']+':'+_proxy['port']
                                _proxyDict['https'] = _proxy['host']+':'+_proxy['port']
                        return config
                except:
                        print("Error reading configuration file {0}".format(_configfile))
                        sys.exit(1)
        else:
                try:
                        print('%s file was not found!' % _configfile)
                        config = configparser.RawConfigParser()
                        config.add_section('TMDB')
                        config.set('TMDB', 'APIKEY', '')
                        config.set('TMDB', 'FILTER', '')
                        config.add_section('TRAKT')
                        config.set('TRAKT', 'CLIENT_ID', '')
                        config.set('TRAKT', 'CLIENT_SECRET', '')
                        config.set('TRAKT', 'ACCESS_TOKEN', '')
                        config.set('TRAKT', 'REFRESH_TOKEN', '')
                        config.set('TRAKT', 'BASEURL', 'https://api-v2launch.trakt.tv')
                        config.add_section('SETTINGS')
                        config.set('SETTINGS', 'PROXY', False)
                        config.set('SETTINGS', 'PROXY_HOST', 'https://127.0.0.1')
                        config.set('SETTINGS', 'PROXY_PORT', '3128')
                        with open(_configfile, 'w') as configfile:
                                config.write(configfile)
                                print("Default settings wrote to file {0}".format(_configfile))
                except:
                        print("Error writing configuration file {0}".format(_configfile))
                sys.exit(1)

def tmdb_api_discover(args):
        """TMDB API call to discover movie from the filter"""
        # https://developers.themoviedb.org/3/discover/movie-discover
        tmdb.API_KEY = _tmdb['apikey']
        discover = tmdb.Discover()
        if not _tmdb['filter']:
            kwargs = {  "page": 1,
                        "vote_average.gte": 6,
                        "primary_release_year": datetime.datetime.today().year,
                        "with_genres": 35,
                        "sort_by": "popularity.desc",
                        "include_adult": "false",
                        "include_video": "false"
                    }
        else:
            kwargs = json.loads(_tmdb['filter'])
        if args.verbose:
            print("TMDB filter {}".format(kwargs))
        if args.type == "movies":
            response = discover.movie(**kwargs)
        else:
            response = discover.tv(**kwargs)
        if args.verbose:
            print("TMDB fetched page {page} of {total} pages".format(total=response['total_pages'], page=response['page']))
        print("TMDB found {total} items".format(total=response['total_results']))
        results = response['results']
        while int(response['page']) < int(response['total_pages']):
            # Increment page
            kwargs['page'] = response['page']+1
            response = discover.movie(**kwargs)
            if args.verbose:
                print("TMDB fetched page {page} of {total} pages".format(total=response['total_pages'], page=response['page']))
            results += response['results']
        return results

def api_auth(options, config=None, refresh=False):
        """API call for authentification OAUTH"""
        values = None
        if refresh == False:
            print("Manual authentification. Open the link in a browser and paste the pincode when prompted")
            print(("https://trakt.tv/oauth/authorize?response_type=code&"
                  "client_id={0}&redirect_uri=urn:ietf:wg:oauth:2.0:oob".format(
                      _trakt["client_id"])))
            pincode = str(input('Input PIN:'))
            # Exchange code for access_token
            # First run
            values = {
                "code": pincode,
                "client_id": _trakt["client_id"],
                "client_secret": _trakt["client_secret"],
                "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                "grant_type": "authorization_code"
            }
        else:
            # Exchange refresh_token for access_token
            # Refresh token
            values = {
                "refresh_token": _trakt['refresh_token'],
                "client_id": _trakt['client_id'],
                "client_secret": _trakt["client_secret"],
                "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                "grant_type": "refresh_token"
            }

        url = _trakt['baseurl'] + '/oauth/token'
        request = requests.post(url, data=values)
        if request.status_code == 200:
            response = request.json()
            #pp.pprint(response)
            print("Authentication successful")
            _headers['Authorization'] = 'Bearer ' + response["access_token"]
            _headers['trakt-api-key'] = _trakt['client_id']
            # Update configuration file
            if config:
                config.set('TRAKT', 'ACCESS_TOKEN', response["access_token"])
                config.set('TRAKT', 'REFRESH_TOKEN', response["refresh_token"])
                with open(options.config, 'w') as configfile:
                    config.write(configfile)
                    print('Saved as "access_token" in file {0}: {1}'.format(options.config, response["access_token"]))
                    print('Saved as "refresh_token" in file {0}: {1}'.format(options.config, response["refresh_token"]))
        else:
            print("Sorry, the authentication was not successful.")
            pp.pprint(request)
            sys.exit(1)

def api_user(args):
        """API call for settings / Get username"""
        url = _trakt['baseurl'] + '/users/settings'
        if args.verbose:
            print(url)
        if _proxy['proxy']:
            r = requests.get(url, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
        else:
            r = requests.get(url, headers=_headers, timeout=(5, 60))
        #pp.pprint(r.headers)
        if r.status_code != 200:
            print("Error fetching user settings: {status} [{text}]".format(
                    status=r.status_code, text=r.text))
            return None
        else:
            return json.loads(r.text)

def api_get_lists(args):
        """API call for Sync / Get list for username"""
        url = _trakt['baseurl'] + '/users/{username}/lists'.format(username=_trakt['username'])
        if args.verbose:
            print(url)
        if _proxy['proxy']:
            r = requests.get(url, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
        else:
            r = requests.get(url, headers=_headers, timeout=(5, 60))
        #pp.pprint(r.headers)
        if r.status_code != 200:
            print("Error fetching Get {list}: {status} [{text}]".format(
                    list=args.list, status=r.status_code, text=r.text))
            return None
        else:
            return json.loads(r.text)

def api_get_items_from_list(args):
        """API call for Sync / Get items in list for username"""
        url = _trakt['baseurl'] + '/users/{username}/lists/{id}/items/{type}'.format(
                                username=_trakt['username'], id=args.list, type=args.type)
        if args.verbose:
            print(url)
        if _proxy['proxy']:
            r = requests.get(url, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
        else:
            r = requests.get(url, headers=_headers, timeout=(5, 60))
        #pp.pprint(r.headers)
        if r.status_code != 200:
            print("Error fetching Get {list}: {status} [{text}]".format(
                    list=args.list, status=r.status_code, text=r.text))
            return None
        else:
            return json.loads(r.text)

def api_add_items_to_list(args, import_data):
        """API call for Sync / Add items to custom user list"""
        # 429 [AUTHED_API_POST_LIMIT rate limit exceeded. Please wait 1 seconds then retry your request.]
        # Rate limit for API
        time.sleep(1)
        url = _trakt['baseurl'] + '/users/{username}/lists/{id}/items'.format(
                                username=_trakt['username'], id=args.list)
        values = { args.type : import_data }
        json_data = json.dumps(values)
        if args.verbose:
            print("Sending to URL: {0}".format(url))
            pp.pprint(json_data)
        if _proxy['proxy']:
            r = requests.post(url, data=json_data, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
        else:
            r = requests.post(url, data=json_data, headers=_headers, timeout=(5, 60))
        if r.status_code != 201:
            print("Error Adding items to {list}: {status} [{text}]".format(
                    list=args.list, status=r.status_code, text=r.text))
            return None
        else:
            return json.loads(r.text)

def api_remove_from_list(args, remove_data):
        """API call for Sync / Remove from to custom user list"""
        url = _trakt['baseurl'] + '/users/{username}/lists/{id}/items/remove'.format(
                                username=_trakt['username'], id=args.list)
        if args.type == 'episodes':
            values = { 'shows' : remove_data }
        else:
            values = { args.type : remove_data }
        json_data = json.dumps(values)
        if args.verbose:
            print(url)
            pp.pprint(json_data)
        if _proxy['proxy']:
            r = requests.post(url, data=json_data, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
        else:
            r = requests.post(url, data=json_data, headers=_headers, timeout=(5, 60))
        if r.status_code != 200:
            print("Error removing items from {list}: {status} [{text}]".format(
                    list=args.list, status=r.status_code, text=r.text))
            return None
        else:
            return json.loads(r.text)

def api_get_history_list(args, page):
        """API call for Sync / Get list by type"""
        url = _trakt['baseurl'] + '/sync/history/{type}?page={page}&limit={limit}'.format(
                            type=args.type, page=page, limit=1000)
        if args.verbose:
            print(url)
        if _proxy['proxy']:
            r = requests.get(url, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
        else:
            r = requests.get(url, headers=_headers, timeout=(5, 60))
        #pp.pprint(r.headers)
        if r.status_code != 200:
            print("Error fetching Get {list}: {status} [{text}]".format(
                    list=args.list, status=r.status_code, text=r.text))
            return None
        else:
            global response_arr
            response_arr += json.loads(r.text)
        if 'X-Pagination-Page-Count'in r.headers and r.headers['X-Pagination-Page-Count']:
            print("Fetched page {page} of {PageCount} pages for history list".format(
                    page=page, PageCount=r.headers['X-Pagination-Page-Count']))
            if page != int(r.headers['X-Pagination-Page-Count']):
                api_get_history_list(args, page+1)

        return response_arr

def cleanup_list(args):
        """Empty list prior to import"""
        export_data = api_get_items_from_list(args)
        #pp.pprint(export_data)
        if export_data:
            print("Found {len} items from the '{list}' list for user '{username}'".format(
                len=len(export_data), list=args.list, username=_trakt['username']))
        else:
            print("Warning, Cleanup no '{type}' items return from the '{list}' list for user '{username}'".format(
                type=args.type, list=args.list, username=_trakt['username']))
            return

        results = {'sentids' : 0, 'deleted' : 0, 'not_found' : 0}
        to_remove = []
        for data in export_data:
            to_remove.append({'ids': data[args.type[:-1]]['ids']})
            if len(to_remove) >= 10:
                results['sentids'] += len(to_remove)
                result = api_remove_from_list(args, to_remove)
                if result:
                    print("Result: {0}".format(result))
                    if 'deleted' in result and result['deleted']:
                        results['deleted'] += result['deleted'][args.type]
                    if 'not_found' in result and result['not_found']:
                        results['not_found'] += len(result['not_found'][args.type])
                to_remove = []
        # Remove the rest
        if len(to_remove) > 0:
            #print pp.pprint(data)
            results['sentids'] += len(to_remove)
            result = api_remove_from_list(args, to_remove)
            if result:
                print("Result: {0}".format(result))
                if 'deleted' in result and result['deleted']:
                    results['deleted'] += result['deleted'][args.type]
                if 'not_found' in result and result['not_found']:
                    results['not_found'] += len(result['not_found'][args.type])
        print("Overall cleanup {sent} {type}, results deleted:{deleted}, not_found:{not_found}".format(
            sent=results['sentids'], type=args.type, deleted=results['deleted'], not_found=results['not_found']))

def main():
        """
        Main program loop
        * Read configuration file and validate
        * Find trakt.tv custom user list
        * Fetch watched in trakt.tv history list
        * Cleanup list from Trakt.tv
        * Get data from TMDB
        * Reduce TMDB list to only my langauge fr, en, es and if need watched
        * Inject data into Trakt.tv
        """
        ## Parse inputs if any
        parser = argparse.ArgumentParser(description=desc, epilog=epilog)
        parser.add_argument('-v', action='version', version='%(prog)s 0.3')
        parser.add_argument('-c', '--config',
                      help='allow to overwrite default config filename, default %(default)s',
                      action='store', type=str, dest='config', default='config.ini')
        parser.add_argument('-t', '--type',
                      help='allow to overwrite type, default %(default)s',
                      choices=['movies', 'shows'], dest='type', default='movies')
        parser.add_argument('-l', '--list',
                      help='specify a trakt.tv user list via is slug name',
                      action='store', type=str, dest='list', default='comedy')
        parser.add_argument('-s', '--seen',
                      help='mark as seen, default %(default)s. Use specific time if provided, falback time: "2016-01-01T00:00:00.000Z"',
                      nargs='?', const='2016-01-01T00:00:00.000Z',
                      action='store', type=str, dest='seen', default=False)
        parser.add_argument('-C', '--clean',
                      help='empty trakt.tv list prior to import, default %(default)s',
                      default=False, action='store_true', dest='clean')
        parser.add_argument('-d', '--dryrun',
                      help='do not update the account, default %(default)s',
                      default=False, action='store_true', dest='dryrun')
        parser.add_argument('--skipwatched',
                      help='skip watched items from trakt.tv, default %(default)s',
                      default=True, action='store_true', dest='skipwatched')
        parser.add_argument('-V', '--verbose',
                      help='print additional verbose information, default %(default)s',
                      default=True, action='store_true', dest='verbose')
        args = parser.parse_args()

        ## Display debug information
        if args.verbose:
            print("Args: %s" % args)

        if args.seen:
            try:
                datetime.datetime.strptime(args.seen, '%Y-%m-%dT%H:%M:%S.000Z')
            except:
                sys.exit("Error, invalid format, it's must be UTC datetime, eg: '2016-01-01T00:00:00.000Z'")

        ## Read configuration and validate
        config = read_config(args)

        ## Display debug information
        if args.verbose:
            print("Config: {}".format(config))

        ## Trakt auth
        if not _trakt['access_token'] and not _trakt['refresh_token'] and \
            _trakt['client_id'] and _trakt['client_secret']:
            print("Trakt, no token found in config file, requesting authorization_code")
            api_auth(args, config, False)
        elif _trakt['access_token'] and _trakt['refresh_token'] and \
            _trakt['client_id'] and _trakt['client_secret']:
            ## Check token validity
            ## Trakt access_token is valid for 3 months before it needs to be refreshed again.
            today = datetime.datetime.today()
            modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(args.config))
            duration = today - modified_date
            if duration and duration.seconds < 2592000:
                # 30*24*60*60 = 2592000
                print("Trakt, skipped access token refresh, token is less than 30 days, only %s" % duration)
                _headers['Authorization'] = 'Bearer ' + _trakt["access_token"]
                _headers['trakt-api-key'] = _trakt['client_id']
            else:
                ## Exchange refresh_token for access_token
                print("Trakt, access token refresh, token is more than 30 days, token is %s old" % duration)
                api_auth(args, config, True)
        else:
            print("No valid authentication parameters found in config file")
            sys.exit(1)

        if not _headers['Authorization'] and not _headers['trakt-api-key']:
            print("No valid Authorization header")
            sys.exit(1)

        ## Display debug information
        if args.verbose:
            print("API Trakt: {}".format(_trakt))
            print("Authorization header: {}".format(_headers['Authorization']))
            print("trakt-api-key header: {}".format(_headers['trakt-api-key']))
            print("API TMDB: {}".format(_tmdb))

        # Find trakt.tv username/slug
        if not _trakt['username']:
            user_settings = api_user(args)
            print("User settings: {}".format(user_settings))
            if user_settings and user_settings['user'] and \
                user_settings['user']['ids'] and user_settings['user']['ids']['slug']:
                _trakt['username'] = user_settings['user']['ids']['slug']
                print("Got slug username '{0}'".format(_trakt['username']))
            else:
                print("Error, trakt.tv user slug not found for user")
                sys.exit(1)

        # Find trakt.tv custom user list
        if args.list:
            print("Fetching custom list from trakt.tv for user '{0}'".format(_trakt['username']))
            slug_list = []
            track_lists = api_get_lists(args)
            for track_list in track_lists:
                print("List slug '{0}' name '{1}'".format(track_list['ids']['slug'], track_list['name']))
                slug_list.append(track_list['ids']['slug'])
            #pp.pprint(slug_list)
            if args.list in slug_list:
                print("Found trakt.tv list slug '{0}'".format(args.list))
            else:
                print("Error, trakt.tv list slug '{0}' not found for user '{1}'".format(
                                                        args.list, _trakt['username']))
                sys.exit(1)

        # Fetch watched in trakt.tv history list
        if args.skipwatched:
            watched = []
            print("Fetching history list from trakt.tv for user '{0}'".format(_trakt['username']))
            history_data = api_get_history_list(args, 1)
            for data in history_data:
                watched.append(int(data[args.type[:-1]]['ids']['tmdb']))
            print("Found {len} items in history list from trakt.tv for user '{username}'".format(
                                len=len(watched), username=_trakt['username']))

        # Empty trakt.tv list prior to import
        if args.clean and not args.dryrun:
            cleanup_list(args)
        else:
            print("Dryrun, skip cleanup trakt.tv list slug '{0}' for user '{1}'".format(
                                                        args.list, _trakt['username']))

        # Get discover data from TMDB
        print("Fetching {type} from TMDB".format(type=args.type))
        discover_data = tmdb_api_discover(args)
        if discover_data:
            print("Found {len} {type} from the TMDB discover".format(len=len(discover_data), type=args.type))
        else:
            print("Error, no {type} return from the TMDB discover".format(type=args.type))
            sys.exit(1)

        # Reduce to only my language fr, en, es and if need watched
        skip = 0
        new_discover_data = []
        for movie in discover_data:
            if movie["original_language"] != "en" and \
                movie["original_language"] != "es" and \
                movie["original_language"] != "fr":
                    print("Skip language {lang} movie '{title}'".format(title=movie['original_title'].encode('utf-8'),
                                                                    lang=movie['original_language']))
                    skip += 1
                    continue
            if args.skipwatched and watched and (movie['id'] in watched):
                print("Skip watched movie '{title}' ".format(title=movie['original_title'].encode('utf-8')))
                skip += 1
                continue
            new_discover_data.append(movie)
        print("Filter, removed {0} movies and reduce to {1} out of {2} movies from the TMDB discover".format(
                                            skip, len(new_discover_data), len(discover_data)))
        discover_data = new_discover_data

        # if discover data generate the list into trakt format
        data = []
        results = {'sentids' : 0, 'added' : 0, 'existing' : 0, 'not_found' : 0}
        if discover_data:
            print("Found {0} items to import in trakt.tv list slug '{1}' for user '{2}'".format(
                                            len(discover_data), args.list, _trakt['username']))
            for discover in discover_data:
                if discover['id']:
                    if args.seen:
                        data.append({'ids':{'tmdb': discover['id']}, 'watched_at': args.seen})
                    else:
                        data.append({'ids':{'tmdb': discover['id']}})
                    # Import batch of 10 IDs
                    if len(data) >= 10:
                        results['sentids'] += len(data)
                        if not args.dryrun:
                            result = api_add_items_to_list(args, data)
                            if result:
                                print("Result: {0}".format(result))
                                if 'added' in result and result['added']:
                                    results['added'] += result['added'][args.type]
                                if 'existing' in result and result['existing']:
                                    results['existing'] += result['existing'][args.type]
                                if 'not_found' in result and result['not_found']:
                                    results['not_found'] += len(result['not_found'][args.type])
                        else:
                            print("Dryrun, skip import trakt.tv items into list slug '{0}' for user '{1}'".format(
                                                        args.list, _trakt['username']))
                        data = []
            # Import the rest
            if len(data) > 0:
                #print pp.pprint(data)
                results['sentids'] += len(data)
                if not args.dryrun:
                    result = api_add_items_to_list(args, data)
                    if result:
                        print("Result: {0}".format(result))
                        if 'added' in result and result['added']:
                            results['added'] += result['added'][args.type]
                        if 'existing' in result and result['existing']:
                            results['existing'] += result['existing'][args.type]
                        if 'not_found' in result and result['not_found']:
                            results['not_found'] += len(result['not_found'][args.type])
                else:
                    print("Dryrun, skip import trakt.tv items into list slug '{0}' for user '{1}'".format(
                                                        args.list, _trakt['username']))

        print("Overall imported {sent} {type}, results added:{added}, existing:{existing}, not_found:{not_found}".format(
                sent=results['sentids'], type=args.type, added=results['added'], 
                existing=results['existing'], not_found=results['not_found']))

if __name__ == '__main__':
        main()
