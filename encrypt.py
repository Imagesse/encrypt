import socket
import threading
import os
import base64
import hashlib
import random
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.connections = []

    def accept_connections(self):
        while True:
            client_socket, client_address = self.socket.accept()
            print(f"Verbindung von {client_address} akzeptiert.")
            self.connections.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024)
                if message:
                    decrypted_message = self.decrypt_message(message)
                    print(f"Empfangene Nachricht: {decrypted_message}")
                    response = self.encrypt_message("Nachricht empfangen")
                    client_socket.send(response)
                else:
                    break
        except Exception as e:
            print(f"Fehler bei der Verarbeitung der Nachricht: {e}")
        finally:
            client_socket.close()

    def encrypt_message(self, message):
        key = self.generate_key()
        cipher = Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_message = self.pad_message(message)
        encrypted_message = encryptor.update(padded_message.encode()) + encryptor.finalize()
        return encrypted_message

    def decrypt_message(self, encrypted_message):
        key = self.generate_key()
        cipher = Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
        return self.unpad_message(decrypted_message.decode())

    def generate_key(self):
        password = b"mein_sicheres_passwort"
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
        key = kdf.derive(password)
        return key

    def pad_message(self, message):
        pad_length = 16 - len(message) % 16
        return message + chr(pad_length) * pad_length

    def unpad_message(self, message):
        pad_length = ord(message[-1])
        return message[:-pad_length]

class SecureClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect((self.host, self.port))

    def send_message(self, message):
        encrypted_message = self.encrypt_message(message)
        self.socket.send(encrypted_message)
        response = self.socket.recv(1024)
        decrypted_response = self.decrypt_message(response)
        print(f"Antwort vom Server: {decrypted_response}")

    def encrypt_message(self, message):
        key = self.generate_key()
        cipher = Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_message = self.pad_message(message)
        encrypted_message = encryptor.update(padded_message.encode()) + encryptor.finalize()
        return encrypted_message

    def decrypt_message(self, encrypted_message):
        key = self.generate_key()
        cipher = Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
        return self.unpad_message(decrypted_message.decode())

    def generate_key(self):
        password = b"mein_sicheres_passwort"
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
        key = kdf.derive(password)
        return key

    def pad_message(self, message):
        pad_length = 16 - len(message) % 16
        return message + chr(pad_length) * pad_length

    def unpad_message(self, message):
        pad_length = ord(message[-1])
        return message[:-pad_length]

def start_server():
    server = SecureSocket('localhost', 12345)
    server.accept_connections()

def start_client():
    client = SecureClient('localhost', 12345)
    client.connect()
    client.send_message("Hallo Server")

if __name__ == "__main__":
    threading.Thread(target=start_server).start()
    time.sleep(1)
    start_client()
