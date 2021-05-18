#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) Copyright 2016-2021 xbgmsharp <xbgmsharp@gmail.com>
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
from datetime import datetime
import collections
import pprint

import helpers

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
        'username'      :       ''  # username
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

def read_csv(options):
        """Read CSV of Movies or TVShows IDs and return a dict"""
        reader = csv.DictReader(options.input, delimiter=',')
        print("Done reading " + _trakt['config_path'])
        return list(reader)

# def api_search_by_id(options, id):
#         """API call for Search / ID Lookup / Get ID lookup results"""
#         url = _trakt['baseurl'] + '/search?id_type={0}&id={1}'.format(options.format, id)
#         if options.verbose:
#             print(url)
#         if _proxy['proxy']:
#             r = requests.get(url, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
#         else:
#             r = requests.get(url, headers=_headers, timeout=(5, 60))
#         if r.status_code != 200:
#             print("Error Get ID lookup results: {0} [{1}]".format(r.status_code, r.text))
#             return None
#         else:
#             return json.loads(r.text)

# @limits(calls=1, period=1)
def api_add_to_list(options, import_data):
        """API call for Sync / Add items to list"""
        
        # Rate limit for API 
        time.sleep(1)
        if options.userlist:
            url = _trakt['baseurl'] + '/users/{username}/lists/{list_id}/items'.format(username=_trakt['username'], list_id=options.listid)
        else:
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

# TODO: Not sure if removing from list works 
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

