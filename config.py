import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    #seret key is set in __ini__.py
    #SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'    




    #SQLITE3 connection settings: 

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    #MariaDB mysql database settings
    """
    'mysql+pymysql://'+MYSQL_USER+':'+MYSQL_PASSWORD+'@'+MYSQL_SERVER+'/'+MYSQL_DB+'?charset=utf8mb4'
   
    MYSQL_USER rating
    MYSQL_PASSWORD timotimo
    MYSQL_SERVER localhost
    MYSQL_DB rating_tool_db 
    """