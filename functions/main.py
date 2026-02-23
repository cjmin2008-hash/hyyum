from firebase_functions import https_fn
from app import create_app

app = create_app()

@https_fn.on_request()
def flask_app(req):
    """Firebase Functions entry point for Flask app"""
    with app.request_context(req):
        return app.full_dispatch_request()
