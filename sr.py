"""
TODO: FILL ME WITH DOCSTRING
"""

def ev2Time(filename):
    """
    filename: filename in ev format
    Removes ev format and outputs time as a float
    """
    return float(filename[:-4])

def splitRecordings(files, dist=10.0):
    """
    files: list of files using .ev format
    dist: Distance in seconds where each recording must be to split, defaulted to 10.0s
    """
    recordings = []
    recording = -1
    previous = 0.0
    
    for f in files:
        t =ev2Time(f) # Convert the filename to Time float

        if (abs(t-previous) > dist): # Check if this is a part of a new recording
            recording += 1 # Create new recording
            recordings.append([])

        recordings[recording].append(f) # Append the file to it's recording
        previous = t # Set previous to the time file we just appended

    return recordings
