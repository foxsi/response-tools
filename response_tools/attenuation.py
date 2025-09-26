"""Code to load different attenuators. """

from dataclasses import dataclass
import logging
import os
import pathlib
import sys
import warnings

from astropy.io import fits
import astropy.units as u
import numpy as np
import pandas
import scipy

from response_tools.util import BaseOutput, native_resolution

ATT_PATH = os.path.join(pathlib.Path(__file__).parent, "..", "response-information", "attenuation-data")
ASSETS_PATH = os.path.join(pathlib.Path(__file__).parent, "..", "assets", "response-tools-figs", "att-figs")

@dataclass
class AttOutput(BaseOutput):
    """Class for keeping track of attenuation response values."""
    # numbers
    transmissions: u.Quantity
    # bookkeeping
    attenuation_type: str
    model: bool
    # any other fields needed can be added here
    # can even add with a default so the input is not required for every other instance
    mid_energies: u.Quantity = np.nan<<u.keV
    off_axis_angle: u.Quantity = np.nan<<u.arcmin
    times: u.Quantity = np.nan<<u.second

# thermal blanket attenuation
@u.quantity_input(mid_energies=u.keV)
def att_thermal_blanket(mid_energies, file=None):
    """Thermal blanket transmittance interpolated to the given energies.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the transmission is required. If 
        `numpy.nan<<astropy.units.keV` is passed then an entry for all 
        native file energies are returned. 
        Unit must be convertable to keV.

    file : `str` or `None`
        Gives the ability to provide custom files for the information. 
        Default: None

    Returns
    -------
    : `AttOutput`
        An object containing the energies for each transmission, the 
        transmissions, and more. See accessible information using 
        `.contents` on the output.
    """
    _f = os.path.join(ATT_PATH, "F4_Blanket_transmission_v1.dat") if file is None else file
    att = scipy.io.readsav(_f)
    att_es, att_values = att["energy_kev"] << u.keV, att["f4_transmission"] << u.dimensionless_unscaled
    mid_energies = native_resolution(native_x=att_es, input_x=mid_energies)

    return AttOutput(filename=_f,
                     function_path=f"{sys._getframe().f_code.co_name}",
                     mid_energies=mid_energies,
                     transmissions=np.interp(mid_energies.value, 
                                             att_es.value, 
                                             att_values.value, 
                                             left=0, 
                                             right=1) << u.dimensionless_unscaled,
                     attenuation_type="Thermal-Blanket",
                     model=True,
                     )

# uniform Al attenuation
@u.quantity_input(mid_energies=u.keV)
def att_uniform_al_cdte(mid_energies, position=None, file=None):
    """Uniform Al filter transmittance interpolated to given energies.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the transmission is required. If 
        `numpy.nan<<astropy.units.keV` is passed then an entry for all 
        native file energies are returned. 
        Unit must be convertable to keV.

    position : `int`
        The focal plane position of the desired attenuator. Must be in 
        the list [2, 4]. 
        Default: None

    file : `str` or `None`
        Gives the ability to provide custom files for the information. 
        Default: None

    Returns
    -------
    : `AttOutput`
        An object containing the energies for each transmission, the 
        transmissions, and more. See accessible information using 
        `.contents` on the output.
    """
    if (position is None) or (position not in [2,4]):
        logging.warning(f"The {sys._getframe().f_code.co_name} `position` must be 2 or 4.")
    _f = os.path.join(ATT_PATH, f"unif_att_p{position}_theoretical_v1.csv") if file is None else file
    att = pandas.read_csv(_f)
    att_es, att_values = att["energy[keV]"] << u.keV, att["transmission"] << u.dimensionless_unscaled
    mid_energies = native_resolution(native_x=att_es, input_x=mid_energies)

    return AttOutput(filename=_f,
                     function_path=f"{sys._getframe().f_code.co_name}",
                     mid_energies=mid_energies,
                     transmissions=np.interp(mid_energies.value, 
                                             att_es.value, 
                                             att_values.value, 
                                             left=0, 
                                             right=1) << u.dimensionless_unscaled,
                     attenuation_type="Uniform-Al-Filter",
                     model=True,
                     )

