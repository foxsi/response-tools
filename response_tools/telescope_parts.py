"""Wrappers for position aliases for more specific functions."""

import logging
import sys

import astropy.units as u

from response_tools.attenuation import (att_thermal_blanket,
                                        att_pixelated, 
                                        att_al_mylar,
                                        att_uniform_al_cdte
                                        )
from response_tools.detector_response import (cdte_det_resp, 
                                              cmos_det_resp,
                                              )
from response_tools.effective_area import (eff_area_msfc_10shell,
                                           eff_area_msfc_hi_res,
                                           eff_area_nagoya_hxt,
                                           )

# position 0
@u.quantity_input(mid_energies=u.keV)
def foxsi4_position0_obf(mid_energies):
    pass

# position 1
@u.quantity_input(mid_energies=u.keV)
def foxsi4_position1_obf(mid_energies):
    pass

# position 2
@u.quantity_input(mid_energies=u.keV)
def foxsi4_position2_thermal_blanket(mid_energies):
    """Position 2 thermal blanket transmissions.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the thermal blanketing transmission is 
        required. If `numpy.nan<<astropy.units.keV` is passed then an 
        entry for all native file energies are returned. 
        Unit must be convertable to keV.

    Returns
    -------
    : `attenuation.AttOutput`
        An object containing the attenuation/transmission information of
        the thermal blanket. See accessible information using 
        `.contents` on the output.
    """
    r = att_thermal_blanket(mid_energies)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_position2_optics(mid_energies, off_axis_angle):
    """Position 2 MSFC heritage X-7 optic effective areas.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the position 2 optics is required. If 
        `numpy.nan<<astropy.units.keV` is passed then an entry for all 
        native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.

    Returns
    -------
    : `effective_area.EffAreaOutput`
        An object containing the effective area information of the MSFC 
        heritage X-7 optic. See accessible information using `.contents` 
        on the output.
    """
    r = eff_area_msfc_10shell(mid_energies, 
                              off_axis_angle=off_axis_angle, 
                              optic_id="X-7")
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def foxsi4_position2_uniform_al(mid_energies):
    """Position 2 uniform Al attenuator transmissions.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the uniform Al attenuator transmission is 
        required. If `numpy.nan<<astropy.units.keV` is passed then an 
        entry for all native file energies are returned. 
        Unit must be convertable to keV.

    Returns
    -------
    : `attenuation.AttOutput`
        An object containing the attenuation/transmission information of
        the uniform Al attenuator. See accessible information using 
        `.contents` on the output.
    """
    r = att_uniform_al_cdte(mid_energies, 
                            position=2)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(pitch=u.um)
def foxsi4_position2_detector_response(region:int=None, pitch=None, _side:str="merged", _event_type:str="all"):
    """Position 2 CdTe4 detector response.

    Parameters
    ----------
    region : `int`
        The region of the CdTe detector required. Either provide 
        `region` _xor_ `pitch`. The `region` maps onto the pitches used 
        across the detector. 
            Region 0 -> 60<<astropy.units.um 
            Region 1 -> 80<<astropy.units.um
            Region 2 -> 100<<astropy.units.um

    pitch : `astropy.units.quantity.Quantity`
        Instead of `region`, it might be more usefule to specify the 
        pitch in physical units (must b convertable to 
        `astropy.units.um`). Either provide `region` _xor_ `pitch`.
        The pitches map onto the `region` input.
            60<<astropy.units.um -> Region 0
            80<<astropy.units.um -> Region 1
            100<<astropy.units.um -> Region 2

    _side : `str`
        Define the side on the detector the user requires the response 
        from. Must be in ["pt", "merged"].
        Default: "merged"

    _event_type : `str`
        Define the type of event trigger being considered in the 
        response. Must be in ["1hit", "2hit", ("all", "mix")]. 
        Note: \"all\" and \"mix\" are the same but some from different 
        naming conventions on the merged and individual detector sides. 
        This will be fixed at some point in the future.
        Default: "all"

    Returns
    -------
    : `detector_response.DetectorResponseOutput`
        An object containing all the redistribution matrix information. 
        See accessible information using `.contents` on the output.
    """
    pos2_det = 4
    r = cdte_det_resp(cdte=pos2_det, 
                      region=region, 
                      pitch=pitch, 
                      side=_side, 
                      event_type=_event_type)
    if r is None:
        return
    r.update_function_path(sys._getframe().f_code.co_name)
    r.detector = f"CdTe{pos2_det}-Detector-Response"
    return r

