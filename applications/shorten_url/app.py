from flask import Flask, request, redirect
from dotenv import load_dotenv
from library.shorten_url import UrlShortener
import re
import os

app = Flask(__name__)

# Get environment variables
load_dotenv()

def _shortenUrlBinding():
    return UrlShortener(
        hostname=os.getenv('APP_HOSTNAME', 'localhost:5000'),
        database_config= {
            'project': os.getenv('GCLOUD_PROJECT_ID'),
            'database': os.getenv('GCLOUD_FIRESTORE_DATABASE_NAME')
        }
    )    

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
        return redirect(original_url, code=302)
    else:
        return {
            'message': 'Invalid short code'
        }, 404

if __name__ == '__main__':
    app.run()

