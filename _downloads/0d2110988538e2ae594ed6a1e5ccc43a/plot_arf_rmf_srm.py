"""
Generating and plotting ARFs, RMFs, and SRMs
============================================

Script showing a quick example how to plot the Ancillary Response 
Function (ARF), Redistribution Matrix Function (RMF), and the Spectral 
Response Matrix (SRM) of a FOXSI-4 telescope.

The chosen telescope is Telescope 2 with photon path:

* Thermal blanket -> Marshall 10-shell X-7 -> Al (0.015") -> CdTe4
"""

import astropy.units as u
from matplotlib.colors import LogNorm
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np

import response_tools.responses as responses

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
#   * A detector region.
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
# * **A detector region** (for CdTe, input: ``region`` xor ``pitch``):
#
#   * For CdTe Redistribution Matrix Function (RMF) code.
#
#     * Of course, this should be consistent with the off axis angle being used.
#
#   * Use either, not both, inputs:
#
#     * An integer for ``region`` input in [0,1,2].
#     * Astropy.units unit convertable to micrometers for ``pitch`` input in [60 um,80 um,100 um].
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
#   * Input should come from the RMF.
#
#     * The RMF defines the energy resolution/sampling of the detector.


# %%
# Generating response products
# ----------------------------
#
# Let's define some of these parameters as an example. Our user will 
# assume the source our user is interested in is on-axis: 
# 
# * at 0 arc-minutes, region-0, a pitch of 60 um.

# set up the ARF with the RMF information then make the SRM
user_off_axis_angle = 0 << u.arcmin
user_region = 0 # equivalent to defining ``user_pitch=60<<u.um``

# %%
# Generating the RMF
# ~~~~~~~~~~~~~~~~~~
#
# As stated for previously, the energy array choice should come from the 
# RMF information. Let's get The RMF product first:

# if pitch is defined instead, pass as ``responses.foxsi4_telescope2_rmf(pitch=user_pitch)``
pos_rmf = responses.foxsi4_telescope2_rmf(region=user_region) 

# %%
# Our user can use the RMF field ``input_energy_edges`` (synonymous with 
# the incoming photon energies to the detector) to get the energies at 
# which they want to sample the ARF product. Our user will grab the 
# mid-points of the incoming photon bins to be sensible:

rmf_mid_energies = (pos_rmf.input_energy_edges[:-1]+pos_rmf.input_energy_edges[1:])/2

# %%
# Generating the ARF
# ~~~~~~~~~~~~~~~~~~
#
# Now our user can easily generate the ARF information for their 
# telescope:

pos_arf = responses.foxsi4_telescope2_arf(mid_energies=rmf_mid_energies, 
                                          off_axis_angle=user_off_axis_angle)

# %%
# Generating the SRM
# ~~~~~~~~~~~~~~~~~~
#
# The user can then combine the ARF and RMF into one product describing 
# the whole telescope. 
#
# Of course, the user can do this step manually; however, the codebase 
# provides a functions to make sure sensible things are happening:

pos_srm = responses.foxsi4_telescope_spectral_response(pos_arf, pos_rmf)

# %%
# The ``response_tools.responses.foxsi4_telescope_spectral_response`` 
# function will check:
# 
# * The ARF and RMF objects share the same telescope information via their ``telescope`` field.
#
#   * If they do not match, the function will work but a warning is produced informing the user.
#
# * The ARF ``mid_energies`` field matches the RMF ``input_energy_edges`` field's mid-points.
#
#   * If the do not match, the function will raise a ``ValueError``.

# %%
# Plotting response products
# --------------------------
#
# Likely, a user will be happy just getting the ARF, RMF, and SRM and 
# will be on their way to do science (e.g., spectral fitting) with the 
# product.
#
# However, a user might want to actually inspect what they have before 
# running off. Even if they are not so familiar with and ARF and RMF, 
# they still might be able to pick up on something that is not quite 
# what they expect it to be. At the very least a user might want to ask very 
# sensible questions about what they are working with as these products 
# will heavily influence any spectral fitting results.
#
# Plotting code always turns into a mess but at least the functions in 
# the codebase do not make it any more difficult than it usually is in 
# other code (perhaps easier since we can make use of the output units
# when creating our plot labels).

fig = plt.figure(figsize=(18, 5))
gs = gridspec.GridSpec(1, 3)

# the ARF result (1D) and general plotting code
gs_ax0 = fig.add_subplot(gs[0, 0])
gs_ax0.plot(pos_arf.mid_energies, pos_arf.response)
gs_ax0.set_xlabel(f"Photon Energy [{pos_arf.mid_energies.unit:latex}]")
gs_ax0.set_ylabel(f"Response [{pos_arf.response.unit:latex}]")
gs_ax0.set_title(f"{pos_arf.response_type}:: {pos_arf.telescope}")

# the RMF result (2D) and general plotting code
gs_ax1 = fig.add_subplot(gs[0, 1])
r = gs_ax1.imshow(pos_rmf.response.value, 
                origin="lower", 
                norm=LogNorm(vmin=0.001), 
                extent=[np.min(pos_rmf.output_energy_edges.value), 
                        np.max(pos_rmf.output_energy_edges.value), 
                        np.min(pos_rmf.input_energy_edges.value), 
                        np.max(pos_rmf.input_energy_edges.value)]
                )
cbar = plt.colorbar(r)
cbar.ax.set_ylabel(f"Response [{pos_rmf.response.unit:latex}]")
gs_ax1.set_xlabel(f"Count Energy [{pos_rmf.output_energy_edges.unit:latex}]")
gs_ax1.set_ylabel(f"Photon Energy [{pos_rmf.input_energy_edges.unit:latex}]")
gs_ax1.set_title(f"{pos_rmf.response_type}:: {pos_rmf.telescope}")

# the SRM result (2D) and general plotting code
gs_ax2 = fig.add_subplot(gs[0, 2])
r = gs_ax2.imshow(pos_srm.response.value, 
                origin="lower", 
                norm=LogNorm(vmin=0.001), 
                extent=[np.min(pos_srm.output_energy_edges.value), 
                        np.max(pos_srm.output_energy_edges.value), 
                        np.min(pos_srm.input_energy_edges.value), 
                        np.max(pos_srm.input_energy_edges.value)]
                )
cbar = plt.colorbar(r)
cbar.ax.set_ylabel(f"Response [{pos_srm.response.unit:latex}]")
gs_ax2.set_xlabel(f"Count Energy [{pos_srm.output_energy_edges.unit:latex}]")
gs_ax2.set_ylabel(f"Photon Energy [{pos_srm.input_energy_edges.unit:latex}]")
gs_ax2.set_title(f"{pos_srm.response_type}:: {pos_srm.telescope}")

plt.tight_layout()
plt.show()

# %%
# We can see how the ARF (left panel) and RMF (middle panel) are 
# combined where the photon energy rows of the RMF array are multiplied 
# by the ARF array producing the SRM (right panel).