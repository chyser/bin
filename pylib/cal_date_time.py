import calendar


#-------------------------------------------------------------------------------
def getDateDay(yr, mth, day, cnt):
#-------------------------------------------------------------------------------
    """ find the first, last, second etc day (0:6, Mon:Sun) of the specified
        month, mth and year, yr
    """

    cal = calendar.Calendar(6)

    d = [i for i in cal.itermonthdays2(yr, mth)]

    if cnt < 0:
        d.reverse()
        cnt = abs(cnt)

    for dd, ii in d:
        if day == ii and dd != 0:
            cnt -= 1
            if cnt == 0:
                return dd

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    print getDateDay(2007, 11, 6, 1)
    print getDateDay(2007, 11, 6, 2)
    print getDateDay(2007, 11, 6, -1)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(sys.argv)


