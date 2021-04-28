#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) Copyright 2016-2020 xbgmsharp <xbgmsharp@gmail.com>
#
# Purpose:
# Import Movies or TVShows IDs into Trakt.tv
#
# Requirement on Ubuntu/Debian Linux system
# apt-get install python3-dateutil python3-simplejson python3-requests python3-openssl jq
#
# Requirement on Windows on Python 3
# C:\Python3\Scripts\easy_install3.exe simplejson requests
#

import sys, os
# https://urllib3.readthedocs.org/en/latest/security.html#disabling-warnings
# http://quabr.com/27981545/surpress-insecurerequestwarning-unverified-https-request-is-being-made-in-pytho
# http://docs.python-requests.org/en/v2.4.3/user/advanced/#proxies
try:
        import simplejson as json
        import requests
        requests.packages.urllib3.disable_warnings()
        import csv
        #from ratelimit import limits
        import time
except:
        sys.exit("Please use your favorite method to install the following module requests and simplejson to use this script")

import argparse
import configparser
import datetime
import collections
import pprint

pp = pprint.PrettyPrinter(indent=4)

desc="""This program import Movies or TVShows IDs into Trakt.tv."""

epilog="""Read a list of ID from 'imdb', 'tmdb', 'tvdb' or 'tvrage' or 'trakt'.
Import them into a list in Trakt.tv, mark as seen if need."""

