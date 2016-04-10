#!python

"""digital_archive.py is a drive script to archive all the needed raw data fro ion line processing

$Id: digital_archive.py 1029 2016-03-21 20:01:18Z brideout $
"""
# standard python imports
import os, os.path, sys
import datetime
import argparse

# Millstone imports
import digital_rf_archive
import digital_metadata_archive


# rf data to archive
rf_dict = {'/data0/ringbuffer': ('zenith-l', 'misa-l', 'tx-h')}
metadata_dict = {'/data0/results': ('id_metadata', 'antenna_control_metadata', 'powermeter', 'plasma_line_metadata')}


### main begins here ###
if __name__ == '__main__':

    # command line interface
    parser = argparse.ArgumentParser(description='digital_archive.py is a tool for archiving all ion line raw data.')
    parser.add_argument('--startDT', metavar='start datetime string', 
                        help='Start UT datetime for archiving in format YYYY-MM-DDTHH:MM:SS', required=True)
    parser.add_argument('--endDT', metavar='end datetime string', 
                        help='End UT datetime for archiving in format YYYY-MM-DDTHH:MM:SS', required=True)
    parser.add_argument('--dest', metavar='Full path to archive destination', 
                        help='Full path to destination directory. Will create digital_metadata top level directory if needed.  May be local, or remote in scp form (user@host:)', 
                        required=True)
    parser.add_argument('--gzip', metavar='GZIP compression 1-9.', 
                        help='Level of GZIP compression 1-9.  Default=1. 0 for no compression', 
                        required=False, type=int, default=1)
    args = parser.parse_args()
    
    
    # create datetimes
    try:
        startDT = datetime.datetime.strptime(args.startDT, '%Y-%m-%dT%H:%M:%S')
    except:
        print('startDT <%s> not in expected YYYY-MM-DDTHH:MM:SS format' % (args.startDT))
        sys.exit(-1)
    try:
        endDT = datetime.datetime.strptime(args.endDT, '%Y-%m-%dT%H:%M:%S')
    except:
        print('endDT <%s> not in expected YYYY-MM-DDTHH:MM:SS format' % (args.endDT))
        sys.exit(-1)
        
    for key in rf_dict.keys():
        print('doing archive of digital rf channels: %s' % (str(rf_dict[key])))
        digital_rf_archive.archive(startDT, endDT, key, args.dest, channels=rf_dict[key], verbose=True,
                                   gzip=args.gzip)
        
    for key in metadata_dict.keys():
        for meta_dir in metadata_dict[key]:
            print('working on metadata: %s' % (meta_dir))
            digital_metadata_archive.archive(startDT, endDT, os.path.join(key, meta_dir), args.dest, verbose=True)
            
            
            
    