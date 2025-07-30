import os
import sys
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

CONTENT_PLATFORM_DIR = "content_platform"
KEY_SERVER_DIR = "key_server"


if not (os.path.isdir(CONTENT_PLATFORM_DIR) and os.path.isdir(KEY_SERVER_DIR)):
    print(
        "Required directories do not exist.\nWrong working directory?", file=sys.stderr
    )
    sys.exit(1)


private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()


private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
).decode()

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode()


with open(f"{KEY_SERVER_DIR}/.env", "w") as f:
    f.write(f'jwt_pubkey="{public_pem}"\n')

with open(f"{CONTENT_PLATFORM_DIR}/.env", "w") as f:
    f.write(f'jwt_privkey="{private_pem}"\n')
