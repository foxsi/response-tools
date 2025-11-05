"""Functions to make the RMFs and ARFs. """

from dataclasses import dataclass
import logging
import os
import pathlib
import sys

import astropy.units as u
from matplotlib.colors import LogNorm
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np

from response_tools.attenuation import att_foxsi4_atmosphere
import response_tools.telescope_parts as tp
from response_tools.util import BaseOutput

ASSETS_PATH = os.path.join(pathlib.Path(__file__).parent, "assets", "response-tools-figs", "response-figs")

@dataclass
class Response1DOutput(BaseOutput):
    """Class for keeping track of 1D response response values."""
    # numbers
    mid_energies: u.Quantity
    response: u.Quantity
    # bookkeeping
    response_type: str
    telescope: str
    elements: tuple
    # any other fields needed can be added here
    # can even add with a default so the input is not required for every other instance

@dataclass
class Response2DOutput(BaseOutput):
    """Class for keeping track of 2D response response values."""
    # numbers
    input_energy_edges: u.Quantity # photon axis
    output_energy_edges: u.Quantity # count axis
    response: u.Quantity
    # bookkeeping
    response_type: str
    telescope: str
    elements: tuple
    # any other fields needed can be added here
    # can even add with a default so the input is not required for every other instance

def foxsi4_telescope_spectral_response(arf_response, rmf_response):
    """Full Spectral Response Matrix (SRM) for a given telescope.

    This function will check the Ancillary Response Function (ARF) 
    `mid_energies` field and the Redistribution Matrix Function (RMF) 
    `input_energy_edges` field mid-points to check they match before 
    combining both the ARF and RMF into the Spectral Response Matrix 
    (SRM).

    This function will check both the ARF and RMF have come from the 
    same telescope using the "telescope" field. A warning will be 
    produce if they are different to inform the user but the function 
    will still output the product if possible.

    Parameters
    ----------
    arf_response : `responses.Response1DOutput`
        The Ancillary Response Function (ARF) object for a telescope.

    rmf_response : `responses.Response2DOutput`
        The Redistribution Matrix Function (RMF) object for a telescope.

    Returns
    -------
    : `responses.Response2DOutput`
        An object containing the 2D detector response information for a 
        given ARF and RMF. See accessible information using `.contents` 
        on the output.
    """

    # check compatibility
    rmf_mids = (rmf_response.input_energy_edges[:-1]+rmf_response.input_energy_edges[1:])/2
    if not np.all(arf_response.mid_energies==rmf_mids):
        raise ValueError(f"In {sys._getframe().f_code.co_name}, the `arf_response.mid_energies` do not match the bin centers of `rmf_response.input_energy_edges`.\nSRM product cannot be calculated")
    
    if arf_response.telescope!=rmf_response.telescope:
        logging.warning(f"In {sys._getframe().f_code.co_name}, the \"telescope\" fields from `arf_response` ({arf_response.telescope}) and `rmf_response` ({rmf_response.telescope}) do not match.\nAn output shall be produced if possible (check the returned objects\"telescope\" field) but the user should be cautious.")

    total_response = arf_response.response[:,None] * rmf_response.response

    func_name = sys._getframe().f_code.co_name
    arf_response.update_function_path(func_name)
    rmf_response.update_function_path(func_name)

    return Response2DOutput(filename="No-File",
                            function_path=func_name,
                            input_energy_edges=rmf_response.input_energy_edges,
                            output_energy_edges=rmf_response.output_energy_edges,
                            response=total_response,
                            response_type="SRM",
                            telescope=f"ARF:{arf_response.telescope},RMF:{rmf_response.telescope}",
                            elements=(arf_response,
                                      rmf_response,
                                      ),
                            )

