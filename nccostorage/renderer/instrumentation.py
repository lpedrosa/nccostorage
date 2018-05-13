from prometheus_async.aio import count_exceptions, time
from prometheus_client import Counter, Gauge, Histogram


# pylint: disable-msg=no-value-for-parameter
TEMPLATE_REQUEST = Counter('template_count', 'template method call rate')
# pylint: disable-msg=no-value-for-parameter
TEMPLATE_ERROR = Counter('template_error', 'template error rate')
# pylint: disable-msg=no-value-for-parameter
TEMPLATE_TIME = Histogram('template_time', 'template request latency (in seconds)')


class InstrumentedRenderer(object):

    def __init__(self, renderer):
        self._renderer = renderer

    @TEMPLATE_TIME.time()
    def render(self, ncco, render_params):
        TEMPLATE_REQUEST.inc()
        with TEMPLATE_ERROR.count_exceptions():
            return self._renderer.render(ncco, render_params)
