from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

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
            self.__private_key = RSA.import_key(open(privatefile, 'r').read())

    def encrypt(self, data):
        if self.__public_key is not None:
            cipher = PKCS1_OAEP.new(key=self.__public_key)
            ciphertext = cipher.encrypt(data)

            return ciphertext
        else:
            print("[ ! ]Please Load Public Key")

    def decrypt(self, data):
        decrypt = PKCS1_OAEP.new(key=self.__private_key)
        data = decrypt.decrypt(data)

        return data

if __name__ in '__main__':
    aes = AesInterface()
    aes.load_keys(privatefile="private.pem", publicfile="public.pem")
    ciphertext = aes.encrypt("Data".encode())
    plaintext = aes.decrypt(ciphertext)
    print(ciphertext)
    print(plaintext)