# position 3
@u.quantity_input(mid_energies=u.keV)
def foxsi4_position3_thermal_blanket(mid_energies):
    """Position 3 thermal blanket transmissions.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the thermal blanketing transmission is 
        required. If `numpy.nan<<astropy.units.keV` is passed then an 
        entry for all native file energies are returned. 
        Unit must be convertable to keV.

    Returns
    -------
    : `attenuation.AttOutput`
        An object containing the attenuation/transmission information of
        the thermal blanket. See accessible information using 
        `.contents` on the output.
    """
    r = att_thermal_blanket(mid_energies)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_position3_optics(mid_energies, off_axis_angle=None):
    """Position 3 MSFC high resolution optic effective areas.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the position 3 optics is required. If 
        `numpy.nan<<astropy.units.keV` is passed then an entry for all 
        native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.
        *** Not implemented yet. ***

    Returns
    -------
    : `effective_area.EffAreaOutput`
        An object containing the effective area information of the MSFC 
        high resolution optic. See accessible information using 
        `.contents` on the output.
    """
    if off_axis_angle is not None:
        logging.warning(f"The `off_axis_angle` input for Position 3's optics ({sys._getframe().f_code.co_name}) is not yet implemented.")
    r = eff_area_msfc_hi_res(mid_energies, 
                             off_axis_angle=off_axis_angle,
                             position=3, 
                             use_model=True)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def foxsi4_position3_al_mylar(mid_energies):
    """Position 3 thin Mylar window transmissions.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the thin Mylar window transmission is 
        required. If `numpy.nan<<astropy.units.keV` is passed then an 
        entry for all native file energies are returned. 
        Unit must be convertable to keV.

    Returns
    -------
    : `attenuation.AttOutput`
        An object containing the attenuation/transmission information of
        the thin Mylar window. See accessible information using 
        `.contents` on the output.
    """
    r = att_al_mylar(mid_energies)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def foxsi4_position3_pixelated_attenuator(mid_energies):
    """Position 3 pixelated attenuator transmissions.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the pixelated attenuator transmission is 
        required. If `numpy.nan<<astropy.units.keV` is passed then an 
        entry for all native file energies are returned. 
        Unit must be convertable to keV.

    Returns
    -------
    : `attenuation.AttOutput`
        An object containing the attenuation/transmission information of
        the pixelated attenuator. See accessible information using 
        `.contents` on the output.
    """
    r = att_pixelated(mid_energies, 
                      use_model=True)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(pitch=u.um)
def foxsi4_position3_detector_response(region:int=None, pitch=None, _side:str="merged", _event_type:str="all"):
    """Position 3 CdTe2 detector response.

    Parameters
    ----------
    region : `int`
        The region of the CdTe detector required. Either provide 
        `region` _xor_ `pitch`. The `region` maps onto the pitches used 
        across the detector. 
            Region 0 -> 60<<astropy.units.um 
            Region 1 -> 80<<astropy.units.um
            Region 2 -> 100<<astropy.units.um

    pitch : `astropy.units.quantity.Quantity`
        Instead of `region`, it might be more usefule to specify the 
        pitch in physical units (must b convertable to 
        `astropy.units.um`). Either provide `region` _xor_ `pitch`.
        The pitches map onto the `region` input.
            60<<astropy.units.um -> Region 0
            80<<astropy.units.um -> Region 1
            100<<astropy.units.um -> Region 2

    _side : `str`
        Define the side on the detector the user requires the response 
        from. Must be in ["pt", "merged"].
        Default: "merged"

    _event_type : `str`
        Define the type of event trigger being considered in the 
        response. Must be in ["1hit", "2hit", ("all", "mix")]. 
        Note: \"all\" and \"mix\" are the same but some from different 
        naming conventions on the merged and individual detector sides. 
        This will be fixed at some point in the future.
        Default: "all"

    Returns
    -------
    : `detector_response.DetectorResponseOutput`
        An object containing all the redistribution matrix information. 
        See accessible information using `.contents` on the output.
    """
    pos3_det = 2
    r = cdte_det_resp(cdte=pos3_det, 
                      region=region, 
                      pitch=pitch, 
                      side=_side, 
                      event_type=_event_type)
    if r is None:
        return
    r.update_function_path(sys._getframe().f_code.co_name)
    r.detector = f"CdTe{pos3_det}-Detector-Response"
    return r

