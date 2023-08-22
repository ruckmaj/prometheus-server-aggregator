import server
import aggregator
import time

# Endpoints

endpoints = ['/api/v1/status/buildinfo',
             '/api/v1/status/flags',
             '/api/v1/labels',
             '/api/v1/status/config',
             '/api/v1/targets',
             '/api/v1/alerts',
             '/api/v1/rules',
             '/api/v1/status/runtimeinfo',
             '/api/v1/status/tsdb',
             '/api/v1/status/walreplay',
             '/api/v1/alertmanagers']

try:

    x = server.PrometheusServer(address="192.168.0.227", port=9090)

    s = aggregator.PrometheusAggregator()

    s.add_server(name="server 1", address="192.168.0.227", port=9090)
    s.add_server(name="server 2", address="192.168.0.227", port=9090)

    for endpoint in endpoints:
        s.group_request(resource=endpoint)

    targets = s.targets()


    pass
except Exception as e:
    pass
