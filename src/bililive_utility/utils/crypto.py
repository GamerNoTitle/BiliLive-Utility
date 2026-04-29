import sys
import os
import subprocess
import re
import hashlib
import base64

from Crypto.Cipher import AES


def get_machine_id() -> str:
    """
    获取跨平台硬件唯一标识
    """
    if sys.platform == "win32":
        import winreg
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Cryptography",
            )
            guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            return guid
        except Exception:
            pass
    elif sys.platform == "darwin":
        try:
            out = subprocess.check_output(
                ["ioreg", "-d2", "-c", "IOPlatformExpertDevice"], text=True
            )
            m = re.search(r'"IOPlatformUUID"\s*=\s*"([^"]+)"', out)
            if m:
                return m.group(1)
        except Exception:
            pass
    elif sys.platform.startswith("linux"):
        for path in ("/sys/class/dmi/id/product_uuid", "/etc/machine-id"):
            try:
                with open(path) as f:
                    return f.read().strip()
            except Exception:
                pass

    raise RuntimeError("无法获取硬件表示")


def _derive_key(machine_id: str, salt: bytes) -> bytes:
    """
    PBKDF2 从机器 UUID 派生 256 位 AES 密钥
    """
    return hashlib.pbkdf2_hmac(
        "sha256", machine_id.encode(), salt, 100_000, dklen=32
    )


def encrypt_data(plaintext: str) -> str:
    """
    加密数据
    """
    machine_id = get_machine_id()
    salt = os.urandom(16)
    key = _derive_key(machine_id, salt)

    plain_bytes = plaintext.encode()
    pad_len = 16 - len(plain_bytes) % 16
    plain_bytes += bytes([pad_len] * pad_len)

    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(plain_bytes)

    combined = salt + iv + ciphertext
    return base64.b64encode(combined).decode()


def decrypt_data(encrypted: str) -> str:
    """
    解密数据
    """
    combined = base64.b64decode(encrypted)
    salt = combined[:16]
    iv = combined[16:32]
    ciphertext = combined[32:]

    machine_id = get_machine_id()
    key = _derive_key(machine_id, salt)

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    plain_bytes = cipher.decrypt(ciphertext)

    pad_len = plain_bytes[-1]
    plain_bytes = plain_bytes[:-pad_len]
    return plain_bytes.decode()
