"""Code to load different detector responses. """

from dataclasses import dataclass

import logging
import os
import pathlib
import sys

from astropy.io import fits
import astropy.units as u
from matplotlib.colors import LogNorm, Normalize
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np

import response_tools
from response_tools.util import BaseOutput

FILE_PATH = response_tools.responseFilePath
RESPONSE_INFO_TYPE = response_tools.contextResponseInfo["files"]["detectors"]
ASSETS_PATH = os.path.join(pathlib.Path(__file__).parent, "assets", "response-tools-figs", "det-resp-figs")

@dataclass
class DetectorResponseOutput(BaseOutput):
    """Class for keeping track of effective area response values."""
    # numbers
    input_energy_edges: u.Quantity # photon axis
    output_energy_edges: u.Quantity # count axis
    detector_response: u.Quantity # rmf
    # bookkeeping
    detector: str
    # any other fields needed can be added here
    # can even add with a default so the input is not required for every other instance

def cdte_det_resp_rmf(file):
    """Return the redistribution matrix for CdTe from a given file.

    Parameters
    ----------
    file : `str`
        The file for the RMF.

    Returns
    -------
    : `DetectorResponseOutput`
        An object containing all the redistribution matrix information. 
        See accessible information using `.contents` on the output.
    """
    e_lo, e_hi, ngrp, fchan, nchan, matrix = _read_rmf(file)

    fchan_array = col2arr_py(fchan)
    nchan_array = col2arr_py(nchan)

    energies = np.append(e_lo, e_hi[-1])<<u.keV

    return DetectorResponseOutput(filename=file,
                                  function_path=f"{sys._getframe().f_code.co_name}",
                                  input_energy_edges=energies,
                                  output_energy_edges=energies,
                                  detector_response=vrmf2arr_py(data=matrix,
                                                                n_grp_list=ngrp,
                                                                f_chan_array=fchan_array,
                                                                n_chan_array=nchan_array)<<(u.ct/u.ph),
                                  detector="CdTe-General-Detector-Response"
                                  )

@u.quantity_input(pitch=u.um)
def cdte_det_resp(cdte:int=None, region:int=None, pitch=None, side:str="merged", event_type:str="all", file=None):
    """Return the redistribution matrix for CdTe from a given file.

    Requires the `cdte` input and _either_ `region` _xor_ `pitch`.

    Wrapper for `cdte_det_resp_rmf` with bookkeeping.

    Parameters
    ----------
    cdte : `int`
        The CdTe detector number. Must be in [1,2,3,4].

    region : `int`
        The region of the CdTe detector required. Either provide 
        `region` _xor_ `pitch`. The `region` maps onto the pitches used 
        across the detector. 
        - Region 0 -> 60<<astropy.units.um 
        - Region 1 -> 80<<astropy.units.um
        - Region 2 -> 100<<astropy.units.um

    pitch : `astropy.units.quantity.Quantity`
        Instead of `region`, it might be more usefule to specify the 
        pitch in physical units (must b convertable to 
        `astropy.units.um`). Either provide `region` _xor_ `pitch`.
        The pitches map onto the `region` input.
        - 60<<astropy.units.um -> Region 0
        - 80<<astropy.units.um -> Region 1
        - 100<<astropy.units.um -> Region 2

    side : `str`
        Define the side on the detector the user requires the response 
        from. Must be in ["pt", "merged"].
        Default: "merged"

    event_type : `str`
        Define the type of event trigger being considered in the 
        response. Must be in ["1hit", "2hit", "all"]. 
        Note: \"all\" and \"mix\" (old) are the same but some from 
        different naming conventions on the merged and individual 
        detector sides. This has been fixed and all files use \"all\"
        now.
        Default: "all"

    file : `str`
        The file for the RMF.

    Returns
    -------
    : `DetectorResponseOutput`
        An object containing all the redistribution matrix information. 
        See accessible information using `.contents` on the output.
    """

    have_region, have_pitch = (region is not None), (pitch is not None)
    pitch2region = {60<<u.um:0, 80<<u.um:1, 100<<u.um:2}
    valid_region, valid_pitch = (region in list(pitch2region.values())), (pitch in list(pitch2region.keys()))

    if (cdte is None) or (cdte not in [1,2,3,4]):
        logging.warning(f"In {sys._getframe().f_code.co_name}, `cdte` must be given and in [1,2,3,4].")
        return 
    
    if ((not have_region) and (not have_pitch)) \
        or (have_region and have_pitch):
        logging.warning(f"In {sys._getframe().f_code.co_name}, either `region` [0,1,2] _xor_ `pitch` [60<<u.um,80<<u.um,100<<u.um] must be given.")
        return 
    
    if have_region and (not valid_region):
        logging.warning(f"In {sys._getframe().f_code.co_name}, the `region` must be in [0,1,2].")
        return 

    if have_pitch and (not valid_pitch):
        logging.warning(f"In {sys._getframe().f_code.co_name}, the `pitch` must be in [60<<u.um,80<<u.um,100<<u.um].")
        return 
    
    if side not in ["pt", "merged"]:
        logging.warning(f"In {sys._getframe().f_code.co_name}, the `side` must be in [\"pt\", \"merged\"].")
        return 
    
    if event_type not in ["1hit", "2hit", "all"]:
        logging.warning(f"In {sys._getframe().f_code.co_name}, the `event_type` must be in [\"1hit\", \"2hit\", \"all\"].")
        return 
    
    region = pitch2region[pitch] if have_pitch else region
    
    _f = os.path.join(FILE_PATH, 
                      RESPONSE_INFO_TYPE[f"cdte_det_{side}_resp"], 
                      f"Resp_3keVto30keV_CdTe{cdte}_reg{region}_{event_type}.rmf") if file is None else file
    r = cdte_det_resp_rmf(_f)
    r.update_function_path(sys._getframe().f_code.co_name)
    r.detector = f"CdTe{cdte}-Detector-Response"
    return r

