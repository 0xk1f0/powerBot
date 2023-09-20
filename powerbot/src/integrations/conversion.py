import hashlib
import base64

def sha_checksum(input: str, algorithm: str):
    try:
        match algorithm:
            case 'sha1':
                hasher = hashlib.sha1()
            case 'sha224':
                hasher = hashlib.sha224()
            case 'sha256':
                hasher = hashlib.sha256()
            case 'sha384':
                hasher = hashlib.sha384()
            case 'sha512':
                hasher = hashlib.sha512()

        hasher.update(input.encode('utf-8'))
        checksum = hasher.hexdigest()
    except:
        return False

    return checksum

def md5_checksum(input: str):
    try:
        hasher = hashlib.md5()
        hasher.update(input.encode('utf-8'))
        md5_checksum = hasher.hexdigest()
    except:
        return False

    return md5_checksum

def base_encode(input: str, type: str):
    try:
        match type:
            case 'base32':
                encoded = base64.b32encode(input.encode('utf-8')).decode('utf-8')
            case 'base64':
                encoded = base64.b64encode(input.encode('utf-8')).decode('utf-8')
    except:
        return False

    return encoded

def base_decode(input: str, type: str):
    try:
        match type:
            case 'base32':
                decoded = base64.b32decode(input.encode('utf-8')).decode('utf-8')
            case 'base64':
                decoded = base64.b64decode(input.encode('utf-8')).decode('utf-8')
    except:
        return False

    return decoded
