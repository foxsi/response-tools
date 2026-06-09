Response-tools Code |:fox:|
===========================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   code_tips
   modules

The ``response-tools`` Github repository developed for the FOXSI-4 sounding rocket mission can be found `here <https://github.com/foxsi/response-tools>`__. This page contains the automated documentation for the ``response-tools`` Python package.

The code is written in Python and is relatively bare-bones. There are two things that have
been made use of that the user might want to know:

1. Values and functions in the code have been made to be *unit aware* where possible.

  * When it comes to response elements, the biggest annoyance is units and keeping track of them. The code makes use of `Astropy Units <https://docs.astropy.org/en/stable/units/index.html>`__ to help the user track what they're working with and to avoid making mistakes.

2. Functions return custom data-class objects, not just tuples of values or arrays.

  * To find out what fields are stored in the data-class, all you have to do is either print the returned ``object``, inspect ``object.contents``, or run the method ``object.print_contents``. (Note for IDL users: Using these objects is similar to using an IDL structure.)
  * The data-class object the functions returned can be accessed by either indexing with the field name à la ``[“field_name”]`` or doing ``.field_name`` on the returned object.

Remember, with any function you can always run ``help(function_name)`` and this should let you inspect the documentation written for that function and should explain what the function is, how to use it, and what it returns.

Thank you for considering to use the codebase. If you enjoy (or hate) using the code please consider helping the project via `Pull Requests <https://github.com/foxsi/response-tools/pulls>`__ and `Issues <https://github.com/foxsi/response-tools/issues>`__.

API level design
----------------

The Python code is designed to have three API levels:

.. raw:: html

    <style> .colourbold {color:#e16b27;font-weight:bold;} </style>

.. role:: colourbold

.. raw:: html

    <style> .coloursmall {color:#e16b27;font-size:12px;;} </style>

.. role:: coloursmall

* :colourbold:`Level 3` :coloursmall:`(recommended use)`: Full telescope loaders for the FOXSI(-4) instrument. These are designed to return the ancillary response function (ARF) and redistribution matrix function (RMF) composed of all the relevant telescope components.

  * These can be found in the ``responses`` module.
  * E.g., the function ``foxsi4_telescope2_arf`` will return the ARF data for FOXSI-4 telescope 2.

* :colourbold:`Level 2` :coloursmall:`(recommended use)`: Loader functions that are named after their position in the FOXSI(-4) payload. All of these functions start with ``foxsi4_position#`` where ``#`` refers to the telescope position to which the response product belongs.

  * These can be found in the ``telescope_parts`` module.
  * E.g., the function ``foxsi4_position2_optics`` will return the optics information relating to position 2 using the predetermined and appropriate function from the ``effective_area`` module.

* :colourbold:`Level 1`: Loader functions that have as little as possible description to its place in the FOXSI(-4) instrument, relying on its own description.

  * These can be found in modules like ``attenuation``, ``detector_response``, ``effective_area``, and ``quantum_efficiency``.

Even lower level handling
~~~~~~~~~~~~~~~~~~~~~~~~~

A user can decide in which way they would like to interact with the response products. A potential :colourbold:`Level 0` would be the user interacting with the files themselves directly. Depending on how the package is installed the files may be stored in different locations on your machine.

To find where the files are stored in the package, and indeed your local machine, you can use the global package variable, ``responseFilePath``:

.. code-block:: python
    
    import response_tools
    print(response_tools.responseFilePath)

The functions in the package use this path to automatically find the correct files.