def cmos_det_resp(file=None, telescope=None):
    """Return the redistribution matrix for CMOS from a given file.

    Parameters
    ----------
    file : `str`
        The file for the RMF.

    telescope : `int`
        Either 0 or 1.

    Returns
    -------
    : `DetectorResponseOutput`
        An object containing all the redistribution matrix information. 
        See accessible information using `.contents` on the output.
    """

    if (telescope is None) or (telescope not in [0,1]):
        logging.warning(f"The `telescope` input in {sys._getframe().f_code.co_name} must be 0 or 1.")
        return
    
    _f = os.path.join(FILE_PATH, RESPONSE_INFO_TYPE[f"cmos_det_telescope-{telescope}_resp"]) if file is None else file
    
    with fits.open(_f) as hdul:
        matrix, counts, energy = hdul[1].data<<(u.DN/u.ph), hdul[2].data<<u.DN, hdul[3].data<<u.keV # units?

    # counts & energy come as the bin centers, not edges
    # check for uniform binning and convert to bin edges...
    # round to avoid differences in float precision
    diff_counts, diff_energy = round(np.diff(counts), 3), round(np.diff(energy), 3)
    assert np.min(diff_counts)==np.max(diff_counts), f"In {sys._getframe().f_code.co_name}, the counts axis values do not appear to follow uniform binning and so cannot be automatically converted from bin centers to edges:\n{diff_counts}"
    assert np.min(diff_energy)==np.max(diff_energy), f"In {sys._getframe().f_code.co_name}, the energy axis values do not appear to follow uniform binning and so cannot be automatically converted from bin centers to edges:\n{diff_energy}"
    
    counts_edges = np.append(counts-(0.5*diff_counts[0]), counts[-1]+(0.5*diff_counts[0]))
    energy_edges = np.append(energy-(0.5*diff_energy[0]), energy[-1]+(0.5*diff_energy[0]))

    return DetectorResponseOutput(filename=file,
                                  function_path=f"{sys._getframe().f_code.co_name}",
                                  input_energy_edges=energy_edges,
                                  output_energy_edges=counts_edges,
                                  detector_response=matrix,
                                  detector=f"CMOS{telescope}-Detector-Response"
                                  )

def _read_rmf(file):
    """
    Read a .rmf file and extract useful information from it.

    Parameters
    ----------
    file :  `str`, `file-like` or `pathlib.Path`
        A .rmf file (see `~astropy.fits.io.open` for details).

    Returns
    -------
    `tuple`
        The low and high boundary of energy bins (data['energ_lo'], 
        data['energ_hi']), number of sub-set channels in the energybin 
        (data['n_grp']), starting index of each sub-set of channels 
        (data['f_chan']),number of channels in each sub-set 
        (data['n_chan']), redistribution matrix [counts per photon] 
        (data['matrix']).
    """

    with fits.open(file) as hdul:
        data = hdul[2].data

    return data["energ_lo"], data["energ_hi"], data["n_grp"], data["f_chan"], data["n_chan"], data["matrix"]

