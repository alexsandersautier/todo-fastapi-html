import secrets
import hashlib

def get_token():
    return secrets.token_hex(32)
    
    
def cripty(password):
    return hashlib.sha512(password.encode()).hexdigest()
