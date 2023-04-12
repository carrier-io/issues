from tools import db


def init_db():
    from plugins.issues import models
    db.Base.metadata.create_all(bind=db.engine)