def col2arr_py(data):
    """Takes a list of parameters for each energy channel from a .rmf 
    file and returns it in the correct format [1].

    This original function is taken from Sunkit-spex [2]
    - Tweaked to change `r` below to `[r]` since the values in data 
    aren't lists (e.g., NuSTAR)

    [1] https://lost-contact.mit.edu/afs/physics.wisc.edu/home/craigm/lib/idl/util/vcol2arr.pro
    [2] https://github.com/sunpy/sunkit-spex

    Parameters
    ----------
    data : array/list-like object
        One parameter's array/list from the .rmf file.

    Returns
    -------
    A 2D numpy array of the correctly ordered input data.

    Example
    -------
    >>> data = FITS_rec([(  1.6 ,   1.64,   1, [0]   , [18]  , [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]),
                         (  1.64,   1.68,   1, [0]   , [20]  , [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]),
                         (  1.68,   1.72,   2, [0,22], [20,1], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]),
                         dtype=(numpy.record, [('ENERG_LO', '>f4'), ('ENERG_HI', '>f4'), ('N_GRP', '>i2'),
                                               ('F_CHAN', '>i4', (2,)), ('N_CHAN', '>i4', (2,)), ('MATRIX', '>i4', (2,))]))
    # max row length of 2 so 2 columns, each row is an energy channel.
    >>> col2arr_py(data['F_CHAN'])
    array([[  0.,   0.],
           [  0.,   0.],
           [  0.,  22.]])
    """

    # this is the quicker way I have chosen to do in Python (this may be revised later but is ~30x faster than way below in Python)
    max_len = np.max([len([r]) for r in data])  # find max row length
    chan_array_py = np.array(
        [[*[r], *(max_len - len([r])) * [0]] for r in data]
    )  # make each row that length (padding with 0)

    return chan_array_py

