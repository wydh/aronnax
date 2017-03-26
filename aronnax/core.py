"""!
The main file with the class definitions

Core
==============

This file contains all of the classes for the module.
"""

from contextlib import contextmanager
import os.path as p

import numpy as np
from scipy.io import FortranFile

class Grid(object):
    """!Make a grid object containing all of the axes."""

    def __init__(self,nx,ny,dx,dy,x0=0,y0=0):
        """!Instantiate a grid object for Aronnax."""

        # axes for vorticity points
        self.xp1 = np.linspace(x0,nx*dx+x0,nx+1)
        self.yp1 = np.linspace(y0,ny*dy+y0,ny+1)

        # Axes for tracer points.
        self.x = (self.xp1[1:] + self.xp1[:-1])/2.
        self.y = (self.yp1[1:] + self.yp1[:-1])/2.

        # Size
        self.nx = nx
        self.ny = ny

@contextmanager
def fortran_file(*args, **kwargs):
    f = FortranFile(*args, **kwargs)
    try:
        yield f
    finally:
        f.close()

def interpret_raw_file(name, nx, ny, layers):
    """Read an output file dumped by the Aronnax core.

    Each such file contains one array, whose size depends on what,
    exactly, is in it, and on the resolution of the simulation.
    Hence, the parameters nx, ny, and layers, as well as the file
    naming convetion, suffice to interpret the content (assuming it
    was generated on the same system)."""
    # Note: This depends on inspection of the output writing code in
    # the Aronnax core, to align array sizes and dimensions.  In
    # particular, Fortran arrays are indexed in decreasing order of
    # rate of change as one traverses the elements sequentially,
    # whereas Python (and all other programming languages I am aware
    # of) indexes in increasing order.
    file_part = p.basename(name)
    dx = 0; dy = 0; layered = True
    if file_part.startswith("snap.h"):
        pass
    if file_part.startswith("snap.u"):
        dx = 1
    if file_part.startswith("snap.v"):
        dy = 1
    if file_part.startswith("snap.eta"):
        layered = False
    if file_part.startswith("wind_x"):
        dx = 1
        layered = False
    if file_part.startswith("wind_y"):
        dy = 1
        layered = False
    if file_part.startswith("av.h"):
        pass
    if file_part.startswith("av.u"):
        dx = 1
    if file_part.startswith("av.v"):
        dy = 1
    if file_part.startswith("av.eta"):
        layered = False
    with fortran_file(name, 'r') as f:
        if layered:
            return f.read_reals(dtype=np.float64) \
                    .reshape(layers, ny+dy, nx+dx).transpose()
        else:
            return f.read_reals(dtype=np.float64) \
                    .reshape(ny+dy, nx+dx).transpose()

### General input construction helpers

def write_initial_heights(grid, h_funcs):
    X,Y = np.meshgrid(grid.x, grid.y)
    initH = np.ones((len(h_funcs), grid.ny, grid.nx))
    for i, f in enumerate(h_funcs):
        if isinstance(f, (int, long, float)):
            initH[i,:,:] = f
        else:
            initH[i,:,:] = f(X, Y)
    with fortran_file('initH.bin', 'w') as f:
        f.write_record(initH.astype(np.float64))

def write_wind_x(grid, func):
    X,Y = np.meshgrid(grid.xp1, grid.y)
    if isinstance(func, (int, long, float)):
        wind_x = np.ones(grid.ny, grid.nx+1) * func
    else:
        wind_x = func(X, Y)
    with fortran_file('wind_x.bin', 'w') as f:
        f.write_record(wind_x.astype(np.float64))

def write_wind_y(grid, func):
    X,Y = np.meshgrid(grid.y, grid.xp1)
    if isinstance(func, (int, long, float)):
        wind_y = np.ones(grid.ny+1, grid.nx) * func
    else:
        wind_y = func(X, Y)
    with fortran_file('wind_y.bin', 'w') as f:
        f.write_record(wind_y.astype(np.float64))

### Specific construction helpers

def write_f_plane(nx, ny, coeff):
    """Write files defining an f-plane approximation to the Coriolis force."""
    with fortran_file('fu.bin', 'w') as f:
        f.write_record(np.ones((nx+1, ny), dtype=np.float64) * coeff)
    with fortran_file('fv.bin', 'w') as f:
        f.write_record(np.ones((nx, ny+1), dtype=np.float64) * coeff)

def write_beta_plane(grid, f0, beta):
    """Write files defining a beta-plane approximation to the Coriolis force."""
    with fortran_file('fu.bin', 'w') as f:
        _, Y = np.meshgrid(grid.xp1, grid.y)
        fu = f0 + Y*beta
        f.write_record(fu.astype(np.float64))
    with fortran_file('fv.bin', 'w') as f:
        _, Y = np.meshgrid(grid.x, grid.yp1)
        fv = f0 + Y*beta
        f.write_record(fv.astype(np.float64))

def write_rectangular_pool(nx, ny):
    """Write the wet mask file for a maximal rectangular pool."""
    with fortran_file('wetmask.bin', 'w') as f:
        wetmask = np.ones((nx, ny), dtype=np.float64)
        wetmask[ 0, :] = 0
        wetmask[-1, :] = 0
        wetmask[ :, 0] = 0
        wetmask[ :,-1] = 0
        f.write_record(wetmask)