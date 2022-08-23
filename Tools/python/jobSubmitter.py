import os
import time
import subprocess
import argparse

from HNL.Tools.logger import getLogger
log = getLogger()

def system(command):
    return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)

def checkQueueOnCream02():
    try:
        queue = int(system('qstat -u $USER | wc -l'))
        # if queue > 2000:
        if queue > 1500:
            log.info('Too much jobs in queue (' + str(queue) + '), sleeping')
            time.sleep(500)
            checkQueueOnCream02()
    except:
        checkQueueOnCream02()

# Cream02 running
from datetime import datetime
def launchCream02(command, logfile, checkQueue=False, wallTimeInHours='12', queue='localgrid', cores=1, jobLabel=None):
    jobName = jobLabel + datetime.now().strftime("%d_%H%M%S.%f")[:12]
    if checkQueue: checkQueueOnCream02()
    log.info('Launching ' + command + ' on cream02')
    qsubOptions = ['-v dir="' + os.getcwd() + '",command="' + command + '"',
                   '-q ' +queue +'@cream02',
                   '-o ' + logfile,
                   '-e ' + logfile,
                   '-l walltime='+wallTimeInHours+':00:00 '
                   '-N ' + jobName]
    try:    out = system('qsub ' + ' '.join(qsubOptions) + ' $CMSSW_BASE/src/HNL/Tools/scripts/runOnCream02.sh')
    except: out = 'failed'
    if not out.count('.cream02.iihe.ac.be'):
        time.sleep(10)
        launchCream02(command, logfile, checkQueue = checkQueue, wallTimeInHours=wallTimeInHours, queue=queue, cores=cores, jobLabel=jobLabel)

def runLocal(command, logfile):
    while(int(system('ps uaxw | grep python | grep $USER |grep -c -v grep')) > 8): 
        print int(system('ps uaxw | grep python | grep $USER |grep -c -v grep')), ': sleeping'
        time.sleep(20)
    log.info('Launching ' + command + ' on local machine')
    system('python '+command + ' &> ' + logfile + ' &')

from HNL.Tools.helpers import makePathTimeStamped
def getCondorBase(logfile):
    jobfilebase = logfile.replace('/log/', '/jobs/')
    jobfilebase = jobfilebase.replace('/Latest/', '/')
    jobfilebase = jobfilebase.rsplit('/', 1)[0]
    return jobfilebase

def makeCondorFile(logfile, i, runscriptname, condor_base):
    logfile = os.path.realpath(logfile)
    submit_file_name = makePathTimeStamped(condor_base)
    submit_file_name += '_'+str(i)+'.sub'
    submit_file = open(submit_file_name, 'w') 
    submit_file.write('Universe     = vanilla \n')
    submit_file.write('Executable   = '+runscriptname+' \n')
    submit_file.write('Log          = '+logfile+ '\n')
    submit_file.write('Output       = '+logfile.split('.log')[0]+'.out \n')
    submit_file.write('Error        = '+logfile.split('.log')[0]+'.err \n')
    submit_file.write('Queue \n')
    submit_file.close()
    return submit_file_name

from HNL.Tools.helpers import makeDirIfNeeded
def makeRunScript(arguments, i, condor_base):
    original_script = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Tools', 'scripts', 'runOnCondor.sh'))
    new_script_name = os.path.realpath(os.path.join(condor_base, 'runscripts', str(i)+'.sh'))
    makeDirIfNeeded(new_script_name)
    new_script = open(new_script_name, 'w')
    for line in open(original_script, 'r'):
        new_line = line.replace('$1', arguments[0])
        new_line = new_line.replace('$2', arguments[1])
        new_script.write(new_line)
    new_script.close()
    return new_script_name

def launchOnCondor(logfile, arguments, i, job_label = None):
    condor_base = getCondorBase(os.path.realpath(logfile))
    runscript_name = makeRunScript(arguments, i, condor_base)
    os.system('chmod +x '+runscript_name)
    submit_file_name = makeCondorFile(logfile, i, runscript_name, condor_base)

    command = 'condor_submit '+submit_file_name
    if job_label is not None: command += ' -batch-name ' +job_label
    try:    out = os.system(command)
    except: out = 'failed'
    print out

def cleanJobFiles(argparser, script, sub_log = None):
    args         = argparser.parse_args()
    submitArgs   = getSubmitArgs(argparser, args)
    arg_string = getArgsStr(submitArgs, to_ignore=['isChild'])
    if args.batchSystem != "HTCondor":
        pass
    else:
        jobbase = os.path.realpath(os.path.join('jobs', os.path.basename(script).split('.')[0]+(('-'+sub_log) if sub_log else ''), arg_string))
        os.system('rm -r '+jobbase)
    
    logdir  = os.path.join('log', 'Latest', os.path.basename(script).split('.')[0]+(('-'+sub_log) if sub_log else ''), arg_string)
    clearLogs(logdir)


