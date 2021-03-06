from setuptools import setup

setup(name='aronnax',
      version='0.1',
      description='An idealized isopycnal model with n layers and variable bathymetry.',
      url='http://github.com/edoddridge/aronnax',
      author='Ed Doddridge',
      author_email='blank',
      license='MIT licence',
      packages=['aronnax'],
      scripts = ['aronnax/aronnax'],
      install_requires=[
          'numpy',
          'scipy',],
      zip_safe=False)
