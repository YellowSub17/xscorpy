#!/usr/bin/env python3
'''
make-padf.py

Make padf vol objects.
'''

import scorpy
import numpy as np
np.random.seed(0)



   



#### MAKE PADF FROM PEAKS DATA CORRELATION
runs150 = [112,123,113,125,102,103,104,105]
runs144 = [118,108,119,109,120,110,121]
runs = runs150+runs144

res = 0.25
rmax = 30


nr = round(rmax/res)


for run in runs:
    cor = scorpy.CorrelationVol(path=f'../data/dbins/cosine_sim/{run}/run{run}_qcor')
    padf = scorpy.PadfVol(nr,cor.ntheta, rmax)

    qcor_path = f'/home/pat/Documents/cloudstor/phd/python_projects/scorpy-pkg/data/dbins/cosine_sim/{run}/run{run}_qcor.dbin'
    padf.fill_from_corr(qcor_path, nl=11)

    padf.save_dbin(f'../data/dbins/cosine_sim/{run}/run{run}_padf')