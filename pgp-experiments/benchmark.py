import aes_funct
import pgp_funct
import random
import time

if __name__ in '__main__':
    aes = aes_funct.AesInterface()
    aes.load_keys(privatefile="private.pem", publicfile="public.pem")
    pgp = pgp_funct.PgpInterface()
    pgp.load_keys(privatefile="privatekey.asc", publicfile="publickey.asc")

    original = ''.join([str(random.randint(0, 9)) for i in range(random.randint(100, 254))]).encode()

    start = time.time()
    ciphertext = aes.encrypt(original)
    plaintext = aes.decrypt(ciphertext)
    stop = time.time()
    print("AES: %s" % (str(stop-start)))

    ciphertext = pgp.encrypt(original)
    plaintext = pgp.decrypt(ciphertext)

    start = time.time()
    ciphertext = pgp.encrypt(original)
    plaintext = pgp.decrypt(ciphertext)
    stop = time.time()
    print("PGP: %s" % (str(stop-start)))
