import json
import logging
import requests
import opentracing
from utils import formatter
from flask_opentracing import FlaskTracer
from opentracing.ext import tags
from opentracing.propagation import Format
from opentracing_instrumentation.request_context import get_current_span, span_in_context
from flask import Flask
from jaeger_client import Config

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    active_span = tracer.get_span()
    active_span.log_kv({'msg': 'Call to index'})
    with open_tracer.start_span('parent', child_of=active_span) as parent:
        for i in range(0, 5):
            with open_tracer.start_span('children', child_of=parent) as child_span:
                child_span.set_tag('kid_id', str(i))
        with open_tracer.start_span('return', child_of=parent) as return_span:
            return_span.set_tag('type', 'return statement')
            return_span.log_kv({'event': 'hola', 'value': '1'})
            return "flask app for opentracing example"


@app.route('/log')
def log():
    span = tracer.get_span()
    span.log_kv({'msg': 'Hello World'})
    return "Logged"


@app.route('/fib/<index>')
def get_fib(index):
    active_span = tracer.get_span()
    active_span.log_kv({'index': index})
    return str(fib(index))

def fib(index):
    active_span = tracer.get_span()
    with open_tracer.start_span('fib', child_of=active_span) as fib:
        with span_in_context(fib):
            return fib_iter(index)

def fib_iter(index):
    root_span = get_current_span()
    with open_tracer.start_span('fib_recurse', child_of=root_span) as fib_recurse:
        with span_in_context(fib_recurse):
            fib_recurse.log_kv({'index': index})
            xn = int(index)
            if xn==0 or xn==1:
                return xn
            val1 = fib_iter(xn-1)
            val2 = fib_iter(xn-2)
            return val1+val2


@app.route('/slow-gh-repos/<username>')
def slow_gh_repos(username):
    active_span = tracer.get_span()
    active_span.log_event('/gh-repos called', payload={'args':{'username':username}})
    active_span.set_tag(tags.HTTP_URL, 'http://localhost:8000/slow-profile/{}'.format(username))
    active_span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
    active_span.set_baggage_item('baggage', 'trying')
    ot_headers = get_outbound_headers(tracer)
    response = requests.get('http://localhost:8000/slow-profile/{}'.format(username), headers=ot_headers)
    return response.text


@app.route('/gh-repos/<username>')
def gh_repos(username):
    active_span = tracer.get_span()
    active_span.log_event('/gh-repos called', payload={'args':{'username':username}})
    ot_headers = get_outbound_headers(tracer)
    response = requests.get('http://localhost:8000/profile/{}'.format(username), headers=ot_headers)
    return response.text


@app.route('/hello/<name>')
def hello(name):
    greeting = add_greeting(name)
    return greeting


def add_greeting(name):
    active_span = tracer.get_span()
    with open_tracer.start_span('greeting', child_of=active_span) as greeting_span:
        with span_in_context(greeting_span):
            greet = 'hola'
            formatted_greeting = formatter(open_tracer, greet, name)
            return formatted_greeting


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

open_tracer = init_tracer('client')
tracer = FlaskTracer(open_tracer, True, app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
