"""
Top level of the `response-tools` package.

Namespace
---------

The base `response_tools` namespace includes:

`~response_tools.contextResponseInfo`
    The information stored in a YAML file that includes information from
    the flight.

`~response_tools.responseFilePath`
    The response data file location.

`~response_tools.__version__`
    The current version of the code as stated in the setup script.

Examples
--------
# importing the module is as easy as:

>>> import response_tools

# then accessing, e.g., the context information for the flight/flare

>>> print(response_tools.contextResponseInfo)

# that can be accessed like a native Python dictionary

>>> print(response_tools.contextResponseInfo["..."])
"""

import logging
import os
import pathlib
import traceback

from .version import __version__
from response_tools.io.load_yaml import load_response_context

# for global context info
contextResponseInfo = load_response_context()
responseFilePath = os.path.join(pathlib.Path(__file__).parent, "response-information")

try:
    import response_tools.io.fetch_response_data as fetch
    _missing_files = fetch.foxsi4_list_missing_response_info()
    if _missing_files!=({},{}):
        logging.warning("On `response_tools` package import, it is noticed response files are missing from:")
        logging.warning(f"{responseFilePath}")
        logging.warning("")
        logging.warning("A user can check which files are missing with:")
        logging.warning(">>> import response_tools.io.fetch_response_data as fetch")
        logging.warning(">>> missing_files = fetch.foxsi4_list_missing_response_info()")
        logging.warning("")
        logging.warning("If this is unexpected, consider downloading the files using:")
        logging.warning(">>> fetch.foxsi4_download_required(verbose=True)")
        logging.warning("An `overwrite_all` input exists which may be useful.")
        logging.warning("")
        logging.warning("Consider referrring to the online documentation for more information:")
        logging.warning("[URL] https://foxsi.github.io/response-tools/general_instructions.html#getting-the-response-files")
        logging.warning("[URL] https://foxsi.github.io/response-tools/response_tools.io.html")
except Exception as e:
    logging.warning("An error occurred when checking the downloaded files in `response_tools`.")
    logging.warning("Please raise this issue with the developers and code maintainers.")
    logging.error(traceback.format_exc())