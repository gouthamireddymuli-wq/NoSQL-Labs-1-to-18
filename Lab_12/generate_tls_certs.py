"""
Automated TLS Certificate Management for MongoDB (Lab 12.2)
Uses the Python cryptography library to generate:
  1. Self-signed Certificate Authority (CA) key and certificate
  2. Server key, CSR, and CA-signed certificate (with SAN: localhost, 127.0.0.1, mongo)
  3. Combined server.pem (key + cert) for mongod
  4. Client key and CA-signed certificate + client.pem for PyMongo / mongosh TLS authentication
"""

import os
import sys
import datetime
import ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

CERT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tls")


def generate_certificates(output_dir=CERT_DIR, days_valid=365):
    os.makedirs(output_dir, exist_ok=True)
    print("=" * 65)
    print("  MongoDB PKI & TLS Certificate Generator (cryptography library)")
    print("=" * 65)
    print(f"[*] Target Directory: {output_dir}")

    now = datetime.datetime.now(datetime.timezone.utc)
    expiry = now + datetime.timedelta(days=days_valid)

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1: Root Certificate Authority (CA)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[+] Generating Root Certificate Authority (CA)...")
    ca_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    ca_subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "MongoDB-CA"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "NoSQL Security Labs"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Security Operations"),
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
    ])
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_subject)
        .issuer_name(ca_subject)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(expiry)
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    ca_key_path = os.path.join(output_dir, "ca.key")
    ca_crt_path = os.path.join(output_dir, "ca.crt")

    with open(ca_key_path, "wb") as f:
        f.write(ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    with open(ca_crt_path, "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
    print(f"    - CA Key:  {ca_key_path}")
    print(f"    - CA Cert: {ca_crt_path} (Serial: {hex(ca_cert.serial_number)})")

    # ──────────────────────────────────────────────────────────────────────────
    # Step 2: MongoDB Server Certificate (with SAN for localhost and container host)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[+] Generating MongoDB Server Key and Certificate...")
    server_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    server_subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "NoSQL Security Labs"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Database Services"),
    ])
    server_cert = (
        x509.CertificateBuilder()
        .subject_name(server_subject)
        .issuer_name(ca_subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(expiry)
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("mongo"),
                x509.DNSName("mongodb"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.SERVER_AUTH,
                ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    server_key_path = os.path.join(output_dir, "server.key")
    server_crt_path = os.path.join(output_dir, "server.crt")
    server_pem_path = os.path.join(output_dir, "server.pem")
    mongodb_pem_path = os.path.join(output_dir, "mongodb.pem")

    server_key_bytes = server_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    server_crt_bytes = server_cert.public_bytes(serialization.Encoding.PEM)

    with open(server_key_path, "wb") as f:
        f.write(server_key_bytes)
    with open(server_crt_path, "wb") as f:
        f.write(server_crt_bytes)
    # mongod requires concatenated key + cert in PEM format
    with open(server_pem_path, "wb") as f:
        f.write(server_key_bytes + b"\n" + server_crt_bytes)
    with open(mongodb_pem_path, "wb") as f:
        f.write(server_key_bytes + b"\n" + server_crt_bytes)

    print(f"    - Server Key:  {server_key_path}")
    print(f"    - Server Cert: {server_crt_path} (SAN: localhost, mongo, 127.0.0.1)")
    print(f"    - Combined PEM: {server_pem_path} (and {mongodb_pem_path})")

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3: MongoDB Client Certificate (for mTLS / PyMongo authentication)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[+] Generating MongoDB Client Key and Certificate...")
    client_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    client_subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "mongodb_client"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "NoSQL Security Labs"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Client Applications"),
    ])
    client_cert = (
        x509.CertificateBuilder()
        .subject_name(client_subject)
        .issuer_name(ca_subject)
        .public_key(client_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(expiry)
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    client_key_path = os.path.join(output_dir, "client.key")
    client_crt_path = os.path.join(output_dir, "client.crt")
    client_pem_path = os.path.join(output_dir, "client.pem")

    client_key_bytes = client_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    client_crt_bytes = client_cert.public_bytes(serialization.Encoding.PEM)

    with open(client_key_path, "wb") as f:
        f.write(client_key_bytes)
    with open(client_crt_path, "wb") as f:
        f.write(client_crt_bytes)
    with open(client_pem_path, "wb") as f:
        f.write(client_key_bytes + b"\n" + client_crt_bytes)

    print(f"    - Client Key:  {client_key_path}")
    print(f"    - Client Cert: {client_crt_path}")
    print(f"    - Client PEM:  {client_pem_path}")

    print("\n[OK] Certificate generation completed successfully.")
    print("=" * 65)

    return {
        "ca_crt": ca_crt_path,
        "ca_key": ca_key_path,
        "server_pem": server_pem_path,
        "server_crt": server_crt_path,
        "client_pem": client_pem_path,
        "client_crt": client_crt_path,
        "ca_serial": hex(ca_cert.serial_number),
        "server_serial": hex(server_cert.serial_number),
        "client_serial": hex(client_cert.serial_number),
        "valid_until": expiry.strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


if __name__ == "__main__":
    generate_certificates()
