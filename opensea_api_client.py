import json
from typing import Any, Optional

import requests


class OpenSeaAPIException(Exception):
    def __init__(self, response, text):
        self.code = 0
        try:
            json_res = json.loads(text)
        except ValueError:
            self.message = f"Invalid JSON error message from OpenSea: {response.reason}"
        else:
            self.code = json_res["status_code"]
            self.message = json_res["msg"]
        self.response = response
        self.request = getattr(response, "request", None)

    def __str__(self):
        return f"APIError: {self.message}"


class OpenSeaRequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"OpenSeaRequestException: {self.message}"


class Client:
    """OpenSea API Client

    :param api_key: Api Key
    :type api_key: str.
    :param api_secret: Api Secret
    :type api_secret: str.
    :param requests_params: optional - Dictionary of requests params to use for all calls
    :type requests_params: dict.
    """

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, requests_params: dict[str, Any] = None):
        self.API_URL = 'https://api.opensea.io/api/v1'
        self.TESTNET_API_URL = 'https://testnets-api.opensea.io/api/v1'
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self._requests_params = requests_params
        self.session = self._init_session()
        self.response = None

    def _init_session(self) -> requests.Session:
        headers = self._get_headers()
        session = requests.session()
        session.headers.update(headers)
        return session

    def _get_headers(self) -> dict:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',  # noqa
        }
        if self.API_KEY:
            assert self.API_KEY
            headers['X-MBX-APIKEY'] = self.API_KEY
        return headers

    def _get_request_kwargs(self, method, force_params: bool = False, **kwargs) -> dict:
        if self._requests_params:
            kwargs.update(self._requests_params)
        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = data
            if 'requests_params' in kwargs['data']:
                kwargs.update(kwargs['data']['requests_params'])
                del kwargs['data']['requests_params']
        if data and (method == 'get' or force_params):
            kwargs['params'] = '&'.join(f'{data[0]}={data[1]}' for data in kwargs['data'])
            del kwargs['data']
        return kwargs

    def _request(self, method, uri: str, force_params: bool = False, **kwargs):
        kwargs = self._get_request_kwargs(method, force_params, **kwargs)
        self.response = getattr(self.session, method)(uri, **kwargs)
        return self._handle_response(self.response)

    @staticmethod
    def _handle_response(response: requests.Response):
        if not 200 <= response.status_code < 300:
            raise OpenSeaAPIException(response, response.text)
        try:
            return response.json()
        except ValueError:
            raise OpenSeaAPIException(f"Invalid Response: {response.text}")

    def _create_api_uri(self, path: str) -> str:
        url = self.API_URL
        return url + '/' + path

    def _request_api(self, method, path: str,  **kwargs):
        uri = self._create_api_uri(path)
        return self._request(method, uri, **kwargs)

    def _get(self, path, **kwargs):
        return self._request_api('get', path, **kwargs)

    def _post(self, path, **kwargs) -> dict:
        return self._request_api('post', path, **kwargs)

    def _put(self, path, **kwargs) -> dict:
        return self._request_api('put', path, **kwargs)

    def _delete(self, path, **kwargs) -> dict:
        return self._request_api('delete', path, **kwargs)

    def get_assets(
        self, 
        collection: Optional[str] = None, 
        owner: Optional[str] = None, 
        order_direction: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
        ):
        params = {}
        if collection: params.update({'collection': collection.lower()})
        if owner: params.update({'owner': owner})
        if order_direction: params.update({'order_direction': order_direction})
        if limit: params.update({'limit': limit})
        if offset: params.update({'offset': offset})
        return self._get('assets', params=params)

    def get_events(
        self,
        collection: Optional[str] = None, 
        asset_contract_address: Optional[str] = None, 
        token_id: Optional[str] = None, 
        event_type: Optional[str] = None, 
        ):
        params = {}
        if collection: params['collection_slug'] = collection.lower()
        if asset_contract_address: params['asset_contract_address'] = asset_contract_address
        if token_id: params['token_id'] = token_id
        if event_type: params['event_type'] = event_type
        return self._get('events', params=params)

if __name__ == '__main__':
    c = Client()
    # assets_res = c.get_assets(
    #     collection='nft-worlds',
    #     limit=1
    # )
    # print(assets_res)
    events_res = c.get_events(
        event_type='offer_entered'
    )
    print(events_res)