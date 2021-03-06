"""!
The main file with the class definitions

Core
==============

This file contains all of the classes for the module.
"""

from contextlib import contextmanager
import os.path as p
import re

import numpy as np
from scipy.io import FortranFile

class Grid(object):
    """Make a grid object containing all of the axes.

        :param int nx: Number of grid points in the x direction
        :param int ny: Number of grid points in the y direction
        :param int layers: Number of active layers
        :param float dx: Grid size in x direction in metres
        :param float dy: Grid size in y direction in metres
        :param float x0: x value at lower left corner of domain
        :param float y0: y value at lower left corner of domain


        The initialisation call returns an object containing each of the input parameters as well as the following arrays:

        - x: x locations of the tracer points
        - y: y locations of the tracer points
        - xp1: x locations of the u velocity points and vorticity points
        - yp1: y locations of the v velocity points and vorticity points
        """

    def __init__(self,nx,ny,layers,dx,dy,x0=0,y0=0):
        """Instantiate a grid object for Aronnax."""

        # axes for vorticity points
        self.xp1 = np.linspace(x0,nx*dx+x0,nx+1)
        self.yp1 = np.linspace(y0,ny*dy+y0,ny+1)

        # Axes for tracer points.
        self.x = (self.xp1[1:] + self.xp1[:-1])/2.
        self.y = (self.yp1[1:] + self.yp1[:-1])/2.

        # Size
        self.nx = nx
        self.ny = ny
        self.layers = layers

        # Grid spacing
        self.dx = dx
        self.dy = dy

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
    dx = 0; dy = 0;
    if file_part.startswith("snap.BP"):
        pass
    if file_part.startswith("snap.eta"):
        layers = 1
    if file_part.startswith("snap.eta_new"):
        layers = 1
    if file_part.startswith("snap.eta_star"):
        layers = 1
    if file_part.startswith("snap.h"):
        pass
    if file_part.startswith("snap.u"):
        dx = 1
    if file_part.startswith("snap.ub"):
        dx = 1
        layers = 1
    if file_part.startswith("snap.v"):
        dy = 1
    if file_part.startswith("snap.vb"):
        dy = 1
        layers = 1
    if file_part.startswith("snap.zeta"):
        dx = 1 
        dy = 1   
    if file_part.startswith("wind_x"):
        dx = 1
        layers = 1
    if file_part.startswith("wind_y"):
        dy = 1
        layers = 1
    if file_part.startswith("av.h"):
        pass
    if file_part.startswith("av.u"):
        dx = 1
    if file_part.startswith("av.v"):
        dy = 1
    if file_part.startswith("av.eta"):
        layers = 1
    if file_part.startswith("debug.dhdt"):
        pass
    if file_part.startswith("debug.dudt"):
        dx = 1
    if file_part.startswith("debug.dvdt"):
        dy = 1
    with fortran_file(name, 'r') as f:
        return f.read_reals(dtype=np.float64) \
                    .reshape(layers, ny+dy, nx+dx).transpose()


### General input construction helpers

def tracer_point_variable(grid, field_layers, *funcs):
    """Input generator for a variable at the tracer location of the grid. If passed a function, then that function can depend only on `X` and `Y`."""
    X,Y = np.meshgrid(grid.x, grid.y)
    T_variable = np.ones((field_layers, grid.ny, grid.nx))

    assert field_layers == len(funcs)

    for i, f in enumerate(funcs):
        if isinstance(f, (int, long, float)):
            T_variable[i,:,:] = f
        else:
            T_variable[i,:,:] = f(X, Y)
    return T_variable

def u_point_variable(grid, field_layers, *funcs):
    """Input generator for a variable at the u location of the grid. If passed a function, then that function can depend only on `X` and `Y`."""
    X,Y = np.meshgrid(grid.xp1, grid.y)
    u_variable = np.ones((field_layers, grid.ny, grid.nx+1))

    assert field_layers == len(funcs)

    for i, f in enumerate(funcs):
        if isinstance(f, (int, long, float)):
            u_variable[i,:,:] = f
        else:
            u_variable[i,:,:] = f(X, Y)
    return u_variable

def v_point_variable(grid, field_layers, *funcs):
    """Input generator for a variable at the v location of the grid. If passed a function, then that function can depend only on `X` and `Y`."""
    X,Y = np.meshgrid(grid.x, grid.yp1)
    v_variable = np.ones((field_layers, grid.ny+1, grid.nx))

    assert field_layers == len(funcs)

    for i, f in enumerate(funcs):
        if isinstance(f, (int, long, float)):
            v_variable[i,:,:] = f
        else:
            v_variable[i,:,:] = f(X, Y)
    return v_variable

def time_series_variable(nTimeSteps, dt, func):
    '''Input generator for a time series variable. If passed a function, then that function can depend on the number of timesteps, `nTimeSteps`, and the timestep, `dt`.'''

    ts_variable = np.zeros((nTimeSteps))

    # number of elements in `func` list should always be one
    assert len(func) == 1

    for i, f in enumerate(func):
        if isinstance(f, (int, long, float)):
            ts_variable[:] = np.ones(nTimeSteps) * f
        else:
            ts_variable[:] = f(nTimeSteps, dt)
    return ts_variable

