from abc import ABC, abstractmethod
import string
import time
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from pymongo import MongoClient

class UrlShortener(ABC):
    @abstractmethod
    def shorten(self, url: str) -> str:
        pass

    @abstractmethod
    def get_original_url(self, short_code: str) -> str:
        pass

    @abstractmethod
    def store_visitor_information(self, short_code: str, visitor_info: dict):
        pass

class UrlShortenerFirestore(UrlShortener):
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
             'original_url': url             
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
    
    def store_visitor_information(self, short_code, visitor_info):
        """
        Stores visitor information for the given short code.

        Args:
            short_code (str): The short code for the URL.
            visitor_info (dict): Information about the visitor.
        """
        db = firestore.Client(
            project=self.database_config['project'], 
            database=self.database_config['database']
        )
        doc_ref = db.collection(self.database_config['collection']).document(short_code)
        doc_ref.update({
            'visitors': firestore.ArrayUnion([visitor_info])
        })

        
class UrlShortenerMongoDB(UrlShortener):
    def __init__(self, hostname, database_config) -> None:
        self.hostname = hostname
        self.database_config = database_config
        self.client = MongoClient(self.database_config['uri'])
        self.db = self.client[self.database_config['database']]
        self.collection = self.db[self.database_config['collection']]
    
    def _generate_id(self) -> int:
        return time.time_ns()
    
    def _hash_id(self, id: int) -> str:
        map = string.ascii_letters + string.digits
        short_id = ""        
        while id > 0:
            id, rem = divmod(id, 62)
            short_id += map[rem]
        return short_id
    
    def shorten(self, url: str) -> str:
        id = self._generate_id()
        short_id = self._hash_id(id)
        
        self.collection.insert_one({
            'hash_id': id,
            'short_id': short_id,
            'original_url': url
        })
        
        return f'https://{self.hostname}/{short_id}'
    
    def get_original_url(self, short_code: str) -> str:
        result = self.collection.find_one({'short_id': short_code})
        if result:
            return result['original_url']
        return None
    
    def store_visitor_information(self, short_code, visitor_info):
        self.collection.update_one(
            {'short_id': short_code},
            {'$push': {'visitors': visitor_info}}
        )

class UrlShortenerFactory:
    @staticmethod
    def create_url_shortener(db_type: str, hostname: str, database_config: dict) -> UrlShortener:
        if db_type == 'firestore':
            return UrlShortenerFirestore(hostname, database_config)
        elif db_type == 'mongodb':
            return UrlShortenerMongoDB(hostname, database_config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        