from HNL.Tools.logger import clearLogs
import json
def getSubmitArgs(argparser, args, dropArgs=None, additionalArgs = None, man_changed_args = None, include_all_groups = False):
    #changedArgs looks at all the arguments you gave in the original command. The getattr() skips things like args.sample and so on that have a default of None here but will add those anyway
    #when looping over the subjobs in the zip(subJobArgs, subJob) 
    arg_groups = {}
    for group in argparser._action_groups:
        group_dict = {a.dest:getattr(args,a.dest,None) for a in group._group_actions}
        arg_groups[group.title] = argparse.Namespace(**group_dict)

    if not include_all_groups:
        arg_to_use = arg_groups['submission']
    else:
        arg_to_use = args    

    if man_changed_args is not None:
        for mca in man_changed_args.keys():
            setattr(arg_to_use, mca, man_changed_args[mca])

    changedArgs  = [arg for arg in vars(arg_to_use) if getattr(arg_to_use, arg) and argparser.get_default(arg) != getattr(arg_to_use, arg)]
    submitArgs   = {arg: getattr(arg_to_use, arg) for arg in changedArgs if (not dropArgs or arg not in dropArgs)}
    if additionalArgs is not None:
        for additional_arg in additionalArgs:
            submitArgs[additional_arg[0]] = additional_arg[1]
    return submitArgs

def getArgsStr(arg_list, to_ignore):
    args_str = ''
    for arg in sorted(arg_list.keys()):
        if str(arg) in to_ignore:
            continue
        elif isinstance(arg_list[arg], list):
            args_str += '_' + str(arg) + '-' + '-'.join([str(x).replace('/', '-') for x in sorted(arg_list[arg])])
        else:
            args_str += '_' + str(arg) + '-' + str(arg_list[arg]).replace('/', '-')
    args_str = "".join(i for i in args_str if i not in " &\/:*?<>|")
    return args_str 

def submitJobs(script, subjob_args, subjob_list, argparser, **kwargs):
    drop_args = kwargs.get('dropArgs', None)
    additional_args = kwargs.get('additionalArgs', None)
    sub_log = kwargs.get('subLog', None)
    wall_time = kwargs.get('wallTime', '15')
    queue = kwargs.get('queue', 'localgrid')
    cores = kwargs.get('cores', 1)
    job_label = kwargs.get('jobLabel', None)
    resubmission = kwargs.get('resubmission', False)
    man_changed_args = kwargs.get('man_changed_args', None)
    include_all_groups = kwargs.get('include_all_groups', False)

    try:
        if checkShouldMerge(script, argparser, sub_log, additional_args, man_changed_args = man_changed_args):
            can_continue = raw_input('You are about to submit jobs but there seem to be existing files waiting for a merge. Are you sure you want to submit these jobs anyway? (y/n) \n')    
            if can_continue not in ['y', 'Y']: 
                print 'Aborting job submission'
                return
    except:
        pass
    
    args         = argparser.parse_args()
    args.isChild = True

    ignore_overwrite = False
    if resubmission and 'skimmer' in script and not args.overwrite:
        ignore_overwrite = True
        args.overwrite = True
    submit_args   = getSubmitArgs(argparser, args, drop_args, additional_args, man_changed_args = man_changed_args, include_all_groups = include_all_groups)
    if resubmission and 'skimmer' in script and ignore_overwrite:
        arg_string = getArgsStr(submit_args, to_ignore=['isChild', 'overwrite'])
    else:
        arg_string = getArgsStr(submit_args, to_ignore=['isChild'])
    
    #Do not include isChild in arg_string

    logbase = os.path.join('log', 'Latest', os.path.basename(script).split('.')[0]+(('-'+sub_log) if sub_log else ''), arg_string)
    if not resubmission and not args.dryRun: makeDirIfNeeded(logbase+'/x')
    script = os.path.realpath(script)

    merge_check_pass = logbase.replace('Latest', 'Merge')
    merge_check_pass += '/shouldMerge.txt'
    makeDirIfNeeded(merge_check_pass)
    with open(merge_check_pass, 'w') as filetowrite:
        filetowrite.write('True')

    # save arguments for later checks
    if not resubmission and not args.dryRun:
        with open(logbase+'/args.txt', 'w') as f:
            json.dump(args.__dict__, f, indent = 2)

    for i, subJob in enumerate(subjob_list):
        for arg, value in zip(subjob_args, subJob):
            if value: submit_args[arg] = str(value)
            else:
                try:    submit_args.pop(arg)
                except: pass
        
        args_str_for_command = ' '
        for arg, value in submit_args.iteritems():
            if value == False:
                continue
            elif isinstance(value, list):
                args_str_for_command += ' ' + '--' + arg + ' ' + ' '.join([str(x) for x in sorted(value)])
            elif arg == 'cutString':
                args_str_for_command += ' ' + '--' + arg + '="' + str(value) +'"'            
            else:
                args_str_for_command += ' ' + '--' + arg + '=' + str(value)

        command = script + ' ' + args_str_for_command
        command = command.replace('=True','')
        
        logdir  = os.path.join(logbase, *(str(s) for s in subJob[:-1]))
        logfile = os.path.join(logdir, str(subJob[-1]) + ".log")
        if resubmission:
            os.system('rm '+logfile)
            if not 'resubmission' in job_label: job_label += '-resubmission'

        if not args.dryRun:
            try:    os.makedirs(logdir)
            except: pass

        if args.dryRun:     log.info('Dry-run: ' + command)
        elif args.batchSystem == 'local': runLocal(command, logfile)
        elif args.batchSystem == 'HTCondor': 
            arguments = (os.getcwd(), command)
            launchOnCondor(logfile, arguments, i, job_label=job_label)
        
        else:               launchCream02(command, logfile, checkQueue=(i%100==0), wallTimeInHours=wall_time, queue=queue, cores=cores, jobLabel=job_label+'-'+submit_args['sample'])

    print len(subjob_list), 'jobs submitted'

