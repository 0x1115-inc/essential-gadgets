import string
import time
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

class UrlShortener:
    def __init__(self, hostname, database_config) -> None:
        self.hostname = hostname
        self.database_config = database_config
    
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

        # Store the original URL in Firestore
        db = firestore.Client(
            project=self.database_config['project'], 
            database=self.database_config['database']
        )
        doc_ref = db.collection(self.database_config['collection']).document(short_id)
        doc_ref.set({             
             'hash_id': id,
             'short_id': short_id,             
             'original_url': url,
             'created_at': time.time()            
             })


        return f'https://{self.hostname}/{short_id}'
    
    def get_original_url(self, short_code: str) -> str:
        """
        Retrieves the original URL from the short code.

        Args:
            short_code (str): The short code to look up.

        Returns:
            str: The original URL.
        """
        # Initialize Firestore client
        db = firestore.Client(
            project=self.database_config['project'], 
            database=self.database_config['database']
        )

        # Query database to get original URL with the first matching short code
        query = db.collection(self.database_config['collection']).where(filter=FieldFilter('short_id', '==', short_code)).limit(1)
        doc_ref = query.get()
        
        # If no matching document is found, return None
        if len(doc_ref) == 0:
            return None
        
        # Return the original URL
        return doc_ref[0].get('original_url')
    