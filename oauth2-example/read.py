import BaseHTTPServer
import os
import sys
from six.moves import urllib
from boxsdk import Client
from boxsdk import OAuth2


class ClientRedirectServer(BaseHTTPServer.HTTPServer):
    """A server to handle OAuth 2.0 redirects back to localhost.

    Waits for a single request and parses the query parameters
    into query_params and then stops serving.
    """
    query_params = {}


class ClientRedirectHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """A handler for OAuth 2.0 redirects back to localhost.

    Waits for a single request and parses the query parameters
    into the servers query_params and then stops serving.
    """
    def do_GET(self):
        """Handle a GET request.
        Parses the query parameters and prints a message
        if the flow has completed. Note that we can't detect
        if an error occurred.
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        query = self.path.split('?', 1)[-1]
        query = dict(urllib.parse.parse_qsl(query))
        self.server.query_params = query
        self.wfile.write(b"<html><head><title>Authentication Status</title></head>")
        self.wfile.write(b"<body><p>The authentication flow has completed.</p>")
        self.wfile.write(b"</body></html>")

    def log_message(self, format, *args):
        """Do not log messages to stdout while running as command line program."""


def store_tokens(access_token, refresh_token):
    # store the tokens at secure storage (e.g. Keychain)
    # do nothing
    return


def call_oauth(oauth):
    auth_url, csrf_token = oauth.get_authorization_url('http://localhost:8888/')
    print('auth_url=%s csrf_token=%s\n' % (auth_url, csrf_token))
    import webbrowser
    webbrowser.open(auth_url, new=1, autoraise=True)


def get_oauth():
    client_id = os.getenv('BOX_CLIENT_ID')
    client_secret = os.getenv('BOX_CLIENT_SECRET')

    if not client_id or not client_secret:
        print('Missing environment variable BOX_CLIENT_ID or BOX_CLIENT_SECRET')
        sys.exit(1)

    oauth = OAuth2(client_id=client_id,
                   client_secret=client_secret,
                   store_tokens=store_tokens)

    call_oauth(oauth)

    httpd = ClientRedirectServer(('0.0.0.0', 8888), ClientRedirectHandler)
    httpd.handle_request()
    print("httpd.query_params=" + str(httpd.query_params))
    access_token, refresh_token = oauth.authenticate(httpd.query_params["code"])
    print(access_token, refresh_token)

    return oauth


def do_main():
    oauth = get_oauth()
    client = Client(oauth)
    me = client.user(user_id='me').get()
    print('user_login: ' + me['login'])
    root_folder = client.folder(folder_id='0').get()
    print('folder owner: ' + root_folder.owned_by['login'])
    print('folder name: ' + root_folder['name'])
    items = client.folder(folder_id='0').get_items(limit=100, offset=0)
    print items

if __name__ == '__main__':
    do_main()
