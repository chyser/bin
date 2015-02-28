#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import math
import pylib.util as util

#-------------------------------------------------------------------------------
def amoritization(principle, numMonths, interestRate, downPayment=0, YR=True, APR=True):
#-------------------------------------------------------------------------------
    interestRate /= 100.0

    if APR:
        interestRate /= 12.0

    if YR:
        numMonths *= 12

    principle -= downPayment
    payment = principle * (interestRate + (interestRate / (pow(1 + interestRate, numMonths) - 1)))

    total = payment * numMonths
    totInt = total - principle

    return payment, total, totInt


#-------------------------------------------------------------------------------
def getPrinciple(payment, numMonths, interestRate, YR=True, APR=True):
#-------------------------------------------------------------------------------
    interestRate /= 100.0

    if APR:
        interestRate /= 12.0

    if YR:
        numMonths *= 12

    principle = payment / (interestRate + (interestRate / (pow(1 + interestRate, numMonths) - 1)))

    return principle


#-------------------------------------------------------------------------------
def amortSched(principle, numMonths, interestRate, downPayment=0, extraMonthly=0, extraYear=None, YR=True, APR=True, date=None, PayDict=None):
#-------------------------------------------------------------------------------
    pmt, tot, toti = amoritization(principle, numMonths, interestRate, downPayment, YR, APR)

    nm = numMonths * 12 if YR else numMonths

    interestRate /= 100.0

    if APR:
        interestRate /= 12.0

    balance = principle
    curPrin = paid = ti = tp = 0

    if PayDict is None:
        PayDict = {}

    if date is not None:
        dd = '       '
        du = '======='
    else:
        dd = du = ''

    print("\n Period %sRemaining   Principle    Monthly   Interest   Monthly" % dd)
    print("        %sPrinciple     Paid      Principle    Paid     Interest" % dd)
    print("==================================================================%s" % du)

    out = False
    for i in range(nm):
        mni = balance * interestRate
        ti += mni
        curPrin = pmt - mni
        tp += curPrin
        balance -= curPrin

        if extraMonthly:
            tp += extraMonthly
            balance -= extraMonthly

        ds = str(date) if date else ''
        date = date.nextMonth()

        if extraYear:
            if date.isMonth('Dec'):
                if extraYear < 6:
                    p = pmt * extraYear
                else:
                    p = extraYear

                balance -= p
                tp += p
                print("\nPayment -> %10.2f\n" % p)

        if i in PayDict:
            p = PayDict[i]
            balance -= p
            tp += p
            print("\nPayment -> %10.2f\n" % p)

        if ds in PayDict:
            p = PayDict[ds]
            balance -= p
            tp += p
            print("\nPayment -> %10.2f\n" % p)

        if balance < 0:
            out = True
            balance = 0

        paid += pmt

        print("%3d: %s %10.2f  %10.2f     %5.2f %10.2f     %5.2f  " % (i, ds, balance, tp, curPrin, ti, mni))

        if out:
            break


#-------------------------------------------------------------------------------
def numPayments(payment, principle, interestRate, APR=True):
#-------------------------------------------------------------------------------
    interestRate /= 100.0

    if APR:
        interestRate /= 12.0

    return int(round(math.log(1 + (1 / (((payment / principle) - interestRate) / interestRate))) / math.log(1 + interestRate)))


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    #import pylib.tester as tester

    payment, total, totInt = amoritization(168000 + 98000, 30, 4.2)

    print(payment, total, totInt)

    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__(verbose=True)
    oss.exit(res)


