#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) Copyright 2016-2021 xbgmsharp <xbgmsharp@gmail.com>
#
# Purpose:
# Export Movies or TVShows IDs from Trakt.tv
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
        import csv
        # TODO: Use pandas instead of csv for bigger csv handling
        #   import pandas as pd
except:
        sys.exit("Please use your favorite method to install the following module requests and simplejson to use this script")

import argparse
import configparser
import datetime
import collections
import pprint

import helpers

pp = pprint.PrettyPrinter(indent=4)

desc="""This program export Movies or TVShows IDs from Trakt.tv list."""

epilog="""Read a list from Trakt API.
Export them into a CSV file."""

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

def write_csv(options, results):
        """Write list output into a CSV file format
        """
        print("Writing to: {0}".format(options.output))
        # Write result CSV, works with windows now
        with open(options.output, 'w', encoding = 'utf-8', newline='') as fp:
                mycsv = csv.DictWriter(fp, fieldnames=list(results[0].keys()), quoting=csv.QUOTE_ALL)
                mycsv.writeheader()
                for row in results:
                    mycsv.writerow(row)
        fp.close()

# TODO: Not sure if removing from list works 
def api_remove_from_list(options, remove_data, is_id=False):
        """API call for Sync / Remove from list
        """
        url = _trakt['baseurl'] + '/sync/{list}/remove'.format(list=options.list)
        if options.type == 'episodes':
            values = { 'shows' : remove_data }
        elif not is_id:
            values = { options.type : remove_data }
        else:
            values = { 'ids' : remove_data }
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

