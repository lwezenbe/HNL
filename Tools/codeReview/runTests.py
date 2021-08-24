#
#       Code to run tests of all the specified code in the repo
#       Meant as a check if I broke something before pushing all the broken stuff to github
#

#
# Argument parser and logging
#
import os
import argparse
from HNL.Tools.jobSubmitter import launchCream02, launchOnCondor
from HNL.Tools.helpers import makeDirIfNeeded
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--allCombinations',  action='store_true', default=False,  help='Run code that makes long list of all arguments to be combined in tests')
argParser.add_argument('--rerun',  action='store_true', default=False,  help='rerun failed jobs')
argParser.add_argument('--checkLogs',  action='store_true', default=False,  help='Run code that makes long list of all arguments to be combined in tests')
argParser.add_argument('--batchSystem',  action='store', default='Cream02',  help='What batch system to use', choices = ['Cream02', 'HTCondor'])
args = argParser.parse_args()

if not args.checkLogs:
    confirmation = raw_input("You are about to submit new jobs, are you sure you want to do this? Y/N \n")
    if confirmation == 'n' or confirmation == 'N': exit(0)

#
# Functions to be used later on
#
def makeCombinations(input_dict):
    argument_list = ['']
    for k in input_dict.keys():
        renewed_argument_list = []
        for arg in argument_list:
            for entry in input_dict[k]:
                renewed_argument_list.append(arg+' '+entry)
        argument_list = renewed_argument_list
    return argument_list

def createCommandList(input_list):
    try:
        len(input_list)
    except:
        print "Weird stuff going on in input_list of createCommandList. Are you sure the input_list is a list?"
    if not input_list:
        raise RuntimeError('Invalid input list for createCommandList: '+str(input_list))
    
    #No arguments given
    if len(input_list) == 1:
        return input_list
    else:
        main_command = input_list[0]
        argument_dict = {}
        for arg in input_list[1:]:
            split_arg = arg.split(' ')
            argument_dict[split_arg[0]] = []
            if len(split_arg) == 1:                             # Check if it's an argument with input
                argument_dict[split_arg[0]].append('')
                argument_dict[split_arg[0]].append(split_arg[0])
            else:
                main_arg = split_arg[0]
                argument_dict[main_arg].append('')
                for option in split_arg[1:]:
                    argument_dict[main_arg].append(' '.join([main_arg, option]))
        combination_list = makeCombinations(argument_dict)

        return [' '.join([main_command, c]) for c in combination_list]

#
# Shared constant
#
base_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL')

# launchOnCondor(logfile, arguments, i, job_label = None)

def submitJob(command, log_name, **kwargs):
    label = kwargs.get('label', 'Test')
    i = kwargs.get('i')
    if args.batchSystem == 'Cream02':
        launchCream02(command, log_name, jobLabel=label)
    elif args.batchSystem == 'HTCondor':
        launchOnCondor(log_name, (os.getcwd(), command), i, job_label = label)
    else:
        raise RuntimeError('Unknown batch system: {0}'.format(args.batchSystem))


from HNL.Tools.logger import successfullJob
#
# Run exhaustive mode
#
if args.allCombinations:
    input_file = 'data/input/codeToTest_UL.conf'
    code_to_test = [line.split('#')[0].strip() for line in open(input_file)]
    code_to_test = [l.split('%') for l in code_to_test if l]

    out_name = 'data/output/codeToTest_output.txt'
    makeDirIfNeeded(out_name)
    out_file = open(out_name, 'w')
    out_file.close()

    if args.checkLogs:
        failed_jobs = []

    job_number = 0
    for code in code_to_test:
        out_name_base = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Tools', 'codeReview', 'data', 'output', 'runTests', code[0].split(' ')[0].split('.')[0]))
        makeDirIfNeeded(out_name_base+'/x')
        combinations = createCommandList(code)
        for comb in combinations:
            out_name = str(job_number)
            log_name = os.path.join(out_name_base, out_name)
            if args.batchSystem == 'Cream02': log_name += '.txt'
            elif args.batchSystem == 'HTCondor' and args.checkLogs: log_name += '.err'
            if args.checkLogs and not successfullJob(log_name): 
                if not args.rerun:
                    failed_jobs.append([log_name, comb])
                else:
                    submitJob(os.path.join(base_path, comb), log_name.split('.err')[0], i=job_number, jobLabel='test')
            if not args.checkLogs: submitJob(os.path.join(base_path, comb), log_name, i=job_number, jobLabel='test')
            job_number += 1
    if args.checkLogs:
        if len(failed_jobs) != 0:
            print "FOLLOWING JOBS FAILED"
            for l in failed_jobs:
                print '\033[93m', "FAILED JOB:", '\033[0m'
                print "LOG:", l[0]
                print "JOB: python", l[1]
        else:
            print "All jobs completed successfully!"
    print job_number

else:
    print "This mode requires input in data/input/codeToTest_custom.conf. Make sure you have done that"
    input_file = 'data/input/codeToTest_custom.conf'
    code_to_test = [line.split('#')[0].strip() for line in open(input_file)]
    code_to_test = [l for l in code_to_test if l]
    for code in code_to_test:
        print '\x1b[6;30;42m' + 'RUNNING '+ code + ' \x1b[0m'
        os.system('python '+os.path.join(base_path, code))

#
# Backup
#

# import os
# import glob
# base_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL')
# code_to_test = [line.split('#')[0].strip() for line in open('codeToTest.conf')]
# code_to_test = [l.split('%') for l in code_to_test if l]
# for code in code_to_test:
#     print code
#     # createCommandList(code)
#     # print '\x1b[6;30;42m' + 'RUNNING '+ code + ' \x1b[0m'
#     # os.system('python '+os.path.join(base_path,code))
        