#!/bin/python3

"""
Michael duPont
michael@mdupont.com
"""

# pylint: disable=W0603

from datetime import datetime, timedelta
from json import dump, dumps, load
from requests import Session

ORL_POST_URL = 'https://orlando.nextrequest.com/requests'
CONFIG_PATH = 'requests.config.json'
S3_KEY = 'requests.config.json'
S3_BUCKET = 'cfo-configs'

TESTING = True

if not TESTING:
    import boto3

class FOIARequest:
    """Handles FOIA requests"""

    def __init__(self, config: dict):
        #Create session to keep auth key valid during requests
        self.sess = Session()
        #Create initial data dict
        self.data = {
            'utf8': '✓',
            'authenticity_token': self.get_auth_token(),
            'bar_id': '',
            'department_id': '',
            'commit': 'Make+Request'
        }
        #Add data from the config dict
        for key in ('request', 'requester'):
            self.add_config_data(key, config[key])

    def get_auth_token(self) -> str:
        """Request the form page to grab a form auth token"""
        req = self.sess.get(ORL_POST_URL+'/new').text
        req = req[req.find('name="authenticity_token"'):]
        req = req[req.find('value="')+7:]
        req = req[:req.find('=="')+2]
        return req

    def add_config_data(self, pkey: str, values: dict):
        """Adds formatted key-value pairs to the data dict"""
        for key, val in values.items():
            self.data['{}[{}]'.format(pkey, key)] = val.replace(' ', '+')

    def make_request(self) -> bool:
        """returns whether it was made or not"""
        print(dumps(self.data, indent=4, sort_keys=True))
        if not TESTING:
            req = self.sess.post(ORL_POST_URL, data=self.data)
            return req.status_code in (200, 302, 303)
        return True

def time_elapsed(freq: str, last: str) -> bool:
    """Returns whether the given datetime has exceeded the desired frequency"""
    if last is None:
        return True
    value, unit = int(freq[:-1]), freq[-1]
    if unit == 'W':
        tdelta = timedelta(weeks=value)
    elif unit == 'D':
        tdelta = timedelta(days=value)
    else:
        return False
    last = datetime.strptime(last, '%Y-%m-%dT%H:%M:%S.%f')
    return datetime.utcnow() - last > tdelta

def get_bucket(name: str) -> 'S3 Bucket':
    """Fetch an S3 Bucket object with a given name"""
    bucket = boto3.resource('s3').Bucket(name)
    return bucket

def get_config() -> {str: object}:
    """Returns config dict from local when testing or S3 in production"""
    if not TESTING:
        global CONFIG_PATH
        CONFIG_PATH = '/tmp/' + CONFIG_PATH.split('/')[-1]
        bucket = get_bucket(S3_BUCKET)
        bucket.download_file(S3_KEY, CONFIG_PATH)
    return load(open(CONFIG_PATH))

def save_config(data: {str: object}):
    """Saves the updated config dict to local file or S3"""
    dump(data, open(CONFIG_PATH, 'w'), indent=4, sort_keys=True)
    if not TESTING:
        bucket = get_bucket(S3_BUCKET)
        bucket.upload_file(CONFIG_PATH, S3_KEY)

def main(event, context):
    """Main function to load, handle, and update request data"""
    configs = get_config()
    for i, config in enumerate(configs):
        #Skip if not enabled
        if not config['config']['enabled']:
            print('Skipping disabled request')
            continue
        #Only make the request if the last datetime has exceed the desired frequency
        if time_elapsed(config['config']['frequency'], config['config']['last']):
            req = FOIARequest(config)
            req.make_request()
            configs[i]['config']['last'] = datetime.utcnow().isoformat()
    save_config(configs)

if __name__ == '__main__':
    main(None, None)
