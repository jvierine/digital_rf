% example usage of DigitalMetadataReader.m
% Requires python test_write_digital_metadata.py be run first to create test data
% $Id: testDigitalMetadataReader.m 1019 2016-03-03 19:14:19Z brideout $
metadataDir = '/tmp/test_metadata';

% init the object
reader = DigitalMetadataReader(metadataDir);

% get the sample bounds
[b0, b1] = reader.get_bounds();
disp([b0, b1]);

% access all the object attributes
fields = reader.get_fields();
disp(fields);
disp(reader.get_samples_per_second());
disp(reader.get_subdirectory_cadence_seconds());
disp(reader.get_file_cadence_seconds());
disp(reader.get_file_name());

% call the main method read for each field
for i=1:length(fields)
    data_map = reader.read(b0, b0+100, char(fields(i)));
    disp(fields(i));
    disp(data_map);
end