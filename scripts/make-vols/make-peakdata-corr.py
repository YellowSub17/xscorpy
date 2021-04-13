import numpy as np

import scorpy

## PeakData

runs150 = [112,123,113,125,102,103,104,105]
runs144 = [118,108,119,109,120,110,121]
runs = runs150+runs144

geo = scorpy.ExpGeom('../data/geoms/agipd_2304_vj_opt_v3.geom')

for run in runs:
    print(f'Run: {run}')
    peaks = scorpy.PeakData(f'../data/cxi/{run}/peaks.txt', geo)

    cor = scorpy.CorrelationVol(100,180, 1.4)

    for frame in peaks.split_frames():
        if frame.qlist.shape[0] < 150:
            cor.correlate(frame.qlist[:,-3:])
    cor.save_dbin(f'../data/dbins/cosine_sim/{run}/run{run}_qcor')




## PeakData (Half runs)

runs150 = [112,123,113,125,102,103,104,105]
runs144 = [118,108,119,109,120,110,121]
runs = runs150+runs144

geo = scorpy.ExpGeom('../data/geoms/agipd_2304_vj_opt_v3.geom')

for run in runs:

    print(f'Run: {run}')
    peaks = scorpy.PeakData(f'../data/cxi/{run}/peaks.txt', geo)
    frames = [i for i in peaks.split_frames() if i.qlist.shape[0]<150]
    half_ind = int(len(frames)/2)


    for seed in range(20):
        print(f'Seed: {seed}')

        correl_frames = list(frames)
        np.random.shuffle(correl_frames)

        cora_frames = correl_frames[:half_ind]
        corb_frames = correl_frames[half_ind:]

        cora = scorpy.CorrelationVol(100,180, 1.4)
        for frame in cora_frames:
            cora.correlate(frame.qlist[:,-3:])
        cora.save_dbin(f'../data/dbins/cosine_sim/{run}/run{run}_seed{seed}a_qcor')

        corb = scorpy.CorrelationVol(100,180, 1.4)
        for frame in corb_frames:
            corb.correlate(frame.qlist[:,-3:])
        corb.save_dbin(f'../data/dbins/cosine_sim/{run}/run{run}_seed{seed}b_qcor')


