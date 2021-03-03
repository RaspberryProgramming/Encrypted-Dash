import pgpy
import getpass

class PgpInterface:
    """
    """
    privatekey = None
    publickey = None
    __password = None
    def init(self):
        pass

    def load_keys(self, privatefile=None, publicfile=None):
        """
        """
        if privatefile != None:
            self.privatekey,_ = pgpy.PGPKey.from_file(privatefile)

        if publicfile != None:
            self.publickey,_ = pgpy.PGPKey.from_file(publicfile)

    def encrypt(self, data):
        """
        """
        message = pgpy.PGPMessage.new(data)
        enc_message = self.publickey.encrypt(message)
        return bytes(enc_message)

    def decrypt(self, encdata):
        """
        """
        message = pgpy.PGPMessage.from_blob(encdata)
        if self.__password == None:
            self.__password = getpass.getpass()

        with self.privatekey.unlock(self.__password):
            return self.privatekey.decrypt(message).message


if __name__ in '__main__':
    pgp = PgpInterface()
    pgp.load_keys(privatefile="privatekey.asc", publicfile="publickey.asc")
    encdata = pgp.encrypt("Apple".encode())
    decdata = pgp.decrypt(encdata)
    print(encdata)
    print(decdata)
