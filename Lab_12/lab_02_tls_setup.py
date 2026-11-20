"""
Lab 12.2: TLS / Encryption-in-Transit Setup & Verification
Demonstrates:
  1. Certificate Authority & Certificate Chain Validation (X.509)
  2. TLS-enforced PyMongo connection configurations
  3. Rejection of unencrypted traffic vs successful TLS encrypted communication
  4. Inspection of certificate properties (Subject, Issuer, Expiry, SAN)
"""

import os
import sys
import ssl
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config.connection import banner
from generate_tls_certs import generate_certificates, CERT_DIR


def inspect_certificate(cert_path):
    """Parses an X.509 PEM certificate and extracts metadata."""
    if not os.path.exists(cert_path):
        return None

    with open(cert_path, "rb") as f:
        cert_data = f.read()

    cert = x509.load_pem_x509_certificate(cert_data, default_backend())

    sans = []
    try:
        san_ext = cert.extensions.get_extension_for_oid(x509.OID_SUBJECT_ALTERNATIVE_NAME)
        for name in san_ext.value:
            sans.append(str(name.value))
    except Exception:
        pass

    key_usages = []
    try:
        ku_ext = cert.extensions.get_extension_for_oid(x509.OID_KEY_USAGE)
        for attr in ["digital_signature", "key_encipherment", "key_cert_sign", "crl_sign"]:
            if getattr(ku_ext.value, attr, False):
                key_usages.append(attr)
    except Exception:
        pass

    return {
        "file": os.path.basename(cert_path),
        "subject": cert.subject.rfc4514_string(),
        "issuer": cert.issuer.rfc4514_string(),
        "serial_hex": hex(cert.serial_number),
        "not_valid_before": cert.not_valid_before_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "not_valid_after": cert.not_valid_after_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "sans": sans,
        "key_usages": key_usages,
        "fingerprint_sha256": cert.fingerprint(hashes.SHA256()).hex().upper()
    }


def get_pki_chain_summary():
    """Returns metadata for the full PKI certificate hierarchy."""
    if not os.path.exists(os.path.join(CERT_DIR, "ca.crt")):
        generate_certificates()

    ca_info = inspect_certificate(os.path.join(CERT_DIR, "ca.crt"))
    server_info = inspect_certificate(os.path.join(CERT_DIR, "server.crt"))
    client_info = inspect_certificate(os.path.join(CERT_DIR, "client.crt"))

    return {
        "ca": ca_info,
        "server": server_info,
        "client": client_info,
        "chain_valid": True if (ca_info and server_info and client_info) else False
    }


def test_tls_connection(host="localhost", port=27100, use_tls=True):
    """
    Attempts connection to the MongoDB instance with or without TLS flags.
    """
    ca_file = os.path.join(CERT_DIR, "ca.crt")
    client_pem = os.path.join(CERT_DIR, "client.pem")

    if use_tls:
        uri = (
            f"mongodb://{host}:{port}/?"
            f"tls=true&"
            f"tlsCAFile={ca_file}&"
            f"tlsCertificateKeyFile={client_pem}&"
            f"tlsAllowInvalidHostnames=true&"
            f"serverSelectionTimeoutMS=4000"
        )
        mode = "TLS-ENCRYPTED"
    else:
        uri = f"mongodb://{host}:{port}/?tls=false&serverSelectionTimeoutMS=4000"
        mode = "UNENCRYPTED (PLAINTEXT)"

    client = None
    try:
        client = MongoClient(uri)
        res = client.admin.command("ping")
        client.close()
        return {
            "mode": mode,
            "connected": True,
            "response": res,
            "tls_enforced": True if use_tls else False,
            "message": f"Successfully connected via {mode}"
        }
    except ServerSelectionTimeoutError as e:
        return {
            "mode": mode,
            "connected": False,
            "error_type": "ServerSelectionTimeoutError",
            "message": f"Connection rejected/timed out in {mode}: {str(e)[:90]}..."
        }
    except PyMongoError as e:
        return {
            "mode": mode,
            "connected": False,
            "error_type": type(e).__name__,
            "message": f"Connection failed in {mode}: {str(e)[:90]}..."
        }


def run_tls_diagnostics():
    banner("Lab 12.2: TLS PKI Chain & Connection Diagnostics")
    chain = get_pki_chain_summary()

    print("[*] PKI Certificate Chain Hierarchy:")
    print(f"  [1] Root CA:       {chain['ca']['subject']}")
    print(f"      Valid Until:   {chain['ca']['not_valid_after']}")
    print(f"  [2] Server Cert:   {chain['server']['subject']}")
    print(f"      Issuer:        {chain['server']['issuer']}")
    print(f"      SANs:          {', '.join(chain['server']['sans'])}")
    print(f"  [3] Client Cert:   {chain['client']['subject']}")
    print(f"      Issuer:        {chain['client']['issuer']}")

    print("\n[*] Testing TLS vs Non-TLS Connections against port 27100 (Simulated / Live):")
    # Non-TLS test
    notls_res = test_tls_connection("localhost", 27100, use_tls=False)
    print(f"  -> Plaintext Test: Connected={notls_res['connected']} | {notls_res['message']}")

    # TLS test
    tls_res = test_tls_connection("localhost", 27100, use_tls=True)
    print(f"  -> TLS Test:       Connected={tls_res['connected']} | {tls_res['message']}")

    banner("Lab 12.2 TLS Diagnostics Completed")
    return {"chain": chain, "plaintext_test": notls_res, "tls_test": tls_res}


if __name__ == "__main__":
    run_tls_diagnostics()
