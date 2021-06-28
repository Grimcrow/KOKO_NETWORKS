import requests
import logging

_logger = logging.getLogger(__name__)


class InvalidParameters(Exception):
    """Raised when not all parameters are given"""


class JsonApi(object):
    """Class for calling Odoo 11 JSONRPC API

    :keyword kwargs:
        * `username` or `user`: database username
        * `password` or `passwd`: database password
        * `host`: database host
        * `port`: database port, defaults to 8069
        * `database` or `db`: database name

    :raises InvalidParameters: raise when one of the
        parameters is None or empty
    """

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user', kwargs.pop('username', None))
        self.db = kwargs.pop('database', kwargs.pop('db', None))
        self.host = kwargs.pop('host')
        self.port = kwargs.pop('port', 8069)
        self.passwd = kwargs.pop('password', kwargs.pop('passwd', None))

        if not all([self.user, self.db, self.host, self.port, self.passwd]):
            raise InvalidParameters('One or all of the parameters is invalid. '
                                    'Provide username, database, password, host, port.')

        self.__uid = 0

    @property
    def uid(self):
        return self.__uid

    def _authenticate(self):
        auth_url = self._get_jsonrpc_url()
        _logger.debug('Authenticating to url {} using username {}'.format(auth_url, self.user))

        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'service': 'common',
                'method': 'login',
                'args': [self.db, self.user, self.passwd],
            }
        }

        response = requests.post(auth_url, json=data)

        res = response.json()
        error = res.get('error', '')
        if error:
            _logger.debug('Error encounter while authenticating to url {}'.format(auth_url))
            _msg = '{}: {}'.format(error['code'], error['message'])
            raise Exception(_msg)

        result = res['result']
        if not result or not isinstance(result, int):
            _logger.error(res)
            raise Exception('Invalid auth response')

        _logger.debug('Authentication successful')
        self.__uid = result

    def _make_request(self, url, model, method, *args):
        _logger.debug('Making POST request to url {}'.format(url))

        response = requests.post(
            url,
            json={
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'service': 'object',
                    'method': 'execute',
                    'args': [self.db, self.uid, self.passwd, model, method, *args]
                }
            },
        )
        return response.json()

    def _get_jsonrpc_url(self):
        return "http://{}:{}/jsonrpc".format(self.host, self.port)

    def process(self, model, method, *args):
        """Process an Odoo JSONRPC API action

        `context` is omitted when action is create

        :param str model: the model to call
        :param str method: the method to call
        :param list args: parameters to pass to the method
        :return: a JSON-formatted response
        :rtype: str
        """
        if not self.uid:
            self._authenticate()

        url = self._get_jsonrpc_url()
        response = self._make_request(url, model, method, *args)

        # Validate session
        error = response.get('error', '')
        if error and error.get('code', 0) in (100, 200):
            _logger.debug('Session error encountered. Retrying.')
            self._authenticate()
            response = self._make_request(url, model, method, *args)

        return response
