from collections import defaultdict

from django import template
from django.template import Context, Template
from django.utils.safestring import mark_safe


# If we have jinja2 templates
try:
    from django_jinja import library
except:
    class library:
        global_function = lambda x: x
        filter = lambda x: x

from ..manifest import Manifest

register = template.Library()


class SimpleTemplate:
    def __init__(self, code):
        self.code = code
        self._compiled = None

    def _compile(self):
        self._compiled = Template(self.code)

    def render(self, ctx):
        if not self._compiled:
            self._compile()
        return self._compiled.render(ctx)

SCOPE_TEMPLATES = defaultdict(lambda: SimpleTemplate('{{ url }}'), {
    'javascript': SimpleTemplate("<script src='{{ url }}?{{ checksum }}' {% if checksum %}integrity='sha256-{{ checksum }}'{% endif %} crossorigin='anonymous' ></script>"),
    'scripts': SimpleTemplate("<script src='{{ url }}?{{ checksum }} {% if checksum %}integrity='sha256-{{ checksum }}'{% endif %} crossorigin='anonymous' '></script>"),
    'js': SimpleTemplate("<script src='{{ url }}?{{ checksum }} {% if checksum %}integrity='sha256-{{ checksum }}'{% endif %} crossorigin='anonymous' '></script>"),

    'stylesheets': SimpleTemplate("<link rel='stylesheet' href='{{ url }}?{{ checksum }}' type='text/css' {% if checksum %}integrity='sha256-{{ checksum }}'{% endif %} crossorigin='anonymous' ></link>"),
    'styles': SimpleTemplate("<link rel='stylesheet' href='{{ url }}?{{ checksum }}' type='text/css' {% if checksum %}integrity='sha256-{{ checksum }}'{% endif %} crossorigin='anonymous' ></link>"),

    'images': SimpleTemplate("<img src='{{ url }}?{{ checksum }}'>"),
})


@register.simple_tag
@library.global_function
def asset(bundle_id):
    prefix, scope, name = Manifest.from_id(bundle_id)
    assets = Manifest.find_assets(bundle_id)
    if len(assets) == 0:
        raise Exception("Asset not found:", bundle_id)
    out = []
    for (url, data) in assets:
        ctx = Context(data)
        ctx['url'] = url
        tpl = SCOPE_TEMPLATES[scope]

        out.append(tpl.render(ctx))
    return mark_safe("\n".join(out))

@register.simple_tag
@library.global_function
def asset_url(bundle_id):
    assets = Manifest.find_assets(bundle_id)
    if len(assets) == 0:
        raise Exception("Asset not found:", bundle_id)
    return mark_safe(" ".join([url for url, _ in assets]))
