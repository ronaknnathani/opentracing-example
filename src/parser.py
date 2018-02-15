import logging
import requests
import json
import opentracing
from time import sleep
from flask_opentracing import FlaskTracer
import flask
from flask import Flask
from jaeger_client import Config

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return 'This is a Flask parser'


@app.route('/parse', methods=['POST'])
def parse():
    ret_payload = {}
    active_span = tracer.get_span()
    req_json = flask.request.get_json()
    payload = json.loads(req_json['text'])
    active_span.log_kv({'payload': payload})
    ret_payload['name'] = payload['name']
    ret_payload['repos_url'] = payload['repos_url']
    ret_payload['username'] = payload['login']
    return json.dumps(ret_payload)


@app.route('/slow-parse', methods=['POST'])
def slow_parse():
    ret_payload = {}
    active_span = tracer.get_span()
    req_json = flask.request.get_json()
    payload = json.loads(req_json['text'])
    active_span.log_kv({'payload': payload})
    ret_payload['name'] = payload['name']
    ret_payload['repos_url'] = payload['repos_url']
    ret_payload['username'] = payload['login']
    do_something_imp(1)
    do_something_imp(3)
    do_something_imp(2)
    return json.dumps(ret_payload)


def do_something_imp(n):
    active_span = tracer.get_span()
    with open_tracer.start_span('something', child_of=active_span) as something_span:
        sleep(n)

def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()

open_tracer = init_tracer('parser')
tracer = FlaskTracer(open_tracer, True, app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
