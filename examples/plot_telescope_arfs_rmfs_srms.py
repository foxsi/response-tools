"""
Telescope ARFs, RMFs, and SRMs
==============================

Throughout the `modules in the codebase <https://foxsi.github.io/response-tools/modules.html>`__ 
there are a variety of functions with names starting wtih ``asset``. 
These functions were created to mainly test the functions being written
but they might be useful to see and compare a lot of the response 
elements.

One such example is an ``asset`` function that generates a plot showing 
all of FOXSI-4's telescope ARFs, RMFs, and SRMs in one plot.
"""

import response_tools.responses as responses

# %%
# Some caveats come with these asset functions as many choices that the
# user can make are obviously chosen then hidden in the function but it
# might still be useful to see an idea of what these elements look like:

responses.asset_response_chain_plot()

# %%
# **Note** these functions are not usually names the best since they 
# were originally for testing purposes and so the names might change. 
# Please utilize the `auto-generated code documentation <https://foxsi.github.io/response-tools/modules.html>`__
# to keep up-to-date.
#
# All figures produced using all of the ``asset`` functions can be found
# in the codebase. The ``assets`` folder is on the same directory level 
# as the ``response-information`` folder that can be found using the 
# Python package global variable: ``response_tools.responseFilePath`` 
# (more on the ``responseFilePath`` global variable 
# `here <https://foxsi.github.io/response-tools/general_instructions.html#python-interface-to-pull-data>`__).