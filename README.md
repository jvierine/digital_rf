# digital_rf



On raspbian, the hdf5 library is in a weird place:
> export CFLAGS="-I/usr/include/hdf5/serial"
> sh autogen.sh
> ./configure --prefix=/usr
> sudo python setup.py install build_ext -n -I/usr/include/hdf5/serial
