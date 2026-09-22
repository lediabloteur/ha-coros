#!/usr/bin/env python3
"""Helper script to obtain a personal COROS MCP OAuth token for Home Assistant.

This script uses only Python standard library modules (no pip install required).
It dynamically registers a client, opens your browser to log in to COROS,
and retrieves your personal refresh and access tokens.
"""

import base64
import hashlib
import json
import os
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8585
REDIRECT_URI = f"http://localhost:{PORT}/callback"
REGISTER_URL = "https://mcpeu.coros.com/connect/register"
AUTH_URL = "https://mcpeu.coros.com/oauth2/authorize"
TOKEN_URL = "https://mcpeu.coros.com/oauth2/token"

auth_code = None
server_error = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code, server_error
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/callback":
            params = urllib.parse.parse_qs(parsed.query)
            if "code" in params:
                auth_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                html = """
                <!DOCTYPE html>
                <html>
                <head><title>Connexion COROS reussie</title></head>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h2 style="color: #2e7d32;">Connexion COROS réussie !</h2>
                    <p>Vous pouvez maintenant fermer cette fenêtre et retourner dans votre terminal.</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode("utf-8"))
            elif "error" in params:
                server_error = params.get("error_description", params["error"])[0]
                self.send_response(400)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                html = f"""
                <!DOCTYPE html>
                <html>
                <head><title>Erreur</title></head>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h2 style="color: #c62828;">Erreur d'autorisation</h2>
                    <p>{server_error}</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence default HTTP server logging
        pass


def generate_pkce():
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    return code_verifier, code_challenge


def register_client():
    print("[1/3] Enregistrement du client OAuth auprès de COROS...")
    payload = json.dumps({
        "client_name": "Home Assistant COROS Integration",
        "redirect_uris": [REDIRECT_URI],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none"
    }).encode("utf-8")

    req = urllib.request.Request(
        REGISTER_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("client_id")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du client OAuth : {e}", file=sys.stderr)
        return None


def main():
    print("=" * 70)
    print(" Assistant d'obtention de jeton COROS MCP pour Home Assistant")
    print("=" * 70)

    client_id = register_client()
    if not client_id:
        print("Impossible d'obtenir un identifiant client auprès de COROS.", file=sys.stderr)
        sys.exit(1)

    code_verifier, code_challenge = generate_pkce()

    # Start local HTTP server
    httpd = HTTPServer(("127.0.0.1", PORT), OAuthCallbackHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "openid mcp.tools offline_access",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": secrets.token_hex(16),
    }
    authorize_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    print("\n[2/3] Ouverture de la page de connexion COROS dans votre navigateur...")
    print(f"Si la page ne s'ouvre pas automatiquement, visitez ce lien :\n{authorize_url}\n")
    try:
        webbrowser.open(authorize_url)
    except Exception:
        pass

    print("En attente de votre autorisation dans le navigateur (délai 120s)...")
    waited = 0
    while auth_code is None and server_error is None and waited < 120:
        threading.Event().wait(1)
        waited += 1

    httpd.shutdown()

    if server_error:
        print(f"\nErreur reçue de COROS : {server_error}", file=sys.stderr)
        sys.exit(1)

    if not auth_code:
        print("\nDélai d'attente dépassé sans confirmation d'autorisation.", file=sys.stderr)
        sys.exit(1)

    print("\n[3/3] Échange du code d'autorisation contre le jeton d'accès...")
    token_params = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,
    }).encode("utf-8")

    req = urllib.request.Request(
        TOKEN_URL,
        data=token_params,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            token_data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Erreur lors de l'échange du jeton : {e}", file=sys.stderr)
        sys.exit(1)

    token_data["client_id"] = client_id
    token_json_str = json.dumps(token_data)

    print("\n" + "=" * 70)
    print(" SUCCÈS ! Votre jeton COROS MCP a été généré avec succès.")
    print("=" * 70)
    print("\nCopiez TOUTE la chaîne ci-dessous et collez-la dans le champ")
    print("'Token MCP COROS' dans Home Assistant (Options de l'intégration) :\n")
    print(token_json_str)
    print("\n" + "-" * 70)
    print("Ou si vous préférez, vous pouvez simplement coller ce refresh_token :")
    print(token_data.get("refresh_token", ""))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
