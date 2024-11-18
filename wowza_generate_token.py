import hashlib
import base64
from urllib.parse import urlparse, urlencode, quote
import re

class WowzaGenerateToken:
    # Constants for hash algorithms
    SHA256 = 1
    SHA384 = 2
    SHA512 = 3

    # Algorithm mapping
    algorithms = {
        SHA256: 'sha256',
        SHA384: 'sha384',
        SHA512: 'sha512'
    }

    def __init__(self, prefix: str, shared_secret: str):
        if not self._is_valid_prefix(prefix):
            raise ValueError(f"Prefix [{prefix}] is invalid")
        self.prefix = prefix

        if not self._is_valid_shared_secret(shared_secret):
            raise ValueError(f"Secret [{shared_secret}] is invalid")
        self.shared_secret = shared_secret

        self.client_ip = None
        self.url = None
        self.url_path = None
        self.hash_method = self.SHA256
        self.params = {}

    @staticmethod
    def _is_valid_prefix(prefix: str) -> bool:
        return bool(re.match(r'^[\w\d%\._\-~]+$', prefix))

    @staticmethod
    def _is_valid_shared_secret(secret: str) -> bool:
        return bool(re.match(r'^[\w\d]+$', secret))

    def set_client_ip(self, ip: str):
        if not re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ip):
            raise ValueError(f"User IP ({ip}) is invalid")
        self.client_ip = ip

    def get_client_ip(self) -> str:
        return self.client_ip

    def set_url(self, url: str):
        url_info = urlparse(url)
        if not url_info.path:
            raise ValueError("Invalid URL supplied")
        self.url = url
        self.url_path = url_info.path

    def get_url(self) -> str:
        return self.url

    def set_hash_method(self, hash_method: int):
        if hash_method not in self.algorithms:
            raise ValueError(f"Algorithm [{hash_method}] not defined")
        self.hash_method = hash_method

    def get_hash_method(self) -> int:
        return self.hash_method

    def set_extra_params(self, params: dict):
        if not isinstance(params, dict):
            raise ValueError("$params must be a dictionary")
        if self.prefix:
            params = {f"{self.prefix}{k}" if not k.startswith(self.prefix) else k: v for k, v in params.items()}
        self.params = params

    def get_params(self) -> dict:
        return self.params

    def get_shared_secret(self) -> str:
        return self.shared_secret

    def get_prefix(self) -> str:
        return self.prefix

    def _params_to_query_string(self) -> str:
        params = self.params.copy()
        if self.client_ip:
            params[self.client_ip] = ''
        params[self.shared_secret] = ''

        sorted_keys = sorted(params.keys())
        query = "&".join(
            f"{key}={quote(str(params[key]))}" if params[key] else key
            for key in sorted_keys
        )
        return query

    def get_hash(self) -> str:
        if not self.shared_secret:
            raise ValueError("SharedSecret is not set")

        query = self._params_to_query_string()
        path = self.url_path.lstrip('/')
        path_items = path.split('/')

        if len(path_items) < 2:
            raise ValueError("Application or stream is invalid")

        path = '/'.join([item for i, item in enumerate(path_items) if not (re.search(r'm3u8|redirect', item) and i == 0)])
        path = path.rstrip('/') + f"?{query}"

        hash_func = hashlib.new(self.algorithms[self.hash_method])
        hash_func.update(path.encode('utf-8'))
        hashed_path = hash_func.digest()
        base64_encoded = base64.b64encode(hashed_path).decode('utf-8')
        token = base64_encoded.replace('+', '-').replace('/', '_')

        return token

    def get_full_url(self) -> str:
        query_string = urlencode(self.params, quote_via=quote)
        token = self.get_hash()
        return f"{self.url}?{query_string}&{self.prefix}hash={token}&type=m3u8"