# telescope 0
@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_telescope0_arf(mid_energies, off_axis_angle):
    """The Ancillary Response Function (ARF) for Telescope 0.
    
    **DOES NOT** include atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 0 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 0. 
        See accessible information using `.contents` on the output.
    """
    pf = tp.foxsi4_position0_prefilter(mid_energies)
    co = tp.foxsi4_position0_collimator(off_axis_angle)
    opt = tp.foxsi4_position0_optics(mid_energies, 
                                     off_axis_angle=off_axis_angle) 
    obf = tp.foxsi4_position0_obf(mid_energies)

    arf = pf.transmissions * co.transmissions * opt.effective_areas * obf.transmissions

    func_name = sys._getframe().f_code.co_name
    pf.update_function_path(func_name)
    co.update_function_path(func_name)
    opt.update_function_path(func_name)
    obf.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=arf,
                            response_type="ARF",
                            telescope="foxsi4-telescope0",
                            elements=(pf, 
                                      co,
                                      opt, 
                                      obf,
                                      ),
                            )

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin, time_range=u.second)
def foxsi4_telescope0_flight_arf(mid_energies, off_axis_angle, time_range):
    """The flight Ancillary Response Function (ARF) for telescope 0.
    
    Includes atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 0 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.

    time_range : `astropy.units.quantity.Quantity` or `None`
        The time range the atmsopheric transmissions should be averaged
        over. If `None`, `numpy.nan<<astropy.units.second`, or
        `[numpy.nan, numpy.nan]<<astropy.units.second` then the full 
        time will be considered and the output will not be averaged but 
        a grid of the transmissions at all times and at any provided
        energies. Should be of length 2.
        Can be given as seconds since launch:
        - Observation start: 100<<astropy.units.second
        - Observation end: 461<<astropy.units.second
        Can be given as UTC time as well either as a string or and 
        Astropy time.
        - String format: YYYY-mm-ddTHH:MM:SS
        - Observation start: 2024-04-17T22:14:40
        - Observation end: 2024-04-17T22:20:41

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 0. 
        See accessible information using `.contents` on the output.
    """
    atm = att_foxsi4_atmosphere(mid_energies=mid_energies, 
                                time_range=time_range)
    arf = foxsi4_telescope0_arf(mid_energies, off_axis_angle)

    flight_arf = atm.transmissions*arf.response

    func_name = sys._getframe().f_code.co_name
    atm.update_function_path(func_name)
    arf.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=flight_arf,
                            response_type="ARF-flight",
                            telescope=f"foxsi4-telescope0",
                            elements=(atm, 
                                      arf,
                                      ),
                            )

def foxsi4_telescope0_rmf():
    """The Redistribution Matrix Function (RMF) for Telescope 0. 

    Returns
    -------
    : `responses.Response2DOutput`
        An object containing all the redistribution matrix information. 
        See accessible information using `.contents` on the output.
    """
    
    rmf = tp.foxsi4_position1_detector_response()
    func_name = sys._getframe().f_code.co_name
    rmf.update_function_path(func_name)

    return Response2DOutput(filename="No-File",
                            function_path=func_name,
                            input_energy_edges=rmf.input_energy_edges,
                            output_energy_edges=rmf.output_energy_edges,
                            response=rmf.detector_response,
                            response_type="RMF",
                            telescope="foxsi4-telescope1",
                            elements=(rmf,
                                      ),
                            )

# telescope 1
@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_telescope1_arf(mid_energies, off_axis_angle):
    """The Ancillary Response Function (ARF) for Telescope 1.
    
    **DOES NOT** include atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 1 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 1. 
        See accessible information using `.contents` on the output.
    """
    pf = tp.foxsi4_position1_prefilter(mid_energies)
    co = tp.foxsi4_position1_collimator(off_axis_angle)
    opt = tp.foxsi4_position1_optics(mid_energies, 
                                     off_axis_angle=off_axis_angle) 
    obf = tp.foxsi4_position1_obf(mid_energies)

    arf = pf.transmissions * co.transmissions * opt.effective_areas * obf.transmissions

    func_name = sys._getframe().f_code.co_name
    pf.update_function_path(func_name)
    co.update_function_path(func_name)
    opt.update_function_path(func_name)
    obf.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=arf,
                            response_type="ARF",
                            telescope="foxsi4-telescope1",
                            elements=(pf, 
                                      co,
                                      opt, 
                                      obf,
                                      ),
                            )

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin, time_range=u.second)
def foxsi4_telescope1_flight_arf(mid_energies, off_axis_angle, time_range):
    """The flight Ancillary Response Function (ARF) for telescope 1.
    
    Includes atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 1 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.

    time_range : `astropy.units.quantity.Quantity` or `None`
        The time range the atmsopheric transmissions should be averaged
        over. If `None`, `numpy.nan<<astropy.units.second`, or
        `[numpy.nan, numpy.nan]<<astropy.units.second` then the full 
        time will be considered and the output will not be averaged but 
        a grid of the transmissions at all times and at any provided
        energies. Should be of length 2.
        Can be given as seconds since launch:
        - Observation start: 100<<astropy.units.second
        - Observation end: 461<<astropy.units.second
        Can be given as UTC time as well either as a string or and 
        Astropy time.
        - String format: YYYY-mm-ddTHH:MM:SS
        - Observation start: 2024-04-17T22:14:40
        - Observation end: 2024-04-17T22:20:41

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 1. 
        See accessible information using `.contents` on the output.
    """
    atm = att_foxsi4_atmosphere(mid_energies=mid_energies, 
                                time_range=time_range)
    arf = foxsi4_telescope1_arf(mid_energies, off_axis_angle)

    flight_arf = atm.transmissions*arf.response

    func_name = sys._getframe().f_code.co_name
    atm.update_function_path(func_name)
    arf.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=flight_arf,
                            response_type="ARF-flight",
                            telescope=f"foxsi4-telescope1",
                            elements=(atm, 
                                      arf,
                                      ),
                            )

