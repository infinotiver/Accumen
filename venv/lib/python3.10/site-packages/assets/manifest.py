import os
import json
import re

from django.apps import apps
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.exceptions import ImproperlyConfigured
from django.contrib.staticfiles.templatetags.staticfiles import static

from .storage import ManifestStorage


class Manifest:
    ASSET_LIST = {}

    source_dir = 'static'
    loaded = False
    checksums = {}

    @classmethod
    def to_id(cls, prefix, scope, name):
        """
            Creates a bundle id out of its components, where :param:`prefix` is intended to be
            :param:`scope` the asset type (e.g. javascript, ...) and :param:`name` the name
            of the asset."""
        if prefix is None:
            return ':'.join([scope, name])
        else:
            return ':'.join([prefix, scope, name])

    @classmethod
    def from_id(cls, id):
        """
            Splits a bundle id into its components prefix, scope, name, where :param:`prefix`
            is intended to be :param:`scope` the asset type (e.g. javascript, ...) and
            :param:`name` the name of the asset."""
        parts = id.split(':')
        if len(parts) == 3:
            return parts[0], parts[1], parts[2]
        else:
            return None, parts[0], parts[1]

    @classmethod
    def _tpath(cls, prefix, scope_data, name):
        if prefix is None:
            return os.path.join(scope_data.get('target_dir',''), name) + scope_data.get('target_ext', '')
        else:
            return os.path.join(prefix, scope_data.get('target_dir',''), name) + scope_data.get('target_ext', '')

    @classmethod
    def _match(self, key, id):
        parts = id.split(':')
        pattern = parts[-1]
        stem = id[:-len(pattern)]

        # The prefix:scope: must match exactly
        if not key.startswith(stem):
            return False

        # Now we deal with different patterns

        # Case ``start*``
        if key.startswith(pattern.rstrip('*')):
            return True

        # Case ``*middle*``
        if pattern[0] == '*' and pattern[-1] == '*':
            return pattern.strip('*') in key

        return re.match(pattern, key)

    @classmethod
    def _load_manifest(cls, manifest, prefix=None):
        try:
            if not prefix in cls.checksums:
                cls.checksums[prefix] = {}
                print("Loading checksums from:", cls._tpath(prefix, {}, ManifestStorage._CHECKSUM_NAME))
            with staticfiles_storage.open(cls._tpath(prefix, {}, ManifestStorage._CHECKSUM_NAME)) as CHECKSUMS:
                cls.checksums[prefix].update(json.loads(str(CHECKSUMS.read(), encoding='utf-8')))
        except Exception as ex:
            print("Failed to load checksums", str(ex))
            pass
        for scope_name, scope_data in manifest.items():
            if 'items' in scope_data:
                for item_name, item_data in scope_data['items'].items():
                    key = cls.to_id(prefix, scope_name, item_name)
                    val = cls._tpath(prefix, scope_data, item_name)
                    item_data['checksum'] = cls.checksums[prefix].get(val, '')
                    cls.ASSET_LIST[key] = {'url': static(val), 'data': item_data}
            elif 'copy' in scope_data:
                key = cls.to_id(prefix, scope_name, '*')
                val = cls._tpath(prefix, scope_data, '')
                cls.ASSET_LIST[key] = {'url': static(val), 'data': {}, '__checksum_base__': val}

    @classmethod
    def load(cls):
        locations = []
        app_configs = apps.get_app_configs()
        for app_config in app_configs:
            manifest_path = os.path.join(app_config.path, cls.source_dir, 'manifest.json')
            if os.path.exists(manifest_path):
                manifest = json.load(open(manifest_path, 'r'))
                cls._load_manifest(manifest, app_config.name)
        for root in settings.STATICFILES_DIRS:
            if isinstance(root, (list, tuple)):
                prefix, root = root
            else:
                prefix = ''
            if settings.STATIC_ROOT and os.path.abspath(settings.STATIC_ROOT) == os.path.abspath(root):
                raise ImproperlyConfigured(
                    "The STATICFILES_DIRS setting should "
                    "not contain the STATIC_ROOT setting")
            if (prefix, root) not in locations:
                locations.append((prefix, root))
        for prefix, root in locations:
            manifest_path = os.path.join(root, 'manifest.json')
            if os.path.exists(manifest_path):
                manifest = json.load(open(manifest_path, 'r'))
                cls._load_manifest(manifest, None)

    @classmethod
    def find_assets(cls, bundle_id):
        """
            Returns a list of url, data pairs describing
            the static location of the files in bundle `bundle_id`
            and the data describing the file (e.g. checksum, ...)
        """
        if not cls.loaded:
            cls.load()
        prefix, scope, name = cls.from_id(bundle_id)
        assets = []
        if bundle_id in cls.ASSET_LIST:
            url = cls.ASSET_LIST[bundle_id]['url']
            data = cls.ASSET_LIST[bundle_id]['data']
            assets.append((url, data))
        else:
            key = cls.to_id(prefix, scope, '*')
            if key in cls.ASSET_LIST:
                url = cls.ASSET_LIST[key]['url']+'/'+name
                data = cls.ASSET_LIST[key]['data']
                data['checksum'] = cls.checksums[prefix].get(cls.ASSET_LIST[key].get('__checksum_base__','')+'/'+name, '')
                assets.append((url, data))
            else:
                for (key, val) in cls.ASSET_LIST.items():
                    if cls._match(key, bundle_id):
                        assets.append((val['url'], val['data']))
        return assets
