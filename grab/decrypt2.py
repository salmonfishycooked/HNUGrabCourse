from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64


aesKey = "southsoft12345!#"


# decrypt2 will decrypt ciphers from "Graduation System"
def decrypt2(ciphertext: str, key: str = aesKey) -> str:
    special = "==gwJPTxzG0iY2qTiSUo7wB6"[::-1]
    if ciphertext == special:
        return '-'

    keyBytes = key.encode('utf-8')
    ctBytes = base64.b64decode(ciphertext)
    cipher = AES.new(keyBytes, AES.MODE_ECB)
    decrypted = cipher.decrypt(ctBytes)
    plaintext = unpad(decrypted, AES.block_size)

    return plaintext.decode('utf-8')
