#!/bin/env python

import logging
import opentracing
from opentracing.ext import tags
from opentracing.propagation import Format
from opentracing_instrumentation.request_context import get_current_span, span_in_context
from jaeger_client import Config

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

#format_tracer = init_tracer('formatter')

def formatter(tracer, greeting, name):
    active_span = get_current_span()
    with tracer.start_span('formatter', child_of=active_span) as format_span:
        with span_in_context(format_span):
            return '{} {}!!'.format(greeting.title(), name.title())
