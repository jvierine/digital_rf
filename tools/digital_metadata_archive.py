#!python

"""digital_metadata_archive.py is a tool for archiving Digital Metadata data.

$Id: digital_metadata_archive.py 1016 2016-02-29 13:53:26Z brideout $
"""
# standard python imports
import datetime, time
import calendar
import glob
import argparse
import os, os.path, sys
import subprocess
import shutil

# third party imports
import numpy

# Millstone imports
import digital_metadata




class archive:
    """archive is a class to archive a digital rf data set
    """
    def __init__(self, startDT, endDT, source, dest, verbose=False):
        """
        __init__ will create a Digital RF archive
        
        Inputs:
            startDT - start datetime for the data archive
            endDT end datetime for the data archive
            source - string defining data source. Either a path, or a url.
            dest - where archive is to be created.  May be a path, or a scp
                type path (user@host:/path) If scp-type, keypair must allow
                scp without passwords
            verbose - if True, print one line for each subdirectory.  If False (the default),
                no output except for errors.
                
        Attributes:
            self._source_type - local if local input data, remote if remote
        """
        
        # verify arguments
        if endDT <= startDT:
            print('endDT <%s> must be after startDT <%s>' % (str(endDT), str(startDT)))
            sys.exit(-1)
            
        # save args
        self.startDT = startDT
        self.endDT = endDT
        self.source = source
        self.dm_basename = os.path.basename(source) # name of digital metadata directory
        self.dest = dest
        self.verbose = bool(verbose)
            
        self._source_type = 'local'
        if len(self.source) > 5:
            if self.source[0:5] == 'http:':
                self._source_type = 'remote'
                
        if self._source_type == 'local':
            # make sure source is full path
            if self.source[0] != '/':
                self.source = os.path.join(os.getcwd(), self.source)
                
        dmd = digital_metadata.read_digital_metadata(self.source)
        self._samples_per_second = long(dmd.get_samples_per_second())
        self._subdirectory_cadence_seconds = long(dmd.get_subdirectory_cadence_seconds())
        self._file_cadence_seconds = long(dmd.get_file_cadence_seconds())
        self._file_name = dmd.get_file_name_prefix()
        
                
        self.metadata_dir = os.path.basename(self.source)
        if len(self.metadata_dir) == 0:
            raise ValueError, 'No metadata dir found in %s' % (self.source)
                
        self._dest_type = 'local'
        hyphen = self.dest.find(':')
        slash = self.dest.find('/')
        if hyphen != -1:
            if slash == -1:
                self._dest_type = 'remote'
            elif hyphen < slash:
                self._dest_type = 'remote'
                
        if self.verbose:
            # set up a timer
            t = time.time()
                
            
        # get start and end sample 
        sample0 = calendar.timegm(self.startDT.timetuple()) * self._samples_per_second
        sample1 = calendar.timegm(self.endDT.timetuple()) * self._samples_per_second
        file_list = self._get_file_list(sample0, sample1)
        
        if self._source_type == 'local' and self._dest_type == 'local':
            self._archive_local_local(file_list)
        elif self._source_type == 'local' and self._dest_type == 'remote':
            self._archive_local_remote(file_list)
            
        if self.verbose:
            print('digital_rf_archive took %f seconds' % (time.time() - t))
            
            
        
    def _get_file_list(self, sample0, sample1):
        """_get_file_list returns an ordered list of full file names of metadata files that contain metadata.
        """
        start_ts = long(sample0/self._samples_per_second)
        end_ts = long(sample1/self._samples_per_second)
        
        # convert ts to be divisible by self._file_cadence_seconds
        start_ts = (start_ts // self._file_cadence_seconds) * self._file_cadence_seconds
        end_ts = (end_ts // self._file_cadence_seconds) * self._file_cadence_seconds
        
        # get subdirectory start and end ts
        start_sub_ts = (start_ts // self._subdirectory_cadence_seconds) * self._subdirectory_cadence_seconds
        end_sub_ts = (end_ts // self._subdirectory_cadence_seconds) * self._subdirectory_cadence_seconds
        
        ret_list = ['metadata.h5'] # ordered list of full file paths to return, always include metadata.h5
        
        for sub_ts in range(start_sub_ts, end_sub_ts + self._subdirectory_cadence_seconds, self._subdirectory_cadence_seconds):
            sub_datetime = datetime.datetime.utcfromtimestamp(sub_ts)
            subdir = sub_datetime.strftime('%Y-%m-%dT%H-%M-%S')
            # create numpy array of all file TS in subdir
            file_ts_in_subdir = numpy.arange(sub_ts, sub_ts + self._subdirectory_cadence_seconds, self._file_cadence_seconds)
            valid_file_ts_list = numpy.compress(numpy.logical_and(file_ts_in_subdir >= start_ts, file_ts_in_subdir <= end_ts),
                                                file_ts_in_subdir)
            for valid_file_ts in valid_file_ts_list:
                file_basename = '%s@%i.h5' % (self._file_name, valid_file_ts)
                full_file = os.path.join(subdir, file_basename)
                ret_list.append(full_file)
                
        return(ret_list)

            
        
                
    def _archive_local_local(self, file_list):
        """_archive_local_local archives local digital metadata to a local destination
        """
        last_dir = None
        dest_archive = os.path.join(self.dest, self.dm_basename)
        if not os.access(dest_archive, os.W_OK):
            os.makedirs(dest_archive)
        for this_file in file_list:
            src = os.path.join(self.source, this_file)
            if not os.access(src, os.R_OK):
                continue
            this_dir = os.path.dirname(this_file)
            if this_dir != last_dir:
                dest_dir = os.path.join(dest_archive, this_dir)
                try:
                    os.makedirs(dest_dir)
                except:
                    pass
                last_dir = this_dir
                if self.verbose:
                    print('Working on directory %s' % (this_dir))
            shutil.copyfile(src, os.path.join(dest_dir, os.path.basename(src)))
            
            
    def _archive_local_remote(self, file_list):
        """_archive_local_remote archives local digital metadata to a remote destination
        
        Takes the approach of archiving to local tmp dir, then scp the whole thing
        """
        last_dir = None
        dest_archive = os.path.join('/tmp', 'tmp_archive_%i' % (os.getpid()), self.dm_basename)
        os.makedirs(dest_archive)
        try:
            for this_file in file_list:
                src = os.path.join(self.source, this_file)
                if not os.access(src, os.R_OK):
                    continue
                this_dir = os.path.dirname(this_file)
                if this_dir != last_dir:
                    dest_dir = os.path.join(dest_archive, this_dir)
                    try:
                        os.makedirs(dest_dir)
                    except:
                        pass
                    last_dir = this_dir
                    if self.verbose:
                        print('Working on directory %s' % (this_dir))
                shutil.copyfile(src, os.path.join(dest_dir, os.path.basename(src)))
                
            cmd = 'scp -r %s %s' % (dest_archive, self.dest)
            os.system(cmd)
        except:
            traceback.print_exc()
        finally:
            print('about to call rmtree for %s' % (os.path.dirname(dest_archive)))
            shutil.rmtree(os.path.dirname(dest_archive), True)
        


### main begins here ###
if __name__ == '__main__':

    # command line interface
    parser = argparse.ArgumentParser(description='digital_metadata_archive.py is a tool for archiving Digital Metadata..')
    parser.add_argument('--startDT', metavar='start datetime string', 
                        help='Start UT datetime for archiving in format YYYYMMDDTHHMMSS', required=True)
    parser.add_argument('--endDT', metavar='end datetime string', 
                        help='End UT datetime for archiving in format YYYYMMDDTHHMMSS', required=True)
    parser.add_argument('--source', metavar='Metadata dir', 
                        help='Metadata directory or url containing the Digital Metadata to archive', 
                        required=True)
    parser.add_argument('--dest', metavar='Full path to archive destination', 
                        help='Full path to destination directory. Will create digital_metadata top level directory if needed.  May be local, or remote in scp form (user@host:)', 
                        required=True)
    parser.add_argument('-v',  '--verbose', action='store_true', default=False,
                        help='Get one line of output for each subdirectory archived.')
    args = parser.parse_args()
    
    
    # create datetimes
    try:
        startDT = datetime.datetime.strptime(args.startDT, '%Y%m%dT%H%M%S')
    except:
        print('startDT <%s> not in expected YYYYMMDDTHHMMSS format' % (args.startDT))
        sys.exit(-1)
    try:
        endDT = datetime.datetime.strptime(args.endDT, '%Y%m%dT%H%M%S')
    except:
        print('endDT <%s> not in expected YYYYMMDDTHHMMSS format' % (args.endDT))
        sys.exit(-1)
        
    # call main class
    archive(startDT, endDT, args.source, args.dest, args.verbose)
    
    

