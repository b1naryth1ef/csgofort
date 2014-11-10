from database import red
from functools import wraps
from flask import Response, g, request
import json

def cacheable(fmt, duration=60):
    def deco(f):
        @wraps(f)
        def _f(*args, **kwargs):
            print args, kwargs
            key = fmt.format(g=g, args=args, kwargs=kwargs)
            r = red.get(key)
            if not r:
                r = f(*args, **kwargs)
                r = [r.get_data(), r.mimetype]
                red.setex(key, json.dumps(r), duration)
            else:
                r = json.loads(r)
            return Response(r[0], mimetype=r[1])
        return _f
    return deco
