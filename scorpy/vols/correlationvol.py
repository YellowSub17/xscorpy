from ..utils import angle_between_pol, angle_between_sph, angle_between_rect, index_x

from .vol import Vol
from scipy import special
import numpy as np
import time

from .volspropertymixins import CorrelationVolProps


class CorrelationVol(Vol, CorrelationVolProps):
    '''
    Representation of a scattering correlation volume.

    Arguments:
        nq (int): number of scattering magnitude bins.
        ntheta (int): number of angular bins.
        qmax (float): correlation magnitude limit [1/A].
        path (str): path to dbin (and log) if being created from memory.
    '''

    def __init__(self, nq=100, npsi=180, qmax=1, path=None):
        '''
        Class constructor.
        '''
        Vol.__init__(self, nq, nq, npsi, qmax, qmax, 1, 0, 0, -1, False, False, False, comp=False, path=path)

        self.plot_q1q2 = self.plot_xy

    def _save_extra(self, f):
        f.write('[corr]\n')
        f.write(f'qmax = {self.qmax}\n')
        f.write(f'nq = {self.nq}\n')
        f.write(f'npsi = {self.npsi}\n')
        f.write(f'dq = {self.dq}\n')
        f.write(f'dpsi = {self.dpsi}\n')






    def fill_from_cif(self, cif, method='scat_sph'):
        '''
        Fill the CorrelationVol from a CifData

        Arguments:
            cif (CifData): The CifData object to to fill the CorrelationVol

        Returns:
            None. Updates self.cvol
        '''

        assert cif.qmax==self.qmax, 'CifData and CorrelationVol hae different qmax values.'
        assert method in ['scat_sph', 'scat_rect'], 'Invalid correlation method.'


        if method == 'scat_sph':
            self.correlate_scat_sph(cif.scat_sph)
        elif method == 'scat_rect':
            self.correlate_scat_rect(cif.scat_rect)




    def fill_from_peakdata(self, pk, method='scat_sph', verbose=True):

        '''
        Fill the CorrelationVol from a PeakData

        Arguments:

        Returns:
            None. Updates self.cvol
        '''

        assert self.qmax == pk.qmax, 'Peakdata and CorrelationVol have different qmax values.'
        assert method in ['scat_pol', 'scat_sph', 'scat_rect'], 'Invalid correlation method.'


        nframes = len(pk.split_frames())
        nscats = pk.scat_rect.shape[0]

        if verbose:
            print('')
            print('############')
            print(f'Filling CorrelationVol from Peakdata via {method}.')
            print(f'Correlating {nscats} vectors over {nframes} frames. (Approx. {int(nscats/nframes)} vectors per frame.)')

            print(f'Correlation started: {time.asctime()}\n')

        if method=='scat_pol':
            for i, frame in enumerate(pk.split_frames()):
                print(f'Frame: {i+1}/{nframes}', end='\r')
                self.correlate_scat_pol(frame.scat_pol)
                print('', end='')

        if method=='scat_sph':
            for i, frame in enumerate(pk.split_frames()):
                print(f'Frame: {i+1}/{nframes}', end='\r')
                self.correlate_scat_sph(frame.scat_sph)
                print('', end='')

        if verbose:
            print(f'Correlation finished: {time.asctime()}')
            print('############')
            print('')















    def fill_from_blqq(self, blqq, inc_odds=False):
        '''
        Fill the CorrelationVol from a BlqqVol

        Arguments:
            blqq (BlqqVol): The BlqqVol object to to fill the CorrelationVol

        Returns:
            None. Updates self.cvol
        '''
        assert self.nq == blqq.nq, 'BlqqVol and CorrelationVol have different nq'
        assert self.qmax == blqq.qmax, 'BlqqVol and CorrelationVol have different qmax'

        if inc_odds:
            lskip = 1
        else:
            lskip = 2

        # arguments for the legendre polynomial
        args = self.psipts

        # initialze fmat matrix
        fmat = np.zeros((self.npsi, blqq.nl))

        # for every even spherical harmonic
        for l in range(0, blqq.nl, lskip):
            # leg_vals = (1 / (4 * np.pi)) * special.eval_legendre(l, args)
            leg_vals = special.eval_legendre(l, args)
            fmat[:, l] = leg_vals

        # for every q1 and q2 position
        for q1_ind in range(self.nq):
            for q2_ind in range(q1_ind, self.nq):
                # vector as a function of L
                blv = blqq.vol[q1_ind, q2_ind, :]

                for psi_ind in range(self.npsi):
                    ft = fmat[psi_ind, :]
                    x = np.dot(blv, ft)

                    # fill the volume
                    self.vol[q1_ind, q2_ind, psi_ind] = x
                    if q1_ind != q2_ind:  # if not on diagonal
                        self.vol[q2_ind, q1_ind, psi_ind] = x









    def correlate_scat_pol(self, qti):
        '''
        Correlate diffraction peaks in 2D polar coordinates.

        Arguments:
            qti (n x 3 array): list of peaks to correlate. Columns should be
                                qti[:,0] = polar radius of peak
                                qti[:,1] = polar angle of peak
                                qti[:,2] = intensity of peak
        Returns:
            None. Updates self.cvol with correlations.
        '''
        # only correlate less than qmax
        le_qmax = np.where(qti[:, 0] <= self.qmax)[0]
        qti = qti[le_qmax]

        qti[:,1] = np.degrees(qti[:,1])

        # calculate q indices of every scattering vector outside of loop
        ite = np.ones(qti.shape[0])
        q_inds = list(map(index_x, qti[:, 0], 0 * ite, self.qmax * ite, self.nq * ite))

        for i, q1 in enumerate(qti):
            # get q index
            q1_ind = q_inds[i]

            for j, q2 in enumerate(qti[i:]):
                # get q index
                q2_ind = q_inds[i + j]

                # get the angle between vectors, and index it
                psi = angle_between_pol(q1[1], q2[1])
                psi_ind = index_x(psi, self.zmin, self.zmax, self.npsi, wrap=self.zwrap)

                # fill the volume
                self.vol[q1_ind, q2_ind, psi_ind] += q1[-1] * q2[-1]
                if j > 0:  # if not on diagonal
                    self.vol[q2_ind, q1_ind, psi_ind] += q1[-1] * q2[-1]





    def correlate_scat_rect(self, qxyzi):
        '''
        Correlate diffraction peaks in 3D rectilinear coordinates.

        Arguments:
            qxyzi (n x 4 array): list of peaks to correlate. Columns should be
                                qti[:,0] = qx coordinate of scattering vector
                                qti[:,1] = qy coordinate of scattering vector
                                qti[:,2] = qz coordinate of scattering vector
                                qti[:,3] = intensity of peak
        Returns:
            None. Updates self.cvol with correlations
        '''

        # only correlate less than qmax
        qmags = np.linalg.norm(qxyzi[:, :3], axis=1)
        le_qmax = np.where(qmags <= self.qmax)[0]
        qxyzi = qxyzi[le_qmax]
        qmags = qmags[le_qmax]

        # calculate q indices of every scattering vector outside of loop
        ite = np.ones(qxyzi.shape[0])
        q_inds = list(map(index_x, qmags, 0 * ite, self.qmax * ite, self.nq * ite))

        for i, q1 in enumerate(qxyzi):

            # get q index
            q1_ind = q_inds[i]

            for j, q2 in enumerate(qxyzi[i:]):
                # get q index
                q2_ind = q_inds[i + j]

                # get the angle between vectors, and index it
                psi = angle_between_rect(q1[:3], q2[:3])

                psi_ind = index_x(psi, self.zmin, self.zmax, self.npsi, wrap=self.zwrap)

                # fill the volume
                self.vol[q1_ind, q2_ind, psi_ind] += q1[-1] * q2[-1]
                if j > 0:  # if not on diagonal
                    self.vol[q2_ind, q1_ind, psi_ind] += q1[-1] * q2[-1]




    def correlate_scat_sph(self, qtpi):
        '''
        Correlate diffraction peaks in 3D spherical coordinates.

        Arguments:
            qxyzi (n x 4 array): list of peaks to correlate. Columns should be
                                qti[:,0] = qx coordinate of scattering vector
                                qti[:,1] = qy coordinate of scattering vector
                                qti[:,2] = qz coordinate of scattering vector
                                qti[:,3] = intensity of peak
        Returns:
            None. Updates self.cvol with correlations
        '''
        # only correlate less than qmax
        le_qmax = np.where(qtpi[:, 0] <= self.qmax)[0]
        qtpi = qtpi[le_qmax]

        # calculate q indices of every scattering vector outside of loop
        ite = np.ones(qtpi.shape[0])
        q_inds = list(map(index_x, qtpi[:, 0], 0 * ite, self.qmax * ite, self.nq * ite))

        for i, q1 in enumerate(qtpi):
            # get q index, theta and phi
            q1_ind = q_inds[i]
            theta1 = q1[1]
            phi1 = q1[2]

            for j, q2 in enumerate(qtpi[i:]):
                # get q index, theta and phi
                q2_ind = q_inds[i + j]
                theta2 = q2[1]
                phi2 = q2[2]

                # get the angle between angluar coordinates, and index it
                psi = angle_between_sph(theta1, theta2, phi1, phi2)
                psi_ind = index_x(psi, self.zmin, self.zmax, self.npsi, wrap=self.zwrap)

                # fill the volume
                self.vol[q1_ind, q2_ind, psi_ind] += q1[-1] * q2[-1]
                if j > 0:  # if not on diagonal
                    self.vol[q2_ind, q1_ind, psi_ind] += q1[-1] * q2[-1]







    # def force_sym(self):
        # half_ind = int(self.npsi / 2)
        # for psi_ind in range(0, half_ind):
            # self.vol[..., psi_ind] = self.vol[..., -1 - psi_ind]

    # def sub_t_mean(self):
        # means = self.vol.mean(axis=(0, 1))
        # self.vol -= means[None, None, :]
