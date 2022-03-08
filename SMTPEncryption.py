import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class nws_encryption:
    def __init__(self):
        self._enabled = False
        self._method = None
        self.private_key = None
        self.public_key = None
        self.pem = None
        self.encrypted_msg = None
        self.decrypted_msg = None

    def generate_prv_key(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537,
                                                    key_size=2048,
                                                    backend=default_backend())
    def generate_pub_key(self):
        self.public_key = self.private_key.public_key()

    def store_pub_key(self):
        self.pem = self.public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                           format=serialization.PublicFormat.SubjectPublicKeyInfo)
        with open('public_key.pem', 'wb') as f:
            f.write(self.pem)

    def store_prv_key(self):
        self.pem = self.private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                  format=serialization.PrivateFormat.PKCS8,
                                                  encryption_algorithm=serialization.NoEncryption())
        with open('private_key.pem', 'wb') as f:
            f.write(self.pem)

    def read_pub_key(self):
        with open("public_key.pem", "rb") as key_file:
            self.public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
    def read_prv_key(self):
        with open("private_key.pem", "rb") as key_file:
            self.private_key = serialization.load_pem_private_key(key_file.read(),
                                                                  password=None,
                                                                  backend=default_backend()
            )
    def encrypt_rsa(self, msg):
        self.encrypted_msg = self.public_key.encrypt(
            msg,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None))

    def decrypt_rsa(self, msg):
        self.decrypted_msg = self.private_key.decrypt(
            msg,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None))

    def toggle_enable(self):
        self._enabled = not self._enabled
        return self._enabled

    def set_caesar_key(self, key):
        try:
            self._caesarkey = int(key)
        except TypeError:
            self._caesarkey = 0
            return None
        return self._caesarkey

    def set_vigenere_key(self, key):
        try:
            self._vigenerekey = str(key)
        except TypeError:
            self._vignerekey = "Derby"
            return None
        return self._caesarkey

    def set_method(self, method):
        if method.lower() == "caesar":
            self._method = "caesar"
        elif method.lower() == "vigenere":
            self._method = "vigenere"
        else:
            self._method = None

    def encrypt(self, message) -> str:
        if self._enabled:
            if self._method == "caesar":
                return self._caesarcipherencrypt(message)
            elif self._method == "vigenere":
                return self._vigeneresquareencrypt(message)
        return message

    def decrypt(self, message) -> str:
        if self._enabled:
            if self._method == "caesar":
                return self._caesarcipherdecrypt(message)
            elif self._method == "vigenere":
                return self._vigeneresquaredecrypt(message)
        return message

    def _caesarcipherencrypt(self, message) -> str:
        try:
            message = str(message)
        except TypeError:
            return ""

        # perform caesar cipher here

    def _vigeneresquareencrypt(self, message) -> str:
        try:
            message = str(message)
        except TypeError:
            return ""

        # perform vigenere square here

    def _caesarcipherdecrypt(self, message) -> str:
        try:
            message = str(message)
        except TypeError:
            return ""

        # perform caesar cipher here

    def _vigeneresquaredecrypt(self, message) -> str:
        try:
            message = str(message)
        except TypeError:
            return ""

        # perform vigenere square here