# pixelated attenuator attenuation
@u.quantity_input(mid_energies=u.keV)
def att_pixelated(mid_energies, use_model=False, file=None):
    """Pixelated attenuator transmittance interpolated to energies.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the transmission is required. If 
        `numpy.nan<<astropy.units.keV` is passed then an entry for all 
        native file energies are returned. 
        Unit must be convertable to keV.

    use_model : `bool`
        Defines whether to use the measured values for the pixelated
        attenuator (False) or the modelled values (True).
        Default: False

    file : `str` or `None`
        Gives the ability to provide custom files for the information. 
        Default: None

    Returns
    -------
    : `AttOutput`
        An object containing the energies for each transmission, the 
        transmissions, and more. See accessible information using 
        `.contents` on the output.
    """
    _f = os.path.join(ATT_PATH, "20240607_fosxi4_transmission_v1.csv") if file is None else file
    att = pandas.read_csv(_f)
    att_es, att_values_measured, att_values_modelled = att["energy"] << u.keV, att["measured_transmission"] << u.dimensionless_unscaled, att["modeled_transmission"] << u.dimensionless_unscaled

    mid_energies = native_resolution(native_x=att_es, input_x=mid_energies)
    if use_model:
        att_vals = att_values_modelled
    else:
        att_vals = att_values_measured

    return AttOutput(filename=_f,
                     function_path=f"{sys._getframe().f_code.co_name}",
                     mid_energies=mid_energies,
                     transmissions=np.interp(mid_energies.value, 
                                             att_es.value, 
                                             att_vals.value, 
                                             left=0, 
                                             right=0) << u.dimensionless_unscaled,
                     attenuation_type="Pixelated-Attenuator",
                     model=use_model,
                     )

# aluminized mylar attenuation
@u.quantity_input(mid_energies=u.keV)
def att_al_mylar(mid_energies, file=None):
    """Aluminized mylar transmittance interpolated to given energies.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the transmission is required. If 
        `numpy.nan<<astropy.units.keV` is passed then an entry for all 
        native file energies are returned. 
        Unit must be convertable to keV.

    file : `str` or `None`
        Gives the ability to provide custom files for the information. 
        Default: None

    Returns
    -------
    : `AttOutput`
        An object containing the energies for each transmission, the 
        transmissions, and more. See accessible information using 
        `.contents` on the output.
    """
    _f = os.path.join(ATT_PATH, "thin_mylar_p3_p5_theoretical_v1.csv") if file is None else file
    att = pandas.read_csv(_f)
    att_es, att_values = att["energy[keV]"] << u.keV, att["transmission"] << u.dimensionless_unscaled
    mid_energies = native_resolution(native_x=att_es, input_x=mid_energies)

    return AttOutput(filename=_f,
                     function_path=f"{sys._getframe().f_code.co_name}",
                     mid_energies=mid_energies,
                     transmissions=np.interp(mid_energies.value, 
                                             att_es.value, 
                                             att_values.value, 
                                             left=0, 
                                             right=1) << u.dimensionless_unscaled,
                     attenuation_type="Aluminized-Mylar",
                     model=True,
                     )

# pre-filter attenuation
@u.quantity_input(mid_energies=u.keV)
def _att_old_prefilter(mid_energies, position=None, file=None):
    """Pre-filter transmittance interpolated to the given energies.
    
    This function was used for simulations pre-launch.
    """
    if (position is None) or (position not in [0,1]):
        logging.warning(f"The {sys._getframe().f_code.co_name} `position` must be 0 or 1.")
    logging.warning(f"Caution: This might not be the function you are looking for ({sys._getframe().f_code.co_name}), please see `att_cmos_obfilter`.")
    _f = os.path.join(ATT_PATH, "CMOST_Prefilter_transmission.dat") if file is None else file
    att = scipy.io.readsav(_f)
    att_es, att_values = att["cmos_prefilter_transmission"]["energy_kev"][0] << u.keV, att["cmos_prefilter_transmission"][f"position{position}"][0] << u.dimensionless_unscaled

    mid_energies = native_resolution(native_x=att_es, input_x=mid_energies)

    return AttOutput(filename=_f,
                     function_path=f"{sys._getframe().f_code.co_name}",
                     mid_energies=mid_energies,
                     transmissions=np.interp(mid_energies.value, 
                                             att_es.value, 
                                             att_values.value, 
                                             left=0, 
                                             right=1) << u.dimensionless_unscaled,
                     attenuation_type=f"Old-Prelaunch-Prefiler{position}",
                     model=True,
                     )