def foxsi4_telescope1_rmf():
    """The Redistribution Matrix Function (RMF) for Telescope 1. 

    Returns
    -------
    : `responses.Response2DOutput`
        An object containing all the redistribution matrix information. 
        See accessible information using `.contents` on the output.
    """
    
    rmf = tp.foxsi4_position1_detector_response()
    func_name = sys._getframe().f_code.co_name
    rmf.update_function_path(func_name)

    return Response2DOutput(filename="No-File",
                            function_path=func_name,
                            input_energy_edges=rmf.input_energy_edges,
                            output_energy_edges=rmf.output_energy_edges,
                            response=rmf.detector_response,
                            response_type="RMF",
                            telescope="foxsi4-telescope1",
                            elements=(rmf,
                                      ),
                            )

# telescope 2
@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_telescope2_arf(mid_energies, off_axis_angle):
    """The Ancillary Response Function (ARF) for Telescope 2.
    
    **DOES NOT** include atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 2 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 2. 
        See accessible information using `.contents` on the output.
    """
    tb = tp.foxsi4_position2_thermal_blanket(mid_energies) 
    opt = tp.foxsi4_position2_optics(mid_energies, 
                                     off_axis_angle=off_axis_angle) 
    uni_al = tp.foxsi4_position2_uniform_al(mid_energies)

    arf = tb.transmissions * opt.effective_areas * uni_al.transmissions

    func_name = sys._getframe().f_code.co_name
    tb.update_function_path(func_name)
    opt.update_function_path(func_name)
    uni_al.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=arf,
                            response_type="ARF",
                            telescope="foxsi4-telescope2",
                            elements=(tb, 
                                      opt, 
                                      uni_al,
                                      ),
                            )

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin, time_range=u.second)
def foxsi4_telescope2_flight_arf(mid_energies, off_axis_angle, time_range):
    """The flight Ancillary Response Function (ARF) for telescope 2.
    
    Includes atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 2 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.

    time_range : `astropy.units.quantity.Quantity` or `None`
        The time range the atmsopheric transmissions should be averaged
        over. If `None`, `numpy.nan<<astropy.units.second`, or
        `[numpy.nan, numpy.nan]<<astropy.units.second` then the full 
        time will be considered and the output will not be averaged but 
        a grid of the transmissions at all times and at any provided
        energies. Should be of length 2.
        Can be given as seconds since launch:
        - Observation start: 100<<astropy.units.second
        - Observation end: 461<<astropy.units.second
        Can be given as UTC time as well either as a string or and 
        Astropy time.
        - String format: YYYY-mm-ddTHH:MM:SS
        - Observation start: 2024-04-17T22:14:40
        - Observation end: 2024-04-17T22:20:41

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 2. 
        See accessible information using `.contents` on the output.
    """
    atm = att_foxsi4_atmosphere(mid_energies=mid_energies, 
                                time_range=time_range)
    arf = foxsi4_telescope2_arf(mid_energies, off_axis_angle)

    flight_arf = atm.transmissions*arf.response

    func_name = sys._getframe().f_code.co_name
    atm.update_function_path(func_name)
    arf.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=flight_arf,
                            response_type="ARF-flight",
                            telescope=f"foxsi4-telescope2",
                            elements=(atm, 
                                      arf,
                                      ),
                            )

@u.quantity_input(pitch=u.um)
def foxsi4_telescope2_rmf(region:int=None, pitch=None, _side:str="merged", _event_type:str="all"):
    """The Redistribution Matrix Function (RMF) for Telescope 2. 

    Parameters
    ----------
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

    _side : `str`
        Define the side on the detector the user requires the response 
        from. Must be in ["pt", "merged"].
        Default: "merged"

    _event_type : `str`
        Define the type of event trigger being considered in the 
        response. Must be in ["1hit", "2hit", "all"]. 
        Note: \"all\" and \"mix\" (old) are the same but some from 
        different naming conventions on the merged and individual 
        detector sides. This has been fixed and all files use \"all\"
        now.
        Default: "all"

    Returns
    -------
    : `responses.Response2DOutput`
        An object containing all the redistribution matrix information. 
        See accessible information using `.contents` on the output.
    """
    
    rmf = tp.foxsi4_position2_detector_response(region=region, 
                                                pitch=pitch, 
                                                _side=_side, 
                                                _event_type=_event_type)
    func_name = sys._getframe().f_code.co_name
    rmf.update_function_path(func_name)

    return Response2DOutput(filename="No-File",
                            function_path=func_name,
                            input_energy_edges=rmf.input_energy_edges,
                            output_energy_edges=rmf.output_energy_edges,
                            response=rmf.detector_response,
                            response_type="RMF",
                            telescope="foxsi4-telescope2",
                            elements=(rmf,
                                      ),
                            )

