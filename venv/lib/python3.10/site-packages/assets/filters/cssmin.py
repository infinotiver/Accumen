from . import register_filter

try:
    from cssmin import cssmin

    @register_filter('cssmin')
    def cssmin_filter(bytes_input, cwd, config={}):
        """
            A CSS minifier based on an (unmaintained) Python port of the YUI cssmin program
        """
        return cssmin(bytes_input)
except:
    @register_filter('cssmin')
    def cssmin_filter(bytes, cwd, config={}):
        """
        A stub for the cssmin filter (the stub does nothing)
        """
        return bytes