# TODO: Not sure if cleaning up list works 
def cleanup_list(options):
        """Empty list prior to import"""
        if options.userlist: 
            export_data = helpers.api_get_userlist(_trakt, _headers, _proxyDict, options, 1)
        else:
            export_data = helpers.api_get_list(_trakt, _headers, _proxyDict, options, 1)
        print(export_data)
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
        list_group = parser.add_mutually_exclusive_group(required=True)
        time_group = parser.add_mutually_exclusive_group(required=False)
        parser.add_argument('-v', action='version', version='%(prog)s 0.1')
        parser.add_argument('-c', '--config',
                      help='allow to overwrite default config filename, default %(default)s',
                      action='store', type=str, dest='config', default='config.ini')
        parser.add_argument('-i', '--input',
                      help='CSV file to import, default %(default)s',
                      nargs='?', type=argparse.FileType('r'), default=None, required=True)
        time_group.add_argument('-w', '--watched_at',
                      help='import watched_at date from CSV, the format must be UTC datetime. NOTE: Only works with history, not with watchlist/userlist. default %(default)s',
                      default=False, action='store_true', dest='watched_at')
        now = datetime.now()
        time_group.add_argument('-s', '--seen',
                      help='use custom time for watched_at if importing to history, default %(default)s. NOTE: Only works with history, not with watchlist/userlist. Use specific time if provided, default is current time.',
                      nargs='?', const=now.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                      action='store', type=str, dest='seen', default=False)
        parser.add_argument('-f', '--format',
                      help='allow to overwrite default ID type format, default %(default)s',
                      choices=['imdb', 'tmdb', 'tvdb', 'tvrage', 'trakt'], dest='format', default='trakt')
        parser.add_argument('-t', '--type',
                      help='allow to overwrite type, default %(default)s',
                      choices=['movies', 'shows', 'episodes'], dest='type', default='movies')
        # TODO: I would be surprised if importing to collection works. 
        list_group.add_argument('-l', '--list',
                      help='allow to overwrite default list, default %(default)s',
                      choices=['watchlist', 'collection', 'history'], dest='list', default='watchlist')
        list_group.add_argument('-u', '--userlist',
                help='allow to add item(s) to a user custom list, default %(default)s',
                dest='userlist', default=False, action='store_true')
        parser.add_argument('-C', '--clean',
                      help='empty list prior to import, default %(default)s',
                      default=False, action='store_true', dest='clean')
        #parser.add_argument('-d', '--dryrun',
        #              help='do not update the account, default %(default)s',
        #              default=True, action='store_true', dest='dryrun')
        parser.add_argument('-V', '--verbose',
                      help='print additional verbose information, default %(default)s',
                      default=False, action='store_true', dest='verbose')
        options = parser.parse_args()

        # Display debug information
        if options.verbose:
            print("Options: %s" % options)

        if options.seen and options.list != "history":
            print("Error, you can only mark seen {0} when adding into the history list".format(options.type))
            sys.exit(1)

        if options.seen:
            try:
                datetime.strptime(options.seen, '%Y-%m-%dT%H:%M:%S.000Z')
            except:
                sys.exit("Error, invalid format, it's must be UTC datetime, eg: '2016-01-01T00:00:00.000Z'")

        ## Read configuration and validate
        helpers.read_config(_trakt, options)

        ## Try refreshing to get new access token. If it doesn't work, user needs to authenticate again.
        helpers.api_auth_refresh(_trakt, _headers, options)

        # Display debug information
        if options.verbose:
            print("API Trakt: {}".format(_trakt))
            print("Authorization header: {}".format(_headers['Authorization']))
        
        # Handle userlist
        if options.userlist:
            print(_trakt['access_token'])
            export_data = helpers.api_get_userlists(_trakt, _headers, _proxyDict, options, 1)
            if export_data:
                print("")
                print("Found {0} user list(s)".format(len(export_data)))
                print("")
                #pp.pprint(export_data)
                print("id       | name")
                for data in export_data:
                    print("{id} | {name}".format(name=data['name'], id = data['ids']['trakt']))
                    #print("{id} | {name} | {items}".format(
                    #       name=data['name'], id=data['ids']['trakt'], items=data['item_count'], own=data['user']['username']))
                print("")
                print("Type in the id matching with the name of the list you want to import item(s) to.")
                options.listid = str(input('Input: '))
                print("Importing to {username}'s user list with id: {id}, name: '{name}'".format(username=data['user']['username'], id=data['ids']['trakt'], name=data['name']))
                response_arr = []
            else:
                print("Error, no user lists found")
                sys.exit(1)
        # else:
        #     export_data = helpers.api_get_list(_trakt, _headers, _proxyDict, options, 1)
        #     if not export_data:
        #         print("Error, no item(s) found for {type} from {list}".format(
        #             type=options.type, list=options.list))
        #         sys.exit(1)

        # Empty list prior to import
        if options.clean:
            cleanup_list(options)

        # Read CSV list of IDs
        read_ids = read_csv(options)

        # if IDs make the list into trakt format
        data = []
        results = {'sentids' : 0, 'added' : 0, 'existing' : 0, 'not_found' : 0}

        if options.list == 'history':
            options.time_key = 'watched_at'
        elif options.list == 'watchlist':
            options.time_key = 'listed_at'
        elif options.list == 'collection':
            options.time_key = 'collected_at'
        elif options.userlist != None:
            options.time_key = 'listed_at'

        if read_ids:
            print("Found {0} items to import".format(len(read_ids)))

            for myid in read_ids:
                # If id (row) exists and is not blank (has a format)
                if myid and not options.format in myid:
                    print("Error, myid does not contain format " + options.format)
                    sys.exit(1)
                if myid and myid[options.format]:
                    # Record time format in csv we're importing from. 
                    # NOTE: Trakt API does not allow for custom times for listed_at and collected_at.
                    # Therefore, options.time_key doesn't do anything for lists other than history.
                    # However, this allows for any type of list to be imported in to default lists. 
                    if 'watched_at' in myid: 
                        options.csv_time = 'watched_at'
                    elif 'listed_at' in myid:
                        options.csv_time = 'listed_at'
                    elif 'collected_at' in myid:
                        options.csv_time = 'collected_at'
                    else:
                        options.csv_time = None
                    if options.verbose:
                        pp.pprint(myid)
                    row_title = "" 
                    row_time = "" 
                    if options.seen:
                        row_time = options.seen 
                    elif options.csv_time: 
                        row_time = myid[options.csv_time]
                    # If format is not "imdb" it must be cast to an integer
                    if not options.format == "imdb" and not myid[options.format].startswith('tt'):
                        myid[options.format] = int(myid[options.format])
                    if (options.type == "movies" or options.type == "shows"):
                        row_title = "title: " + myid['title']
                        data.append({'ids':{options.format : myid[options.format]}, options.time_key: row_time})
                    elif options.type == "episodes":
                        row_title = "title: " + myid['show_title'] + ", episode_title: " + myid['episode_title']
                        data.append({'ids':{options.format : myid[options.format]}, options.time_key: row_time})
                    else:
                        data.append({'ids':{options.format : myid[options.format]}})
                    if options.csv_time:
                        print("Importing record, {title}, id: {id}, {csv_time}: {time}".format(title=row_title, id=myid[options.format], csv_time=options.csv_time, time=row_time))
                    else:
                        print("Importing record, {title}, id: {id}, no time recorded in csv file".format(title=row_title, id=myid[options.format]))
                    # Import batch of 10 IDs
                    if len(data) >= 10:
                        #pp.pprint(json.dumps(data))
                        results['sentids'] += len(data)
                        result = api_add_to_list(options, data)
                        if result:
                            # print("Result: {0}".format(result))
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
                    # pp.pprint("Result: {0}".format(result))
                    if 'added' in result and result['added']:
                        results['added'] += result['added'][options.type]
                    if 'existing' in result and result['existing']:
                        results['existing'] += result['existing'][options.type]
                    if 'not_found' in result and result['not_found']:
                        results['not_found'] += len(result['not_found'][options.type])
        else:
            # TODO: Read STDIN to ID
            print("No items found, nothing to do.")
            sys.exit(0)

        print("Overall imported {sent} {type}, results added:{added}, existing:{existing}, not_found:{not_found}".format(
                sent=results['sentids'], type=options.type, added=results['added'], 
                existing=results['existing'], not_found=results['not_found']))

if __name__ == '__main__':
        main()