def vrmf2arr_py(data=None, n_grp_list=None, f_chan_array=None, n_chan_array=None):
    """Takes redistribution parameters for each energy channel from a 
    .rmf file and returns it in the correct format [1].

    This original function is taken from Sunkit-spex [2].

    [1] https://lost-contact.mit.edu/afs/physics.wisc.edu/home/craigm/lib/idl/spectral/vrmf2arr.pro
    [2] https://github.com/sunpy/sunkit-spex

    Parameters
    ----------
    data : array/list-like object
            Redistribution matrix parameter array/list from the .rmf 
            file. Units are counts per photon.
            Default : None

    no_of_channels : int
            Number of entries is the total number of photon channels, 
            the entries themselves show the total number
            of count channels to which that photon channel contributes.
            Default : None

    f_chan_array : numpy.array
            The index of each sub-set channel from each energy bin from 
            the .rmf file run through col2arr_py().
            Default : None

    n_chan_array : numpy.array
            The number of sub-set channels in each index for each energy 
            bin from the .rmf file run through col2arr_py().
            Default : None

    Returns
    -------
    A 2D numpy array of the correctly ordered input data with dimensions 
    of energy in the rows and channels in the columns.

    Example
    -------
    >>> d_rmf = 'directory/'
    >>> f_rmf = 'file.rmf'
    >>> e_lo, e_hi, ngrp, fchan, nchan, matrix = det_io._read_rmf(d_rmf+f_rmf)
    >>> fchan_array = nu_spec.col2arr_py(fchan)
    >>> nchan_array = nu_spec.col2arr_py(nchan)
    >>> rmf = nu_spec.vrmf2arr_py(data=matrix,
                                  n_grp_list=ngrp,
                                  f_chan_array=fchan_array,
                                  n_chan_array=nchan_array)
    # rows = photon/energy channels, columns = counts channels
    >>> rmf
    array([[0.00033627, 0.0007369 , 0.00113175, ..., 0.        , 0.        , 0.        ],
           [0.00039195, 0.00079259, 0.00138341, ..., 0.        , 0.        , 0.        ],
           [0.00042811, 0.00083381, 0.00157794, ..., 0.        , 0.        , 0.        ],
                                                ...,
           [0.        , 0.        , 0.        , ..., 0.00408081, 0.00409889, 0.00403308],
           [0.        , 0.        , 0.        , ..., 0.00405333, 0.00413722, 0.00413216],
           [0.        , 0.        , 0.        , ..., 0.        , 0.        , 0.        ]])

    What's Going On?
    ----------------
    The RMF file has the photon-to-counts conversion information in it.
    The martix has the photon-to-count conversion value for each count 
    channel (column) that is involved with theach photon channel (rows).
    E.g., matrix = [ [a, b, c, d, e, f, ...] , ... ]
    F_chan is the starting index of contiguous counts channels that are 
    involved with the photon channel.
    E.g., f_chan = [ [0, 5, 0, 0, 0, ...] , ... ]
    For the first photon channel, there are rows of counts channels 
    starting at index 0 and 5 N_chan is the corresponding number of 
    counts channels from each index in the f_chan array.
    E.g., n_chan = [ [2, 3, 0, 0, 0, ...] , ... ]
    Starting at index 0 for the first photon channel we have the first 2 
    matrix values, then at index 5 we have the next 3.
    The total of each row is the same as the n_grp_list and the number 
    of entries in each row of the matrix entry.
    Putting all this together, the rmf matrix is:
    rmf_matrix = [ [a, b, 0, 0, 0, c , d , e, 0 , 0 , ...] , ... ]
    Index 0 (f_chan) with 2 entries (n_chan) with photon-to-counts 
    conversion (matrix).
    """
    # this was is about >6x quicker in than the IDL code written in Python

    n_grp_list = n_grp_list.astype("<i2")  # change from ‘big-endian’ (">i2") to ‘little-endian’ ("<i2")

    # find the non-zero entries in Nchan, this is the number to counts channels
    #  in a row that contribute so will have a value if it is useful
    b = np.nonzero(n_chan_array)

    # now only want the useful entries from the pre-formatted Nchan and Fchan arrays
    c = f_chan_array[b]
    d = n_chan_array[b]

    # to help with indexing, this provides a running sum of the number of counts
    #  channels that a single photon channel contributes to
    e = np.cumsum(n_chan_array, axis=1)

    # these entries will give the final indices in the row on counts channels
    final_inds = e[b]

    # need to find the starting index so -1, but that means any entry that is
    #  -1 will be where a zero is needed
    starting_inds = b[1] - 1

    # get the  starting indices but the ones that should be 0 are replaced with
    #  the final one in the list at the minute (-1 in starting_inds)
    start_inds = np.cumsum(n_chan_array, axis=1)[(b[0], starting_inds)]

    # where starting_inds==-1 that value should be 0, i.e. starting from the first
    #  value in the rmf matrix
    new_e = np.where(starting_inds != -1, start_inds, 0)

    # initialise the rmf matrix
    mat_array_py = np.zeros((len(data), len(n_grp_list)))

    # now go through row by row (this is the slowest part and needs to be made faster).
    #  Here we go through each photon channel's number of discrete rows of counts channels.
    for r in range(len(c)):
        mat_array_py[b[0][r], c[r] : c[r] + d[r]] = data[b[0][r]][new_e[r] : final_inds[r]]

    return mat_array_py

def asset_cmos_resp(save_location=None):
    """Plot the CMOS responses."""
    # CMOS
    fig = plt.figure(figsize=(12,7))

    gs = gridspec.GridSpec(1, 2)
    gs_ax0 = fig.add_subplot(gs[0, 0])
    telescope = 0
    cmos0_resp = cmos_det_resp(file=None, telescope=telescope)
    extent = [np.min(cmos0_resp.output_energy_edges.value), 
              np.max(cmos0_resp.output_energy_edges.value), 
              np.min(cmos0_resp.input_energy_edges.value), 
              np.max(cmos0_resp.input_energy_edges.value)]
    i = gs_ax0.imshow(cmos0_resp.detector_response.value, origin="lower", aspect=(extent[1]-extent[0])/(extent[3]-extent[2]), extent=extent, norm=LogNorm())
    gs_ax0.set_ylim([0,10])
    gs_ax0.set_xlabel(f"Counts [{cmos0_resp.output_energy_edges.unit:latex}]")
    gs_ax0.set_ylabel(f"Energy [{cmos0_resp.input_energy_edges.unit:latex}]")
    gs_ax0.set_title(f"CMOS{telescope}")
    cax = gs_ax0.inset_axes([0.1, 0.08, 0.8, 0.05],)
    cbar = fig.colorbar(i, cax=cax, orientation='horizontal')
    cbar.set_label(f"{cmos0_resp.detector_response.unit:latex}", size=8, labelpad=0)
    cax.tick_params(axis='both', which='major', labelsize=6)


    gs_ax1 = fig.add_subplot(gs[0, 1])
    telescope = 1
    cmos1_resp = cmos_det_resp(file=None, telescope=telescope)
    extent = [np.min(cmos1_resp.output_energy_edges.value), 
              np.max(cmos1_resp.output_energy_edges.value), 
              np.min(cmos1_resp.input_energy_edges.value), 
              np.max(cmos1_resp.input_energy_edges.value)]
    i = gs_ax1.imshow(cmos1_resp.detector_response.value, origin="lower", aspect=(extent[1]-extent[0])/(extent[3]-extent[2]), extent=extent, norm=LogNorm())
    gs_ax1.set_ylim([0,10])
    gs_ax1.set_xlabel(f"Counts [{cmos1_resp.output_energy_edges.unit:latex}]")
    gs_ax1.set_ylabel(f"Energy [{cmos1_resp.input_energy_edges.unit:latex}]")
    gs_ax1.set_title(f"CMOS{telescope}")
    cax = gs_ax1.inset_axes([0.1, 0.08, 0.8, 0.05],)
    cbar = fig.colorbar(i, cax=cax, orientation='horizontal')
    cbar.set_label(f"{cmos1_resp.detector_response.unit:latex}", size=8, labelpad=0)
    cax.tick_params(axis='both', which='major', labelsize=6)

    plt.tight_layout()
    if save_location is not None:
        pathlib.Path(save_location).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(save_location,"cmos-response-matrices.png"), dpi=200, bbox_inches="tight")
    plt.show()

