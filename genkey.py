from Crypto.PublicKey import RSA

def generateNewKeys(keysize=1024):
    """
    Generates and returns new keys
    keysize: size of key, default at 1024

    return: private_key, public_key
    """
    key = RSA.generate(keysize) # Generate private key

    # Extract the private key
    private_key = key.export_key()

    # Extract the public key
    public_key = key.publickey().export_key()
    return private_key, public_key

def writeNewKeys(keysize=1024):
    """
    Write new private and public keys as private.pem and public.pem
    keysize: size of key, default at 1024
    """
    key = RSA.generate(keysize) # Generate private key

    # Write the private key
    private_key = key.export_key()
    file_out = open("private.pem", "wb")
    file_out.write(private_key)
    file_out.close()

    # Extract and write the public key
    public_key = key.publickey().export_key()
    file_out = open("public.pem", "wb")
    file_out.write(public_key)
    file_out.close()

if __name__ in '__main__':
    writeNewKeys()
