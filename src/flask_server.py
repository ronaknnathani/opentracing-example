import logging
import requests
import json
import opentracing
from time import sleep
from flask_opentracing import FlaskTracer
from flask import Flask
from jaeger_client import Config

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return 'This is a Flask server'

@app.route('/profile/<username>')
def get_profile(username):
    active_span = tracer.get_span()
    active_span.log_event('/profiles called', payload={'args':username})
    url = 'https://api.github.com/users/{}'.format(username)
    response = requests.get(url)
    parsed = requests.post(
                'http://localhost:8001/parse',
                json={'text': response.text},
                headers=get_outbound_headers(tracer)).json()
    return json.dumps(parsed)


@app.route('/slow-profile/<username>')
def slow_get_profile(username):
    active_span = tracer.get_span()
    baggage = active_span.get_baggage_item('baggage')
    print(baggage)
    active_span.log_event('/profiles called', payload={'args':username})
    url = 'https://api.github.com/users/{}'.format(username)
    response = requests.get(url)
    parsed = requests.post(
                'http://localhost:8001/slow-parse',
                json={'text': response.text},
                headers=get_outbound_headers(tracer)).json()
    return json.dumps(parsed)


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

def get_outbound_headers(flask_tracer):
    headers = {}
    active_span = flask_tracer.get_span()
    opentracing.tracer.inject(
        active_span.context,
        opentracing.Format.HTTP_HEADERS,
        headers)
    return headers
tracer = FlaskTracer(init_tracer('server'), True, app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
