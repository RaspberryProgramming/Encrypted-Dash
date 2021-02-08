
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
            self.filename = "" # name of the file
            self.next = None # next Frame in the sequence
            self.previous = None # previous Frame in the sequence

    def __init__(self):
        self.first = None # refers to the first/oldest Frame
        self.last = None # refers to the last/newest Frame

    def append(self, filename):
        """
        Appends new frame to the end of the frame queue

        filename: string variable with filename of the new frame.
        """
        # Create a new frame object for the given filename
        frame = self.Frame() # Create a new Frame and add a filename to it
        frame.filename = filename


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
        return self.last.filename

    def getFirst(self):
        """
        Return the first Frame's filename
        """
        return self.first.filename

    def popFirst(self):
        """
        Remove the first Frame and return it's value
        """

        filename = self.first.filename
        self.deleteFirst()

        return filename

    def popLast(self):
        """
        Remove the last Frame and return it's value
        """
        filename = self.last.filename
        self.deleteLast()

        return filename
