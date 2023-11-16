from app import create_app
from flask import Flask
from config import Config


app = create_app()

if __name__ == '__main__':
    # Remove debug=True when deploying to production
    app.run(debug=True, host='0.0.0.0', port=8080)
