import hmac
import hashlib

# Back of the head, remember to verify github uses same method as we do here, 
# sha256 and not sha1 or something else. 
# Also, the signature is in the format "sha256=..." 
# so we need to prepend "sha256=" to our expected signature before comparing.


def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    if not signature:
        return False

    expected = "sha256=" + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)