# telescope 3
@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_telescope3_arf(mid_energies, off_axis_angle=None):
    """The Ancillary Response Function (ARF) for Telescope 3.
    
    **DOES NOT** include atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 3 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.
        *** Not implemented yet. ***

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 3. 
        See accessible information using `.contents` on the output.
    """
    if off_axis_angle is not None:
        logging.warning(f"The `off_axis_angle` input for Telescope 3's optics ({sys._getframe().f_code.co_name}) is not yet implemented.")
    tb = tp.foxsi4_position3_thermal_blanket(mid_energies) 
    opt = tp.foxsi4_position3_optics(mid_energies) 
    mylar = tp.foxsi4_position3_al_mylar(mid_energies)
    pix_att = tp.foxsi4_position3_pixelated_attenuator(mid_energies)

    arf = tb.transmissions * opt.effective_areas * mylar.transmissions * pix_att.transmissions

    func_name = sys._getframe().f_code.co_name
    tb.update_function_path(func_name)
    opt.update_function_path(func_name)
    mylar.update_function_path(func_name)
    pix_att.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=arf,
                            response_type="ARF",
                            telescope="foxsi4-telescope3",
                            elements=(tb, 
                                      opt,
                                      mylar, 
                                      pix_att,
                                      ),
                            )

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin, time_range=u.second)
def foxsi4_telescope3_flight_arf(mid_energies, time_range, off_axis_angle=None):
    """The flight Ancillary Response Function (ARF) for Telescope 3.
    
    Includes atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 3 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.
        *** Not implemented yet. ***

    time_range : `astropy.units.quantity.Quantity` or `None`
        The time range the atmsopheric transmissions should be averaged
        over. If `None`, `numpy.nan<<astropy.units.second`, or
        `[numpy.nan, numpy.nan]<<astropy.units.second` then the full 
        time will be considered and the output will not be averaged but 
        a grid of the transmissions at all times and at any provided
        energies. Should be of length 2.
        Can be given as seconds since launch:
        - Observation start: 100<<astropy.units.second
        - Observation end: 461<<astropy.units.second
        Can be given as UTC time as well either as a string or and 
        Astropy time.
        - String format: YYYY-mm-ddTHH:MM:SS
        - Observation start: 2024-04-17T22:14:40
        - Observation end: 2024-04-17T22:20:41

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 3. 
        See accessible information using `.contents` on the output.
    """
    if off_axis_angle is not None:
        logging.warning(f"The `off_axis_angle` input for Telescope 3's optics ({sys._getframe().f_code.co_name}) is not yet implemented.")
    atm = att_foxsi4_atmosphere(mid_energies=mid_energies, 
                                time_range=time_range)
    arf = foxsi4_telescope3_arf(mid_energies)

    flight_arf = atm.transmissions*arf.response

    func_name = sys._getframe().f_code.co_name
    atm.update_function_path(func_name)
    arf.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=flight_arf,
                            response_type="ARF-flight",
                            telescope=f"foxsi4-telescope3",
                            elements=(atm, 
                                      arf,
                                      ),
                            )

@u.quantity_input(pitch=u.um)
def foxsi4_telescope3_rmf(region:int=None, pitch=None, _side:str="merged", _event_type:str="all"):
    """The Redistribution Matrix Function (RMF) for Telescope 3. 

    Parameters
    ----------
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

    _side : `str`
        Define the side on the detector the user requires the response 
        from. Must be in ["pt", "merged"].
        Default: "merged"

    _event_type : `str`
        Define the type of event trigger being considered in the 
        response. Must be in ["1hit", "2hit", "all"]. 
        Note: \"all\" and \"mix\" (old) are the same but some from 
        different naming conventions on the merged and individual 
        detector sides. This has been fixed and all files use \"all\"
        now.
        Default: "all"

    Returns
    -------
    : `responses.Response2DOutput`
        An object containing all the redistribution matrix information. 
        See accessible information using `.contents` on the output.
    """
    
    rmf = tp.foxsi4_position3_detector_response(region=region, 
                                                pitch=pitch, 
                                                _side=_side, 
                                                _event_type=_event_type)
    func_name = sys._getframe().f_code.co_name
    rmf.update_function_path(func_name)

    return Response2DOutput(filename="No-File",
                            function_path=func_name,
                            input_energy_edges=rmf.input_energy_edges,
                            output_energy_edges=rmf.output_energy_edges,
                            response=rmf.detector_response,
                            response_type="RMF",
                            telescope="foxsi4-telescope3",
                            elements=(rmf,
                                      ),
                            )

