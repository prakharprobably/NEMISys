from flask import Flask
def create(key):
    app = Flask(__name__)
    app.config['SECRET_KEY']=key
    from .router import routes
    from .auth import auth
    from .admin import admin
    from .participantmgr import manage
    from .regatt import regatt
    from .discauth import discauth
    from .events import events
    from .confirm import confirm
    from .results import results
    from .about import about
    from .certs import certs
    app.register_blueprint(routes, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/admin/')
    app.register_blueprint(manage, url_prefix='/participants/')
    app.register_blueprint(regatt, url_prefix='/registry/')
    app.register_blueprint(discauth, url_prefix='/discauth/')
    app.register_blueprint(events, url_prefix='/events/')
    app.register_blueprint(confirm, url_prefix='/confirm/')
    app.register_blueprint(results, url_prefix='/results/')
    app.register_blueprint(about, url_prefix='/about/')
    app.register_blueprint(certs, url_prefix='/certs/')
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}")
    return app
