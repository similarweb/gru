#!/usr/bin/env python

import subprocess
import sys
import httplib
import urlparse
import json
import time


def get_facts():
    """
    We'll use facter as a source of host metadata
    """
    process = subprocess.Popen('facter --json -p', shell="true", stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    process.wait()
    if process.returncode != 0:
        raise RuntimeError('Could not fetch facter facts')
    raw_json = stdout
    parsed_json = json.loads(raw_json)
    # ES craps out on field names that contain a "."
    # To work around that, let's recursively remove them.
    return replace_periods(parsed_json)


def replace_periods(dict_val, replace_with='_'):
    """
    Recursively replace "." fonud in keys in the given dict with the value
        of replace_with
    """
    facts = dict()
    for k, v in dict_val.items():
        if '.' in k:
            if replace_with:
                k = k.replace('.', '_')
        if isinstance(v, dict):
            facts[k] = replace_periods(v)
        else:
            facts[k] = v
    return facts


def update_inventory(facts_dict, es_url):
    """
    do an HTTP PUT request to the given ES URL
        (should be an index/document type/<host_id>) with the given facts
    """
    parsed_url = urlparse.urlparse(es_url)
    conn = httplib.HTTPConnection(parsed_url.hostname, parsed_url.port)
    facts_dict['last_update'] = int(time.time())
    conn.request('PUT', parsed_url.path, json.dumps(facts_dict))
    response = conn.getresponse()

    if response.status >= 400:
        raise ValueError(
            'Could not write document to elasticsearch: {}'.format(
                response.read()))


def main():
    """
    Reads facts from Facter, and index them in ElasticSearch.
    Only one required parameter - es_url. Should be a document URL in
        ElasticSearch.
    i.e. http://elastic.internal:9200/inventory-facter/host/i-83427194
    """
    es_url = sys.argv[1]
    facts_dict = get_facts()
    update_inventory(facts_dict, es_url)


if __name__ == '__main__':
    main()
