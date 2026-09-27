import base64
import json
import sys
import unicodedata
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from encrypt import ITERATIONS, OUTPUT_PATH, ROOT, read_keywords


KEYWORDS_PATH = ROOT / "keywords.json"
OUTPUT_PATH_LOCAL = ROOT / "data_plain_decrypted.json"


def main() -> int:
    try:
        keywords = read_keywords(KEYWORDS_PATH)
        encrypted = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        users = encrypted["users"]
        iterations = int(encrypted.get("iterations", ITERATIONS))
        decrypted = {}

        for name, keyword in keywords.items():
            record = users.get(name)
            if not isinstance(record, dict):
                continue
            salt = base64.b64decode(record["salt"], validate=True)
            nonce = base64.b64decode(record["nonce"], validate=True)
            ciphertext = base64.b64decode(record["ciphertext"], validate=True)
            if len(salt) != 16 or len(nonce) != 12:
                raise ValueError(f"Invalid salt or nonce length for {name}")
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations
            )
            normalized_keyword = unicodedata.normalize("NFC", keyword)
            plaintext = AESGCM(kdf.derive(normalized_keyword.encode("utf-8"))).decrypt(
                nonce, ciphertext, None
            )
            decrypted[name] = plaintext.decode("utf-8")

        OUTPUT_PATH_LOCAL.write_text(
            json.dumps(decrypted, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {OUTPUT_PATH_LOCAL.name}")
        return 0
    except Exception as error:
        print(f"Decryption failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())