@u.quantity_input(mid_energies=u.keV)
def att_sigmoid(mid_energies, l ,x0, k, b):
    """Sigmoid model for a general/fake attenuator.

    The functional form of the sigmoid is:

    .. math::
        (l / (1 + np.exp(-k*(mid_energies.value-x0))) + b)

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the transmission is required. 
        Unit must be convertable to keV.

    Returns
    -------
    : `AttOutput`
        An object containing the energies for each transmission, the 
        transmissions, and more. See accessible information using 
        `.contents` on the output.
    """

    return AttOutput(filename="No-File",
                     function_path=f"{sys._getframe().f_code.co_name}",
                     mid_energies=mid_energies,
                     transmissions=(l / (1 + np.exp(-k*(mid_energies.value-x0))) + b) << u.dimensionless_unscaled,
                     attenuation_type=f"Analytical-Sigmoid-Model",
                     model=True,
                     )

@u.quantity_input(mid_energies=u.keV)
def att_cmos_filter(mid_energies, telescope=None, file=None):
    """CMOS pre-filters for the SXR telescopes.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the transmission is required. If 
        `numpy.nan<<astropy.units.keV` is passed then an entry for all 
        native file energies are returned. 
        Unit must be convertable to keV.

    telescope : `int`
        The focal plane position of the desired attenuator. Must be in 
        the list [0, 1]. 
        Default: None

    file : `str` or `None`
        Gives the ability to provide custom files for the information. 
        Default: None

    Returns
    -------
    : `AttOutput`
        An object containing the energies for each transmission, the 
        transmissions, and more. See accessible information using 
        `.contents` on the output.
    """
    if (telescope is None) or (telescope not in [0,1]):
        logging.warning(f"The `telescope` input in {sys._getframe().f_code.co_name} must be 0 or 1.")
        return
    _f = os.path.join(ATT_PATH, f"foxsi4_telescope-{telescope}_BASIC_attenuation_filter_transmittance_v1.fits") if file is None else file
    with fits.open(_f) as hdul:
        es, t = hdul[2].data << u.keV, hdul[1].data << u.dimensionless_unscaled
    mid_energies = native_resolution(native_x=es, input_x=mid_energies)

    return AttOutput(filename=_f,
                     function_path=f"{sys._getframe().f_code.co_name}",
                     mid_energies=mid_energies,
                     transmissions=np.interp(mid_energies.value, 
                                             es.value, 
                                             t.value, 
                                             left=0, 
                                             right=1) << u.dimensionless_unscaled,
                     attenuation_type=f"CMOS-Prefilter{telescope}",
                     model=True,
                     )

@u.quantity_input(mid_energies=u.keV)
def att_cmos_obfilter(mid_energies, telescope=None, file=None):
    """CMOS OBF filters for the SXR telescopes.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the transmission is required. If 
        `numpy.nan<<astropy.units.keV` is passed then an entry for all 
        native file energies are returned. 
        Unit must be convertable to keV.

    telescope : `int`
        The focal plane position of the desired attenuator. Must be in 
        the list [0, 1]. 
        Default: None

    file : `str` or `None`
        Gives the ability to provide custom files for the information. 
        Default: None

    Returns
    -------
    : `AttOutput`
        An object containing the energies for each transmission, the 
        transmissions, and more. See accessible information using 
        `.contents` on the output.
    """
    if (telescope is None) or (telescope not in [0,1]):
        logging.warning(f"The `telescope` input in {sys._getframe().f_code.co_name} must be 0 or 1.")
        return
    _f = os.path.join(ATT_PATH, f"foxsi4_telescope-{telescope}_BASIC_optical_blocking_filter_transmittance_v1.fits") if file is None else file
    with fits.open(_f) as hdul:
        es, t = hdul[2].data << u.keV, hdul[1].data << u.dimensionless_unscaled
    mid_energies = native_resolution(native_x=es, input_x=mid_energies)

    return AttOutput(filename=_f,
                     function_path=f"{sys._getframe().f_code.co_name}",
                     mid_energies=mid_energies,
                     transmissions=np.interp(mid_energies.value, 
                                             es.value, 
                                             t.value, 
                                             left=0, 
                                             right=1) << u.dimensionless_unscaled,
                     attenuation_type=f"CMOS-OBF-filter{telescope}",
                     model=True,
                     )

