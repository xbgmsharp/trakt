#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) Copyright 2016-2020 xbgmsharp <xbgmsharp@gmail.com>
#
# Purpose:
# Helpers for 
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

desc="""This program contains helpers for import_trakt.py and export_trakt.py"""

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

# response_arr = []

def read_config(_trakt, options):
        """Read config file and if provided overwrite default values.
        If no config file exist, create one with default values.
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
                        if config.has_option('TRAKT','USERNAME') and len(config.get('TRAKT','USERNAME')) != 0:
                                _trakt['username'] = config.get('TRAKT','username')
                        else:
                                print('Error, you must specify a trakt.tv username for user lists to work')
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
                        config.set('TRAKT', 'USERNAME', '')
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

def api_auth_refresh(_trakt, _headers, options): 
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
                api_auth(_trakt, _headers, options) 
        else:   
            print("No refresh_token found in config file. Get new refresh_token and access_token by manually authenticating again")
            api_auth(_trakt, _headers, options) 

def api_auth(_trakt, _headers, options):
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

def api_get_request(_headers, _proxyDict, options, url, page): 
    """Uses Trakt API to sends a request to the URL given and returns the results as a response array, starting with page.
    """
    response_arr = [] 
    if options.verbose:
        print(url)
    if _proxy['proxy']:
        r = requests.get(url, headers=_headers, proxies=_proxyDict, timeout=(10, 60))
    else:
        r = requests.get(url, headers=_headers, timeout=(5, 60))
    #pp.pprint(r.headers) 
    if r.status_code != 200:
        print("Error fetching GET response for {list}: {status} [{text}]".format(
                list=options.list, status=r.status_code, text=r.text))
        return None
    else:
        json_dict = json.loads(r.text)
        if type(json_dict) is list:
                response_arr += json.loads(r.text)
        else: 
                response_arr.append(json_dict) 
    #print(response_arr)

    # if 'X-Pagination-Page-Count'in r.headers and r.headers['X-Pagination-Page-Count'] != "0":
    if 'X-Pagination-Page-Count'in r.headers and r.headers['X-Pagination-Page-Count']:
        if int(r.headers['X-Pagination-Page-Count']) == 0: 
            print("No pages found in response, trakt list may be empty")
            return response_arr

        print("Fetched page {page} of {PageCount} pages for {list}".format(
                page=page, PageCount=r.headers['X-Pagination-Page-Count'], list=options.list))
        if page != int(r.headers['X-Pagination-Page-Count']):
            api_get_request(_headers, _proxyDict, options, url, page + 1)

    return response_arr

def api_get_list(_trakt, _headers, _proxyDict, options, page):
        """Get items of default list (e.g history) by type starting from page
        """
        url = _trakt['baseurl'] + '/sync/{list}/{type}?page={page}&limit={limit}'.format(
                            list=options.list, type=options.type, page=page, limit=1000)
        return api_get_request(_headers, _proxyDict, options, url, page)

def api_get_userlists(_trakt, _headers, _proxyDict, options, page):
        """Get list of all user lists
        """
        url = _trakt['baseurl'] + '/users/{user}/lists'.format(
                            user=_trakt['username'], page=page, limit=1000)
        #url = _trakt['baseurl'] + '/users/{user}/lists/{list_id}?page={page}&limit={limit}'.format(
        #                    list=options.list, type=options.type, page=page, limit=1000)
        # print(url)
        return api_get_request(_headers, _proxyDict, options, url, page)

def api_get_userlist(_trakt, _headers, _proxyDict, options, page):
        """Get items of user list by type
        """
        url = _trakt['baseurl'] + '/users/{user}/lists/{list_id}'.format(
                            user=_trakt['username'], list_id=options.listid, type=options.type, page=page, limit=1000)
        return api_get_request(_headers, _proxyDict, options, url, page)


def api_get_userlist_items(_trakt, _headers, _proxyDict, options, page):
        """Get items of user list by type
        """
        url = _trakt['baseurl'] + '/users/{user}/lists/{list_id}/items/{type}?page={page}&limit={limit}'.format(
                            user=_trakt['username'], list_id=options.listid, type=options.type, page=page, limit=1000)
        return api_get_request(_headers, _proxyDict, options, url, page)
