import random
import logging
import sys

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Query 


db = SQLAlchemy()

DB_FILENAME = "data_store.sqlite"
db_url = "sqlite:///%s" % (DB_FILENAME)

LOG_FILE_NAME = '/var/log/supervisor/db_app.log'

engine = create_engine(db_url, convert_unicode=True, echo=False)
Base = declarative_base()
Base.metadata.reflect(engine, extend_existing=True)


myseed=1000
base_str = "XYZ"

def setup_logging():   
    try:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)  
   

        handler = logging.FileHandler( LOG_FILE_NAME)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    except Exception as e:
        print ( ' logger exception', str(x) )   

    return None


class Person(db.Model):

    __tablename__ = 'persons'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(100))
    #foo = db.Column(db.ForeignKey('another_MySQLTableName.id'))

    def __repr__(self):
        return "<Person {0} {1}>".format (self.id, self.name) 


def create_table(session, t_name):
    table_name = t_name
    session.execute ( 'CREATE TABLE %s (id Integer PRIMARY_KEY, name VARCHAR VARCHAR(256)) ' % (table_name) )


def insert_into_table(session, nrows, start=1):

    for i in range(start, start+nrows):
        myid =  i
        name = str (base_str[i % len(base_str) ] + str( ( random.randint(i, myseed)) ) )
        a_user = Person(id=myid, name=name)
        db_session.add(a_user)
        db_session.commit()
       

try:

    logger = setup_logging()

   
except Exception as x:
    print ( ' exception', str(x) )
   
    sys.exit(0)



if __name__ == '__main__':

    start_count = 10;
    if len (sys.argv) > 1:
        start_count = int (sys.argv[1])


    db_session = scoped_session(sessionmaker(bind=engine))

  
    try:
        Base.metadata.drop_all(engine)
    except Exception as e:
        logger.info('DROP Exception ... {}' .format (e) )
    
    #This will create all the tables that do not exist yet
    #Required for SQLite 
    
    try:
        Base.metadata.create_all(engine, checkfirst=True)
    except Exception as e:
        logger.info('CREATE Exception ... {}' .format (e) )
    
    try:
        insert_into_table (db_session, 8, start=start_count)        
    except Exception as e:
        logger.info( ' Exception ... {}' .format (e) )
    
    db_session.commit()

    items = db_session.query(Person).all()

    if items:
        for item in items:
            logger.info (item )
    else:
        logger.info( ' no rows in table ')

