from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
#istantiate 
app = Flask(__name__)

#load the routes here

csrf = CSRFProtect()
def create_app():
    from pkg.models import db
    app = Flask(__name__,instance_relative_config=True)

    
#load the routes here
    app.config.from_pyfile("config.py",silent=True)
    db.init_app(app)
    csrf.init_app(app)
    migrate = Migrate(app,db)
    return app
app = create_app()
from pkg import admin_routes,user_routes,admin
from pkg import *