@u.quantity_input(off_axis_angle=u.arcmin)
def att_cmos_collimator_ratio(off_axis_angle, telescope=None, file=None):
    """CMOS OBF filters for the SXR telescopes.

    Parameters
    ----------
    off_axis_angle : `astropy.units.quantity.Quantity`
        The off-axis angle of the source.
        Unit must be convertable to arc-minutes.
        Default: 0 arc-minutes (on axis)

    telescope : `int`
        The focal plane position of the desired attenuator. Must be in 
        the list [0, 1]. 
        Default: None

    file : `str` or `None`
        Gives the ability to provide custom files for the information. 
        Default: None

    Returns
    -------
    : `AttOutput`
        An object containing the energies for each transmission, the 
        transmissions, and more. See accessible information using 
        `.contents` on the output.
    """
    if (telescope is None) or (telescope not in [0,1]):
        logging.warning(f"The `telescope` input in {sys._getframe().f_code.co_name} must be 0 or 1.")
        return
    _f = os.path.join(ATT_PATH, f"foxsi4_telescope-{telescope}_BASIC_collimator_aperture_ratio_v1.fits") if file is None else file
    with fits.open(_f) as hdul:
        oa_angles, aperture_ratio = hdul[2].data << u.arcmin, hdul[1].data << u.dimensionless_unscaled
    off_axis_angle = native_resolution(native_x=oa_angles, input_x=off_axis_angle)

    return AttOutput(filename=_f,
                     function_path=f"{sys._getframe().f_code.co_name}",
                     off_axis_angle=off_axis_angle,
                     transmissions=np.interp(off_axis_angle.value, 
                                             oa_angles.value, 
                                             aperture_ratio.value, 
                                             left=0, 
                                             right=0) << u.dimensionless_unscaled,
                     attenuation_type=f"CMOS-Collimator-Ratio{telescope}",
                     model=True,
                     )

