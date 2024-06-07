from flask import Flask, request
from dotenv import load_dotenv
from library.shorten_url import UrlShortener
import re
import os

app = Flask(__name__)

# Get environment variables
load_dotenv()


@app.route('/shorten', methods=['POST'])
def shorten():
    url = request.json['url']
    
    # Check if the URL is valid
    if not re.match(r'^https?://', url):
        return {
            'message': 'Invalid URL'
        }, 400

    url_shortener = UrlShortener(hostname=os.getenv('APP_HOSTNAME', 'localhost:5000'))    

    return {
        'message': 'URL shortened successfully',
        'data': {
            'original_url': url,
            'shortened_url':  url_shortener.shorten(url)
        }
        
    }

@app.route('/<short_code>')
def redirect(short_code):
    url_shortener = UrlShortener(hostname=os.getenv('APP_HOSTNAME', 'localhost:5000'))
    original_url = url_shortener.get_original_url(short_code)
    if original_url:
        return redirect(original_url)
    else:
        return {
            'message': 'Invalid short code'
        }, 404

if __name__ == '__main__':
    app.run()

