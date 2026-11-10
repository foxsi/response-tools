"""
Functions & Outputs
===================

Script showing a quick example on how to use the functions.

The chosen telescope for the example is Telescope 2 with photon path:

- Thermal blanket -> Marshall 10-shell X-7 -> Al (0.015") -> CdTe4

Mainly a quick example on unit aware objects and how to access the 
returned data-class objects.

This example shows the use of nice high level functions that are tied to
FOXSI-4 telescopes. 

* The ``responses`` module.
* The ``telescope_parts`` module

This means we will eventually be dealing with high-level telescope 
response products such as the Ancillary Response Function (ARF) and the 
Redistribution Matrix Function (RMF).

If you're looking for access to response data of the 
individual components with more freedom then you'll likely be interested 
in the longer named moduels in the package like:

* The ``attenuation`` module.
* The ``detector_response`` module.
* The ``effective_area`` module.
* The ``quantum_efficiency`` module.
"""

# %%
#
# .. raw:: html
# 
#     <style> .colour {color:#e16b27;font-style:italic;} </style>
# 
# .. role:: colour
#
# :colour:`Please look over the FOXSI-4 observation resources to add` 
# :colour:`more context as to how a user might decide on their choice` 
# :colour:`of the function parameters. Additionally, look over the` 
# :colour:`FOXSI-4 instrumentation resources when deciding which`
# :colour:`functions to use.`
#
# Let's start with importing trusty Numpy as I'm sure we'll need it.


import numpy as np

# %%
# For high-level user engagement, the following two modules are the 
# ones likely to use. The `telescope_parts` are well-named functions 
# tied to FOXSI positions: E.g., `foxsi4_position2_optics` will return 
# FOXSI-4's optical information for Position/Telescope 2.
# 
# The `responses` module will contains functions that combine the 
# relevant `telescope_parts` functions into one to return higher level 
# products such as the telescope's Ancillary Response Function (ARF), 
# Redistribution Matrix Function (RMF), and/or Spectral Response Matrix 
# (SRM).

import response_tools.responses as responses
import response_tools.telescope_parts as telescope_parts

# %%
# Let's look at the `foxsi4_position2_optics` function since we 
# mentioned it earlier. To see the documentation for this, and any 
# function, we can always run:

help(telescope_parts.foxsi4_position2_optics)

# %%
# We see that the help function tells us about the function, how to use 
# it, and what it returns *(for those that are familiar with Python, 
# ``help`` will display the docstring the queried Python object)*.
# 
# The above function is looking for some energies and an off-axis angle.
# 
# The ``help`` function also shows the function is making use of unit 
# aware inputs to functions (believe me, when it comes to response 
# units, this will save time). 
# 
# So let's import Astropy's unit module.

import astropy.units as u

# %%
# Let's choose a sensible energy array and off-axis angle (remembering 
# to add the units to the array/value):

mid_energies = np.arange(4,20,0.5) << u.keV 
off_axis_angle = 0 << u.arcmin
pos2_optics = telescope_parts.foxsi4_position2_optics(mid_energies, 
                                                      off_axis_angle)

# %%
# One great thing about the unit-awareness of the inputs/outputs is that 
# you can pass any reasonable input units and they'll be converted for 
# you so you don't need to worry about conversion factors throughout 
# your code to use the functions.
# 
# E.g., the following will result in the same function output

mid_energies_eV = np.arange(4_000,20_000,500) << u.eV 
off_axis_angle_arcsec = 0 << u.arcsec
_pos2_ = telescope_parts.foxsi4_position2_optics(mid_energies_eV, 
                                                 off_axis_angle_arcsec)

# %%
# I.e., `pos2_optics` and `_pos2_` are identical.
# 
# You can also access just the value or just the unit from a unit-aware 
# object with `.value` or `.unit` as well. This can useful for axis 
# labels when necessary.
# 
# The output of `pos2_optics` (an `pos2_optics_new`) isn't just an array 
# now, it's a data-class. The data-class contains the effective areas of 
# the optics but also the energy, file, off-axis angle information used 
# to produce it. This is crucial to track when there are a lot of files 
# flying around.
# 
# As suggested in the "Output" section of the helpful documentation 
# earlier, we can see the contents of the data-class and how to access 
# the information within it:

# %%
# Print
print(pos2_optics.contents)

# %%
# The above might be a bit cumbersome and you may only wish to look at 
# the data fields contained in the output. For this we can simply run:

print(pos2_optics.fields)

# %%
# which might be a bit easier to read.
# 
# Note: there is a method called `print_contents()` you can use on the 
# function output that might format the contents a little nicer than the
# above you may wish to use.
# 
# Each field can be accessed with the displayed name. For example, to 
# get the effective areas of the optics, simply:

print(pos2_optics.effective_areas)

# %%
# Notice that these are also unit-aware, help you see at a glance you're 
# working with a product that you might expect.
# 
# The `telescope_parts.foxsi4_position2_optics` function is helpful but 
# an even higher level exists that will allow a user to specify a 
# FOXSI-4 telescope to obtain the Ancillary Response Function (ARF), 
# Redistribution Matrix Function (RMF), and/or Spectral Response Matrix 
# (SRM).
# 
# First, we can get the RMF for a telescope, say, Telescope 2 to be 
# consistent with using position 2's components previously. 

tel2_rmf = responses.foxsi4_telescope2_rmf(region=0)

# %%
# We need to pass the detector region we are interested in for the 
# correct response to be returned for the CdTe detectors. A user can 
# define the detector area of interest another way using the strip pitch 
# values for the CdTe detector. Feel free to make use of the ``help`` 
# function to see how else the following function can be used.
# 
# The RMF defined the input and output energy axes for the detector so 
# we might as well access the RMF input energies for those energies we 
# want the ARF values for:

mid_energies = (tel2_rmf.input_energy_edges[:-1]\
                +tel2_rmf.input_energy_edges[1:])/2
tel2_arf = responses.foxsi4_telescope2_arf(mid_energies=mid_energies, 
                                           off_axis_angle=0<<u.arcmin)

# %%
# Once we have the RMF and ARF for a given instrument, you might want to 
# just see what the total SRM is. This can be done by passing the ARF 
# and RMF to the general `responses.foxsi4_telescope_spectral_response` 
# function:

tel2_srm = responses.foxsi4_telescope_spectral_response(tel2_arf, tel2_rmf)

# %%
# Note that with the FOXSI-4 Telescope fucntions (`foxsi4_telescope*`), 
# there exists a field in the class called `elements`. This field 
# contains all the data-classes used to produce the objects `response` 
# field.
# 
# Checking the `elements` field for, say, the ARF object:

print(tel2_arf.elements)

# %%
# We find that the `elements` field contains all the data-classes that 
# produced the Telescope 2 ARF such as the thermal blanket transmission 
# (dimensionless), the Marshall 10-shell X-7 optics effective areas 
# (cm^2), and the Al (0.015") attenuator transmissions (dimensionless).