@u.quantity_input(mid_energies=u.keV, time=u.second)
def att_foxsi4_atmosphere(mid_energies, time_range=None, file=None):
    """ 
    Atmsopheric attenuation from and for FOXSI-4 flight data.

    energy = array containing energy in keV for energies 0.01 - 30 keV. Array has 506 elements
		 
    atmospheric_trans = array containing transmission for all energy values in energy array.
                        Transmission is calculated for 10284 times covering the FOXSI-4 flight. 
                        Array shape is: [10284,506] which corresponds to transmission for [time,energy]
                        
                        Launch time t = 0 corresponds to  index [0,*] 
                        Observation starts at t = 100s corresponds to index [2000,*]
                        Approximate middle of observation at t = 280s corresponds to index [5600,*]
                        End of observation at t = 461s corresponds to index [9200,*] 


    Units in the FITS header needs to change from keV->eV
    Need an array of times included
    -> 10,284 entries and t=0 is index `0` while t=100 is index `2000`
    -> final time is 100/2000 * 10284 = 514.2

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the transmission is required. If 
        `numpy.nan<<astropy.units.keV` is passed then an entry for all 
        native file energies are returned. 
        Unit must be convertable to keV.

    time_range : `astropy.units.quantity.Quantity` or `None`
        The time range the atmsopheric transmissions should be averaged
        over. If `None`, `numpy.nan<<astropy.units.second`, or
        `[numpy.nan, numpy.nan]<<astropy.units.second` then the full 
        time will be considered and the output will not be averaged but 
        a grid of the transmissions at all times and at any provided
        energies.
    
    file : `str` or `None`
        Path/name of a custom file wanting to be loaded in as the 
        atmospheric data file.

    Returns
    -------
    : `AttOutput`
        An object containing the energies for each transmission, the 
        transmissions, and more. See accessible information using 
        `.contents` on the output.
    """
    if (time_range is None) or np.all(np.isnan(time_range)):
        time_range = [np.nan, np.nan] << u.second
    
    if (len(time_range)!=2):
        warnings.warn(f"{sys._getframe().f_code.co_name} `time_range` (convertable to astropy.units.seconds) should be of length 2.")
        return

    _f = os.path.join(ATT_PATH, f"FOXSI4_atmospheric_transmission_v1.fits") if file is None else file
    with fits.open(_f) as hdul:
        native_times, native_energies, transmission = hdul[1].data["TIME"][0]<<u.second, (hdul[1].data["ENERGY"][0]<<u.eV)<<u.keV, hdul[1].data["ATMOSPHERIC_TRANS"][0]<<u.dimensionless_unscaled

        # assume some sort of uniform uniform binning
        en_res = np.mean(np.diff(native_energies))

    # if the time range is nothing them just want all the times, deal with energies separately
    if np.all(np.isnan(time_range)):
        if np.all(np.isnan(mid_energies)):
            # don't bother going further if we're just going to return the native data
            return AttOutput(filename=_f,
                             function_path=f"{sys._getframe().f_code.co_name}",
                             mid_energies=native_energies<<u.keV,
                             times=native_times,
                             transmissions=transmission,
                             attenuation_type="File-Atmospheric-Transmissions",
                             model=True,
                             )
        
        # the grid can be huge so let's help cut down on the interpolation amount
        cut_native_energies_inds = np.nonzero(((mid_energies[0]-en_res)<=native_energies) & (native_energies<=(mid_energies[-1]+en_res)))
        cut_native_energies = native_energies[cut_native_energies_inds]
        cut_transmission = transmission[cut_native_energies_inds]

        x, y = np.meshgrid(cut_native_energies, native_times)
        # PROPER INTERPOLATION: i = scipy.interpolate.LinearNDInterpolator(list(zip(x.flatten().value, y.flatten().value)), cut_transmission.T.flatten().value)
        # the grid is really fine so is it good enough to just use nearest neighbours?
        i = scipy.interpolate.NearestNDInterpolator(list(zip(x.flatten().value, y.flatten().value)), cut_transmission.T.flatten().value)

        mid_energies = native_resolution(native_x=native_energies, input_x=mid_energies)
        all_times = native_resolution(native_x=native_times, input_x=time_range)
        X, Y = np.meshgrid(mid_energies, all_times)

        return AttOutput(filename=_f,
                         function_path=f"{sys._getframe().f_code.co_name}",
                         mid_energies=mid_energies,
                         times=all_times,
                         transmissions=i(X, Y)<<u.dimensionless_unscaled,
                         attenuation_type="Energy-Interpolated-Atmospheric-Transmissions",
                         model=True,
                         )

    # this is a big array so let's slice before interpolating
    time_inds = np.nonzero((time_range[0]<=native_times) & (native_times<=time_range[1]))[0]

    mid_energies = native_resolution(native_x=native_energies, input_x=mid_energies)

    # # we'll interpolate so make sure to include a range one wider for the energy range
    # energy_inds = np.nonzero((mid_energies[0]<=native_energies) & (native_energies<=mid_energies[-1]))[0]
    # energy_inds = np.insert(energy_inds, 0, energy_inds[0]-1) if energy_inds[0]>0 else energy_inds
    # energy_inds = np.insert(energy_inds, 1, energy_inds[-1]+1) if energy_inds[-1]<(len(energy_inds)-1) else energy_inds

    times = native_times[time_inds]
    transmissions = transmission[:,time_inds]

    tave_transmissions = np.mean(transmissions, axis=1)

    return AttOutput(filename=_f,
                     function_path=f"{sys._getframe().f_code.co_name}",
                     mid_energies=mid_energies<<u.keV,
                     times=times,
                     transmissions=np.interp(mid_energies.value, 
                                             native_energies.value, 
                                             tave_transmissions.value, 
                                             left=0, 
                                             right=0) << u.dimensionless_unscaled,
                     attenuation_type="Time-Averaged-Atmospheric-Transmissions",
                     model=True,
                     )

