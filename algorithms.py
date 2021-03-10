
class AesInterface:
    """
    """

    __public_key = None
    __private_key = None

    def __init__(self):
        from Crypto.PublicKey import RSA
        from Crypto.Random import get_random_bytes
        from Crypto.Cipher import AES, PKCS1_OAEP
        import io
        
        self.io = io
        self.RSA = RSA
        self.AES = AES
        self.PKCS1_OAEP = PKCS1_OAEP
        self.get_random_bytes = get_random_bytes

    def load_keys(self, privatefile=None, publicfile=None):
        if publicfile != None:
            # Load the private key
            try:
                self.__public_key = RSA.import_key(open(publicfile, 'r').read())
                self.__session_key = get_random_bytes(16)
            except FileNotFoundError:
                print("[ ! ] Public Key Not Found")

        if privatefile != None:
            #cipher_rsa = PKCS1_OAEP.new(private_key)
            try:
                self.__private_key = RSA.import_key(open(privatefile, 'r').read())
            except FileNotFoundError:
                print("[ ! ] Private Key Not Found")

    def encrypt(self, data):
        """
        encrypt - Encrypts data using class' public key

        data: plaintext byte data to be encrypted

        return: If all goes well the encrypted sequence of data is returned. If there are any errors, an error is displayed, and -1 is returned to signify an error.
        """
        if self.__public_key is not None:

            # Encrypt the session key with the public RSA key
            cipher_rsa = PKCS1_OAEP.new(self.__public_key)
            enc_session_key = cipher_rsa.encrypt(self.__session_key)

            # Encrypt the data with the AES session key
            cipher_aes = AES.new(self.session_key, AES.MODE_EAX)
            ciphertext, tag = cipher_aes.encrypt_and_digest(data)

            return enc_session_key + cipher_aes.nonce + tag + ciphertext

        else:
            print("[ ! ] Please Load Public Key")
            return -1

    def decrypt(self, data):
        if self.__private_key is not None:
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
        
        else:
            print("[ ! ] Please Load Private Key")
            return -1

if __name__ in '__main__':
    aes = AesInterface()
    aes.load_keys(privatefile="private.pem", publicfile="public.pem")
    ciphertext = aes.encrypt("Data".encode())
    plaintext = aes.decrypt(ciphertext)
    print(ciphertext)
    print(plaintext)