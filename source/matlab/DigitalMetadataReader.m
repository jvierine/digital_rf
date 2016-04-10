classdef DigitalMetadataReader
    % class DigitalMetadataReader allows easy read access to  Digital
    % metadata
    %   See testDigitalMetadataReader.m for usage, or run <doc DigitalMetadataReader>
    %
    % $Id: DigitalMetadataReader.m 1019 2016-03-03 19:14:19Z brideout $
    
    properties
        metadataDir % a string of metadata directory
        subdirectory_cadence_seconds % a number of seconds per direcorty
        file_cadence_seconds % number of seconds per file
        samples_per_second % samples per second of metadata
        file_name % file naming prefix
        fields % a char array of field names in metadata 
        dir_glob % string to glob for directories
    end % end properties
    
    methods
        function reader = DigitalMetadataReader(metadataDir)
            % DigitalMetadataReader is the contructor for this class.  
            % Inputs - metadataDir - a string of the path to the metadata
            
            reader.metadataDir = metadataDir;
            % read properties from metadata.h5
            metaFile = fullfile(metadataDir, 'metadata.h5');
            reader.subdirectory_cadence_seconds = uint64(h5readatt(metaFile, '/', 'subdirectory_cadence_seconds'));
            reader.file_cadence_seconds = uint64(h5readatt(metaFile, '/', 'file_cadence_seconds'));
            reader.samples_per_second = uint64(h5readatt(metaFile, '/', 'samples_per_second'));
            reader.file_name = h5readatt(metaFile, '/', 'file_name');
            fields = h5read(metaFile, '/fields');
            reader.fields = cellstr(fields.column');
            reader.dir_glob = '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]-[0-9][0-9]-[0-9][0-9]';
            
        end % end DigitalMetadataReader
        
        function [lower_sample, upper_sample] = get_bounds(obj)
            % get_bounds returns a tuple of first sample, last sample for this metadata. A sample 
            % is the unix time times the sample rate as a integer.
            glob_str = fullfile(obj.metadataDir, obj.dir_glob);
            result = glob(glob_str);
            
            % get first sample
            glob_str = fullfile(result(1), sprintf('%s@*.h5', char(obj.file_name)));
            result2 = glob(char(glob_str));
            h5_summary = h5info(char(result2(1)));
            name = h5_summary.Groups(1).Name;
            lower_sample = uint64(str2double(name(2:end)));
            
            % get last sample
            glob_str = fullfile(result(end), sprintf('%s@*.h5', char(obj.file_name)));
            result2 = glob(char(glob_str));
            h5_summary = h5info(char(result2(end)));
            name = h5_summary.Groups(end).Name;
            upper_sample = uint64(str2double(name(2:end)));
            
        end % end get_bounds
        
        function fields = get_fields(obj)
            fields = obj.fields;
        end % end get_fields
        
        function fields = get_samples_per_second(obj)
            fields = obj.samples_per_second;
        end % end get_samples_per_second
        
        function fields = get_subdirectory_cadence_seconds(obj)
            fields = obj.subdirectory_cadence_seconds;
        end % end get_subdirectory_cadence_seconds
        
        function fields = get_file_cadence_seconds(obj)
            fields = obj.file_cadence_seconds;
        end % end get_file_cadence_seconds
        
        function fields = get_file_name(obj)
            fields = obj.file_name;
        end % end get_file_name
        
        function data_map = read(obj, sample0, sample1, field)
            % read returns a containers.Map() object containing key=sample as uint64,
            % value = data at that sample for all fields
            %
            %   Inputs:
            %       sample0 - first sample for which to return metadata
            %       sample1 - last sample for which to return metadata. A sample
            %           is the unix time times the sample rate as a long.
            %       field - the valid field you which to get
            data_map = containers.Map('KeyType','uint64','ValueType','any');
            sample0 = uint64(sample0);
            sample1 = uint64(sample1);
            file_list = obj.get_file_list(sample0, sample1);
            for i=1:length(file_list)
                obj.add_metadata(data_map, file_list{i}, sample0, sample1, field);
            end % end for file_list
        end % end read
        
        
        function file_list = get_file_list(obj, sample0, sample1)
            % get_file_list is a private method that returns a cell array
            % of strings representing the full path to files that exist
            % with data
            %   Inputs:
            %       sample0 - first sample for which to return metadata
            %       sample1 - last sample for which to return metadata. A sample
            %           is the unix time times the sample rate as a long.
            start_ts = uint64(sample0/obj.samples_per_second);
            end_ts = uint64(sample1/obj.samples_per_second);

            % convert ts to be divisible by obj.file_cadence_seconds
            start_ts = (start_ts ./ obj.file_cadence_seconds) * obj.file_cadence_seconds;
            end_ts = (end_ts ./ obj.file_cadence_seconds) * obj.file_cadence_seconds;

            % get subdirectory start and end ts
            start_sub_ts = (start_ts ./ obj.subdirectory_cadence_seconds) * obj.subdirectory_cadence_seconds;
            end_sub_ts = (end_ts ./ obj.subdirectory_cadence_seconds) * obj.subdirectory_cadence_seconds;
            
            num_sub = uint64(1 + ((end_sub_ts - start_sub_ts) ./ obj.subdirectory_cadence_seconds));
            
            sub_arr = linspace(double(start_sub_ts), double(end_sub_ts), double(num_sub));
            
            file_list = {}; 
            
            for i=1:length(sub_arr)
                sub_ts = uint64(sub_arr(i));
                sub_datetime = datetime( sub_ts, 'ConvertFrom', 'posixtime' );
                subdir = fullfile(obj.metadataDir, datestr(sub_datetime, 'yyyy-mm-ddTHH-MM-SS'));
                num_file_ts = uint64(1 + (obj.subdirectory_cadence_seconds - obj.file_cadence_seconds) ./ obj.file_cadence_seconds);
                file_ts_in_subdir = linspace(double(sub_ts), ...
                    double(sub_ts + (obj.subdirectory_cadence_seconds - obj.file_cadence_seconds)), double(num_file_ts));
                file_ts_in_subdir = uint64(file_ts_in_subdir);
                ind = find(file_ts_in_subdir >= start_ts & file_ts_in_subdir <= end_ts);
                valid_file_ts_list = file_ts_in_subdir(ind);
                for j=1:length(valid_file_ts_list)
                    basename = sprintf('%s@%i.h5', char(obj.file_name), valid_file_ts_list(j));
                    full_file = fullfile(subdir, basename);
                    if exist(full_file, 'file') == 2
                        file_list{1+length(file_list)} = full_file;
                    end % end if exist
                end % end for valid_file_ts_list
            end % end for sub_arr
            
        end % end get_file_list
        
        
        function add_metadata(obj, data_map, filename, sample0, sample1, field)
            % add metadata adds all needed metadata from filename to
            % data_map
            %   Inputs:
            %       data_map - a containers.Map() object containing key=sample as uint64,
            %           value = data at that sample for all fields
            %       filename - full path of file to read
            %       sample0 - first sample for which to return metadata
            %       sample1 - last sample for which to return metadata. A sample
            %           is the unix time times the sample rate as a long.
            %       field - the valid field you which to get
            h5_summary = h5info(filename);
            keys = h5_summary.Groups;
            for i=1:length(keys)
                sample = uint64(str2double(keys(i).Name(2:end)));
                if (sample >= sample0 && sample <= sample1)
                    path = fullfile(keys(i).Name, field);
                    value = h5read(filename, path);
                    data_map(sample) = value;
                end
            end % end for keys
        end % end add_metadata
       
    end % end methods
    
    
end % end DigitalMetadataReader class