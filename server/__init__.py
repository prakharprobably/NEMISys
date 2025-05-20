from flask import Flask
def create(key):
    app = Flask(__name__)
    app.config['SECRET_KEY']=key
    from .router import routes
    from .auth import auth
    from .admin import admin
    from .participantmgr import manage
    from .regatt import regatt
    app.register_blueprint(routes, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/admin/')
    app.register_blueprint(manage, url_prefix='/participants/')
    app.register_blueprint(regatt, url_prefix='/registry/')
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}")
    return app
