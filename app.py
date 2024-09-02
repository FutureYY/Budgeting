from flask import Flask
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def home():
    return "Hello, World!"
@app.errorhandler(404)
def not_found(error):
    return "This page was not found!", 404

@app.errorhandler(500)
def internal_error(error):
    return "Internal server error!", 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
