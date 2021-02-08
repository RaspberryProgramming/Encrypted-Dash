
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
            self.filename = ""
            self.next = None
            self.previous = None

    def __init__(self):
        self.first = None
        self.last = None

    def append(self, filename):
        """
        Appends new frame to the end of the frame queue

        filename: string variable with filename of the new frame.
        """
        # Create a new frame object for the given filename
        frame = self.Frame()
        frame.filename = filename


        if self.first != None:
            # Set the last frame's next variable to the new frame,
            self.last.next = frame
            frame.previous = self.last
            self.last = frame

        else:

            self.first = frame
            self.last = frame

    def deleteFirst(self):
        if self.first != None:
            if self.first.next == None:
                self.last = None
            else:
                self.first.next.previous = None
            self.first = self.first.next

    def deleteLast(self):
        if self.last != None:
            if self.last.previous == None:
                self.first = None
            else:
                self.last.previous.next = None
            self.last = self.last.previous

    def getLast(self):
        return self.last.filename

    def getFirst(self):
        return self.first.filename

    def popFirst(self):
        filename = self.first.filename
        self.deleteFirst()
        return filename

    def popLast(self):
        filename = self.last.filename
        self.deleteLast()
        return filename
