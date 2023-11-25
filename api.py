import requests
import hashlib
import os
import time

class DessApiException(Exception):
    pass

class DessAPI:
    def __init__(self, action):
        self.secret = os.getenv("DESS_SECRET")
        self.token = os.getenv("DESS_TOKEN")
        self.action = action
        self.salt_string = None

    # Generate the current timestamp as salt
    def __salt(self):
        if self.salt_string is None:
            self.salt_string  = str(int(time.time()))
      
        return self.salt_string
    
    # Calculate the signature
    def sign(self, **other_params):
        query_params = "&".join([f"{key}={value}" for key, value in other_params.items()])
        signature_raw = self.__salt() + self.secret + self.token + f"&action={self.action}&{query_params}"
        return hashlib.sha1(signature_raw.encode()).hexdigest()
    
    # @return response: Response object
    def get(self, **other_params):
        params = {
            'sign': self.sign(**other_params),
            'salt': self.__salt(),
            'token': self.token,
            'action': self.action,
        }
        # print("&".join([f"{key}={value}" for key, value in {**params, **other_params}.items()]))
        url = "http://web.dessmonitor.com/public/"
        response = requests.get(url, params={**params, **other_params})
        if response.status_code != 200:
            raise DessApiException(f"API returned status code {response.status_code}")
        if "Content-disposition" not in response.headers:
            raise DessApiException("API returned no data - probably expired token & secret.")
        
        return response