"""
TODO:
"""
#######################################
# Classes                             #
#######################################

class AesInterface:
    """
    Class that is used to encrypt and decrypt bytedata using Assymetric AES Encryption.
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
        self.file_extension = ".pem"

    def load_keys(self, privatefile=None, publicfile=None):
        """
        load_keys: Loads private and public keys into the class to make encryption/decryption more efficient. This must be run before running any other functions in the class

        privatefile: string with the path to the private key file (must have .pem extension)
        publicfile: string with the path to the public key file (must have .pem extension)
        """
        if publicfile != None:
            # Load the private key
            try:
                self.__public_key = self.RSA.import_key(open(publicfile, 'r').read())
                self.__session_key = self.get_random_bytes(16)
                # Encrypt the session key with the public RSA key
                self.cipher_rsa = self.PKCS1_OAEP.new(self.__public_key)
                self.enc_session_key = self.cipher_rsa.encrypt(self.__session_key)

            except FileNotFoundError:
                print("[ ! ] Public Key Not Found")

        if privatefile != None:
            #cipher_rsa = PKCS1_OAEP.new(private_key)
            try:
                self.__private_key = self.RSA.import_key(open(privatefile, 'r').read())
                self.cipher_rsa = self.PKCS1_OAEP.new(self.__private_key)
            except FileNotFoundError:
                print("[ ! ] Private Key Not Found")

    def encrypt(self, data):
        """
        encrypt - Encrypts data using class' public key

        data: plaintext byte data to be encrypted

        return: If all goes well the encrypted sequence of data is returned. If there are any errors, an error is displayed, and -1 is returned to signify an error.
        """
        if self.__public_key is not None:
            # Encrypt the data with the AES session key
            cipher_aes = self.AES.new(self.__session_key, self.AES.MODE_EAX)

            ciphertext, tag = cipher_aes.encrypt_and_digest(data)

            return self.enc_session_key + cipher_aes.nonce + tag + ciphertext

        else:
            print("[ ! ] Please Load Public Key")
            return -1

    def decrypt(self, data):
        """
        decrypt: decryption function which will encrypt any data passed to it

        data: byte data that will be decrypted
        """
        if self.__private_key is not None:
            
            # Start reading from first beggining

            if data[:3] == b'aes':
                head = 3
            else:
                head = 0

            enc_session_key = data[head:head+self.__private_key.size_in_bytes()] # Read the size of private key starting at head to get session key
            head += self.__private_key.size_in_bytes()

            nonce = data[head:head+16] # Read 16 bytes after to get nonce
            head += 16

            tag = data[head:head+16] # Read 16 Bytes after to get tag
            head += 16

            ciphertext = data[head:] # Read the rest of the file to get ciphertext

            # Decrypt the session key
            session_key = self.cipher_rsa.decrypt(enc_session_key)


            # Decrypt the data with the AES session key
            cipher_aes = self.AES.new(session_key, self.AES.MODE_EAX, nonce)
            data = cipher_aes.decrypt_and_verify(ciphertext, tag)

            return data
        
        else:
            print("[ ! ] Please Load Private Key")
            return -1

#######################################
# Configurations                      #
#######################################

# Stores a dictionary with a keycode used to identify the algorithm in data files to it's mapped
algorithms = {
    '': AesInterface,
    'aes': AesInterface,
    'pgp': None,
}

if __name__ in '__main__':
    aes = AesInterface()
    aes.load_keys(privatefile="private.pem", publicfile="public.pem")

    ciphertext = aes.encrypt(text.encode())
    
    plaintext = aes.decrypt(ciphertext)
    print(ciphertext)
    print(plaintext)
