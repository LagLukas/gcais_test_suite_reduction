import numpy as np
try:
    from source.set_cover import SetCover
except Exception as _:
    from set_cover import SetCover

class BeasleyReader:

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_ptr = open(file_path, "r")

    def read_file(self):
        first = self.file_ptr.readline().split()
        rows = int(first[0]) # rows
        cols = int(first[1]) # sets
        count = -1
        prob_ins = np.zeros((rows, cols))
        linecount = 0
        changecount = 0
        for line in self.file_ptr:
            linecount += 1
            chunks = line.split()
            if len(chunks) == 1 and changecount != linecount - 1:
                count += 1
                changecount = linecount
            elif count != -1:
                for chunk in chunks:
                    index = int(chunk)
                    prob_ins[count - 1][index - 1] = 1
        prob_ins.transpose()
        return SetCover(prob_ins)
