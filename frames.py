import os

class Frames:
    """
        Object used to store Queue of frame filenames in order to quickly and
        easily find the first few frames when storage becomes sparse.
    """

    class Frame:
        """
            Object used to represent each frame in the queue.
        """
        def __init__(self):
            self.path = "" # path to the file itself
            self.filename = "" # name of the file
            self.next = None # next Frame in the sequence
            self.previous = None # previous Frame in the sequence

        def algorithm(self):
            f = open(self.path, "rb")
            algorithm = f.read(3)
            f.close()

            return algorithm

        def getTimestamp(self, filename=None):
            """
            Convert .ev filename format to epoch time

            filename: filename in ev format
            """
            if filename == None:
                return float(self.filename[:-4])
            else:
                return float(filename[:-4])

        def __str__(self):
            """
            __str__: returns string when object is refered to as so
            """

            return self.filename

    def __init__(self):
        self.first = None # refers to the first/oldest Frame
        self.last = None # refers to the last/newest Frame

    def __str__(self):
        out = ""
        
        if self.first != None:
            fr = self.first
            
            while fr.next != None:
                out += fr.filename + " => "
                fr = fr.next
            
            out += fr.filename
        

        return out

    def print(self):
        """
        Prints the queue represented with arrows
        """

        print(self)

    def append(self, filename, directory):
        """
        Appends new frame to the end of the frame queue

        filename: string variable with filename of the new frame.
        """
        # Create a new frame object for the given filename
        frame = self.Frame() # Create a new Frame and add a filename to it
        frame.filename = filename
        frame.path = directory + "/" + filename


        if self.first != None: # If Frames already exist

            # Set the last frame's next variable to the new frame,
            self.last.next = frame
            frame.previous = self.last
            self.last = frame

        else: # No Frames exist

            self.first = frame
            self.last = frame

    def deleteFirst(self):
        """
        Deletes the first frame in the sequence with no return
        """

        if self.first != None: # If frames exist

            if self.first.next == None: # If this is the last frame Remove the last reference
                self.last = None
            else: # If other frames exist
                self.first.next.previous = None # set the next's previous reference to None

            self.first = self.first.next # Move first's next frame to the first frame

    def deleteLast(self):
        """
        Deletes the last frame in the sequence
        """

        if self.last != None: # If frames exist

            if self.last.previous == None: # Set first frame to None if there aren't any previous frames
                self.first = None
            else: # Set the last's previous' next to None
                self.last.previous.next = None

            self.last = self.last.previous # Move last's previous frame to the last frame

    def getLast(self):
        """
        Return the last Frame's filename
        """
        if self.last != None:
            return self.last.filename
        else:
            return None

    def getFirst(self):
        """
        Return the first Frame's filename
        """
        if self.first != None:
            return self.first.filename
        else:
            return None

    def popFirst(self):
        """
        Remove the first Frame and return it's value
        """
        if self.first != None:
            filename = self.first.filename
            self.deleteFirst()
            return filename
        else:
            return None
       

    def popLast(self):
        """
        Remove the last Frame and return it's value
        """
        if self.last != None:
            filename = self.last.filename
            self.deleteLast()
            return filename
        else:
            return None
        
    def empty(self):
        if self.last == None:
            return True
        else:
            return False

    def importFrames(self, directory):
        """
        Generates frame object and imports frames from given directory

        directory: directory or path to destined folder with frames
        """

        files = os.listdir(directory) # Get list of files in destination path
        files.sort() # Sort the files in order from oldest to newest frame

        extension = "ev" # extension of files

        for f in files: # Put each file into the Frames object
            fext = f.split(".")[-1] # File extension extracted
            if fext == extension:
                self.append(f, directory)
                