def asset_att(save_asset=False):
    mid_energies = create_energy_midpoints()

    tb_col, obf0_col, obf1_col, cdte_fixed2_col, cdte_fixed4_col = plt.cm.viridis([0, 0.2, 0.4, 0.6, 0.8])
    pix_att_meas_col, pix_att_mod_col, al_mylar_mod_col, cmost0_col, cmost1_col = plt.cm.plasma([0, 0.2, 0.4, 0.6, 0.8])
    cmost2_col, cmost3_col = plt.cm.cividis([0.1, 0.9])

    # all attenuators
    plt.figure(figsize=(10,8))
    att_therm_bl = zeroes2nans(att_thermal_blanket(mid_energies).transmissions)
    plt.ylabel(f"Transmission [{att_therm_bl.unit:latex}]")
    plt.xlabel(f"Energy [{mid_energies.unit:latex}]")
    p1 = plt.plot(mid_energies, att_therm_bl, color=tb_col, ls="-", label="Thermal blanket")

    old_prefilter0 = zeroes2nans(_att_old_prefilter(mid_energies, position=0).transmissions)
    p2 = plt.plot(mid_energies, old_prefilter0, color=obf0_col, ls="--", label="Old pre-filter 0", lw=3)

    old_prefilter1 = zeroes2nans(_att_old_prefilter(mid_energies, position=1).transmissions)
    p3 = plt.plot(mid_energies, old_prefilter1, color=obf1_col, ls="-.", label="Old pre-filter 1", lw=3)

    cdte_fixed4 = zeroes2nans(att_uniform_al_cdte(mid_energies, position=4).transmissions)
    p4 = plt.plot(mid_energies, cdte_fixed4, color=cdte_fixed4_col, ls="-.", label="CdTe fixed p4")

    cdte_fixed2 = zeroes2nans(att_uniform_al_cdte(mid_energies, position=2).transmissions)
    p5 = plt.plot(mid_energies, cdte_fixed2, color=cdte_fixed2_col, ls="-.", label="CdTe fixed p2")

    pix_att_meas = zeroes2nans(att_pixelated(mid_energies, use_model=False).transmissions)
    p6 = plt.plot(mid_energies, pix_att_meas, color=pix_att_meas_col, ls="--", label="Pix. Att. Measured")

    pix_att_mod = zeroes2nans(att_pixelated(mid_energies, use_model=True).transmissions)
    p7 = plt.plot(mid_energies, pix_att_mod, color=pix_att_mod_col, ls="--", label="Pix. Att. Modelled")

    al_mylar_mod = zeroes2nans(att_al_mylar(mid_energies).transmissions)
    p8 = plt.plot(mid_energies, al_mylar_mod, color=al_mylar_mod_col, ls="-", label="Al-Mylar")

    cmos_t0 = att_cmos_filter(mid_energies, telescope=0).transmissions
    p9 = plt.plot(mid_energies, cmos_t0, color=cmost0_col, ls="-", label="CMOS0-filter", lw=2)

    cmos_t1 = att_cmos_filter(mid_energies, telescope=1).transmissions
    p10 = plt.plot(mid_energies, cmos_t1, color=cmost1_col, ls="-.", label="CMOS1-filter", lw=2)

    cmos_t2 = att_cmos_obfilter(mid_energies, telescope=0).transmissions
    p11 = plt.plot(mid_energies, cmos_t2, color=cmost2_col, ls="--", label="CMOS0-OBF", lw=1)

    cmos_t3 = att_cmos_obfilter(mid_energies, telescope=1).transmissions
    p12 = plt.plot(mid_energies, cmos_t3, color=cmost3_col, ls=":", label="CMOS1-OBF", lw=1)

    plt.ylim([0,1.05])
    plt.xlim([0.5, 30])
    plt.xscale("log")

    plt.title("Attenuators")
    
    plt.legend(handles=p1+p2+p3+p4+p5+p6+p7+p8+p9+p10+p11+p12)
    plt.tight_layout()
    if save_asset:
        pathlib.Path(ASSETS_PATH).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(ASSETS_PATH,"transmissions.png"), dpi=200, bbox_inches="tight")
    plt.show()

