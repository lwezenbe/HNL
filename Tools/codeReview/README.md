Code for testing your setup after making changes or pushing to github

**Integration tests**\
runTests.py runs all the code you have with the --isTest argument added. It currently has two modes: custom input and all combinations. 

The custom input mode requires you to put the commands (as they should be run) in the data/input/codeToTest_custom.conf file. It will then run all of them in the terminal and tell you if something goes wrong. No log files are produced, you can read everything in terminal

If the option allCombinations is specified, it will look to data/input/codeToTest.conf for input. In this file, every script that you want to test should be specified. Each line should refer to a script and start with "scriptfolder/scriptname --isTest" followed by "%". After this you can define all arguments to test in all different possible combinations of them. Every argument should be separated by a "%". If there are specific options for an argument that you want to test, you can just write them after the argument divided by spaces. The code with then automatically make all possible combinations of arguments possible and submit a job for each one. Note: If you want an argument to always be defined the same for all your jobs, also put it as an argument (like you would when running in terminal) before the first "%".

The output log of these jobs will be dropped into their respective folder at "/data/output/runTests/name of script". If a job was succesful, it will state "JOB SUCCESSFULLY COMPLETED. NO NEED TO RESUBMIT" in these files. If you run `python runTests.py --allCombinations --checkLogs` it will produce a summary of which jobs failed for you.

**Output tests**\
You can also test the output of your tests. If you propagate the isTest argument correctly when creating all histogram objects in your script, it will make a copy to a folder "Testing" in your home directory. In order to be consistent, please keep the number of entries for the testmode of the scripts at the same number (default 20000). When running the runTests.py script, it will then copy all output from the testjobs into "Testing/Latest". (Job logs are still in the folder described in the Integration tests section, you will not find them in ~/Testing)

After all test jobs have completed and you checked that everything ran succesfully (see last section), you can run `python checkOutputTests.py`. It will open every histogram from your test output and compare all bins to the bins in its equivalent folder in "Testing/Previous". For each job, a .txt file is written in "Testing/LOG" that says if your output is the same. If everything is fine, it will say "EVERYTHING CLEAR", otherwise it will show you in which bin there is a difference. It will also make reports for larger chunks (checking the previous text files automatically for i.e. calcYields). If everything is fine, it will say "EVERYTHING CLEAR", otherwise it will give a list of the subreports where there are differences.

If everything is clear or the changes are expected, you can run `python checkOutputTests.py --overwrite` to move the output from "Testing/Latest" to "Testing/Previous".