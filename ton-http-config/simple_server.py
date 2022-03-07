from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from urllib.parse import urlparse, parse_qs
import logging
import sys
import base64 as b

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

current_wallet = 1


class SimpleServeFiles(BaseHTTPRequestHandler):
    def do_GET(self):
        global current_wallet
        o = urlparse(self.path)
        params = parse_qs(o.query)

        privelaged = False
        if 'token' in params and params['token'][0] == os.getenv('SHARED_SECRET'):
            privelaged = True

        logger.debug(f"GET, Url: {o.path}, Params: {params}, Privelage: {privelaged}")

        files_to_share = ['config-local.json', 'config.json', 'wallet/valik-wallet.fif', 'wallet/main-wallet.fif']
        if o.path[1:] in files_to_share:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            with open(f'/var/ton-work/network/{o.path[1:]}', 'r') as file:
                json_data = file.read()

                self.wfile.write(json_data.encode(encoding='utf_8'))
        elif privelaged and o.path == '/private':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write('true'.encode())
        elif privelaged and o.path[1:] in ['valik.pk', 'main-wallet.pk', 'main-wallet.addr']:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            with open(f'/var/ton-work/network/wallet/{o.path[1:]}', 'rb') as file:
                data = file.read()
                data = b.b64encode(data).decode()
            self.wfile.write(data.encode(encoding='utf_8'))
        elif o.path == '/wallet':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(f"{current_wallet}".encode())
            current_wallet += 1
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write("<h1>Hi</h1>".encode())


if __name__ == '__main__':
    logger.debug(f"Start listen 🤓")
    simple_serve = HTTPServer(('0.0.0.0', int(os.getenv('PUBLIC_PORT'))), SimpleServeFiles)
    simple_serve.serve_forever()
    logger.debug(f"Stop listen 🤓")