# telescope 4
@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_telescope4_arf(mid_energies, off_axis_angle=None):
    """The Ancillary Response Function (ARF) for Telescope 4.
    
    **DOES NOT** include atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 4 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.
        *** Not implemented yet. ***

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 4. 
        See accessible information using `.contents` on the output.
    """
    if off_axis_angle is not None:
        logging.warning(f"The `off_axis_angle` input for Telescope 4's optics ({sys._getframe().f_code.co_name}) is not yet implemented.")
    tb = tp.foxsi4_position4_thermal_blanket(mid_energies) 
    opt = tp.foxsi4_position4_optics(mid_energies) 
    uni_al = tp.foxsi4_position4_uniform_al(mid_energies)

    arf = tb.transmissions * opt.effective_areas * uni_al.transmissions

    func_name = sys._getframe().f_code.co_name
    tb.update_function_path(func_name)
    opt.update_function_path(func_name)
    uni_al.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=arf,
                            response_type="ARF",
                            telescope="foxsi4-telescope4",
                            elements=(tb, 
                                      opt, 
                                      uni_al,
                                      ),
                            )

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin, time_range=u.second)
def foxsi4_telescope4_flight_arf(mid_energies, time_range, off_axis_angle=None):
    """The flight Ancillary Response Function (ARF) for Telescope 4.
    
    Includes atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 4 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.
        *** Not implemented yet. ***

    time_range : `astropy.units.quantity.Quantity` or `None`
        The time range the atmsopheric transmissions should be averaged
        over. If `None`, `numpy.nan<<astropy.units.second`, or
        `[numpy.nan, numpy.nan]<<astropy.units.second` then the full 
        time will be considered and the output will not be averaged but 
        a grid of the transmissions at all times and at any provided
        energies. Should be of length 2.
        Can be given as seconds since launch:
        - Observation start: 100<<astropy.units.second
        - Observation end: 461<<astropy.units.second
        Can be given as UTC time as well either as a string or and 
        Astropy time.
        - String format: YYYY-mm-ddTHH:MM:SS
        - Observation start: 2024-04-17T22:14:40
        - Observation end: 2024-04-17T22:20:41

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 4. 
        See accessible information using `.contents` on the output.
    """
    if off_axis_angle is not None:
        logging.warning(f"The `off_axis_angle` input for Telescope 4's optics ({sys._getframe().f_code.co_name}) is not yet implemented.")
    atm = att_foxsi4_atmosphere(mid_energies=mid_energies, 
                                time_range=time_range)
    arf = foxsi4_telescope4_arf(mid_energies)

    flight_arf = atm.transmissions*arf.response

    func_name = sys._getframe().f_code.co_name
    atm.update_function_path(func_name)
    arf.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=flight_arf,
                            response_type="ARF-flight",
                            telescope=f"foxsi4-telescope4",
                            elements=(atm, 
                                      arf,
                                      ),
                            )

@u.quantity_input(pitch=u.um)
def foxsi4_telescope4_rmf(region:int=None, pitch=None, _side:str="merged", _event_type:str="all"):
    """The Redistribution Matrix Function (RMF) for Telescope 4. 

    Parameters
    ----------
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
        - pitches map onto the `region` input.
        - 60<<astropy.units.um -> Region 0
        - 80<<astropy.units.um -> Region 1
        - 100<<astropy.units.um -> Region 2

    _side : `str`
        Define the side on the detector the user requires the response 
        from. Must be in ["pt", "merged"].
        Default: "merged"

    _event_type : `str`
        Define the type of event trigger being considered in the 
        response. Must be in ["1hit", "2hit", "all"]. 
        Note: \"all\" and \"mix\" (old) are the same but some from 
        different naming conventions on the merged and individual 
        detector sides. This has been fixed and all files use \"all\"
        now.
        Default: "all"

    Returns
    -------
    : `responses.Response2DOutput`
        An object containing all the redistribution matrix information. 
        See accessible information using `.contents` on the output.
    """
    
    rmf = tp.foxsi4_position4_detector_response(region=region, 
                                                pitch=pitch, 
                                                _side=_side, 
                                                _event_type=_event_type)
    func_name = sys._getframe().f_code.co_name
    rmf.update_function_path(func_name)

    return Response2DOutput(filename="No-File",
                            function_path=func_name,
                            input_energy_edges=rmf.input_energy_edges,
                            output_energy_edges=rmf.output_energy_edges,
                            response=rmf.detector_response,
                            response_type="RMF",
                            telescope="foxsi4-telescope4",
                            elements=(rmf,
                                      ),
                            )

