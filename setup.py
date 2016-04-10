"""setup file for the digital_rf_hdf5 python module
$Id: setup.py 1023 2016-03-15 18:14:07Z rvolz $
"""

from distutils.core import setup, Extension
import warnings

pkg_dict = dict(
    libraries=['hdf5'],
    library_dirs=[],
    include_dirs=[],
)
try:
    import pkgconfig
except ImportError:
    warnings.warn('python-pkgconfig not installed, using default search path to find HDF5')
else:
    if pkgconfig.exists('hdf5'):
        pkg_dict = pkgconfig.parse('hdf5')
    else:
        warnings.warn('pkgconfig cannot find HDF5, using default path')

setup(name="digital_rf_hdf5",
        version="1.1.3",
        description="Python tools to read and write digital rf data in Hdf5 format",
        author="Bill Rideout",
        author_email="brideout@haystack.mit.edu",
        url="http://www.haystack.mit.edu/~brideout/",
        package_dir = {'': 'source'},
        py_modules=['digital_rf_hdf5', 'digital_metadata'],
        ext_modules=[Extension("_py_rf_write_hdf5",
                              ["source/_py_rf_write_hdf5.c", "source/rf_write_hdf5.c"],
                              libraries=list(pkg_dict['libraries']),
                              library_dirs=list(pkg_dict['library_dirs']),
                              include_dirs=list(pkg_dict['include_dirs']),
                              )
                    ])
