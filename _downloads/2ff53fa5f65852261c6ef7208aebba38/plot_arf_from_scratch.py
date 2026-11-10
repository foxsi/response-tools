"""
Create an ARF from scratch
==========================

Script showing a quick example how to create an Ancillary Response 
Function (ARF) from scratch from a FOXSI-4 telescope.

Check out the `What is a Response <https://foxsi.github.io/response-tools/response_guide.html>`__ 
section in the online documentation for more details on an ARF's 
purpose.

The chosen telescope is Telescope 2 with photon path:

* Thermal blanket -> Marshall 10-shell X-7 -> Al (0.015") -> CdTe4
"""

import astropy.units as u
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np

import response_tools.telescope_parts as tp

# %%
# A note on usage and user options
# --------------------------------
#
# One great thing about the unit-awareness of the inputs/outputs is that 
# you can pass any reasonable input units and they'll be converted for 
# you so you don't need to worry about conversion factors throughout 
# your code to use the functions.
#
# As other examples will likely go into more detail than here, to 
# generate a telescope response you only need to make a few core 
# decisions related to the **FOXSI-4 observation** and the data in which 
# the user is interested.
#
# .. raw:: html
# 
#     <style> .colour {color:#e16b27;font-style:italic;} </style>
# 
# .. role:: colour
#
# :colour:`Please look over the FOXSI-4 observation resources to add` 
# :colour:`more context as to how a user might decide on their choice` 
# :colour:`of the following parameters. Additionally, look over the` 
# :colour:`FOXSI-4 instrumentation resources when deciding which`
# :colour:`functions to use.`
#
# These crucial choices will be:
#
# * **A source location** to obtain:
#
#   * An off axis angle.
#
# * **A time range during the flight**.
# * **An energy array** *(sometimes)*.
#
# For more detail on choices:
# 
# * **An off axis angle** (input: ``off_axis_angle``):
#
#   * For Ancillary Response Function (ARF) code.
#   * Astropy.units unit convertable to arc-minutes.
# 
# * **A time range during the flight** (input: ``time_range``):
#
#   * For Ancillary Response Function (ARF) code.
#   * *Input ``time_range`` will change to something more readable after some time calibration:*
#
#     * E.g., converted to use UTC time strings.
#
#   * Inputs in functions that reference the flight: 
#
#     * E.g., in ``response_tools.responses.foxsi4_telescope2_flight_arf``.
#
#   * Astropy.units unit convertable to seconds:
#
#     * Launch: 0 s.
#     * Observation start: 100 s.
#     * Observation end: 461 s.
# 
# * **An energy array** (input: ``mid_energies``):
#
#   * For Ancillary Response Function (ARF) code.
#   * Astropy.units unit convertable to keV.
#   * Input should come from the redistribution matrix function (RMF).
#
#     * The RMF defines the energy resolution/sampling of the detector.


# %%
# Identify the telescope components
# ---------------------------------
#
# First, a user has to be aware of the telescope components in which 
# they are interested. The example we will look at is telescope 2. 
# 
# From the photon path described above, the user can see telescope 2 has 
# three 1D components to be involved in its ARF
#
# * Thermal blanket  
# * Marshall 10-shell X-7  
# * Al (0.015")
#
# (For telescope components, see the 
# `FOXSI-4 Instrumentation <https://foxsi.github.io/response-tools/instrument.html>`__ 
# documentation)
# 
# The thermal blanket and the Al attenuator trnsmissions are monolithic 
# so the only *real* choice needed here is to pick an off-axis angle for 
# the optic. Let's go for a simple value of 0 arc-minutes.
#
# Additionally, since we're only looking at the ARF components, we can 
# take the liberty of making up our own energies at which to evaluate 
# all of these components.
#
# (For observational choices, see the 
# `FOXSI-4 Observation <https://foxsi.github.io/response-tools/observation.html>`__ 
# documentation)

# set up the ARF with the RMF information then make the SRM
user_off_axis_angle = 0 << u.arcmin
user_energies = np.linspace(4, 20, 50) << u.keV # 50 energies between 4-20 keV 

# %%
# Evaluating the telescope components
# -----------------------------------
#
# Now a user can get the response elements they want evaluated at the 
# parameters they've chosen:

pos2_tb = tp.foxsi4_position2_thermal_blanket(user_energies)
pos2_op = tp.foxsi4_position2_optics(user_energies, 
                                     off_axis_angle=user_off_axis_angle)
pos2_at = tp.foxsi4_position2_uniform_al(user_energies)

# %%
# A user can quickly plot these individual telescope response components
# to see if they make sense and what is expected:

fig = plt.figure(figsize=(18, 5))
gs = gridspec.GridSpec(1, 3)