# telescope 5
@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_telescope5_arf(mid_energies, off_axis_angle):
    """The Ancillary Response Function (ARF) for Telescope 5.
    
    **DOES NOT** include atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 5 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 5. 
        See accessible information using `.contents` on the output.
    """
    tb = tp.foxsi4_position5_thermal_blanket(mid_energies) 
    opt = tp.foxsi4_position5_optics(mid_energies, 
                                     off_axis_angle=off_axis_angle) 
    mylar = tp.foxsi4_position5_al_mylar(mid_energies)
    pix_att = tp.foxsi4_position5_pixelated_attenuator(mid_energies)

    arf = tb.transmissions * opt.effective_areas * mylar.transmissions * pix_att.transmissions

    func_name = sys._getframe().f_code.co_name
    tb.update_function_path(func_name)
    opt.update_function_path(func_name)
    mylar.update_function_path(func_name)
    pix_att.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=arf,
                            response_type="ARF",
                            telescope="foxsi4-telescope5",
                            elements=(tb, 
                                      opt, 
                                      mylar,
                                      pix_att,
                                      ),
                            )

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin, time_range=u.second)
def foxsi4_telescope5_flight_arf(mid_energies, off_axis_angle, time_range):
    """The flight Ancillary Response Function (ARF) for Telescope 5.
    
    Includes atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 5 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.

    time_range : `astropy.units.quantity.Quantity` or `None`
        The time range the atmsopheric transmissions should be averaged
        over. If `None`, `numpy.nan<<astropy.units.second`, or
        `[numpy.nan, numpy.nan]<<astropy.units.second` then the full 
        time will be considered and the output will not be averaged but 
        a grid of the transmissions at all times and at any provided
        energies. Should be of length 2.
        Can be given as seconds since launch:
        - Observation start: 100<<astropy.units.second
        - Observation end: 461<<astropy.units.second
        Can be given as UTC time as well either as a string or and 
        Astropy time.
        - String format: YYYY-mm-ddTHH:MM:SS
        - Observation start: 2024-04-17T22:14:40
        - Observation end: 2024-04-17T22:20:41

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 5. 
        See accessible information using `.contents` on the output.
    """
    atm = att_foxsi4_atmosphere(mid_energies=mid_energies, 
                                time_range=time_range)
    arf = foxsi4_telescope5_arf(mid_energies, off_axis_angle)

    flight_arf = atm.transmissions*arf.response

    func_name = sys._getframe().f_code.co_name
    atm.update_function_path(func_name)
    arf.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=flight_arf,
                            response_type="ARF-flight",
                            telescope=f"foxsi4-telescope5",
                            elements=(atm, 
                                      arf,
                                      ),
                            )

@u.quantity_input(pitch=u.um)
def foxsi4_telescope5_rmf(region:int=None, pitch=None, _side:str="merged", _event_type:str="all"):
    """The Redistribution Matrix Function (RMF) for Telescope 5. 

    Parameters
    ----------
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

    _side : `str`
        Define the side on the detector the user requires the response 
        from. Must be in ["pt", "merged"].
        Default: "merged"

    _event_type : `str`
        Define the type of event trigger being considered in the 
        response. Must be in ["1hit", "2hit", "all"]. 
        Note: \"all\" and \"mix\" (old) are the same but some from 
        different naming conventions on the merged and individual 
        detector sides. This has been fixed and all files use \"all\"
        now.
        Default: "all"

    Returns
    -------
    : `responses.Response2DOutput`
        An object containing all the redistribution matrix information. 
        See accessible information using `.contents` on the output.
    """
    
    rmf = tp.foxsi4_position5_detector_response(region=region, 
                                                pitch=pitch, 
                                                _side=_side, 
                                                _event_type=_event_type)
    func_name = sys._getframe().f_code.co_name
    rmf.update_function_path(func_name)

    return Response2DOutput(filename="No-File",
                            function_path=func_name,
                            input_energy_edges=rmf.input_energy_edges,
                            output_energy_edges=rmf.output_energy_edges,
                            response=rmf.detector_response,
                            response_type="RMF",
                            telescope="foxsi4-telescope5",
                            elements=(rmf,
                                      ),
                            )

# telescope 6
@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_telescope6_arf(mid_energies, off_axis_angle):
    """The Ancillary Response Function (ARF) for Telescope 6.
    
    **DOES NOT** include atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 6 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 6. 
        See accessible information using `.contents` on the output.
    """
    tb = tp.foxsi4_position6_thermal_blanket(mid_energies) 
    opt = tp.foxsi4_position6_optics(mid_energies, 
                                     off_axis_angle=off_axis_angle) 
    mylar = tp.foxsi4_position5_al_mylar(mid_energies)

    arf = tb.transmissions * opt.effective_areas * mylar.transmissions 

    func_name = sys._getframe().f_code.co_name
    tb.update_function_path(func_name)
    opt.update_function_path(func_name)
    mylar.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=arf,
                            response_type="ARF",
                            telescope="foxsi4-telescope6",
                            elements=(tb, 
                                      opt, 
                                      mylar,
                                      ),
                            )

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin, time_range=u.second)
def foxsi4_telescope6_flight_arf(mid_energies, off_axis_angle, time_range):
    """The flight Ancillary Response Function (ARF) for Telescope 6.
    
    Includes atmospheric attenuation from flight.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the Telescope 6 componented are calculated. 
        If `numpy.nan<<astropy.units.keV` is passed then an entry for 
        all native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.

    time_range : `astropy.units.quantity.Quantity` or `None`
        The time range the atmsopheric transmissions should be averaged
        over. If `None`, `numpy.nan<<astropy.units.second`, or
        `[numpy.nan, numpy.nan]<<astropy.units.second` then the full 
        time will be considered and the output will not be averaged but 
        a grid of the transmissions at all times and at any provided
        energies. Should be of length 2.
        Can be given as seconds since launch:
        - Observation start: 100<<astropy.units.second
        - Observation end: 461<<astropy.units.second
        Can be given as UTC time as well either as a string or and 
        Astropy time.
        - String format: YYYY-mm-ddTHH:MM:SS
        - Observation start: 2024-04-17T22:14:40
        - Observation end: 2024-04-17T22:20:41

    Returns
    -------
    : `responses.Response1DOutput`
        An object containing the 1D response information of Telescope 6. 
        See accessible information using `.contents` on the output.
    """
    atm = att_foxsi4_atmosphere(mid_energies=mid_energies, 
                                time_range=time_range)
    arf = foxsi4_telescope6_arf(mid_energies, off_axis_angle)

    flight_arf = atm.transmissions*arf.response

    func_name = sys._getframe().f_code.co_name
    atm.update_function_path(func_name)
    arf.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=flight_arf,
                            response_type="ARF-flight",
                            telescope=f"foxsi4-telescope6",
                            elements=(atm, 
                                      arf,
                                      ),
                            )

