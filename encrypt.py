import base64
import json
import secrets
import sys
import unicodedata
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


ROOT = Path(__file__).resolve().parent
PLAIN_PATH = ROOT / "data_plain.json"
KEYWORDS_PATH = ROOT / "keywords.json"
OUTPUT_PATH = ROOT / "public" / "data.json"
ITERATIONS = 200_000
SALT_LENGTH = 16
NONCE_LENGTH = 12


def read_keywords(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    content = "\n".join(line for line in lines if not line.lstrip().startswith("#"))
    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("keywords.json must contain a JSON object")
    return {
        str(name): keyword
        for name, keyword in data.items()
        if isinstance(keyword, str) and keyword
    }


def read_messages(path: Path, names: list[str]) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("data_plain.json must contain a JSON object")

    if isinstance(data.get("message"), str):
        messages = {name: data["message"] for name in names}
    else:
        messages = data

    return {
        str(name): message
        for name, message in messages.items()
        if isinstance(message, str) and message.strip()
    }


def derive_key(keyword: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    normalized_keyword = unicodedata.normalize("NFC", keyword)
    return kdf.derive(normalized_keyword.encode("utf-8"))


def main() -> int:
    try:
        keywords = read_keywords(KEYWORDS_PATH)
        messages = read_messages(PLAIN_PATH, list(keywords))
        encrypted_users = {}

        for name, keyword in keywords.items():
            message = messages.get(name)
            if message is None:
                continue

            salt = secrets.token_bytes(SALT_LENGTH)
            nonce = secrets.token_bytes(NONCE_LENGTH)
            ciphertext = AESGCM(derive_key(keyword, salt)).encrypt(
                nonce, message.encode("utf-8"), None
            )
            encrypted_users[name] = {
                "salt": base64.b64encode(salt).decode("ascii"),
                "nonce": base64.b64encode(nonce).decode("ascii"),
                "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
            }
            print(f"encrypted {name}")

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(
            json.dumps(
                {"version": 1, "iterations": ITERATIONS, "users": encrypted_users},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print("Wrote public/data.json")
        return 0
    except Exception as error:
        print(f"Encryption failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())