"""
Module that has ConfigCacheLite class

This module is intended to be used in wmcontrol project
in order to remove wmcontrol's dependency on WMCore

wmcontrol: https://github.com/cms-PdmV/wmcontrol/
WMCore: https://github.com/dmwm/WMCore/
"""
import os
import json
import hashlib
import base64
try:
    import httplib
except ImportError:
    import http.client as httplib


class ConfigCacheLite():
    """
    Stripped down version of WMCore's ConfigCache
    ConfigCacheLite has a couple of basic attributes and can read and attach a file
    """
    def __init__(self, cmsweb_url):
        env_proxy = os.getenv('X509_USER_PROXY')
        env_cert = os.getenv('X509_USER_CERT')
        env_key = os.getenv('X509_USER_KEY')
        if env_proxy:
            cert_file = env_proxy
            key_file = env_proxy
        elif env_cert and env_key:
            cert_file = env_cert
            key_file = env_key
        else:
            raise Exception('Missing X509_USER_PROXY or X509_USER_CERT and X509_USER_KEY')

        self.database_name = '/couchdb/reqmgr_config_cache'
        cmsweb_url = cmsweb_url.rstrip('/')
        self.http_client = httplib.HTTPSConnection(cmsweb_url,
                                                   cert_file=cert_file,
                                                   key_file=key_file)

        self.document = {}
        self.document['type'] = "config"
        self.document['description'] = {}
        self.document['description']['config_label'] = None
        self.document['description']['config_desc'] = None
        self.document['pset_tweak_details'] = None
        self.document['info'] = None
        self.document['config'] = None
        self.document['pset_hash'] = None
        self.attachments = {}

    def __str__(self):
        return json.dumps(self.document, indent=2, sort_keys=True)

    def __repr__(self):
        return str(self)

    def __http_request(self, url, method='GET', data=None, headers=None):
        """
        Do a HTTP request to a given url using created HTTPS connection
        'method' can be GET, PUT, POST, DELETE, etc.
        'data' must be a string
        """
        self.http_client.request(method, url, data, headers=headers)
        response = self.http_client.getresponse()
        response_text = response.read()
        response_code = response.status
        return response_text, response_code

    def set_description(self, description):
        """
        Set description.config_desc
        """
        self.document['description']['config_desc'] = description

    def set_label(self, label):
        """
        Set description.config_label
        """
        self.document['description']['config_label'] = label

    def set_user_group(self, user, group):
        """
        Set owner.user and owner.group
        """
        self.document['owner'] = {'user': user,
                                  'group': group}

    def add_config(self, config_path):
        """
        Add file as 'configFile' attachment
        This also sets 'md5_hash' to hexadecimal md5 of file contents
        """
        with open(config_path) as config_file:
            config_string = config_file.read()

        config_md5 = hashlib.md5(config_string.encode('utf-8')).hexdigest()
        self.document['md5_hash'] = config_md5
        self.attachments['configFile'] = config_string

    def set_PSet_tweaks(self, tweaks):
        """
        Set pset_tweak_details
        """
        self.document['pset_tweak_details'] = tweaks

    def save(self):
        """
        Save document and it's attachment to CouchDB
        """
        # Save one document as "bulk" as this automatically
        # generates document _id
        doc_url = self.database_name + '/_bulk_docs'
        doc_data = json.dumps({'docs': [self.document]})
        doc_headers = {'Content-Type': 'application/json'}
        doc_response, _ = self.__http_request(doc_url, 'POST', doc_data, doc_headers)
        if isinstance(doc_response, bytes):
            # It is bytes in python 3.4
            doc_response = doc_response.decode('utf-8')

        doc_response = json.loads(doc_response)[0]
        self.document['_id'] = doc_response['id']
        self.document['_rev'] = doc_response['rev']

        # Save (attach) attachments to the document
        for attachment_name, attachment_data in self.attachments.items():
            attachment_data = attachment_data.encode('utf-8')
            attachment_md5_base64 = base64.b64encode(hashlib.md5(attachment_data).digest())
            # Add Content-MD5 as 'checksum' header
            attachment_headers = {'Content-MD5': attachment_md5_base64,
                                  'Content-Type': 'application/json'}
            # .../<database_name>/<doc_id>/<attachment_name>?rev=<doc_rev>
            attachment_url = '%s/%s/%s?rev=%s' % (self.database_name,
                                                  doc_response['id'],
                                                  attachment_name,
                                                  doc_response['rev'])
            self.__http_request(attachment_url, 'PUT', attachment_data, attachment_headers)

        return doc_response['id']