_trakt = {
        'client_id'     :       '', # Auth details for trakt API
        'client_secret' :       '', # Auth details for trakt API
        'access_token'  :       '', # Auth details for trakt API
        'refresh_token' :       '', # Auth details for trakt API
        'baseurl'       :       'https://api.trakt.tv', # Sandbox environment https://api-staging.trakt.tv,
        'config_parser' :       '', # configparser.ConfigParser object 
        'config_path'   :       '', # path of config file 
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

def read_config(options):
        """
        Read config file and if provided overwrite default values
        If no config file exist, create one with default values
        """
        global work_dir
        work_dir = ''
        if getattr(sys, 'frozen', False):
                work_dir = os.path.dirname(sys.executable)
        elif __file__:
                work_dir = os.path.dirname(__file__)
        _configfile = os.path.join(work_dir, options.config)
        if os.path.exists(options.config):
                _configfile = options.config
        if options.verbose:
                print("Config file: {0}".format(_configfile))
        # For recording configparser 
        config = "" 
        if os.path.exists(_configfile):
                try:
                        config = configparser.ConfigParser()
                        config.read(_configfile)
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
                except:
                        print("Error reading configuration file {0}".format(_configfile))
                        sys.exit(1)
        else:
                try:
                        print('%s file was not found!' % _configfile)
                        config = configparser.RawConfigParser()
                        config.add_section('TRAKT')
                        config.set('TRAKT', 'CLIENT_ID', '')
                        config.set('TRAKT', 'CLIENT_SECRET', '')
                        config.set('TRAKT', 'ACCESS_TOKEN', '')
                        config.set('TRAKT', 'REFRESH_TOKEN', '')
                        config.set('TRAKT', 'BASEURL', 'https://api.trakt.tv')
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
        _trakt['config_parser'] = config 
        _trakt['config_path'] = _configfile

def read_csv(options):
        """Read CSV of Movies or TVShows IDs and return a dict"""
        reader = csv.DictReader(options.input, delimiter=',')
        return list(reader)

def api_auth(options):
        """API call for authentification OAUTH"""
        print("Manual authentification. Open the link in a browser and paste the pincode when prompted")
        print(("https://trakt.tv/oauth/authorize?response_type=code&"
              "client_id={0}&redirect_uri=urn:ietf:wg:oauth:2.0:oob".format(
                  _trakt["client_id"])))
        pincode = str(input('Input:'))
        url = _trakt['baseurl'] + '/oauth/token'
        values = {
            "code": pincode,
            "client_id": _trakt["client_id"],
            "client_secret": _trakt["client_secret"],
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "grant_type": "authorization_code"
        }

        request = requests.post(url, data=values)
        response = request.json()
        _headers['Authorization'] = 'Bearer ' + response["access_token"]
        _headers['trakt-api-key'] = _trakt['client_id']
        config = _trakt['config_parser']
        config.set('TRAKT', 'ACCESS_TOKEN', response["access_token"])
        config.set('TRAKT', 'REFRESH_TOKEN', response["refresh_token"])
        with open(options.config, 'w') as configfile:
            config.write(configfile)
            print('Saved as "access_token" in file {0}: {1}'.format(options.config, response["access_token"]))
            print('Saved as "refresh_token" in file {0}: {1}'.format(options.config, response["refresh_token"]))

def api_search_by_id(options, id):
        """API call for Search / ID Lookup / Get ID lookup results"""
        url = _trakt['baseurl'] + '/search?id_type={0}&id={1}'.format(options.format, id)
        if options.verbose:
            print(url)
        if _proxy['proxy']:
            r = requests.get(url, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
        else:
            r = requests.get(url, headers=_headers, timeout=(5, 60))
        if r.status_code != 200:
            print("Error Get ID lookup results: {0} [{1}]".format(r.status_code, r.text))
            return None
        else:
            return json.loads(r.text)

def api_get_list(options, page):
        """API call for Sync / Get list by type"""
        url = _trakt['baseurl'] + '/sync/{list}/{type}?page={page}&limit={limit}'.format(
                            list=options.list, type=options.type, page=page, limit=1000)
        if options.verbose:
            print(url)
        if _proxy['proxy']:
            r = requests.get(url, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
        else:
            r = requests.get(url, headers=_headers, timeout=(5, 60))
        #pp.pprint(r.headers)
        if r.status_code != 200:
            print("Error fetching Get {list}: {status} [{text}]".format(
                    list=options.list, status=r.status_code, text=r.text))
            return None
        else:
            global response_arr
            response_arr += json.loads(r.text)
        if 'X-Pagination-Page-Count'in r.headers and r.headers['X-Pagination-Page-Count']:
            print("Fetched page {page} of {PageCount} pages for {list} list".format(
                    page=page, PageCount=r.headers['X-Pagination-Page-Count'], list=options.list))
            if page != int(r.headers['X-Pagination-Page-Count']):
                api_get_list(options, page+1)

        return response_arr

# @limits(calls=1, period=1)
def api_add_to_list(options, import_data):
        """API call for Sync / Add items to list"""
        
        # Rate limit for API 
        time.sleep(1)
        url = _trakt['baseurl'] + '/sync/{list}'.format(list=options.list)
        #values = '{ "movies": [ { "ids": { "imdb": "tt0000111" } }, { "ids": { , "imdb": "tt1502712" } } ] }'
        #values = '{ "movies": [ { "watched_at": "2014-01-01T00:00:00.000Z", "ids": { "imdb": "tt0000111" } }, { "watched_at": "2013-01-01T00:00:00.000Z", "ids": { "imdb": "tt1502712" } } ] }'
        if options.type == 'episodes':
            values = { 'episodes' : import_data }
        else:
            values = { options.type : import_data }

        json_data = json.dumps(values)
        if options.verbose:
            print("Sending to URL: {0}".format(url))
            pp.pprint(json_data)

        if _proxy['proxy']:
            #print(url)
            r = requests.post(url, data=json_data, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
        else:
            r = requests.post(url, data=json_data, headers=_headers, timeout=(5, 60))

        if r.status_code != 201:
            print("Error Adding items to {list}: {status} [{text}]".format(
                    list=options.list, status=r.status_code, text=r.text))
            return None
        else:
            return json.loads(r.text)

def api_remove_from_list(options, remove_data):
        """API call for Sync / Remove from list"""
        url = _trakt['baseurl'] + '/sync/{list}/remove'.format(list=options.list)
        if options.type == 'episodes':
            values = { 'shows' : remove_data }
        else:
            values = { options.type : remove_data }
        json_data = json.dumps(values)
        if options.verbose:
            print(url)
            pp.pprint(json_data)
        if _proxy['proxy']:
            r = requests.post(url, data=json_data, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
        else:
            r = requests.post(url, data=json_data, headers=_headers, timeout=(5, 60))
        if r.status_code != 200:
            print("Error removing items from {list}: {status} [{text}]".format(
                    list=options.list, status=r.status_code, text=r.text))
            return None
        else:
            return json.loads(r.text)

def cleanup_list(options):
        """Empty list prior to import"""
        export_data = api_get_list(options, 1)
        if export_data:
            print("Found {0} Item-Count".format(len(export_data)))
        else:
            print("Error, Cleanup no item return for {type} from the {list} list".format(
                type=options.type, list=options.list))
            sys.exit(1)
        results = {'sentids' : 0, 'deleted' : 0, 'not_found' : 0}
        to_remove = []
        for data in export_data:
            to_remove.append({'ids': data[options.type[:-1]]['ids']})
            if len(to_remove) >= 10:
                results['sentids'] += len(to_remove)
                result = api_remove_from_list(options, to_remove)
                if result:
                    print("Result: {0}".format(result))
                    if 'deleted' in result and result['deleted']:
                        results['deleted'] += result['deleted'][options.type]
                    if 'not_found' in result and result['not_found']:
                        results['not_found'] += len(result['not_found'][options.type])
                to_remove = []
        # Remove the rest
        if len(to_remove) > 0:
            #pp.pprint(data)
            results['sentids'] += len(to_remove)
            result = api_remove_from_list(options, to_remove)
            if result:
                print("Result: {0}".format(result))
                if 'deleted' in result and result['deleted']:
                    results['deleted'] += result['deleted'][options.type]
                if 'not_found' in result and result['not_found']:
                    results['not_found'] += len(result['not_found'][options.type])
        print("Overall cleanup {sent} {type}, results deleted:{deleted}, not_found:{not_found}".format(
            sent=results['sentids'], type=options.type, deleted=results['deleted'], not_found=results['not_found']))

def main():
        """
        Main program loop
        * Read configuration file and validate
        * Read CSV file
        * Authenticate if require
        * Cleanup list from Trakt.tv
        * Inject data into Trakt.tv
        """
        # Parse inputs if any
        parser = argparse.ArgumentParser(description=desc, epilog=epilog)
        parser.add_argument('-v', action='version', version='%(prog)s 0.1')
        parser.add_argument('-c', '--config',
                      help='allow to overwrite default config filename, default %(default)s',
                      action='store', type=str, dest='config', default='config.ini')
        parser.add_argument('-i', '--input',
                      help='CSV file to import, default %(default)s',
                      nargs='?', type=argparse.FileType('r'), default=None, required=True)
        parser.add_argument('-w', '--watched_at',
                      help='import watched_at date from CSV, it\'s must be UTC datetime, default %(default)s',
                      default=False, action='store_true', dest='watched_at')
        parser.add_argument('-f', '--format',
                      help='allow to overwrite default ID type format, default %(default)s',
                      choices=['imdb', 'tmdb', 'tvdb', 'tvrage', 'trakt'], dest='format', default='imdb')
        parser.add_argument('-t', '--type',
                      help='allow to overwrite type, default %(default)s',
                      choices=['movies', 'shows', 'episodes'], dest='type', default='movies')
        parser.add_argument('-l', '--list',
                      help='allow to overwrite default list, default %(default)s',
                      choices=['watchlist', 'collection', 'history'], dest='list', default='watchlist')
        parser.add_argument('-s', '--seen',
                      help='mark as seen, default %(default)s. Use specific time if provided, falback time: "2016-01-01T00:00:00.000Z"',
                      nargs='?', const='2016-01-01T00:00:00.000Z',
                      action='store', type=str, dest='seen', default=False)
        parser.add_argument('-C', '--clean',
                      help='empty list prior to import, default %(default)s',
                      default=False, action='store_true', dest='clean')
        #parser.add_argument('-d', '--dryrun',
        #              help='do not update the account, default %(default)s',
        #              default=True, action='store_true', dest='dryrun')
        parser.add_argument('-V', '--verbose',
                      help='print additional verbose information, default %(default)s',
                      default=True, action='store_true', dest='verbose')
        options = parser.parse_args()

        # Display debug information
        if options.verbose:
            print("Options: %s" % options)

        if options.seen and options.list != "history":
            print("Error, you can only mark seen {0} when adding into the history list".format(options.type))
            sys.exit(1)

        if options.seen:
            try:
                datetime.datetime.strptime(options.seen, '%Y-%m-%dT%H:%M:%S.000Z')
            except:
                sys.exit("Error, invalid format, it's must be UTC datetime, eg: '2016-01-01T00:00:00.000Z'")

        ## Read configuration and validate
        config = read_config(options)

        ## Try refreshing to get new access token. If it doesn't work, user needs to authenticate again.
        if _trakt['refresh_token']: 
            values = {
                    "refresh_token": _trakt['refresh_token'],
                    "client_id": _trakt['client_id'],
                    "client_secret": _trakt["client_secret"],
                    "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                    "grant_type": "refresh_token"
            }

            url = _trakt['baseurl'] + '/oauth/token'
            r = requests.post(url, data=values)
            print(r.status_code)
            if r.status_code == 200: 
                response = r.json()
                _trakt['access_token'] = response["access_token"]
                _trakt['refresh_token'] = response["refresh_token"]
                _headers['Authorization'] = 'Bearer ' + response["access_token"]
                _headers['trakt-api-key'] = _trakt['client_id']
                config = _trakt['config_parser']
                config.set('TRAKT', 'ACCESS_TOKEN', response["access_token"])
                config.set('TRAKT', 'REFRESH_TOKEN', response["refresh_token"])
                with open(options.config, 'w') as configfile:
                    config.write(configfile)
                    print('Saved as "access_token" in file {0}: {1}'.format(options.config, response["access_token"]))
                    print('Saved as "refresh_token" in file {0}: {1}'.format(options.config, response["refresh_token"]))
            else:
                print("Refreshing access_token failed. Get new refresh_token and access_token by manually authenticating again")
                api_auth(options) 
        else:   
            print("No refresh_token found in config file. Get new refresh_token and access_token by manually authenticating again")
            api_auth(options) 

        # Display debug information
        if options.verbose:
            print("API Trakt: {}".format(_trakt))
            print("Authorization header: {}".format(_headers['Authorization']))

        # Empty list prior to import
        if options.clean:
            cleanup_list(options)

        # Read CSV list of IDs
        read_ids = read_csv(options)

        # if IDs make the list into trakt format
        data = []
        results = {'sentids' : 0, 'added' : 0, 'existing' : 0, 'not_found' : 0}
        if read_ids:
            print("Found {0} items to import".format(len(read_ids)))

            for myid in read_ids:
                # If id (row) exists and is not blank (has a format)
                if myid and myid[options.format]:
                    #pp.pprint(myid)
                    # If format is not "imdb" it must be cast to an integer
                    if not options.format == "imdb" and not myid[options.format].startswith('tt'):
                        myid[options.format] = int(myid[options.format])
                    if (options.type == "movies" or options.type == "shows") and options.seen:
                        data.append({'ids':{options.format : myid[options.format]}, "watched_at": options.seen})
                    elif (options.type == "movies" or options.type == "shows") and options.watched_at:
                        data.append({'ids':{options.format : myid[options.format]}, "watched_at": myid["watched_at"]})
                    elif options.type == "episodes" and options.seen:
                        data.append({'ids':{options.format : myid[options.format]},"watched_at": options.seen})
                    elif options.type == "episodes" and options.watched_at:
                        data.append({'ids':{options.format : myid[options.format]},"watched_at": myid["watched_at"]})
                    else:
                        data.append({'ids':{options.format : myid[options.format]}})
                    # Import batch of 10 IDs
                    if len(data) >= 10:
                        #pp.pprint(json.dumps(data))
                        results['sentids'] += len(data)
                        result = api_add_to_list(options, data)
                        if result:
                            print("Result: {0}".format(result))
                            if 'added' in result and result['added']:
                                results['added'] += result['added'][options.type]
                            if 'existing' in result and result['existing']:
                                results['existing'] += result['existing'][options.type]
                            if 'not_found' in result and result['not_found']:
                                results['not_found'] += len(result['not_found'][options.type])
                        data = []
            # Import the rest
            if len(data) > 0:
                #pp.pprint(data)
                results['sentids'] += len(data)
                result = api_add_to_list(options, data)
                if result:
                    print("Result: {0}".format(result))
                    if 'added' in result and result['added']:
                        results['added'] += result['added'][options.type]
                    if 'existing' in result and result['existing']:
                        results['existing'] += result['existing'][options.type]
                    if 'not_found' in result and result['not_found']:
                        results['not_found'] += len(result['not_found'][options.type])
        else:
            # TODO Read STDIN to ID
            print("No items found, nothing to do.")
            sys.exit(0)

        print("Overall imported {sent} {type}, results added:{added}, existing:{existing}, not_found:{not_found}".format(
                sent=results['sentids'], type=options.type, added=results['added'], 
                existing=results['existing'], not_found=results['not_found']))

if __name__ == '__main__':
        main()