def foxsi4_telescope6_rmf():
    """The Redistribution Matrix Function (RMF) for Telescope 6. 

    Returns
    -------
    : `None`
    """
    logging.warning(f"The Telescope 6 Timepix detector response from {sys._getframe().f_code.co_name} does not yet exist.")
    rmf = tp.foxsi4_position6_detector_response()
    return rmf

def asset_response_chain_plot(save_location=None):
    """Plot the response chain data to visually check."""
    pos2arffunc = {0:foxsi4_telescope0_arf, 
                   1:foxsi4_telescope1_arf, 
                   2:foxsi4_telescope2_arf, 
                   3:foxsi4_telescope3_arf, 
                   4:foxsi4_telescope4_arf, 
                   5:foxsi4_telescope5_arf,
                   6:foxsi4_telescope6_arf,
                   }
    pos2rmffunc = {0:foxsi4_telescope0_rmf, 
                   1:foxsi4_telescope1_rmf, 
                   2:foxsi4_telescope2_rmf, 
                   3:foxsi4_telescope3_rmf, 
                   4:foxsi4_telescope4_rmf, 
                   5:foxsi4_telescope5_rmf,
                   6:foxsi4_telescope6_rmf,
                   }
    
    fig = plt.figure(figsize=(18, 6))
    positions = list(pos2rmffunc.keys())
    gs = gridspec.GridSpec(3, len(positions))

    original_fs = plt.rcParams["font.size"]
    plt.rcParams["font.size"] = 6

    for c, key in enumerate(positions):
        off_axis_angle = 0 << u.arcmin
        pos_rmf = pos2rmffunc[key](region=0) if 2<=key<=5 else pos2rmffunc[key]()
        mid_energies = np.linspace(5,20,100)<<u.keV if pos_rmf is None else (pos_rmf.input_energy_edges[:-1]+pos_rmf.input_energy_edges[1:])/2
        pos_arf = pos2arffunc[key](mid_energies=mid_energies, off_axis_angle=off_axis_angle)

        gs_ax0 = fig.add_subplot(gs[0, c])
        gs_ax1 = fig.add_subplot(gs[1, c])
        gs_ax2 = fig.add_subplot(gs[2, c])

        gs_ax0.plot(pos_arf.mid_energies, pos_arf.response)
        gs_ax0.set_xlabel(f"Photon Energy [{pos_arf.mid_energies.unit:latex}]")
        gs_ax0.set_ylabel(f"Response [{pos_arf.response.unit:latex}]")
        gs_ax0.set_title(f"Pos. {key}: ARF")

        if pos_rmf is None:
            continue

        extent = [np.min(pos_rmf.output_energy_edges.value), 
                  np.max(pos_rmf.output_energy_edges.value), 
                  np.min(pos_rmf.input_energy_edges.value), 
                  np.max(pos_rmf.input_energy_edges.value)]
        aspect=(extent[1]-extent[0])/(extent[3]-extent[2])
        r = gs_ax1.imshow(pos_rmf.response.value, 
                        origin="lower", 
                        norm=LogNorm(vmin=1e-7), 
                        extent=extent,
                        aspect=aspect,
                        )
        cbar = plt.colorbar(r)
        cbar.ax.set_ylabel(f"Response [{pos_rmf.response.unit:latex}]")
        gs_ax1.set_xlabel(f"Count Energy [{pos_rmf.output_energy_edges.unit:latex}]")
        gs_ax1.set_ylabel(f"Photon Energy [{pos_rmf.input_energy_edges.unit:latex}]")
        gs_ax1.set_title(f"Pos. {key}: RMF")

        pos_srm = foxsi4_telescope_spectral_response(pos_arf, pos_rmf)

        r = gs_ax2.imshow(pos_srm.response.value, 
                        origin="lower", 
                        norm=LogNorm(vmin=1e-7), 
                        extent=extent,
                        aspect=aspect,
                        )
        cbar = plt.colorbar(r)
        cbar.ax.set_ylabel(f"Response [{pos_srm.response.unit:latex}]")
        gs_ax2.set_xlabel(f"Count Energy [{pos_srm.output_energy_edges.unit:latex}]")
        gs_ax2.set_ylabel(f"Photon Energy [{pos_srm.input_energy_edges.unit:latex}]")
        gs_ax2.set_title(f"Pos. {key}: SRM")
    plt.tight_layout()
    if save_location is not None:
        pathlib.Path(save_location).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(save_location,"response-chain.png"), dpi=200, bbox_inches="tight")
    plt.show()
    plt.rcParams["font.size"] = original_fs