# the thermal blanket result 
gs_ax0 = fig.add_subplot(gs[0, 0])
gs_ax0.plot(pos2_tb.mid_energies, pos2_tb.transmissions)
gs_ax0.set_xlabel(f"Photon Energy [{pos2_tb.mid_energies.unit:latex}]")
gs_ax0.set_ylabel(f"Transmission [{pos2_tb.transmissions.unit:latex}]")
gs_ax0.set_title(f"Telecope 2: {pos2_tb.attenuation_type}")
gs_ax0.set_xlim([np.min(user_energies).value, np.max(user_energies).value])

# the optics effective areas result
gs_ax1 = fig.add_subplot(gs[0, 1])
gs_ax1.plot(pos2_op.mid_energies, pos2_op.effective_areas)
gs_ax1.set_xlabel(f"Photon Energy [{pos2_op.mid_energies.unit:latex}]")
gs_ax1.set_ylabel(f"Effective Area [{pos2_op.effective_areas.unit:latex}]")
gs_ax1.set_title(f"Telecope 2: {pos2_op.optic_id}")
gs_ax1.set_xlim([np.min(user_energies).value, np.max(user_energies).value])

# the fixed attenuator result
gs_ax2 = fig.add_subplot(gs[0, 2])
gs_ax2.plot(pos2_at.mid_energies, pos2_at.transmissions)
gs_ax2.set_xlabel(f"Photon Energy [{pos2_at.mid_energies.unit:latex}]")
gs_ax2.set_ylabel(f"Transmission [{pos2_at.transmissions.unit:latex}]")
gs_ax2.set_title(f"Telecope 2: {pos2_at.attenuation_type}")
gs_ax2.set_xlim([np.min(user_energies).value, np.max(user_energies).value])

plt.tight_layout()
plt.show()

# %%
# A user can see the three components together and investigate the 
# individual features in each response element. 
# 
# This might be useful if the user wanted to investigate any features at
# certain energies where a response element might have a unique 
# behaviour compared to other elements.

# %%
# Creating the telescope ARF
# --------------------------
#
# Now the user has the individual components, they might want to combine 
# them to make an ARF.
#
# A user can easily do this to get the ARF 1D array:

# 1D ARF from components
arf_array = pos2_tb.transmissions * pos2_op.effective_areas * pos2_at.transmissions

# %%
# This will produce a valid ARF; however, notice that all the useful 
# data-class fucntionality is now gone. Unit-awareness will be 
# preserved.
#
# A user can see what their ARF looks like by plotting the array as 
# normal:

fig = plt.figure(figsize=(6, 5))
gs = gridspec.GridSpec(1, 1)

# the manually made ARF array result 
gs_ax0 = fig.add_subplot(gs[0, 0])
gs_ax0.plot(user_energies, arf_array)
gs_ax0.set_xlabel(f"Photon Energy [{user_energies.unit:latex}]")
gs_ax0.set_ylabel(f"ARF [{arf_array.unit:latex}]")
gs_ax0.set_title(f"Telecope 2: Manually Made ARF")
gs_ax0.set_xlim([np.min(user_energies).value, np.max(user_energies).value])

plt.tight_layout()
plt.show()

# A user can then see different features in the ARF and might be able to 
# attribute those features to the individual components (e.g., the 
# thermal blanket, the Marshall 10-shell X-7 optics, and/or the Al 
# attenuator). A user can then visually see what photons of different 
# enegies experience travelling through the telescope on their way to 
# the detector.
# 
# **A user can take advantage of pre-prepared functions that create the 
# total ARF for each telescope** while maintaining the data-class 
# structure:

import response_tools.responses as responses
pos2_arf = responses.foxsi4_telescope2_arf(mid_energies=user_energies, 
                                          off_axis_angle=user_off_axis_angle)

# %%
# Now, `pos2_arf` will contain fields and track items for the user.
#
# A user can plot both ARFs (`arf_array` and the one from `pos2_arf`) to
# validate they are the same result:

fig = plt.figure(figsize=(12, 5))
gs = gridspec.GridSpec(1, 2)

# the manually made ARF array result 
gs_ax0 = fig.add_subplot(gs[0, 0])
gs_ax0.plot(user_energies, arf_array)
gs_ax0.set_xlabel(f"Photon Energy [{user_energies.unit:latex}]")
gs_ax0.set_ylabel(f"ARF [{arf_array.unit:latex}]")
gs_ax0.set_title(f"Telecope 2: Manually Made ARF")
gs_ax0.set_xlim([np.min(user_energies).value, np.max(user_energies).value])

