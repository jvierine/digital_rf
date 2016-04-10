# digital_rf

> apt-get install python-pkgconfig libhdf5-dev

On raspbian, the hdf5 library is in a weird place:

> export CFLAGS="-I/usr/include/hdf5/serial"
> sh autogen.sh
> ./configure --prefix=/usr

> sudo python setup.py install 
