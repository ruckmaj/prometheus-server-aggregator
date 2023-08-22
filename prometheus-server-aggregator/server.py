import json

import requests
import time

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Datastore:

    def __init__(self, data, reference, ttl):
        self.reference = reference
        self.data = data
        self.timestamp = time.time()
        self.ttl = ttl
        self.stale = True

    # def __repr__(self):
    #     if self.data is None:
    #         return {}
    #     else:
    #         return self.data

    @property
    def is_expired(self):
        now = time.time()
        expiry = self.timestamp + self.ttl
        if now > expiry:
            self.stale = True
        else:
            self.stale = False

        return self.stale


class PrometheusServer:

    def __repr__(self):
        return self.url

    def __init__(self, address, port, name: str = None, resource=None, username=None, password=None):

        if port is None:
            port = 9109

        if resource is None:
            resource = "/api/v1/status/config"

        if username is not None or password is not None:
            self.use_auth = True
            self.authentication = {'username': username, 'password': password}
        else:
            self.use_auth = True

        self.protocol = 'http://'
        self.address = address
        self.port = port
        self.resource = resource
        self.timeout = 2000

        self.url = f"{self.protocol}{self.address}:{self.port}"
        if name is None:
            self.name = self.url
        else:
            self.name = name
        self.last_scan = 0
        self.ttl = 60
        self.data_expired = True
        self.datastore = {}

    @classmethod
    def simple_query(cls, url, resource, timeout, ttl):

        try:
            r = requests.get(url=url + resource, timeout=timeout, headers={'Accept': 'application/json'})
            if r.status_code > 200:
                pass

            try:
                xx = r.json()['data']['yaml']
                data = yaml.load(stream=xx, Loader=Loader)
            except Exception as e:

                data = r.json()['data']

            return Datastore(data=data, reference=resource, ttl=ttl)

        except Exception as e:
            return Datastore(data={"error":"Unable to perform query"}, reference=resource, ttl=ttl)

    def query_sever(self, resource: str = "/api/v1/status/config"):

        if not resource in self.datastore:
            do_query = True
        else:
            do_query = False

        if resource in self.datastore:
            if not self.datastore[resource].is_expired:
                do_query = True
            else:
                return self.datastore[resource]

        if do_query:
            try:
                r = requests.get(url=self.url + resource, timeout=self.timeout, headers={'Accept': 'application/json'})
                if r.status_code > 200:
                    pass

                try:
                    xx = r.json()['data']['yaml']
                    data = yaml.load(stream=xx, Loader=Loader)
                except Exception as e:

                    data = r.json()['data']

                self.datastore[resource] = Datastore(data=data, reference=resource, ttl=self.ttl)
                return self.datastore[resource]
            except Exception as e:
                pass
        else:
            return self.datastore[resource]