from HNL.Tools.logger import successfullJob
def checkCompletedJobs(script, subJobList, argparser, subLog = None, additionalArgs=None, level = 0):
    failed_jobs = []
    args = argparser.parse_args()
    submitArgs   = getSubmitArgs(argparser, args, additionalArgs=additionalArgs)
    arg_string = getArgsStr(submitArgs, to_ignore=['isChild'])

    for subJob in subJobList:
        logdir  = os.path.join('log', 'Latest', os.path.basename(script).split('.')[0]+(('-'+subLog) if subLog else ''), arg_string, *(str(s) for s in subJob[:-1]))
        if args.batchSystem != 'HTCondor':
            logfile = os.path.join(logdir, str(subJob[-1]) + ".log")
        else:
            logfile = os.path.join(logdir, str(subJob[-1]) + ".err")
        if not successfullJob(logfile, level = level): failed_jobs.append(subJob)
    
    if len(failed_jobs) != 0:
        print "FOLLOWING JOBS FAILED"
        for l in failed_jobs:
            print ' '.join(str(s) for s in l)
        
        print "=> {0} out of {1} jobs failed: {2}".format(len(failed_jobs), len(subJobList), float(len(failed_jobs))/float(len(subJobList)))
        return failed_jobs
    else:
        print "All jobs completed successfully!"
        return None

def checkShouldMerge(script, argparser, subLog = None, additionalArgs=None, man_changed_args = None, full_path = None):
    args = argparser.parse_args()
    submitArgs   = getSubmitArgs(argparser, args, additionalArgs=additionalArgs, man_changed_args = man_changed_args)
    arg_string = getArgsStr(submitArgs, to_ignore=['isChild', 'subJob'])

    if full_path is None:
        path_to_check = os.path.join('log', 'Merge', os.path.basename(script).split('.')[0]+(('-'+subLog) if subLog else ''), arg_string, 'shouldMerge.txt')
    else:
        path_to_check = os.path.join(full_path, 'log', 'Merge', os.path.basename(script).split('.')[0]+(('-'+subLog) if subLog else ''), arg_string, 'shouldMerge.txt')
    
    with open(path_to_check) as f:
        first_line = f.readline()

    #if first_line == 'True':
    if 'True' in first_line:
        return True
    else:
        return False

def disableShouldMerge(script, argparser, subLog = None, additionalArgs=None):
    args = argparser.parse_args()
    submitArgs   = getSubmitArgs(argparser, args, additionalArgs=additionalArgs)
    arg_string = getArgsStr(submitArgs, to_ignore=['isChild'])

    path_to_check = os.path.join('log', 'Merge', os.path.basename(script).split('.')[0]+(('-'+subLog) if subLog else ''), arg_string, 'shouldMerge.txt')
    with open(path_to_check, 'w') as filetowrite:
        filetowrite.write('False')

if __name__ == '__main__':
    launchOnCondor('a', 'b', 'c', 0)
