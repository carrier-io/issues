from sqlalchemy.orm.exc import NoResultFound
# from pylon.core.tools import log
from uuid import uuid4
from pylon.core.tools import log
from tools import auth
from tools import db
from PIL import Image
import io


def make_unique_filename(name):
    prefix = uuid4().__str__()
    return f"{prefix}-{name}"


def _wrap_exceptions(fn):
    try:
        return fn()
    except NoResultFound:
        return {"ok": False, "error": "Issue is not found"}, 404
    except Exception as e:
        log.error(e)
        db.session.rollback()
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


def delete_attachments_from_minio(module, attachment):
    module.context.event_manager.fire_event(
        'issues_attachment_deleted', 
        {'attachment': attachment}
    )


def generate_thumbnail(file, size=(132, 85)):
    with Image.open(file) as image:
        image.thumbnail(size)
        thumbnail_data = io.BytesIO()
        ext = file.filename.split('.')[-1]
        image.save(thumbnail_data, format=ext)
        thumbnail_data.seek(0)
        thumb_filename = "thumbnails_" + file.filename
        return thumb_filename, thumbnail_data



def get_users():
    all_users = auth.list_users()
    for user in all_users:
        del user['last_login']   
    return {str(user['id']): user for user in all_users}