def asset_sigmoid(save_asset=False):
    mid_energies = create_energy_midpoints()

    plt.figure(figsize=(10,8))

    # any fake/functionaly model attenuators
    # sigmoid
    l ,x0, k, b = 1, 0, 1, 0
    example = att_sigmoid(mid_energies, l ,x0, k, b)
    p1 = plt.plot(mid_energies, example.transmissions, ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1.04, 0, 1, 0
    p2 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b).transmissions, ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1, 3, 1, 0
    p3 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b).transmissions, ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1, 3, 1, 0.04
    p4 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b).transmissions, ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1, 10, 0.5, 0
    p5 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b).transmissions, ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1, 10, 1, 0
    p6 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b).transmissions, ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1, 10, 2, 0
    p7 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b).transmissions, ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1, 25, 1, 0
    p8 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b).transmissions, ls="-", label=f"spectrometer-like:\nl:{l} ,x0:{x0}, k:{k}, b:{b}")

    plt.ylabel(f"Transmission [{example.transmissions.unit:latex}]")
    plt.xlabel(f"Energy [{mid_energies.unit:latex}]")
    plt.title("Fake Attenuator, Sigmoid$=l/(1+exp^{-k*(x-x0)})+b")
    plt.ylim([0,1.05])
    plt.xlim([0.5, 30])
    plt.xscale("log")

    plt.legend(handles=p1+p2+p3+p4+p5+p6+p7+p8)
    plt.tight_layout()
    if save_asset:
        pathlib.Path(ASSETS_PATH).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(ASSETS_PATH,"model-transmissions.png"), dpi=200, bbox_inches="tight")
    plt.show()

