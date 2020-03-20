# InputFiles

Contains list of input for all the code to be ran in HNL. There is a strict format to be followed here. Every sample should have it's own line with the following information (in the following order):

-Name (Unique name by which to identify this specific sample in the code)

-Path (Path at which the file in question can be found. In case it is a group of files on pnfs, add all directories up to but not including the date)

-Output (Output name in which this sample is to be grouped. Different samples with same output will be grouped together and merged in the end)

-Number of jobs (You can specificy a number of write "Calc", which well then cause the code to calculate the number of jobs. You can add a modifier * to multiple this number with a factor n)

-Cross section (Add the cross section in pb here or put "data" if the sample is data)

The name and output are not allowed to have underscores in them as this will cause merging conflicts later on
