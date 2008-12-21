from sqlalchemy.orm import create_session, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from rdrei.core.local import local, local_manager
from rdrei.utils import application

Base = declarative_base()
metadata = Base.metadata
session = scoped_session(lambda: create_session(application.database_engine,
                         autocommit=False, autoflush=True), local_manager.get_ident)
