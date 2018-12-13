from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel
from flask import request
from flask import session
from flask import flash
import pymysql

app = Flask(__name__)
#app.config['BABEL_DEFAULT_LOCALE'] = 'fin'
#app.config['BABEL_TRANSLATION_DIRECTORIES'] ='C:/Users/Timo/git/pet-rating/app/translations'
babel = Babel(app)

@babel.localeselector
def get_locale():
    if request.args.get('lang'):

        session['lang'] = request.args.get('lang')
        
        if session['lang'] == 'en':
            session['language'] = 'English'

        if session['lang'] == 'fi':
            session['language'] = 'Finnish'

        if session['lang'] == 'fa':
            session['language'] = 'Persian'

        if session['lang'] == 'el':
            session['language'] = 'Greek'
            
        if session['lang'] == 'it':
            session['language'] = 'Italian'
    
        if session['lang'] == 'zh':
            session['language'] = 'Chinese'

    
    
    return session.get('lang', 'en')



"""
@babel.localeselector
def get_locale():

    if session:
        
        return 'fi'
        
    else:
        
        return 'en'
"""
"""
@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])
"""


#mariabd mysql portti 3306 tarkista?

Bootstrap(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'


app.secret_key = 'random string'
"""app.secret_key = os.urandom(24)"""


from app import routes, models
