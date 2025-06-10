# 회원가입 // 로그인
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    hashed = pwd_context.hash(plain_password)
    return hashed

def verify_password(plain_password: str, hashed: str) -> bool:
    is_valid = pwd_context.verify(plain_password, hashed)
    return is_valid