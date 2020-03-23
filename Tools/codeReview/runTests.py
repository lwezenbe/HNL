#
#       Code to run tests of all the specified code in the repo
#       Meant as a check if I broke something before pushing all the broken stuff to github
#       TODO: Add test output like in heavyNeutrino
#

import os
import glob
base_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL')
code_to_test = [line.strip() for line in open('codeToTest.conf')]
for code in code_to_test:
    print '\x1b[6;30;42m' + 'RUNNING '+ code + ' \x1b[0m'
    os.system('python '+os.path.join(base_path,code))






# exceptions = ['codeReview', 'scripts', 'inputFiles', 'plot', 'merge']
# all_base_dir = glob.glob(os.path.join(base_path, '*/'))
# for base_dir in all_base_dir:
#     all_base_python_files = glob.glob(os.path.join(base_dir, '*.py'))
#     for python_file in all_base_python_files:
#         if any([e in python_file for e in exceptions]): continue
#         print python_file
        