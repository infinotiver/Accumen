import json
import os
import re
import subprocess
import sys
from tempfile import NamedTemporaryFile, gettempdir
from pathlib import Path

from . import register_filter
from .utils import pipe

try:
    import shutil

    if shutil.which('webpack') is not None:
        @register_filter('babel')
        def babel_filter(input_bytes, cwd, config={}):
            """
            A filter for bundling javascript with webpack using the babel loader. Provide
            babel options under the "config.babel" key of a given item in manifest.json
            """

            # Create temporary files
            #    temp_in contains the source to transform
            #    temp_out will contain the transformed source
            temp_in = NamedTemporaryFile(suffix='.js', dir=cwd)
            temp_out = NamedTemporaryFile(suffix='.js')
            temp_cfg = NamedTemporaryFile(suffix='.js', dir=cwd)

            # Construct the configuration
            babel_options = {}
            if hasattr(babel_filter, "_config"):
                babel_options.update(babel_filter._config)
            babel_options.update(config.get('babel', {}))

            webpack_config = {
                "entry": temp_in.name,
                "output": {
                    "path": gettempdir(),
                    "filename": Path(temp_out.name).name
                },
                "module": {
                    "rules": [{
                        "test": "/\.js$/",
                        "exclude": "/(node_modules|bower_components)/",
                        "use": {
                            "loader": "babel-loader",
                            "options": babel_options,
                        }
                    }]
                }
            }
            webpack_config.update(config.get('webpack'))

            # Write the source & config to temporary files
            temp_in.write(input_bytes)
            temp_in.flush()
            temp_cfg.write(bytes("const config="+json.dumps(webpack_config, indent=4)+";module.exports=config;", encoding='utf-8'))
            temp_cfg.flush()

            # Run webpack
            try:
                p = subprocess.run(["webpack", "--config", temp_cfg.name], stdout=sys.stdout, stderr=sys.stderr, cwd=cwd, check=True)
            except:
                print("Error running webpack")
                print("Config:", Path(temp_cfg.name).read_text())
                raise

            # Read the output
            temp_out.seek(0)
            ret = temp_out.read()

            # Cleanup
            temp_out.close()
            temp_in.close()
            temp_cfg.close()

            return ret

    else:
        @register_filter('babel')
        def babel_filter(bytes, cwd, config={}):
            """
            A stub for babel converter (the stub does nothing)
            """
            return bytes
except:
    @register_filter('babel')
    def babel_filter(bytes, cwd, config={}):
        """
        The webpack program not found, this is just a stub. To install
        run

        $ npm -i -g webpack

        """
        return bytes



