__author__ = 'Matthew Clairmont'
__version__ = '1.0'
__date__ = ''
# Remake of the Python 2.7 version
# VT Domain Scanner takes a file of domains, submits them to the Virus Total
# domain scanning API and outputs the domain and AV hits to a text file.

import time
import requests
import apikey

apikey = apikey.apikey

requests.urllib3.disable_warnings()
client = requests.session()
client.verify = False

domainErrors = []
# scan the domain to ensure results are fresh
def DomainScanner(domain):
    url = 'https://www.virustotal.com/vtapi/v2/url/scan'
    params = {'apikey': apikey, 'url': domain}

    # attempt connection to VT API and save response as r
    try:
        r = requests.post(url, params=params)
    except requests.ConnectTimeout as timeout:
        print('Connection timed out. Error is as follows-')
        print(timeout)

    # sanitize domain after upload for safety
    domain = domain.replace('.', '[.]')
    # handle ValueError response which may indicate an invalid key or an error with scan
    # if an except is raised, add the domain to a list for tracking purposes
    if r.status_code == 200:
        try:
            jsonResponse = r.json()
            # print error if the scan had an issue
            if jsonResponse['response_code'] is not 1:
                print('There was an error submitting the domain for scanning.')
                print(jsonResponse['verbose_msg'])
            elif jsonResponse['response_code'] == -2:
                print('{!r} is queued for scanning.'.format(domain))
                delay = 15
            else:
                print(domain, 'was scanned successfully.')

        except ValueError:
            print('There was an error when scanning {!s}. Adding domain to error list....'.format(domain))
            domainErrors.append(domain)

        # return domain errors for notifying user when script completes
        return domainErrors, delay

    # API TOS issue handling
    elif r.status_code == 204:
        print('Received HTTP 204 response. You may have exceeded your API request quota or rate limit.')
        print('https://support.virustotal.com/hc/en-us/articles/115002118525-The-4-requests-minute-limitation-of-the-'
              'Public-API-is-too-low-for-me-how-can-I-have-access-to-a-higher-quota-')


def DomainReportReader(domain):
    # sleep 15 to control requests/min to API. Public APIs only allow for 4/min threshold,
    # you WILL get a warning email to the owner of the account if you exceed this limit.
    # Private API allows for tiered levels of queries/second.
    time.sleep(1)

    url = 'https://www.virustotal.com/vtapi/v2/url/report'
    params = {'apikey': apikey, 'resource': domain}

    # attempt connection to VT API and save response as r
    try:
        r = requests.post(url, params=params)
    except requests.ConnectTimeout as timeout:
        print('Connection timed out. Error is as follows-')
        print(timeout)

    # sanitize domain after upload for safety
    domain = domain.replace('.', '[.]')
    # handle ValueError response which may indicate an invalid key or an error with scan
    # if an except is raised, add the domain to a list for tracking purposes
    if r.status_code == 200:
        try:
            jsonResponse = r.json()
            # print error if the scan had an issue
            if jsonResponse['response_code'] is 0:
                print('There was an error submitting the domain for scanning.')
                print(jsonResponse['verbose_msg'])

            elif jsonResponse['response_code'] == -2:
                print('{!r} is queued for scanning.'.format(domain))
                delay = 15

            else:
                print('Report is ready for', domain)

        except ValueError:
            print('There was an error when scanning {!s}. Adding domain to error list....'.format(domain))
            domainErrors.append(domain)


    # API TOS issue handling
    elif r.status_code == 204:
        print('Received HTTP 204 response. You may have exceeded your API request quota or rate limit.')
        print('https://support.virustotal.com/hc/en-us/articles/115002118525-The-4-requests-minute-limitation-of-the-'
              'Public-API-is-too-low-for-me-how-can-I-have-access-to-a-higher-quota-')

    print(jsonResponse)
    permalink = jsonResponse['permalink']
    scandate = jsonResponse['scan_date']
    positives = jsonResponse['positives']
    total = jsonResponse['total']
    detections = {}
    for vendor, result in jsonResponse['scans'].items():  # sheer laziness of not having to reassign variables
        if 'clean site' not in result['result'] and 'unrated site' not in result['result']:
            detections[vendor] = result['result']



domain = 'taxhuge.com'
# DomainScanner(domain)
DomainReportReader(domain)


count = len(domainErrors)
if count > 0:
    print('There were {!s} errors scanning domains'.format(count))

