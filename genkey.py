from Crypto.PublicKey import RSA

def generateNewKeys():
    """
    Generates and returns new keys

    return: private_key, public_key
    """
    key = RSA.generate(1024) # Generate private key

    # Extract the private key
    private_key = key.export_key()

    # Extract the public key
    public_key = key.publickey().export_key()
    return private_key, public_key

def writeNewKeys():
    """
    Write new private and public keys as private.pem and public.pem
    """
    key = RSA.generate(1024) # Generate private key

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