### Specific construction helpers

def f_plane_f_u(grid, field_layers, coeff):
    """Define an f-plane approximation to the Coriolis force (u location)."""
    assert field_layers == 1
    return np.ones((grid.nx+1, grid.ny), dtype=np.float64) * coeff

def f_plane_f_v(grid, field_layers, coeff):
    """Define an f-plane approximation to the Coriolis force (v location)."""
    assert field_layers == 1
    return np.ones((grid.nx, grid.ny+1), dtype=np.float64) * coeff

def beta_plane_f_u(grid, field_layers, f0, beta):
    """Define a beta-plane approximation to the Coriolis force (u location)."""
    assert field_layers == 1
    _, Y = np.meshgrid(grid.xp1, grid.y)
    fu = f0 + Y*beta
    return fu

def beta_plane_f_v(grid, field_layers, f0, beta):
    """Define a beta-plane approximation to the Coriolis force (v location)."""
    assert field_layers == 1
    _, Y = np.meshgrid(grid.x, grid.yp1)
    fv = f0 + Y*beta
    return fv

def rectangular_pool(grid, field_layers):
    """The wet mask file for a maximal rectangular pool."""
    assert field_layers == 1
    nx = grid.nx; ny = grid.ny
    wetmask = np.ones((nx, ny), dtype=np.float64)
    wetmask[ 0, :] = 0
    wetmask[-1, :] = 0
    wetmask[ :, 0] = 0
    wetmask[ :,-1] = 0
    return wetmask

specifier_rx = re.compile(r':(.*):(.*)')

ok_generators = {
    'tracer_point_variable': tracer_point_variable,
    'u_point_variable': u_point_variable,
    'v_point_variable': v_point_variable,
    'time_series_variable': time_series_variable,
    'beta_plane_f_u': beta_plane_f_u,
    'beta_plane_f_v': beta_plane_f_v,
    'f_plane_f_u': f_plane_f_u,
    'f_plane_f_v': f_plane_f_v,
    'rectangular_pool': rectangular_pool,

}

def interpret_data_specifier(string):
    m = re.match(specifier_rx, string)
    if m:
        name = m.group(1)
        arg_str = m.group(2)
        if len(arg_str) > 0:
            args = [float(a) for a in arg_str.split(',')]
        else:
            args = []
        return (ok_generators[name], args)
    else:
        return None

def interpret_requested_data(requested_data, shape, config):
    """Interpret a flexible input data specification.

    The requested_data can be one of

    - TODO A string giving the path to a NetCDF file, whose content
      will be interpolated to match the desired grid specification;

    - A string giving the path to a raw Fortran array file, whose
      content will be used as-is;

    - TODO A numpy array in memory, whose content will be used as-is,
      or TODO interpolated; or

    - A string specifying auto-generation of the required data, in this format:
      :<generator_func_name>:arg1,arg2,...argn

    - Python objects specifying auto-generation of the required data.
      In this case, `interpret_requested_data` will construct the
      appropriate `Grid` instance and pass it, together with the
      `requested_data`, to an appropriate meta-generator for the array
      shape of the needful datum (determined by the `shape` argument).
      The exact API varies with the meta-generator, but they typically
      interpret numbers as that constant and functions as an analytic
      definition of the field, which is evaluated on appropriate numpy
      arrays to produce the needed numerical values.
    """
    grid = Grid(config.getint("grid", "nx"), config.getint("grid", "ny"),
                config.getint("grid", "layers"),
                config.getfloat("grid", "dx"), config.getfloat("grid", "dy"))
    field_layers = find_field_layers(shape, grid)

    if isinstance(requested_data, basestring):
        candidate = interpret_data_specifier(requested_data)
        if candidate is not None:
            (func, args) = candidate
            return func(grid, field_layers, *args)
        else:
            # Assume Fortran file name
            with fortran_file(requested_data, 'r') as f:
                return f.read_reals(dtype=np.float64)
    else:
        if shape == "2dT" or shape == "3dT":
            return tracer_point_variable(grid, field_layers, *requested_data)
        if shape == "2dU" or shape == "3dU":
            return u_point_variable(grid, field_layers, *requested_data)
        if shape == "2dV" or shape == "3dV":
            return v_point_variable(grid, field_layers, *requested_data)
        if shape == "time":
            nTimeSteps = config.getint("numerics", "nTimeSteps")
            dt = config.getfloat("numerics", "dt")
            return time_series_variable(nTimeSteps, dt, requested_data)
        else:
            raise Exception("TODO implement custom generation for other input shapes")

def find_field_layers(shape, grid):
    """Given a particular field shape, return how many layers it should have."""

    if shape == "2dT":
        return 1
    if shape == "3dT":
        return grid.layers
    if shape == "2dU":
        return 1
    if shape == "3dU":
        return grid.layers
    if shape == "2dV":
        return 1
    if shape == "3dV":
        return grid.layers