# the pre-prepared ARF result
gs_ax1 = fig.add_subplot(gs[0, 1])
gs_ax1.plot(pos2_arf.mid_energies, pos2_arf.response)
gs_ax1.set_xlabel(f"Photon Energy [{pos2_arf.mid_energies.unit:latex}]")
gs_ax1.set_ylabel(f"Effective Area [{pos2_arf.response.unit:latex}]")
gs_ax1.set_title(f"{pos2_arf.response_type}:: {pos2_arf.telescope}")
gs_ax1.set_xlim([np.min(user_energies).value, np.max(user_energies).value])

plt.tight_layout()
plt.show()

# %%
# Creating the telescope ARF **(Advanced)**
# -----------------------------------------
#
# If a user wishes to manually create their own data-class result, this 
# is also possible.
#
# First, the correct data-class should be identified. The user here is 
# looking at an data-class similar to thos in 
# `response_tools.responses`; therefore, looking at the 
# `online documentation for this <https://foxsi.github.io/response-tools/response_tools.html#module-response_tools.responses>`__
# the user can see the `Response1DOutput` data-class object so let's use
# that:

custom_arf_dataclass = responses.Response1DOutput(filename="No-File",
                                                  function_path="No-Function",
                                                  mid_energies=user_energies,
                                                  response=arf_array,
                                                  response_type="ARF",
                                                  telescope="custom-foxsi4-telescope2",
                                                  elements=(pos2_tb, 
                                                            pos2_op, 
                                                            pos2_at,
                                                            ),
                                                  )

# %%
# The user can plot this with the previous examples to check the output:

fig = plt.figure(figsize=(18, 5))
gs = gridspec.GridSpec(1, 3)

# the manually made ARF array result 
gs_ax0 = fig.add_subplot(gs[0, 0])
gs_ax0.plot(user_energies, arf_array)
gs_ax0.set_xlabel(f"Photon Energy [{user_energies.unit:latex}]")
gs_ax0.set_ylabel(f"ARF [{arf_array.unit:latex}]")
gs_ax0.set_title(f"Telecope 2: Manually Made ARF")
gs_ax0.set_xlim([np.min(user_energies).value, np.max(user_energies).value])

# the pre-prepared ARF result
gs_ax1 = fig.add_subplot(gs[0, 1])
gs_ax1.plot(pos2_arf.mid_energies, pos2_arf.response)
gs_ax1.set_xlabel(f"Photon Energy [{pos2_arf.mid_energies.unit:latex}]")
gs_ax1.set_ylabel(f"Effective Area [{pos2_arf.response.unit:latex}]")
gs_ax1.set_title(f"{pos2_arf.response_type}:: {pos2_arf.telescope}")
gs_ax1.set_xlim([np.min(user_energies).value, np.max(user_energies).value])

# the pre-prepared ARF result
gs_ax2 = fig.add_subplot(gs[0, 2])
gs_ax2.plot(custom_arf_dataclass.mid_energies, custom_arf_dataclass.response)
gs_ax2.set_xlabel(f"Photon Energy [{custom_arf_dataclass.mid_energies.unit:latex}]")
gs_ax2.set_ylabel(f"Effective Area [{custom_arf_dataclass.response.unit:latex}]")
gs_ax2.set_title(f"Custom:: {custom_arf_dataclass.response_type}:: {custom_arf_dataclass.telescope}")
gs_ax2.set_xlim([np.min(user_energies).value, np.max(user_energies).value])

plt.tight_layout()
plt.show()

# %%
# If the user is wrapping this in a function then it might be a good 
# idea to use the `update_function_path` method on the response 
# components before passing them as elements to the class. E.g., 

import sys

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def custom_telescope_arf(mid_energies, off_axis_angle):
    """Manual Telescope ARF. """
    tb = tp.foxsi4_position2_thermal_blanket(mid_energies) 
    opt = tp.foxsi4_position2_optics(mid_energies, 
                                     off_axis_angle=off_axis_angle) 
    uni_al = tp.foxsi4_position2_uniform_al(mid_energies)

    arf = tb.transmissions * opt.effective_areas * uni_al.transmissions

    # get the function name automatically _or_ manually type the function name
    func_name = sys._getframe().f_code.co_name 
    # update the elements to show they've passed through this function
    tb.update_function_path(func_name)
    opt.update_function_path(func_name)
    uni_al.update_function_path(func_name)

    return responses.Response1DOutput(filename="No-File",
                                      function_path=func_name,
                                      mid_energies=mid_energies,
                                      response=arf,
                                      response_type="ARF",
                                      telescope="custom-telescope2",
                                      elements=(tb, 
                                                opt, 
                                                uni_al,
                                                ),
                                      )