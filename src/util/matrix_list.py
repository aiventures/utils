""" manipulating two dimensional lists """

class MatrixList():
    
    @staticmethod
    def normalize(matrix:list,fill:any=None)->list:
        """ fill up lists with fill element so as to get a rectangular matrix  """
        _max_elems = max([len(_lines) for _lines in matrix])
        for _line in matrix:
            _num_fills = _max_elems - len(_line)
            if _num_fills == 0:
                continue
            _line.extend(fill * _num_fills)
        return matrix
    
    @staticmethod
    def transpose_matrix(matrix:list,normalize:bool=False,fill:any=None)->list:
        """" transpose a list of list aka matrix the good old way """
        if normalize:
            matrix = MatrixList.normalize(matrix,fill)
        _rows = len(matrix)
        _cols = len(matrix[0])
        out = []
        for _c in range(_cols):
            _line=[]
            for _r in range(_rows):
                _line.append(matrix[_r][_c])
            out.append(_line)
        return out    

    @staticmethod
    def reshape2rows(matrix:list,normalize:bool=False,fill:any=None)->list:
        """ reshaping list to rows 
               [0] [1]
          [0]  |a | d|     [0] [a,b]
          [1]  |b | e| =>  [1] [b,e] 
          [2]  |c | f|     [2] [c,f]
        """
        out = []
        if normalize:
            matrix = MatrixList.normalize(matrix,fill)        
        _num_rows = len(matrix[0])
        _num_cols = len(matrix)
        for _row in range(_num_rows):
            _row_list = []
            for _col in range(_num_cols):
                _row_list.append(matrix[_col][_row])
            out.append(_row_list)
        return out
    
    # @todo sum by rows and columns