# position 4
@u.quantity_input(mid_energies=u.keV)
def foxsi4_position4_thermal_blanket(mid_energies):
    """Position 4 thermal blanket transmissions.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the thermal blanketing transmission is 
        required. If `numpy.nan<<astropy.units.keV` is passed then an 
        entry for all native file energies are returned. 
        Unit must be convertable to keV.

    Returns
    -------
    : `attenuation.AttOutput`
        An object containing the attenuation/transmission information of
        the thermal blanket. See accessible information using 
        `.contents` on the output.
    """
    r = att_thermal_blanket(mid_energies)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_position4_optics(mid_energies, off_axis_angle=None):
    """Position 4 Nagoya high resolution optic effective areas.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the position 4 optics is required. If 
        `numpy.nan<<astropy.units.keV` is passed then an entry for all 
        native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.
        *** Not implemented yet. ***

    Returns
    -------
    : `effective_area.EffAreaOutput`
        An object containing the effective area information of the 
        Nagoya high resolution optic. See accessible information using 
        `.contents` on the output.
    """
    if off_axis_angle is not None:
        logging.warning(f"The `off_axis_angle` input for Position 4's optics ({sys._getframe().f_code.co_name}) is not yet implemented.")
    r = eff_area_nagoya_hxt(mid_energies, 
                            off_axis_angle=off_axis_angle,
                            use_model=True)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def foxsi4_position4_uniform_al(mid_energies):
    """Position 4 uniform Al attenuator transmissions.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the uniform Al attenuator transmission is 
        required. If `numpy.nan<<astropy.units.keV` is passed then an 
        entry for all native file energies are returned. 
        Unit must be convertable to keV.

    Returns
    -------
    : `attenuation.AttOutput`
        An object containing the attenuation/transmission information of
        the uniform Al attenuator. See accessible information using 
        `.contents` on the output.
    """
    r = att_uniform_al_cdte(mid_energies, 
                            position=4)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(pitch=u.um)
def foxsi4_position4_detector_response(region:int=None, pitch=None, _side:str="merged", _event_type:str="all"):
    """Position 4 CdTe3 detector response.

    Parameters
    ----------
    region : `int`
        The region of the CdTe detector required. Either provide 
        `region` _xor_ `pitch`. The `region` maps onto the pitches used 
        across the detector. 
            Region 0 -> 60<<astropy.units.um 
            Region 1 -> 80<<astropy.units.um
            Region 2 -> 100<<astropy.units.um

    pitch : `astropy.units.quantity.Quantity`
        Instead of `region`, it might be more usefule to specify the 
        pitch in physical units (must b convertable to 
        `astropy.units.um`). Either provide `region` _xor_ `pitch`.
        The pitches map onto the `region` input.
            60<<astropy.units.um -> Region 0
            80<<astropy.units.um -> Region 1
            100<<astropy.units.um -> Region 2

    _side : `str`
        Define the side on the detector the user requires the response 
        from. Must be in ["pt", "merged"].
        Default: "merged"

    _event_type : `str`
        Define the type of event trigger being considered in the 
        response. Must be in ["1hit", "2hit", ("all", "mix")]. 
        Note: \"all\" and \"mix\" are the same but some from different 
        naming conventions on the merged and individual detector sides. 
        This will be fixed at some point in the future.
        Default: "all"

    Returns
    -------
    : `detector_response.DetectorResponseOutput`
        An object containing all the redistribution matrix information. 
        See accessible information using `.contents` on the output.
    """
    pos4_det = 3
    r = cdte_det_resp(cdte=pos4_det, 
                      region=region, 
                      pitch=pitch, 
                      side=_side, 
                      event_type=_event_type)
    if r is None:
        return
    r.update_function_path(sys._getframe().f_code.co_name)
    r.detector = f"CdTe{pos4_det}-Detector-Response"
    return r

