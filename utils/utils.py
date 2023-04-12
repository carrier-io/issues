from sqlalchemy.orm.exc import NoResultFound
# from pylon.core.tools import log
from uuid import uuid4
from pylon.core.tools import log


def make_unique_filename(name):
    prefix = uuid4().__str__()
    return f"{prefix}-{name}"


def _wrap_exceptions(fn):
    try:
        return fn()
    except NoResultFound:
        return {"ok": False, "error": "Issue is not found"}, 404
    except Exception as e:
        log.info(e)
        return {"ok": False, "error": str(e)}, 400        


def make_response(fn, schema, *args, **kwargs):
    def run():
        status_code = 200
        item = fn(*args, **kwargs)
        result = {"ok": True, "item": schema.dump(item)}
        return result, status_code
    return _wrap_exceptions(run)


def make_list_response(fn, schema, *args, **kwargs):
    def run():
        status_code = 200
        items = fn(*args, **kwargs)
        result = {"ok": True, "items": schema.dump(items)}
        return result, status_code
    return _wrap_exceptions(run)


def make_delete_response(fn, *args, **kwargs):
    def run():
        status_code = 200
        fn(*args, **kwargs)
        return {"ok": True}, status_code
    return _wrap_exceptions(run)


def make_create_response(fn, schema, *args, **kwargs):
    def run():
        status_code = 201
        item = fn(*args, **kwargs)
        result = {"ok": True, "item": schema.dump(item)}
        return result, status_code
    return _wrap_exceptions(run)