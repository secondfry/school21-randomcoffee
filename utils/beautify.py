import json

import jsbeautifier
from requests import Response

_opts = jsbeautifier.default_options()
_opts.indent_size = 2


def beautify(json_data) -> str:
    return beautify_str(json.dumps(json_data))


def beautify_str(data: str) -> str:
    return jsbeautifier.beautify(data, _opts)


def beautify_response(res: Response) -> str:
    return beautify(res.json())
