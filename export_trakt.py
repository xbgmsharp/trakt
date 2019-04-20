#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2016-2018 xbgmsharp <xbgmsharp@gmail.com>
#
# Purpose:
# Export Movies or TVShows IDs from Trakt.tv
#
# Requirement on Ubuntu/Debian Linux system
# apt-get install python-dateutil python-simplejson python-requests python-openssl jq
#
# Requirement on Windows on Python 2.7
# C:\Python2.7\Scripts\easy_install-2.7.exe simplejson requests
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
except:
        sys.exit("Please use your favorite mehtod to install the following module requests and simplejson to use this script")

import argparse
import ConfigParser
import datetime
import collections
import pprint

pp = pprint.PrettyPrinter(indent=4)

desc="""This program export Movies or TVShows IDs from Trakt.tv list."""

epilog="""Read a list from Trakt API.
Export them into a CSV file."""

_trakt = {
        'client_id'     :       '', # Auth details for trakt API
        'client_secret' :       '', # Auth details for trakt API
        'oauth_token'   :       '', # Auth details for trakt API
        'baseurl'       :       'https://api.trakt.tv' # Sandbox environment https://api-staging.trakt.tv
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
                print "Config file: {0}".format(_configfile)
        if os.path.exists(_configfile):
                try:
                        config = ConfigParser.SafeConfigParser()
                        config.read(_configfile)
                        if config.has_option('TRAKT','CLIENT_ID') and len(config.get('TRAKT','CLIENT_ID')) != 0:
                                _trakt['client_id'] = config.get('TRAKT','CLIENT_ID')
                        else:
                                print 'Error, you must specify a trakt.tv CLIENT_ID'
                                sys.exit(1)
                        if config.has_option('TRAKT','CLIENT_SECRET') and len(config.get('TRAKT','CLIENT_SECRET')) != 0:
                                _trakt['client_secret'] = config.get('TRAKT','CLIENT_SECRET')
                        else:
                                print 'Error, you must specify a trakt.tv CLIENT_SECRET'
                                sys.exit(1)
                        if config.has_option('TRAKT','OAUTH_TOKEN') and len(config.get('TRAKT','OAUTH_TOKEN')) != 0:
                                _trakt['oauth_token'] = config.get('TRAKT','OAUTH_TOKEN')
                        else:
                                print 'Warning, authentification is required'
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
                        print "Error reading configuration file {0}".format(_configfile)
                        sys.exit(1)
        else:
                try:
                        print '%s file was not found!' % _configfile
                        config = ConfigParser.RawConfigParser()
                        config.add_section('TRAKT')
                        config.set('TRAKT', 'CLIENT_ID', '')
                        config.set('TRAKT', 'CLIENT_SECRET', '')
                        config.set('TRAKT', 'OAUTH_TOKEN', '')
                        config.set('TRAKT', 'BASEURL', 'https://api.trakt.tv')
                        config.add_section('SETTINGS')
                        config.set('SETTINGS', 'PROXY', False)
                        config.set('SETTINGS', 'PROXY_HOST', 'https://127.0.0.1')
                        config.set('SETTINGS', 'PROXY_PORT', '3128')
                        with open(_configfile, 'wb') as configfile:
                                config.write(configfile)
                                print "Default settings wrote to file {0}".format(_configfile)
                except:
                        print "Error writing configuration file {0}".format(_configfile)
                sys.exit(1)

def write_csv(options, results):
        """Write list output into a CSV file format"""
        if options.verbose:
                print "CSV output file: {0}".format(options.output)
        # Write result CSV
        with open(options.output, 'wb') as fp:
                keys = {}
                for i in results:
                    for k in i.keys():
                        keys[k] = 1
                mycsv = csv.DictWriter(fp, fieldnames=keys.keys(), quoting=csv.QUOTE_ALL)
                mycsv.writeheader()
                for row in results:
                        mycsv.writerow(row)
        fp.close()

def api_auth(options):
        """API call for authentification OAUTH"""
        print("Open the link in a browser and paste the pincode when prompted")
        print("https://trakt.tv/oauth/authorize?response_type=code&"
              "client_id={0}&redirect_uri=urn:ietf:wg:oauth:2.0:oob".format(
                  _trakt["client_id"]))
        pincode = str(raw_input('Input PIN:'))
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
        print 'Save as "oauth_token" in file {0}: {1}'.format(options.config, response["access_token"])

def api_get_list(options, page):
        """API call for Sync / Get list by type"""
        url = _trakt['baseurl'] + '/sync/{list}/{type}?extended=full&page={page}&limit={limit}'.format(
                            list=options.list, type=options.type, page=page, limit=1000)
        if options.verbose:
            print(url)
        if _proxy['proxy']:
            r = requests.get(url, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
        else:
            r = requests.get(url, headers=_headers, timeout=(5, 60))
        #pp.pprint(r.headers)
        if r.status_code != 200:
            print "Error fetching Get {list}: {status} [{text}]".format(
                    list=options.list, status=r.status_code, text=r.text)
            return None
        else:
            global response_arr
            # pp.pprint(r.text)
            response_arr += json.loads(r.text)
        if 'X-Pagination-Page-Count'in r.headers and r.headers['X-Pagination-Page-Count']:
            print "Fetched page {page} of {PageCount} pages for {list} list".format(
                    page=page, PageCount=r.headers['X-Pagination-Page-Count'], list=options.list)
            if page != int(r.headers['X-Pagination-Page-Count']):
                api_get_list(options, page+1)

        return response_arr

def api_get_userlists(options, page):
        """API call for Sync / Get list by type"""
        url = _trakt['baseurl'] + '/users/{user}/lists'.format(
                            user=options.userlist, page=page, limit=1000)
        #url = _trakt['baseurl'] + '/users/{user}/lists/{list_id}?page={page}&limit={limit}'.format(
        #                    list=options.list, type=options.type, page=page, limit=1000)
        if options.verbose:
            print(url)
        if _proxy['proxy']:
            r = requests.get(url, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
        else:
            r = requests.get(url, headers=_headers, timeout=(5, 60))
        #pp.pprint(r.headers)
        if r.status_code != 200:
            print "Error fetching Get {list}: {status} [{text}]".format(
                    list=options.list, status=r.status_code, text=r.text)
            return None
        else:
            global response_arr
            response_arr += json.loads(r.text)
        if 'X-Pagination-Page-Count'in r.headers and r.headers['X-Pagination-Page-Count']:
            print "Fetched page {page} of {PageCount} pages for {list} list".format(
                    page=page, PageCount=r.headers['X-Pagination-Page-Count'], list=options.list)
            if page != int(r.headers['X-Pagination-Page-Count']):
                api_get_list(options, page+1)

        return response_arr

def api_get_userlist(options, page):
        """API call for Sync / Get list by type"""
        # url = _trakt['baseurl'] + '/users/{user}/lists/{list_id}/items/{type}?extended=metadata&page={page}&limit={limit}'.format(
                            # user=options.userlist, list_id=options.listid, type=options.type, page=page, limit=1000)

        url = _trakt['baseurl'] + '/users/{user}/watched/shows'.format(user=options.userlist)
        if options.verbose:
            print(url)
        if _proxy['proxy']:
            r = requests.get(url, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
        else:
            r = requests.get(url, headers=_headers, timeout=(5, 60))
        #pp.pprint(r.headers)
        if r.status_code != 200:
            print "Error fetching Get {list}: {status} [{text}]".format(
                    list=options.list, status=r.status_code, text=r.text)
            return None
        else:
            global response_arr
            response_arr += json.loads(r.text)
        if 'X-Pagination-Page-Count'in r.headers and r.headers['X-Pagination-Page-Count']:
            print "Fetched page {page} of {PageCount} pages for {list} list".format(
                    page=page, PageCount=r.headers['X-Pagination-Page-Count'], list=options.list)
            if page != int(r.headers['X-Pagination-Page-Count']):
                api_get_userlist(options, page+1)

        return response_arr

def api_remove_from_list(options, remove_data, is_id=False):
        """API call for Sync / Remove from list"""
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
            print "Error removing items from {list}: {status} [{text}]".format(
                    list=options.list, status=r.status_code, text=r.text)
            return None
        else:
            return json.loads(r.text)

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
        parser = argparse.ArgumentParser(version='%(prog)s 0.3', description=desc, epilog=epilog)
        parser.add_argument('-c', '--config',
                      help='allow to overwrite default config filename, default %(default)s',
                      action='store', type=str, dest='config', default='config.ini')
        parser.add_argument('-o', '--output',
                      help='allow to overwrite default output filename, default %(default)s',
                      nargs='?', type=str, const='export.csv', default=None)
        parser.add_argument('-t', '--type',
                      help='allow to overwrite type, default %(default)s',
                      choices=['movies', 'shows', 'episodes'], dest='type', default='movies')
        parser.add_argument('-l', '--list',
                      help='allow to overwrite default list, default %(default)s',
                      choices=['watchlist', 'collection', 'history'], dest='list', default='history')
        parser.add_argument('-u', '--userlist',
                      help='allow to export a user custom list, default %(default)s',
                      dest='userlist', default=None)
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
                      default=True, action='store_true', dest='verbose')
        options = parser.parse_args()

        ## Display debug information
        if options.verbose:
            print "Options: %s" % options

        if options.type == 'episodes' and options.list == "collection":
            print "Error, you can only fetch {0} from the history or watchlist list".format(options.type)
            sys.exit(1)

        if options.userlist:
            options.list = options.userlist

        if not options.output:
            options.output = 'export_{type}_{list}.csv'.format(type=options.type, list=options.list)

        ## Read configuration and validate
        read_config(options)

        ## Display oauth token if exist, otherwise authenticate to get one
        if _trakt['oauth_token']:
            _headers['Authorization'] = 'Bearer ' + _trakt['oauth_token']
            _headers['trakt-api-key'] = _trakt['client_id']
        else:
            api_auth(options)

        ## Display debug information
        if options.verbose:
            print "trakt: {}".format(_trakt)
            print "Authorization header: {}".format(_headers['Authorization'])

        ## Get lits from Trakt user
        export_data = []
        if options.userlist:
            export_data = api_get_userlists(options, 1)
            if export_data:
                print "Found {0} user list".format(len(export_data))
                #pp.pprint(export_data)
                for data in export_data:
                    print "Found list id '{id}' name '{name}' with {items} items own by {own}".format(
                            name=data['name'], id=data['ids']['trakt'], items=data['item_count'], own=data['user']['username'])
                print("Input the custom list id to export")
                options.listid = str(raw_input('Input:'))
                global response_arr ## Cleanup global....
                response_arr = []
                export_data = api_get_userlist(options, 1)
                #pp.pprint(export_data)
                if export_data:
                    print "Found {0} Item-Count".format(len(export_data))
            else:
                print "Error, no item return for {type} from the user list {list}".format(
                    type=options.type, list=options.userlist)
                sys.exit(1)

        ## Get data from Trakt
        if not export_data:
            export_data = api_get_list(options, 1)
            if export_data:
                print "Found {0} Item-Count".format(len(export_data))
                # print "Data {0}".format(export_data)
            else:
                print "Error, no item return for {type} from the {list} list".format(
                    type=options.type, list=options.list)
                sys.exit(1)

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
        #    pp.pprint(data)
        #    pp.pprint(options.type)
           if options.type[:-1] != "episode" and 'imdb' in data[options.type[:-1]]['ids']:
                find_dupids.append(data[options.type[:-1]]['ids']['imdb'])
                if options.type == "movies":
                    export_csv.append({ 'imdb' : data[options.type[:-1]]['ids']['imdb'],
                                        'trakt_id' : data[options.type[:-1]]['ids']['trakt'],
                                        options.time : data[options.time],
                                        'title' : data[options.type[:-1]]['title'].encode('utf-8'),
                                        'duration' : data['movie']['runtime']})
                    pp.pprint('Hit here')
                if options.type == "shows":
                    export_csv.append({ 'imdb' : data[options.type[:-1]]['ids']['imdb'],
                                        'trakt_id' : data[options.type[:-1]]['ids']['trakt'],
                                        options.time : data[options.time],
                                        'title' : data[options.type[:-1]]['title'].encode('utf-8'),
                                        'duration' : data['show']['runtime']})
                    
           elif 'tmdb' in data[options.type[:-1]]['ids']:
                find_dupids.append(data[options.type[:-1]]['ids']['tmdb'])
                if not data['episode']['title']: data['episode']['title'] = "no episode title"
                export_csv.append({ 'tmdb' : data[options.type[:-1]]['ids']['tmdb'],
                                    'trakt_id' : data[options.type[:-1]]['ids']['trakt'],
                                    options.time : data[options.time],
                                    'season' : data[options.type[:-1]]['season'],
                                    'episode' : data[options.type[:-1]]['number'],
                                    'episode_title' : data['episode']['title'].encode('utf-8'),
                                    'show_title' : data['show']['title'].encode('utf-8'),
                                    'duration' : data['show']['runtime']})
        #print export_csv
        ## Write export data into CSV file
        write_csv(options, export_csv)

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
                        print "Result: {0}".format(result)
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
                    print "Result: {0}".format(result)
                    if 'deleted' in result and result['deleted']:
                        cleanup_results['deleted'] += result['deleted'][options.type]
                    if 'not_found' in result and result['not_found']:
                        cleanup_results['not_found'] += len(result['not_found'][options.type])
            print "Overall cleanup {sent} {type}, results deleted:{deleted}, not_found:{not_found}".format(
                sent=cleanup_results['sentids'], type=options.type, 
                deleted=cleanup_results['deleted'], not_found=cleanup_results['not_found'])

        ## Found duplicate and remove duplicate
        dup_ids = [item for item, count in collections.Counter(find_dupids).items() if count > 1]
        print "Found {dups} duplicate out of {total} {entry}".format(
                    entry=options.type, dups=len(dup_ids), total=len(find_dupids))
        if options.dup:
            if len(dup_ids) > 0:
                print dup_ids
            dup_results = {'sentids' : 0, 'deleted' : 0, 'not_found' : 0}
            to_remove = []
            for dupid in find_dupids:
                count = 0
                for data in export_data:
                    if data[options.type[:-1]]['ids']['imdb'] == dupid:
                        #print "{0} {1}".format(dupid, data['id'])
                        count += 1
                        if count > 1:
                            print "Removing {0} {1}".format(dupid, data['id'])
                            to_remove.append(data['id'])
                            dup_results['sentids'] += len(to_remove)
                            result = api_remove_from_list(options, to_remove, is_id=True)
                            if len(to_remove) >= 10: # Remove by batch of 10
                                if result:
                                    print "Result: {0}".format(result)
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
                    print "Result: {0}".format(result)
                    if 'deleted' in result and result['deleted']:
                        dup_results['deleted'] += result['deleted'][options.type]
                    if 'not_found' in result and result['not_found']:
                        dup_results['not_found'] += len(result['not_found'][options.type])
                    to_remove = []
            print "Overall {dup} duplicate {sent} {type}, results deleted:{deleted}, not_found:{not_found}".format(
                dup=len(dup_ids), sent=dup_results['sentids'], type=options.type, 
                deleted=dup_results['deleted'], not_found=dup_results['not_found'])

if __name__ == '__main__':
        main()
