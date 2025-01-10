from flask import Flask, request, redirect
from dotenv import load_dotenv
from library.shorten_url import UrlShortenerFactory
from flask_cors import CORS
import re
import os
import time

app = Flask(__name__)
CORS(app)

# Get environment variables
load_dotenv()

def _shortenUrlBinding():
    hostname = os.getenv('APP_HOSTNAME', 'localhost:5000')
    # Replace non readable special characters in string with underscore
    
    config = {
        'database_provider': os.getenv('DATABASE_PROVIDER', 'firestore'),
        'mongodb': {
            'uri': os.getenv('MONGODB_URI'),
            'database': os.getenv('MONGODB_DATABASE_NAME'),
            'collection': f'{re.sub(r"[^a-zA-Z0-9]", "_", hostname)}_urls'
        },
        'firestore': {
            'project': os.getenv('DB_FIRESTORE_PROJECT_ID'),
            'database': os.getenv('DB_FIRESTORE_DATABASE_NAME'),
            'collection': f'{re.sub(r"[^a-zA-Z0-9]", "_", hostname)}_urls'
        }
    }

    provider = config.get('database_provider')
    if provider not in config.keys() or provider == 'database_provider':
        raise ValueError(f'Invalid database provider {provider}')

    return UrlShortenerFactory.create_url_shortener(provider, hostname, config[provider])    

@app.route('/', methods=['POST'])
def shorten():
    url = request.json['url']
    
    # Check if the URL is valid
    if not re.match(r'^https?://', url):
        return {
            'message': 'Invalid URL'
        }, 400

    url_shortener = _shortenUrlBinding()

    return {
        'message': 'URL shortened successfully',
        'data': {
            'original_url': url,
            'shortened_url':  url_shortener.shorten(url)
        }
        
    }

@app.route('/<short_code>')
def fetch_original_url(short_code):
    url_shortener = _shortenUrlBinding()
    original_url = url_shortener.get_original_url(short_code)
    
    if original_url:
        url_shortener.store_visitor_information(short_code, {            
            'timestamp': time.time(),
            'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            'headers': dict(request.headers.items()),            
        })
        return redirect(original_url, code=302)
    else:
        return {
            'message': 'Invalid short code'
        }, 404

if __name__ == '__main__':
    app.run()

