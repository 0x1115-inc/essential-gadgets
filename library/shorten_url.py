import string
import time
from google.cloud import firestore

class UrlShortener:
    def __init__(self, hostname) -> None:
        self.hostname = hostname
    
    def _generate_id(self) -> id:
            """
            Generates a unique ID based on the current time in nanoseconds.

            Returns:
                id: A unique ID.
            """
            return time.time_ns()
    
    def _hash_id(self, id: int) -> str:
        map = string.ascii_letters + string.digits
        short_id = ""        
        while id > 0:
            id, rem = divmod(id, 62)
            short_id += map[rem]
        return short_id
    
    def shorten(self, url: str) -> str:
        """
        Shortens the given URL.

        Args:
            url (str): The URL to shorten.

        Returns:
            str: The shortened URL.
        """
        id = self._generate_id()        
        short_id = self._hash_id(id)

        return f'https://{self.hostname}/{short_id}'
    
    def get_original_url(self, short_code: str) -> str:
        """
        Retrieves the original URL from the short code.

        Args:
            short_code (str): The short code to look up.

        Returns:
            str: The original URL.
        """

        # TODO: Verify 
        # Initialize Firestore client
        db = firestore.Client()

        # Query the database for the original URL
        doc_ref = db.collection('short_urls').document(short_code)
        doc = doc_ref.get()
        if doc.exists:
            original_url = doc.to_dict().get('original_url')
            return original_url

        return None