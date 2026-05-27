from peewee import SqliteDatabase, Model, CharField, TextField, DateField, AutoField
from werkzeug.security import generate_password_hash

db = SqliteDatabase('api_app.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    password_hash = CharField()


class Task(BaseModel):
    id = AutoField()
    summary = CharField()
    full_description = TextField()
    due_date = DateField()


def init_db(seed=True):
    db.connect(reuse_if_open=True)
    db.create_tables([User, Task])
    if seed and User.select().count() == 0:
        User.create(username='alice', password_hash=generate_password_hash('password1'))
        User.create(username='bob', password_hash=generate_password_hash('password2'))
    db.close()


def get_user(username):
    db.connect(reuse_if_open=True)
    try:
        return User.get(User.username == username)
    except User.DoesNotExist:
        return None
    finally:
        db.close()
