# FOIA-Auto-Requester

Script to automatically make FOIA requests

**Project Lead:**  
Michael duPont (@mdupont)

---

## About

This project is supposed to automate FOIA (Freedom of Information Act) requests that occur on on a regular basis. In addition to simplifying the requester's job, it has the added benefit of surfacing particular datasets for inclusion into open data portals. For this reason, it is recommended that the request include a line about placing the info into the open data portal. The hope is that these datasets become regularly updated in the portal without a FOIA prompt.

This project uses Python running inside an AWS Lambda function. Production settings are located in S3 while test settings are local.

## Project Details

This script works by making POST requests to [NextRequest](https://www.nextrequest.com/) based on config data from a JSON file. The JSON file follows this template: 

```json
[
    {
        "config": {
            "frequency": "[int][D/W]",
            "last": "2017-01-01T00:00:00.000000" or null,
            "enabled": true / false
        },
        "request": {
            "request_text": "Message including desired data and handling"
        },
        "requester": {
            "address": "123 Foo St",
            "city": "Orlando",
            "company": "Code for Orlando",
            "email": "foo@bar.com",
            "name": "Foo Bar",
            "phone_number": "1234567890",
            "state": "Florida",
            "zipcode": "12345"
        }
    },
    {...}
]
```

JSON Configs:

* frequency: How often the request will be made. The value is a string containing an integer followed by a "D" for days or "W" for weeks
* last: The datetime string representing the most recent request. UTC POSIX format (%Y-%m-%dT%H:%M:%S.%f). If null (recommended initial value), the request will be made.
* enabled: Enable or disable a given request

There is also a global TESTING flag at the top of the Python script to negate all enabled flags when True. Code will read config data locally, execute everything except the POST request, and act as though it was successful.

## Install

```
git clone https://github.com/cforlando/FOIA-Auto-Requester.git
cd FOIA-Auto-Requester
pip install -r requirements.txt
```

## Running

Double check that TESTING is set to True before running locally. If TESTING is set to False, the script should fail because it lacks AWS credentials to fetch the S3 configs.

```
python foiareq.py
```

## Deployment

There are three things we need to in order to deploy to AWS Lambda:

1. Downgrade script from Python3 to Python2. In its current state, the only things needed are to remove function annotations and change `dict.items()` to `dict.iteritems()`

2. Download the dependencies. Because Lambda is like its own virtual env, any third-party libraries must be included with the code

```
pip2 install -r requirements.txt -t deployment/
```

3. Compress the deployment folder into a zip file

Once that is done, you upload the zip file to AWS Lambda and check that the daily trigger is still enabled.

You will also need to create an S3 Bucket to read the production config file from. The name of the bucket and file are stored as S3\_BUCKET and S3\_KEY at the top of the code.

## Contributing

It's possible to add new requests to requests.config.json without having to test the program yourself. Contact us and/or create issues with any questions, bugs, or to add your request to the production version. Use [this GitHub issue](https://github.com/cforlando/FOIA-Auto-Requester/issues/4) as an example.

## License

MIT [LICENSE](https://github.com/cforlando/foia-auto-requester/blob/master/LICENSE) file.

## About Code for Orlando

Code for Orlando, a local Code for America brigade, brings the community together to improve Orlando through technology. We are a group of “civic hackers” from various disciplines who are committed to volunteering our talents to make a difference in the local community through technology. We unite to improve the way the community, visitors, and local government experience Orlando.
