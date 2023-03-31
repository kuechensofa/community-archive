import os
import mimetypes


def get_content_type(file):
    _, ext = os.path.splitext(file.name)

    mimetypes.init()
    ext = ext.lower()

    if ext in mimetypes.types_map:
        return mimetypes.types_map[ext]

    if ext == '.wacz':
        return 'application/wacz'

    return 'application/octet-stream'
