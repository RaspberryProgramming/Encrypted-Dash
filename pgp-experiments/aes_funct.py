from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import io

class AesInterface:
    """
    """

    __public_key = None
    __private_key = None

    def __init__(self):
        pass

    def load_keys(self, privatefile=None, publicfile=None):
        if publicfile != None:
            # Load the private key
            try:
                self.__public_key = RSA.import_key(open(publicfile, 'r').read())
            except FileNotFoundError:
                print("[ ! ] Please provide proper public key")

        if privatefile != None:
            #cipher_rsa = PKCS1_OAEP.new(private_key)
            self.__private_key = RSA.import_key(open(privatefile, 'r').read())

    def encrypt(self, data):
        if self.__public_key is not None:
            # Load the private key
            try:
                recipient_key = RSA.import_key(open("public.pem").read())
                session_key = get_random_bytes(16)
            except FileNotFoundError:
                print("[!] Please Generate keys with genkey.py")
                import sys
                sys.exit(0)

            # Encrypt the session key with the public RSA key
            cipher_rsa = PKCS1_OAEP.new(recipient_key)
            enc_session_key = cipher_rsa.encrypt(session_key)
            print(len(enc_session_key))
            # Encrypt the data with the AES session key
            cipher_aes = AES.new(session_key, AES.MODE_EAX)
            ciphertext, tag = cipher_aes.encrypt_and_digest(data)

            print(len(enc_session_key + cipher_aes.nonce + tag + ciphertext))
            return enc_session_key + cipher_aes.nonce + tag + ciphertext

        else:
            print("[ ! ] Please Load Public Key")

    def decrypt(self, data):
        cipher_rsa = PKCS1_OAEP.new(self.__private_key)

        head = 0

        enc_session_key = data[head:head+self.__private_key.size_in_bytes()]
        head += self.__private_key.size_in_bytes()

        nonce = data[head:head+16]
        head += 16

        tag = data[head:head+16]
        head += 16

        ciphertext = data[head:]

        print(len(enc_session_key), len(nonce), len(tag), len(ciphertext))
        # Decrypt the session key
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)

        return data

if __name__ in '__main__':
    aes = AesInterface()
    aes.load_keys(privatefile="private.pem", publicfile="public.pem")
    ciphertext = aes.encrypt("Data".encode())
    plaintext = aes.decrypt(ciphertext)
    print(ciphertext)
    print(plaintext)
