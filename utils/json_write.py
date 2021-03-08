from utils.beautify import beautify


def json_write(json_data, filename):
    with open(filename, 'w+') as f:
        pretty = beautify(json_data)
        f.write(pretty)