def process_export_data(options, export_data): 
        """Process a set of data and create a csv"""
        if export_data:
            print("Found {count} {type}(s) from {list}".format(count=len(export_data), type=options.type, list=options.list))

        if options.list == 'history':
            options.time = 'watched_at'
        elif options.list == 'watchlist':
            options.time = 'listed_at'
        elif options.list == 'collection':
            options.time = 'collected_at'
        elif options.userlist != None:
            options.time = 'listed_at'

        export_csv = []
        find_dupids = []
        for data in export_data:
            # TODO: Add support for exporting movies and episodes to the same lsit
            #pp.pprint(data)
            # If movie or show 
            #if options.type[:-1] != "episode" and 'imdb' in data[options.type[:-1]]['ids']:
            #print(data)
            if data['type'] == 'movie':
                # Since exporting from Trakt, use Trakt id for finding dupids
                find_dupids.append(data[options.type[:-1]]['ids']['trakt'])
                export_csv.append({ 
                                    options.time : data[options.time],
                                    'title' : data[options.type[:-1]]['title'],
                                    'year' : data[options.type[:-1]]['year'],
                                    'trakt' : data[options.type[:-1]]['ids']['trakt'],
                                    'imdb' : data[options.type[:-1]]['ids']['imdb'],
                                    'tmdb' : data[options.type[:-1]]['ids']['tmdb']})
            # If episode
            elif data['type'] == 'episode':
                find_dupids.append(data[options.type[:-1]]['ids']['trakt'])
                if not data['episode']['title']: data['episode']['title'] = "no episode title"

                export_csv.append({ 
                                    options.time : data[options.time],
                                    'season' : data[options.type[:-1]]['season'],
                                    'episode' : data[options.type[:-1]]['number'],
                                    'episode_title' : data['episode']['title'],
                                    'show_title' : data['show']['title'],
                                    'trakt' : data[options.type[:-1]]['ids']['trakt'],
                                    'tvdb' : data[options.type[:-1]]['ids']['tvdb'],
                                    'tmdb' : data[options.type[:-1]]['ids']['tmdb']})
        # TODO: Don't know if options.clean works 
        ## Empty list after export
        if options.clean:
            cleanup_results = {'sentids' : 0, 'deleted' : 0, 'not_found' : 0}
            to_remove = []
            for data in export_data:
                # TODO add filter
                #if data[options.time] == "2012-01-01T00:00:00.000Z":
                to_remove.append({'ids': data[options.type[:-1]]['ids']})
                if len(to_remove) >= 10: # Remove by batch of 10
                    cleanup_results['sentids'] += len(to_remove)
                    result = api_remove_from_list(options, to_remove)
                    if result:
                        print("Result: {0}".format(result))
                        if 'deleted' in result and result['deleted']:
                            cleanup_results['deleted'] += result['deleted'][options.type]
                        if 'not_found' in result and result['not_found']:
                            cleanup_results['not_found'] += len(result['not_found'][options.type])
                    to_remove = []
            # Remove the rest
            if len(to_remove) > 0:
                #print pp.pprint(data)
                cleanup_results['sentids'] += len(to_remove)
                result = api_remove_from_list(options, to_remove)
                if result:
                    print("Result: {0}".format(result))
                    if 'deleted' in result and result['deleted']:
                        cleanup_results['deleted'] += result['deleted'][options.type]
                    if 'not_found' in result and result['not_found']:
                        cleanup_results['not_found'] += len(result['not_found'][options.type])
            print("Overall cleanup {sent} {type}, results deleted:{deleted}, not_found:{not_found}".format(
                sent=cleanup_results['sentids'], type=options.type, 
                deleted=cleanup_results['deleted'], not_found=cleanup_results['not_found']))

        ## Find duplicate and remove duplicate
        dup_ids = [item for item, count in list(collections.Counter(find_dupids).items()) if count > 1]
        print("Found {dups} duplicate(s) out of {total} {entry}(s)".format(
                    entry=options.type, dups=len(dup_ids), total=len(find_dupids)))
        # print all duplicates
        if options.verbose:
            for dupid in find_dupids:
                count = 0
                for myid in export_data:
                    if myid[options.type[:-1]]['ids']['trakt'] == dupid:
                        #print "{0} {1}".format(dupid, data['id'])
                        count += 1
                        if count > 1:
                            if 'watched_at' in myid: 
                                options.csv_time = 'watched_at'
                            elif 'listed_at' in myid:
                                options.csv_time = 'listed_at'
                            elif 'collected_at' in myid:
                                options.csv_time = 'collected_at'
                            else:
                                options.csv_time = None
                            #if options.verbose:
                                #pp.pprint(myid)
                            row_title = "" 
                            row_time = "" 
                            if options.csv_time: 
                                row_time = myid[options.csv_time]
                            # If format is not "imdb" it must be cast to an integer
                            if (options.type == "movies" or options.type == "shows"):
                                row_title = "title: " + myid[options.type[:-1]]['title']
                            elif options.type == "episodes":
                                row_title = "title: " + myid['show']['title'] + ", episode_title: " + myid['episode']['title']
                            else:
                                data.append({'ids':{'trakt' : myid['trakt']}})
                            if options.csv_time:
                                print("Duplicate record, {title}, id: {id}, {csv_time}: {time}".format(title=row_title, id=myid[options.type[:-1]]['ids']['trakt'], csv_time=options.csv_time, time=row_time))
                            else:
                                print("Duplciate record, {title}, id: {id}, no time recorded in csv file".format(title=row_title, id=myid[options.type[:-1]]['ids']['trakt']))

        if options.dup:
            if len(dup_ids) > 0:
                print(dup_ids)
            dup_results = {'sentids' : 0, 'deleted' : 0, 'not_found' : 0}
            to_remove = []
            for dupid in find_dupids:
                count = 0
                for data in export_data:
                    if data[options.type[:-1]]['ids']['trakt'] == dupid:
                        #print "{0} {1}".format(dupid, data['id'])
                        count += 1
                        if count > 1:
                            print("Removing {0} {1}".format(dupid, data['id']))
                            to_remove.append(data['id'])
                            dup_results['sentids'] += len(to_remove)
                            result = api_remove_from_list(options, to_remove, is_id=True)
                            if len(to_remove) >= 10: # Remove by batch of 10
                                if result:
                                    print("Result: {0}".format(result))
                                    if 'deleted' in result and result['deleted']:
                                        dup_results['deleted'] += result['deleted'][options.type]
                                    if 'not_found' in result and result['not_found']:
                                        dup_results['not_found'] += len(result['not_found'][options.type])
                                    to_remove = []
            ## Remove the rest
            if len(to_remove) > 0:
                dup_results['sentids'] += len(to_remove)
                result = api_remove_from_list(options, to_remove, is_id=True)
                if result:
                    print("Result: {0}".format(result))
                    if 'deleted' in result and result['deleted']:
                        dup_results['deleted'] += result['deleted'][options.type]
                    if 'not_found' in result and result['not_found']:
                        dup_results['not_found'] += len(result['not_found'][options.type])
                    to_remove = []
            print("Overall {dup} duplicate {sent} {type}, results deleted:{deleted}, not_found:{not_found}".format(
                dup=len(dup_ids), sent=dup_results['sentids'], type=options.type, 
                deleted=dup_results['deleted'], not_found=dup_results['not_found']))
        # print(export_csv)
        ## Write export data into CSV file
        write_csv(options, export_csv)


