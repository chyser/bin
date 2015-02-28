#!/usr/bin/env python
"""
Library:

    simplex algorithm for optimization (LP)

"""

import sys

#-------------------------------------------------------------------------------
def simplex(f,contraints):
#-------------------------------------------------------------------------------
    matrix, ans = create_tableau(f, contraints)

    while True:
        #print "TAB: \n",matrix,ans,"\n\n\n"
        pivot_column = select_pivot_column(matrix)
        if pivot_column == -1:
            result = calculate_answer(matrix, ans)
            break

        pivot_row = select_pivot_row(matrix, ans, pivot_column)
        #print "PIVOT: ",pivot_column,pivot_row,"\n\n\n"
        matrix, ans = pivoting(matrix, ans, pivot_row, pivot_column)

    return result


#-------------------------------------------------------------------------------
def create_tableau(f,constraints):
#-------------------------------------------------------------------------------
        matrix = list()
        ans = list()
        n_dim = len(f)
        n_const = len(constraints)

        for i in range(len(constraints)):
                (c,a) = constraints[i]
                matrix.append(c)
                matrix[i].extend([0.0 for x in range(n_const+1)])
                matrix[i][n_dim+i]=1.0
                ans.append(a)

        matrix.append(f)
        matrix[n_const].extend([0.0 for x in range(n_const+1)])
        matrix[n_const][n_dim+n_const]=1.0
        ans.append(0.0)

        return (matrix,ans)


#-------------------------------------------------------------------------------
def calculate_answer(matrix,ans):
#-------------------------------------------------------------------------------
        answer=list()

        for i in range(len(matrix[0])):
                active = False
                val_active = 0

                for j in range(len(ans)):
                        if matrix[j][i]!=0:
                                if not active:
                                        active=True
                                        val_active = ans[j]/matrix[j][i]
                                else:
                                        val_active=0
                                        break
                answer.append(val_active)
        return answer


#-------------------------------------------------------------------------------
def pivoting(matrix,ans,i,j):
#-------------------------------------------------------------------------------
        piv_val = matrix[i][j]

        for k in range(len(matrix[i])):
                matrix[i][k]=matrix[i][k]/piv_val

        ans[i]=ans[i]/piv_val

        for l in range(len(matrix)):
                if l==i:
                        continue

                new_row = list()
                for k in range(len(matrix[-1])):
                        new_row.append(matrix[i][j]*matrix[l][k]-matrix[l][j]*matrix[i][k])

                ans[l]=matrix[i][j]*ans[l]-matrix[l][j]*ans[i]
                matrix[l]=new_row

        return (matrix,ans)


#-------------------------------------------------------------------------------
def select_pivot_column(matrix):
#-------------------------------------------------------------------------------
    min_val = min(matrix[-1])
    min_i = matrix[-1].index(min_val)

    if min_val < 0.0:
        return min_i
    else:
        return -1


#-------------------------------------------------------------------------------
def select_pivot_row(matrix, ans, pivot_column):
#-------------------------------------------------------------------------------
    pivot_row = -1
    max_val = sys.maxint

    for i in range(len(matrix)-1):
        if matrix[i][pivot_column]>0:
            val = ans[i]/matrix[i][pivot_column]

            if pivot_row==-1 or val < max_val:
                max_val = val
                pivot_row = i

    return pivot_row


#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester

    ans = simplex([-52.4,-73.0,-83.4, -41.8],
    [([1.5,1.0,2.4,1.0],200.0),
    ([1.0,5.0,1.0,3.5],800.0),
    ([1.5,3.0,3.5,1.0],500.0)])

    tester.Assert(ans ==  [29.411764705882376, 150.0, 0, 5.8823529411764568, 0, 0, 0, 12737.058823529411])
    return 0

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss

    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__()
    oss.exit(res)


