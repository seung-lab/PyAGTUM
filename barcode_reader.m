try
    I = imread("C:/dev/data/barcode_out.png");

    % Read the 1-D barcode and determine the format..
    [msg, format, locs] = readBarcode(I);

    % Display the detected message and format.
    disp("Detected format and message: " + format + ", " + msg)

    file = fopen('C:/dev/data/barcode_file.txt', 'wt');
    fprintf(file,msg);
    fclose(file);
catch
    fprintf('Error: could not read barcode')
end