# position 5
@u.quantity_input(mid_energies=u.keV)
def foxsi4_position5_thermal_blanket(mid_energies):
    """Position 5 thermal blanket transmissions.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the thermal blanketing transmission is 
        required. If `numpy.nan<<astropy.units.keV` is passed then an 
        entry for all native file energies are returned. 
        Unit must be convertable to keV.

    Returns
    -------
    : `attenuation.AttOutput`
        An object containing the attenuation/transmission information of
        the thermal blanket. See accessible information using 
        `.contents` on the output.
    """
    r = att_thermal_blanket(mid_energies)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_position5_optics(mid_energies, off_axis_angle):
    """Position 5 MSFC heritage X-8 optic effective areas.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the position 5 optics is required. If 
        `numpy.nan<<astropy.units.keV` is passed then an entry for all 
        native file energies are returned. 
        Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.

    Returns
    -------
    : `effective_area.EffAreaOutput`
        An object containing the effective area information of the MSFC 
        heritage X-8 optic. See accessible information using `.contents` 
        on the output.
    """
    r = eff_area_msfc_10shell(mid_energies, 
                              off_axis_angle=off_axis_angle<<u.arcmin, 
                              optic_id="X-8")
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def foxsi4_position5_al_mylar(mid_energies):
    """Position 5 thin Mylar window transmissions.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the thin Mylar window transmission is 
        required. If `numpy.nan<<astropy.units.keV` is passed then an 
        entry for all native file energies are returned. 
        Unit must be convertable to keV.

    Returns
    -------
    : `attenuation.AttOutput`
        An object containing the attenuation/transmission information of
        the thin Mylar window. See accessible information using 
        `.contents` on the output.
    """
    r = att_al_mylar(mid_energies)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def foxsi4_position5_pixelated_attenuator(mid_energies):
    """Position 5 pixelated attenuator transmissions.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the pixelated attenuator transmission is 
        required. If `numpy.nan<<astropy.units.keV` is passed then an 
        entry for all native file energies are returned. 
        Unit must be convertable to keV.

    Returns
    -------
    : `attenuation.AttOutput`
        An object containing the attenuation/transmission information of
        the pixelated attenuator. See accessible information using 
        `.contents` on the output.
    """
    r = att_pixelated(mid_energies, 
                      use_model=True)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(pitch=u.um)
def foxsi4_position5_detector_response(region:int=None, pitch=None, _side:str="merged", _event_type:str="all"):
    """Position 5 CdTe1 detector response.

    Parameters
    ----------
    region : `int`
        The region of the CdTe detector required. Either provide 
        `region` _xor_ `pitch`. The `region` maps onto the pitches used 
        across the detector. 
            Region 0 -> 60<<astropy.units.um 
            Region 1 -> 80<<astropy.units.um
            Region 2 -> 100<<astropy.units.um

    pitch : `astropy.units.quantity.Quantity`
        Instead of `region`, it might be more usefule to specify the 
        pitch in physical units (must b convertable to 
        `astropy.units.um`). Either provide `region` _xor_ `pitch`.
        The pitches map onto the `region` input.
            60<<astropy.units.um -> Region 0
            80<<astropy.units.um -> Region 1
            100<<astropy.units.um -> Region 2

    _side : `str`
        Define the side on the detector the user requires the response 
        from. Must be in ["pt", "merged"].
        Default: "merged"

    _event_type : `str`
        Define the type of event trigger being considered in the 
        response. Must be in ["1hit", "2hit", ("all", "mix")]. 
        Note: \"all\" and \"mix\" are the same but some from different 
        naming conventions on the merged and individual detector sides. 
        This will be fixed at some point in the future.
        Default: "all"

    Returns
    -------
    : `detector_response.DetectorResponseOutput`
        An object containing all the redistribution matrix information. 
        See accessible information using `.contents` on the output.
    """
    pos5_det = 1
    r = cdte_det_resp(cdte=pos5_det, 
                      region=region, 
                      pitch=pitch, 
                      side=_side, 
                      event_type=_event_type)
    if r is None:
        return
    r.update_function_path(sys._getframe().f_code.co_name)
    r.detector = f"CdTe{pos5_det}-Detector-Response"
    return r

if __name__=="__main__":
    # mid_energies = [4.5,  5.5,  6.5,  7.5,  8.5,  9.5, 11. , 13. , 15. , 17. , 19. , 22.5, 27.5] << u.keV
    # p2_tb = position2_thermal_blanket(mid_energies)
    p2_dr_reg = position2_detector_response(region=0)
    p2_dr_pitch = position2_detector_response(pitch=60<<u.um)
    position2_detector_response(region=0, pitch=60<<u.um)
    position2_detector_response(pitch=80<<u.um, _side="merged", _event_type="1hit")