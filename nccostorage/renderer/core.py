import jinja2


class RenderError(Exception):
    pass


class Jinja2NccoRenderer(object):

    def __init__(self):
        self._env = jinja2.Environment(undefined=jinja2.StrictUndefined)

    def render(self, ncco, render_params):
        template = self._env.from_string(ncco)

        try:
            rendered_ncco = template.render(render_params)
        except jinja2.exceptions.UndefinedError:
            raise RenderError('missing params while rendering ncco')

        return rendered_ncco
