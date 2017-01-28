#!/bin/python3

"""
Michael duPont
michael@mdupont.com
"""

from datetime import datetime, timedelta
from json import dump, dumps, load
from requests import Session

ORL_POST_URL = 'https://orlando.nextrequest.com/requests'
CONFIG_PATH = 'requests.config.json'

TESTING = True

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
        for k, v in values.items():
            self.data['{}[{}]'.format(pkey, k)] = v.replace(' ', '+')

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

def main():
    configs = load(open(CONFIG_PATH))
    for i, config in enumerate(configs):
        #Skip if not enabled
        if not config['config']['enabled']:
            continue
        #Only make the request if the last datetime has exceed the desired frequency
        if time_elapsed(config['config']['frequency'], config['config']['last']):
            req = FOIARequest(config)
            req.make_request()
            configs[i]['config']['last'] = datetime.utcnow().isoformat()
    dump(configs, open(CONFIG_PATH, 'w'), indent=4, sort_keys=True)

if __name__ == '__main__':
    main()
