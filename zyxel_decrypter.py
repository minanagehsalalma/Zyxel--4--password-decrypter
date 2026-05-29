import argparse
import base64
import binascii
import re
import sys

from Crypto.Cipher import AES


AES_KEY_HEX = "001200054A1F23FB1F060A14CD0D018F5AC0001306F0121C"
AES_IV_HEX = "0006001C01F01FC0FFFFFFFFFFFFFFFF"
SCHEME4_RE = re.compile(r"\$4\$(?P<salt>[A-Za-z0-9]{8})\$(?P<cipher>[A-Za-z0-9+/=]+)\$")

KEY = binascii.unhexlify(AES_KEY_HEX)
IV = binascii.unhexlify(AES_IV_HEX)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Decrypt Zyxel Scheme ID 4 ($4$) password strings from router configuration data."
        )
    )
    parser.add_argument(
        "input_text",
        help=(
            "Either the full $4$<salt>$<cipher>$ string or an entire config line containing it."
        ),
    )
    parser.add_argument(
        "--salt",
        help="Salt to use when INPUT_TEXT is only the Base64 ciphertext.",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Also print the raw decrypted buffer before password extraction.",
    )
    return parser.parse_args()


def normalize_ciphertext(ciphertext: str) -> str:
    value = ciphertext.strip()
    missing_padding = len(value) % 4
    if missing_padding:
        value += "=" * (4 - missing_padding)
    return value


def extract_inputs(input_text: str, salt_override: str | None) -> tuple[str, str]:
    text = input_text.strip()
    match = SCHEME4_RE.search(text)
    if match:
        return match.group("salt"), match.group("cipher")

    if salt_override:
        salt = salt_override.strip()
        if len(salt) != 8:
            raise ValueError("The Zyxel $4$ scheme expects an 8-byte ASCII salt.")
        return salt, text

    raise ValueError(
        "Could not find a full $4$<salt>$<cipher>$ string. "
        "If you are passing only the Base64 ciphertext, provide --salt."
    )


def decrypt_buffer(ciphertext_b64: str) -> bytes:
    normalized = normalize_ciphertext(ciphertext_b64)
    ciphertext = base64.b64decode(normalized, validate=True)
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return cipher.decrypt(ciphertext)


def extract_password(decrypted: bytes, salt: str) -> str:
    decoded = decrypted.decode("utf-8", errors="ignore")
    start_idx = decoded.find(salt)
    if start_idx == -1:
        raise ValueError("Salt not found in decrypted buffer; input may not be a valid Zyxel $4$ value.")

    start_idx += len(salt)
    end_idx = decoded.find("\x00", start_idx)
    if end_idx == -1:
        end_idx = len(decoded)

    password = decoded[start_idx:end_idx]
    if not password:
        raise ValueError("Extracted password is empty; input may be malformed.")
    return password


def main() -> int:
    args = parse_args()

    try:
        salt, ciphertext = extract_inputs(args.input_text, args.salt)
        decrypted = decrypt_buffer(ciphertext)
        password = extract_password(decrypted, salt)
    except (ValueError, binascii.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Salt: {salt}")
    if args.raw:
        print(f"Decrypted (raw): {decrypted!r}")
    print(f"Decrypted Password: {password}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
