[![Build Status](https://travis-ci.org/edoddridge/aronnax.svg?branch=master)](https://travis-ci.org/edoddridge/aronnax)
[![codecov](https://codecov.io/gh/edoddridge/aronnax/branch/master/graph/badge.svg)](https://codecov.io/gh/edoddridge/aronnax)

# Aronnax

An idealised isopycnal ocean circulation model that can either be run
as a reduced gravity model with n + 1/2 layers, or with n layers and
variable bathymetry.

Aronnax is
- [Easy to install](https://edoddridge.github.io/aronnax/installation.html)
  on a laptop or a compute node, including without
  administrative privileges.
- Easy to configure.  All parameters, including grid size, are
  specified at runtime in a simple configuration file.
- [Easy to use](https://edoddridge.github.io/aronnax/examples.html).
  Aronnax can be controlled programmatically as a Python library.
- Easy to learn and understand, with extensive [online
  documentation](https://edoddridge.github.io/aronnax/), including a
  complete description of [the
  physics](https://edoddridge.github.io/aronnax/about_aronnax.html#the-physics)
  and [the
  numerics](https://edoddridge.github.io/aronnax/about_aronnax.html#discretisation).
- [Verified](https://edoddridge.github.io/aronnax/verification.html).
  Aronnax successfully [reproduces published results](https://edoddridge.github.io/aronnax/examples.html#reproducing-published-results) from
  idealised models appearing in the literature.
- [Fast](https://edoddridge.github.io/aronnax/benchmarks.html).  The
  main integration loop is a multi-core Fortran program, wrapped in
  Python for convenient use.


# Get Involved

- TODO Contact email, and/or list?
- Please report any bugs you come across in the [Github issue
  tracker](https://github.com/edoddridge/aronnax/issues)

- We are happy to receive pull requests for new features or bug fixes;
  check out the [issues](https://github.com/edoddridge/aronnax/issues) for
  stuff that we know needs doing, and [HACKING.md](HACKING.md) for a
  developer's intro to the repository.
