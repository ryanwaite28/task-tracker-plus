import sys, os, string, random, psycopg2

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy import create_engine, desc
from sqlalchemy.sql import func

from chamber import uniqueValue



Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id                  = Column(Integer, primary_key = True)
    displayname         = Column(String(80), nullable = False)
    email               = Column(String(80), nullable = False)
    password            = Column(String(80), nullable = False)
    icon                = Column(String, default = '/static/img/anon.png')
    icon_id             = Column(String, default = '')
    tasks_rel           = relationship('Tasks', cascade='delete, delete-orphan', backref="Tasks")
    date_created        = Column(DateTime, server_default = func.now())
    last_loggedin       = Column(DateTime, server_default = func.now())
    last_loggedout      = Column(DateTime)
    unique_value        = Column(String, default = uniqueValue)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'displayname': self.displayname,
            'email': self.email,
            'icon': self.icon,
            'icon_id': self.icon_id,
            'tasks_len': len(self.tasks_rel),
            'date_created': str(self.date_created),
            'last_loggedin': str(self.last_loggedin),
            'last_loggedout': str(self.last_loggedout),
            'unique_value': self.unique_value
        }

    @property
    def serialize_small(self):
        return {
            'id': self.id,
            'displayname': self.displayname,
            'email': self.email,
            'icon': self.icon,
            'unique_value': self.unique_value
        }



class ResetPasswordRequests(Base):
    __tablename__ = 'reset_password_requests'

    id                  = Column(Integer, primary_key = True)
    user_email          = Column(String(100), nullable = False)
    date_created        = Column(DateTime, server_default = func.now())
    unique_value        = Column(String, default = uniqueValue)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_email': self.user_email,
            'date_created': str(self.date_created),
            'unique_value': self.unique_value
        }

# https://stackoverflow.com/questions/5649385/many-to-one-relationship-with-sqlalchemy-in-the-same-table
# https://docs.sqlalchemy.org/en/13/orm/self_referential.html
class Tasks(Base):
    __tablename__ = 'tasks'

    id                  = Column(Integer, nullable = False, primary_key = True)
    owner_id            = Column(Integer, ForeignKey('users.id'))
    owner_rel           = relationship('Users')

    parent_task_id      = Column(Integer, ForeignKey('tasks.id'), nullable = True)
    parent_task         = relationship('Tasks', remote_side=[id])

    text                = Column(String, nullable = False)
    notes               = Column(Text, nullable = False, default = "")
    done                = Column(Boolean, default = False)
    subtasks            = relationship('Tasks', cascade='delete, delete-orphan', backref=backref('parent', remote_side=[id]))
    date_created        = Column(DateTime, server_default = func.now())
    last_updated        = Column(DateTime, nullable = True)
    due_date            = Column(DateTime, nullable = True)
    unique_value        = Column(String, default = uniqueValue)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'parent_task_id': self.parent_task_id,
            'text': self.text,
            'notes': self.notes,
            'done': self.done,
            'subtasks': [st.serialize for st in self.subtasks],
            'date_created': str(self.date_created),
            'last_updated': str(self.last_updated) if self.last_updated else None,
            'due_date': str(self.due_date) if self.due_date else None,
            'unique_value': self.unique_value
        }


class Notifications(Base):
    __tablename__ = 'notifications'

    id                  = Column(Integer, nullable = False, primary_key = True)
    owner_id            = Column(Integer, ForeignKey('users.id'))
    owner_rel           = relationship('Users')
    header              = Column(Text, nullable = False)
    message             = Column(Text, nullable = False)
    date_created        = Column(DateTime, server_default = func.now())
    unique_value        = Column(String, default = uniqueValue)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'header': self.header,
            'message': self.message,
            'date_created': str(self.date_created),
            'last_updated': str(self.last_updated),
            'unique_value': self.unique_value
        }




# --- Create Database Session --- #

sqlite_file = "sqlite:///database.db"
db_string = os.environ.get('DATABASE_URL', sqlite_file)
app_state = ''

if db_string[:8] == 'postgres':
    app_state = 'production'
    print('--- production ---')
else:
    app_state = 'development'
    print('--- development ---')

engine = create_engine(db_string, echo=True)
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
db_session = DBSession()
