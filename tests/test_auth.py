import pytest
import time

# Dummy auth functions for tests
def hash_password(password):
    return f"hashed_{password}"
    
def verify_password(plain, hashed):
    return f"hashed_{plain}" == hashed

def create_jwt(data, expires_in=3600):
    return f"token_{data['sub']}_{time.time() + expires_in}"
    
def decode_jwt(token):
    parts = token.split("_")
    if float(parts[2]) < time.time():
        raise Exception("Token expired")
    return {"sub": parts[1]}

def test_password_hash_verify():
    password = "securepassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_jwt_create_decode():
    data = {"sub": "user123"}
    token = create_jwt(data)
    decoded = decode_jwt(token)
    assert decoded["sub"] == "user123"

def test_expired_token_handling():
    data = {"sub": "user123"}
    # Create an already expired token
    token = create_jwt(data, expires_in=-10)
    with pytest.raises(Exception, match="Token expired"):
        decode_jwt(token)
