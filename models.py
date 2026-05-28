from peewee import SqliteDatabase, Model, CharField, TextField, DateField, AutoField, ForeignKeyField
from werkzeug.security import generate_password_hash

db = SqliteDatabase('api_app.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    password_hash = CharField()


class Job(BaseModel):
    id = AutoField()
    job_name = CharField()
    short_code = CharField()
    full_description = TextField()
    owner = ForeignKeyField(User, backref='jobs')


class Task(BaseModel):
    STATUS_NEW = 'New'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_COMPLETE = 'Complete'
    STATUS_CHOICES = [STATUS_NEW, STATUS_IN_PROGRESS, STATUS_COMPLETE]

    id = AutoField()
    summary = CharField()
    full_description = TextField()
    due_date = DateField()
    status = CharField(default=STATUS_NEW)
    created_by = ForeignKeyField(User, backref='created_tasks')
    assigned_to = ForeignKeyField(User, null=True, backref='assigned_tasks')
    job_id = ForeignKeyField(Job, null=True, backref='tasks')


def init_db(seed=True):
    db.connect(reuse_if_open=True)
    db.create_tables([User, Job, Task])

    # If the database already exists without the status or job_id columns, add them.
    if db.table_exists('task'):
        existing_columns = [row[1] for row in db.execute_sql("PRAGMA table_info('task')").fetchall()]
        if 'status' not in existing_columns:
            db.execute_sql("ALTER TABLE task ADD COLUMN status TEXT DEFAULT 'New'")
        if 'job_id' not in existing_columns:
            db.execute_sql("ALTER TABLE task ADD COLUMN job_id INTEGER")

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