def asset_atm(save_asset=False):
    fig = plt.figure(figsize=(16,6))

    obs_start = 100
    obs_mid = 280
    obs_end = 461

    gs = gridspec.GridSpec(1, 3)

    gs_ax0 = fig.add_subplot(gs[0, 0])

    energy0, time0 = [1]<<u.keV, np.nan<<u.second
    atm0 = att_foxsi4_atmosphere(mid_energies=energy0, time_range=time0)
    p0 = gs_ax0.plot(atm0.times, atm0.transmissions, ls=":", label=f"energy:{energy0:latex}\ntime:{time0:latex}", lw=3)

    energy1, time1 = [1, 3, 5, 10, 15]<<u.keV, np.nan<<u.second
    atm1 = att_foxsi4_atmosphere(mid_energies=energy1, time_range=time1)
    p1 = []
    for i in range(len(energy1)):
        p1 += gs_ax0.plot(atm1.times, atm1.transmissions[:,i], ls="-", label=f"energy:{energy1[i]:latex}")

    gs_ax0.set_ylabel(f"Transmission [{atm0.transmissions.unit:latex}]")
    gs_ax0.set_xlabel(f"Time (Obs. start=100 s) [{atm0.times.unit:latex}]")
    gs_ax0.set_ylim([0,1.05])
    v0 = gs_ax0.axvline(obs_start, ls="-.", c="k", label="obs. start")
    v1 = gs_ax0.axvline(obs_mid, ls="-.", c="k", label="obs. middle")
    v2 = gs_ax0.axvline(obs_end, ls="-.", c="k", label="obs. end")
    gs_ax0.set_xlim([0, 600])
    gs_ax0.set_title("Sampled energy band transmission vs. time")
    plt.legend(handles=p0+p1+[v0,v1,v2])
    

    gs_ax1 = fig.add_subplot(gs[0, 1])

    energy2, time2 = np.nan<<u.keV, [obs_start, obs_end]<<u.second
    atm2 = att_foxsi4_atmosphere(mid_energies=energy2, time_range=time2)
    p2 = gs_ax1.plot(atm2.mid_energies, atm2.transmissions, ls="-", label=f"time range:{time2:latex}")

    energy3, time3 = np.nan<<u.keV, np.nan<<u.second
    atm3 = att_foxsi4_atmosphere(mid_energies=energy3, time_range=time3)

    # will come back here: st, mid, en = np.nonzero(t3==obs_start), np.nonzero(t3==obs_mid), np.nonzero(t3==obs_end)
    p3 = gs_ax1.plot(atm3.mid_energies, atm3.transmissions[:, 2000], ls="-", label=f"time:{atm3.times[2000]:latex}")
    p4 = gs_ax1.plot(atm3.mid_energies, atm3.transmissions[:, 5600], ls="-", label=f"time:{atm3.times[5600]:latex}")
    p5 = gs_ax1.plot(atm3.mid_energies, atm3.transmissions[:, 9200], ls="-", label=f"time:{atm3.times[9200]:latex}")

    gs_ax1.set_ylabel(f"Transmission [{atm3.transmissions.unit:latex}]")
    gs_ax1.set_xlabel(f"Energy [{atm3.mid_energies.unit:latex}]")
    gs_ax1.set_ylim([0,1.05])
    gs_ax1.set_xlim([0.01, 30])
    gs_ax1.set_xscale("log")
    gs_ax1.set_title("Time averaged and time sampled transmission vs. energy")
    plt.legend(handles=p2+p3+p4+p5)

    
    gs_ax2 = fig.add_subplot(gs[0, 2])

    energy4, time4 = [0.01, 0.02, 0.05, 0.1, 0.3, 0.5, 1, 3, 5, 10, 15, 30]<<u.keV, [obs_start, obs_end]<<u.second
    atm4 = att_foxsi4_atmosphere(mid_energies=energy4, time_range=time4)
    colour4 = "blue"
    p6 = gs_ax2.plot(atm4.mid_energies, atm4.transmissions, label=f"time range:{atm4.times[0]:.2f}$-${atm4.times[-1]:.2f}\nrandom-ish energy sampling", marker="x", ms=4, c=colour4)

    energy5, time5 = np.arange(3,30.1, 0.1)<<u.keV, [obs_start, obs_end]<<u.second
    atm5 = att_foxsi4_atmosphere(mid_energies=energy5, time_range=time5)
    colour5 = "orange"
    gs_ax2.plot(atm5.mid_energies, atm5.transmissions, label=f"time range:{atm5.times[0]:.2f}$-${atm5.times[-1]:.2f}\nCdTe range+response resolution", marker="x", ms=2, c=colour5)
    # inset Axes for the CdTe plot
    x1, x2, y1, y2 = 2.5, 30, 0.95, 1.04  # subregion of the original image
    axins = gs_ax2.inset_axes([0.4, 0.35, 0.5, 0.4],
                              xlim=(x1, x2), 
                              ylim=(y1, y2)) #, xticklabels=[], yticklabels=[])
    axins.plot(atm4.mid_energies, atm4.transmissions, label=f"time range:{atm4.times[0]:.2f}$-${atm4.times[-1]:.2f}\nrandom-ish energy sampling", marker="x", ms=6, c=colour4)
    p7 = axins.plot(atm5.mid_energies, atm5.transmissions, label=f"time range:{atm5.times[0]:.2f}$-${atm5.times[-1]:.2f}\nCdTe range+response resolution", marker="x", ms=4, c=colour5)
    axins.set_xscale("log")
    _rectangle, _connectors = gs_ax2.indicate_inset_zoom(axins, edgecolor="black")
    # edit the connecting lines so they make sense
    _connectors[0].__dict__["_visible"] = False 
    _connectors[1].__dict__["_visible"] = True

    gs_ax2.set_ylabel(f"Transmission [{atm3.transmissions.unit:latex}]")
    gs_ax2.set_xlabel(f"Energy [{atm3.mid_energies.unit:latex}]")
    gs_ax2.set_ylim([0,1.05])
    gs_ax2.set_xlim([0.01, 30])
    gs_ax2.set_xscale("log")
    gs_ax2.set_title("Time averaged transmission vs. sampled energy")
    plt.legend(handles=p6+p7)

    plt.suptitle("FOXSI-4 Flight Atmospheric Transmission")

    plt.tight_layout()
    if save_asset:
        pathlib.Path(ASSETS_PATH).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(ASSETS_PATH,"atmospheric-transmissions.png"), dpi=200, bbox_inches="tight")
    plt.show()

if __name__=="__main__":
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    from phot_spec import create_energy_midpoints, zeroes2nans

    SAVE_ASSETS = False
    
    asset_att(save_asset=SAVE_ASSETS)
    
    ## other
    # collimator (so far, only have value for on-axis)
    print(att_cmos_collimator_ratio(0<<u.arcsec, file=None, telescope=0).transmissions)
    print(att_cmos_collimator_ratio(0<<u.arcsec, file=None, telescope=1).transmissions)

    asset_sigmoid(save_asset=SAVE_ASSETS)

    asset_atm(save_asset=SAVE_ASSETS)