def asset_response_hit_combination_plot(save_location=None):
    """Look at different combinations of the 1hit and 2hit responses."""
    p5_rmf1 = foxsi4_telescope5_rmf(region=0, _event_type="1hit")
    p5_rmf2 = foxsi4_telescope5_rmf(region=0, _event_type="2hit")

    fig = plt.figure(figsize=(18, 4.9))
    gs = gridspec.GridSpec(1, 3)

    gs_ax0 = fig.add_subplot(gs[0, 0])
    h1f, h2f = 0.6, 0.4
    m = h1f*p5_rmf1.response + h2f*p5_rmf2.response
    r = gs_ax0.imshow(m.value, 
                      origin="lower", 
                      norm=LogNorm(vmin=0.001), 
                      extent=[np.min(p5_rmf1.output_energy_edges.value), 
                              np.max(p5_rmf1.output_energy_edges.value), 
                              np.min(p5_rmf1.input_energy_edges.value), 
                              np.max(p5_rmf1.input_energy_edges.value)]
                      )
    cbar = plt.colorbar(r)
    cbar.ax.set_ylabel(f"Response [{m.unit:latex}]")
    gs_ax0.set_xlabel(f"Count Energy [{p5_rmf1.output_energy_edges.unit:latex}]")
    gs_ax0.set_ylabel(f"Photon Energy [{p5_rmf1.input_energy_edges.unit:latex}]")
    gs_ax0.set_title(f"Pos. 5: RMF-({h1f}*1hit+{h2f}*2hit)")

    gs_ax1 = fig.add_subplot(gs[0, 1])
    h1f, h2f = 0.1, 0.9
    m = h1f*p5_rmf1.response + h2f*p5_rmf2.response
    r = gs_ax1.imshow(m.value, 
                      origin="lower", 
                      norm=LogNorm(vmin=0.001), 
                      extent=[np.min(p5_rmf1.output_energy_edges.value), 
                              np.max(p5_rmf1.output_energy_edges.value), 
                              np.min(p5_rmf1.input_energy_edges.value), 
                              np.max(p5_rmf1.input_energy_edges.value)]
                      )
    cbar = plt.colorbar(r)
    cbar.ax.set_ylabel(f"Response [{m.unit:latex}]")
    gs_ax1.set_xlabel(f"Count Energy [{p5_rmf1.output_energy_edges.unit:latex}]")
    gs_ax1.set_ylabel(f"Photon Energy [{p5_rmf1.input_energy_edges.unit:latex}]")
    gs_ax1.set_title(f"Pos. 5: RMF-({h1f}*1hit+{h2f}*2hit)")

    gs_ax2 = fig.add_subplot(gs[0, 2])
    h1f, h2f = 0.9, 0.1
    m = h1f*p5_rmf1.response + h2f*p5_rmf2.response
    r = gs_ax2.imshow(m.value, 
                      origin="lower", 
                      norm=LogNorm(vmin=0.001), 
                      extent=[np.min(p5_rmf1.output_energy_edges.value), 
                              np.max(p5_rmf1.output_energy_edges.value), 
                              np.min(p5_rmf1.input_energy_edges.value), 
                              np.max(p5_rmf1.input_energy_edges.value)]
                      )
    cbar = plt.colorbar(r)
    cbar.ax.set_ylabel(f"Response [{m.unit:latex}]")
    gs_ax2.set_xlabel(f"Count Energy [{p5_rmf1.output_energy_edges.unit:latex}]")
    gs_ax2.set_ylabel(f"Photon Energy [{p5_rmf1.input_energy_edges.unit:latex}]")
    gs_ax2.set_title(f"Pos. 5: RMF-({h1f}*1hit+{h2f}*2hit)")
    plt.tight_layout()
    if save_location is not None:
        pathlib.Path(save_location).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(save_location,"response-hit-combinations.png"), dpi=200, bbox_inches="tight")
    plt.show()

if __name__=="__main__":
    save_location = None # ASSETS_PATH
    asset_response_chain_plot(save_location=save_location)
    asset_response_hit_combination_plot(save_location=save_location)