def asset_cdte_resp(save_location=None):
    """Plot the CdTe1, region 0, 1-hit response."""
    # CdTe
    d_rmf = os.path.join(FILE_PATH, RESPONSE_INFO_TYPE[f"cdte_det_pt_resp"])
    f_rmf = "Resp_3keVto30keV_CdTe1_reg0_1hit.rmf"

    cdte_resp = cdte_det_resp_rmf(os.path.join(pathlib.Path(__file__).parent, d_rmf, f_rmf))

    fig = plt.figure(figsize=(12, 5))
    gs = gridspec.GridSpec(1, 2)

    gs_ax0 = fig.add_subplot(gs[0, 0])
    r = gs_ax0.imshow(cdte_resp.detector_response.value, 
                      origin="lower", 
                      norm=Normalize(vmin=0.001, 
                                     vmax=np.max(cdte_resp.detector_response.value)*0.9), 
                      extent=[np.min(cdte_resp.output_energy_edges.value), 
                              np.max(cdte_resp.output_energy_edges.value), 
                              np.min(cdte_resp.input_energy_edges.value), 
                              np.max(cdte_resp.input_energy_edges.value)]
                      )
    cbar = plt.colorbar(r)
    cbar.ax.set_ylabel(f"Response [{cdte_resp.detector_response.unit:latex}]")
    gs_ax0.set_xlabel(f"Count Energy [{cdte_resp.output_energy_edges.unit:latex}]")
    gs_ax0.set_ylabel(f"Photon Energy [{cdte_resp.input_energy_edges.unit:latex}]")
    gs_ax0.set_title("Linear Scale")

    gs_ax1 = fig.add_subplot(gs[0, 1])
    r = gs_ax1.imshow(cdte_resp.detector_response.value, 
                      origin="lower", 
                      norm=LogNorm(vmin=0.001, 
                                   vmax=np.max(cdte_resp.detector_response.value)*0.9), 
                      extent=[np.min(cdte_resp.output_energy_edges.value), 
                              np.max(cdte_resp.output_energy_edges.value), 
                              np.min(cdte_resp.input_energy_edges.value), 
                              np.max(cdte_resp.input_energy_edges.value)]
                      )
    cbar = plt.colorbar(r)
    cbar.ax.set_ylabel(f"Response [{cdte_resp.detector_response.unit:latex}]")
    gs_ax1.set_xlabel(f"Count Energy [{cdte_resp.output_energy_edges.unit:latex}]")
    gs_ax1.set_ylabel(f"Photon Energy [{cdte_resp.input_energy_edges.unit:latex}]")
    gs_ax1.set_title("Log Scale")

    fig.suptitle(f_rmf)

    if save_location is not None:
        pathlib.Path(save_location).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(save_location,"cdte-response-matrix.png"), dpi=200, bbox_inches="tight")
    plt.show()

if __name__=="__main__":
    save_location = None # ASSETS_PATH
    asset_cdte_resp(save_location=save_location)
    asset_cmos_resp(save_location=save_location)