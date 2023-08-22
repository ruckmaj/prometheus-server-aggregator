import threading
import server
from helpers import BaseThread


class PrometheusAggregator:

    def __init__(self):

        self.servers = {}
        self.data = {}

    def add_server(self, name, address, port, resource=None, username=None, password=None):
        self.servers[name] = server.PrometheusServer(name=name, address=address, port=port, resource=resource)

    def group_request(self, resource=None):
        try:
            for name, url in self.servers.items():
                url: server.PrometheusServer
                if resource is None:
                    resource = url.resource
                try:
                    z = url.simple_query(url.url, resource, url.timeout, url.ttl)
                    if url.name not in self.data:
                        self.data[url.name] = {}

                    self.data[url.name][resource] = {'data': z.data, 'timestamp': z.timestamp}

                except Exception as e:
                    return False
        except Exception as e:
            pass
            return False
        return True

    def targets(self):

        o = {}

        try:
            for server, resource in self.data.items():

                for name, data in resource['/api/v1/targets'].items():
                    if name == 'data':
                        for target in data['activeTargets']:
                            try:
                                if not target['labels']['instance'] in o:
                                    o[target['labels']['instance']] = []

                                o[target['labels']['instance']].append(
                                    {'server': target['labels']['instance'],
                                     'lastScrape': target['lastScrape'],
                                     'health': target['health'],
                                     'scrapePool': target['scrapePool'],
                                     'scrapeUrl': target['scrapeUrl']

                                     })
                            except Exception as e:
                                pass


        except Exception as e:
            pass
        finally:
            return o
