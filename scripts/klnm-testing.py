#!/usr/bin/env python3
from scorpy.utils import ylm_wrapper
import scorpy
import numpy as np
import matplotlib.pyplot as plt
import timeit
import healpy as hp


plt.close('all')

name = '3wct'
name = '1al1'
cor = scorpy.CorrelationVol(path=f'../data/dbins/{name}_qcor')


#get eigenvectors
bl = scorpy.BlqqVol(cor.nq, 27, cor.qmax)
bl.fill_from_corr(cor)
bl_l, bl_u = bl.get_eigh()


#make initial (target) intensities
cif = scorpy.CifData(f'../data/xtal/{name}-sf.cif', qmax=cor.qmax)
Iv_init = scorpy.SphInten(cor.nq, 2**5, cor.qmax).fill_from_cif(cif)

Iv_mask = Iv_init.copy().make_mask()
#get the spherical harmonics from inital intensity
sph_init = scorpy.SphHarmHandler(cor.nq, bl.nl, cor.qmax).fill_from_ivol(Iv_init)

# filtered inten (cif -> Iv -> sph -> Iv)
Iv_filt = Iv_init.copy().fill_from_sph(sph_init)


# Calculate klnm
sph_Klnm = sph_init.copy().calc_klnm(bl_u)
# Recompose Ilnm
sph_Ilmp = sph_Klnm.copy().calc_Ilm_p(bl_u)
# k data (cif -> Iv -> sph -> klnm -> Ilm' -> Iv)
Iv_data = Iv_init.copy().fill_from_sph(sph_Ilmp)

sf = np.outer(1/np.linspace(1e-19, Iv_data.qmax, Iv_data.nq)**2, np.ones(Iv_data.npix))
Iv_data.ivol *=sf


Iv_data2_sph = sph_init.copy().fill_from_ivol(Iv_data).calc_klnm(bl_u).calc_Ilm_p(bl_u)
Iv_data2 = Iv_init.copy().fill_from_sph(Iv_data2_sph)
Iv_data2.ivol *=sf


# relative intensity ( Iv_fil/k_data )
Iv_rela = Iv_init.copy()
Iv_rela.ivol = (Iv_filt.ivol/Iv_data.ivol)
Iv_rela.ivol[np.where(np.logical_and(Iv_filt.ivol ==0,Iv_data.ivol==0))] = 0

Iv_rela2 = Iv_init.copy()
Iv_rela2.ivol = (Iv_data2.ivol/Iv_data.ivol)
Iv_rela2.ivol[np.where(np.logical_and(Iv_data2.ivol ==0,Iv_data.ivol==0))] = 0

nsphere=14
Iv_init.plot_sphere(nsphere)
plt.title('I_init: Initial Intensity')

Iv_filt.plot_sphere(nsphere)
plt.title('Iv_filt: ivol -> Ilm -> ivol')

Iv_data.plot_sphere(nsphere)
plt.title('Iv_data: ivol -> Ilm -> k -> Ilm -> ivol')

Iv_data2.plot_sphere(nsphere)
plt.title('Iv_data2: Iv_data -> Ilm -> k -> Ilm -> ivol')

Iv_rela.plot_sphere(nsphere)
plt.title('Iv_rela: Iv_filt/Iv_data')
Iv_rela2.plot_sphere(nsphere)
plt.title('Iv_rela2: Iv_data2/Iv_data')



q = np.linspace(0, cor.qmax, cor.nq)

plt.figure()
aves = np.mean(Iv_rela.ivol, axis=-1)
plt.plot(q, aves)
plt.title('Iv_filt/Iv_data')
plt.xlabel('nq')
plt.ylabel('Average Relative Difference')

plt.figure()
aves = np.mean(Iv_rela2.ivol, axis=-1)
plt.plot(q, aves)
plt.title('Iv_data2/Iv_data')
plt.xlabel('nq')
plt.ylabel('Average Relative Difference')



plt.show()
