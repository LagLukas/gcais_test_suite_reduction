# Reading an excel file using Python
import xlrd
import numpy as np


class PolarionReader:

    COL_OFFSET = 1
    ROW_OFFSET = 6

    def __init__(self, path, transpose=True):
        self.path = path
        self.transpose = transpose

    def available_tests(self, sheet, row, dims):
        for y in range(0, dims[1]):
            if sheet.cell_value(row + PolarionReader.ROW_OFFSET, y + PolarionReader.COL_OFFSET) != "":
                return True
        return False

    def get_covered_req(self, sheet, dims):
        avail = []
        for i in range(0, dims[0]):
            if self.available_tests(sheet, i, dims):
                avail.append(i)
        return avail

    def create_np_matrix(self):
        wb = xlrd.open_workbook(self.path)
        sheet = wb.sheet_by_index(0)
        dims = sheet.cell_value(3, 1).split("x")
        dims = list(map(lambda x: int(x), dims))
        avail = self.get_covered_req(sheet, dims)
        problem_mat = np.zeros((len(avail), dims[1]))
        line = 0
        for index in avail:
            for j in range(0, dims[1]):
                if sheet.cell_value(index + PolarionReader.ROW_OFFSET, j + PolarionReader.COL_OFFSET) != "":
                    problem_mat[line][j] = 1
            line += 1
        if self.transpose:
            return problem_mat.transpose()
        else:
            return problem_mat


if __name__ == "__main__":
    # Give the location of the file
    loc = "polarion.xlsx"
    mat = PolarionReader(loc).create_np_matrix()
    from source.set_cover import SetCover
    prob = SetCover(mat)
    from source.GCAIS import GCAIS
    from source.mylogging import Logging
    from source.greedy import GreedyAlgorithm
    print(GreedyAlgorithm(prob).get_greedy_solution().cost)
    print(mat.shape)
    gcais = GCAIS(prob, 10000)
    logger = Logging("fu.json")
    gcais.set_logging(logger)
    best = gcais.find_approximation()
    print(best.cost)
    print(mat.shape)
    '''
    # To open Workbook
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)
    
    dims = sheet.cell_value(3, 1).split("x")
    dims = list(map(lambda x: int(x), dims))
    
    avail = get_covered_req(sheet, dims)
    
    print(len(avail) / dims[0] * 100)
    '''
