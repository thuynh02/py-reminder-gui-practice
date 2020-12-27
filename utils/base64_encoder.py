import base64


def encode_file(path):
    with open(path, "rb") as image_file:
        encoded_bytes = base64.b64encode(image_file.read())

    return encoded_bytes