def main():
        """
        Main program loop
        * Read configuration file and validate
        * Authenticate if require
        * Export data from Trakt.tv
        * Cleanup list from Trakt.tv
        * Write to CSV
        """
        ## Parse inputs if any
        parser = argparse.ArgumentParser(description=desc, epilog=epilog)
        list_group = parser.add_mutually_exclusive_group(required=True)
        parser.add_argument('-v', action='version', version='%(prog)s 0.3')
        parser.add_argument('-c', '--config',
                      help='allow to overwrite default config filename, default %(default)s',
                      action='store', type=str, dest='config', default='config.ini')
        parser.add_argument('-o', '--output',
                      help='allow to overwrite default output filename, default %(default)s',
                      nargs='?', type=str, const='export.csv', default=None)
        parser.add_argument('-t', '--type',
                      help='allow to overwrite type, default %(default)s',
                      choices=['movies', 'shows', 'episodes'], dest='type', default='movies')
        list_group.add_argument('-l', '--list',
                      help='allow to overwrite default list, default %(default)s',
                      choices=['watchlist', 'collection', 'history'], dest='list', default='history')
        list_group.add_argument('-u', '--userlist',
                      help='allow to export a user custom list, default %(default)s',
                      dest='userlist', default=False, action='store_true')
        parser.add_argument('-C', '--clean',
                      help='empty list after export, default %(default)s',
                      default=False, action='store_true', dest='clean')
        parser.add_argument('-D', '--duplicate',
                      help='remove duplicate from list after export, default %(default)s',
                      default=False, action='store_true', dest='dup')
        #parser.add_argument('-d', '--dryrun',
        #              help='do not update the account, default %(default)s',
        #              default=True, action='store_true', dest='dryrun')
        parser.add_argument('-V', '--verbose',
                      help='print additional verbose information, default %(default)s',
                      default=False, action='store_true', dest='verbose')
        options = parser.parse_args()

        ## Display debug information
        if options.verbose:
            print("Options: %s" % options)

        if options.type == 'episodes' and options.list == "collection":
            print("Error, you can only fetch {0} from the history or watchlist list".format(options.type))
            sys.exit(1)

        if options.userlist:
            options.list = "user list"

        if not options.output:
            options.output = 'export_{type}_{list}.csv'.format(type=options.type, list=options.list)

        ## Read configuration and validate
        helpers.read_config(_trakt, options)

        ## Try refreshing to get new access token. If it doesn't work, user needs to authenticate again. 
        helpers.api_auth_refresh(_trakt, _headers, options)

        ## Display debug information
        if options.verbose:
            print("trakt: {}".format(_trakt))
            print("Authorization header: {}".format(_headers['Authorization']))

        export_data = []
        ## Get Trakt user lists (custom lists)
        if options.userlist:
            export_data = helpers.api_get_userlists(_trakt, _headers, _proxyDict, options, 1)
            #print("export data")
            #print(export_data)
            if export_data:
                print("Found {0} user list(s)".format(len(export_data)))
                print("")
                #pp.pprint(export_data)
                # TODO: add export all user lists functionality
                print("id       | name")
                for data in export_data:
                    print("{id} | {name}".format(name=data['name'], id = data['ids']['trakt']))
                    #print("{id} | {name} | {items}".format(
                    #       name=data['name'], id=data['ids']['trakt'], items=data['item_count'], own=data['user']['username']))
                print("")
                print("Type in the id matching with the name of the list you want to export, or 'all' for all lists.")
                options.listid = str(input('Input: '))
                if options.listid == "all":
                    for data in export_data:
                        options.listid = data['ids']['trakt']
                        options.list = "{username}'s user list with id: {id}, name: '{name}'".format(username=data['user']['username'], id=data['ids']['trakt'], name=data['name'])
                        global response_arr ## Cleanup global....
                        response_arr = []
                        export_data = helpers.api_get_userlist_items(_trakt, _headers, _proxyDict, options, 1)
                        options.output = data['name'] + ".csv"
                        process_export_data(options, export_data)
                else:
                    response_arr = []
                    user_list = helpers.api_get_userlist(_trakt, _headers, _proxyDict, options, 1)[0]
                    # print(user_list)
                    options.list = "{username}'s user list with id: {id}, name: '{name}'".format(username=user_list['user']['username'], id=user_list['ids']['trakt'], name=user_list['name'])
                    export_data = helpers.api_get_userlist_items(_trakt, _headers, _proxyDict, options, 1)
                    #pp.pprint(export_data)
                    process_export_data(options, export_data)
            else:
                print("Error, no user lists found".format(
                    type=options.type, list=options.userlist))
                sys.exit(1)
        else:
            export_data = helpers.api_get_list(_trakt, _headers, _proxyDict, options, 1)
            if export_data:
                process_export_data(options, export_data) 
            else:
                print("Error, no item(s) found for {type} from {list}".format(
                    type=options.type, list=options.list))
                sys.exit(1)

if __name__ == '__main__':
        main()
