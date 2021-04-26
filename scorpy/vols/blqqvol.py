

from .vol import Vol
import numpy as np
from scipy import special
import matplotlib.pyplot as plt
from .propertymixins import BlqqVolProperties



class BlqqVol(Vol, BlqqVolProperties):
    '''
    Representation of the B_l(q1,q2) volume, an invertible correlation matrix.

    Arguments:
        nq (int): number of scattering magnitude bins.
        nl (int): number of spherical harmonics (inc. 0th harmonic, so 1+lmax).
        qmax (float): correlation magnitude limit [1/A].
        path (str): path to dbin (and log) if being created from memory.
    '''


    def __init__(self, nq=100, nl=37, qmax=1, path=None, comp=False):
        Vol.__init__(self, nx = nq, ny = nq, nz = nl, \
                        xmax = qmax, ymax = qmax, zmax = nl, \
                        xmin = 0, ymin = 0, zmin = 0, \
                        comp = False, path = None)

        self.plot_q1q2 = self.plot_xy



    def fill_from_corr(self,corr):
        assert corr.qmax == self.qmax, 'CorrelationVol and BlqqVol have different qmax'
        assert corr.nq == self.nq, 'CorrelationVol and BlqqVol have different nq'


        #TODO compensate for ewald sphere
        q_range = np.linspace(0,self.qmax, self.nq)

        # # # create args of legendre eval
        args = np.cos( np.linspace(0, np.pi, corr.npsi))


        # initialze fmat matrix
        fmat = np.zeros( (corr.npsi, self.nl) )

        #for every even spherical harmonic
        for l in range(0, self.nl, 2):
            leg_vals = special.eval_legendre(l, args)
            fmat[:,l] = leg_vals


        #TODO check svd
        fmat_inv = np.linalg.pinv(fmat)

        for iq1 in range(self.nq):
            for iq2 in range(iq1, self.nq):
                dot =  np.dot(fmat_inv,corr.vol[iq1,iq2,:])
                self.vol[iq1,iq2,:] = dot
                if iq1 !=iq2:
                    self.vol[iq2,iq1,:] = dot

        # times 4pi because we multi 2root(pi) in the ylm calc.
        # self.vol *= 4*np.pi





    def fill_from_sphv(self, sphv):

        all_q_coeffs = list(map(sphv.get_coeffs,range(self.nq)))

        for i, q1_coeffs in enumerate(all_q_coeffs):

            for j, q2_coeffs in enumerate(all_q_coeffs[i:]):

                multi = np.conj(q1_coeffs)*q2_coeffs

                self.vol[i,j+i,:] = multi.sum(axis=0).sum(axis=1)[:self.nl]
                if j>0:
                    self.vol[j+i,i,:] = multi.sum(axis=0).sum(axis=1)[:self.nl]










    # def fill_from_sph(self, sph):
        # print(f'Calculating BlqqVol from SphHarmHandler\n')

        # if self.comp:
            # bl = np.zeros((self.nq, self.nq), dtype=np.complex128)
        # else:
            # bl = np.zeros((self.nq, self.nq))

        # for l in range(0, self.nl, 2):
            # for iq1 in range(self.nq):
                # for iq2 in range(iq1, self.nq):
                    # bl[iq1,iq2] = np.sum(np.conj(sph.vals_lnm[l][iq1])*sph.vals_lnm[l][iq2])
                    
                    # if iq1 !=iq2:
                        # bl[iq2,iq1] = np.sum(np.conj(sph.vals_lnm[l][iq2])*sph.vals_lnm[l][iq1])

            # self.vol[...,l] = bl






