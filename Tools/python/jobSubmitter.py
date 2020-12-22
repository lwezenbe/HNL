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
        if queue > 2000:
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
    print command
    system('python '+command + ' &> ' + logfile + ' &')

from HNL.Tools.helpers import makePathTimeStamped
def getCondorBase(logfile):
    jobfilebase = logfile.replace('/log/', '/jobs/')
    jobfilebase = jobfilebase.replace('/Latest/', '/')
    jobfilebase = jobfilebase.rsplit('/', 1)[0]
    return jobfilebase

def makeCondorFile(logfile, script, i, runscriptname, condor_base):
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
def makeRunScript(script, arguments, i, condor_base):
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


def launchOnCondor(logfile, script, arguments, i):
    # submit_file = open(submit_file_name, 'a')
    # submit_file.write('Arguments        = '+ arguments +'\n')
    # submit_file.write('Queue \n')
    # submit_file.close()

    condor_base = getCondorBase(os.path.realpath(logfile))
    runscript_name = makeRunScript(script, arguments, i, condor_base)
    submit_file_name = makeCondorFile(logfile, script, i, runscript_name, condor_base)

    print 'condor_submit '+submit_file_name
    try:    out = os.system('condor_submit '+submit_file_name)
    except: out = 'failed'
    print out

def cleanJobFiles(argparser, script, sub_log = None):
    args         = argparser.parse_args()
    if args.batchSystem != "HTCondor":
        pass
    else:
        submitArgs   = getSubmitArgs(argparser, args)
        arg_string = getArgsStr(submitArgs, to_ignore=['isChild'])
        logbase = os.path.realpath(os.path.join('jobs', os.path.basename(script).split('.')[0]+(('-'+sub_log) if sub_log else ''), arg_string))
        os.system('rm -r '+logbase)

from HNL.Tools.logger import clearLogs
import json
def getSubmitArgs(argparser, args, dropArgs=None):
    #changedArgs looks at all the arguments you gave in the original command. The getattr() skips things like args.sample and so on that have a default of None here but will add those anyway
    #when looping over the subjobs in the zip(subJobArgs, subJob) 
    arg_groups={}
    for group in argparser._action_groups:
        group_dict={a.dest:getattr(args,a.dest,None) for a in group._group_actions}
        arg_groups[group.title]=argparse.Namespace(**group_dict)

    changedArgs  = [arg for arg in vars(arg_groups['submission']) if getattr(arg_groups['submission'], arg) and argparser.get_default(arg) != getattr(arg_groups['submission'], arg)]
    submitArgs   = {arg: getattr(arg_groups['submission'], arg) for arg in changedArgs if (not dropArgs or arg not in dropArgs)}
    return submitArgs

def getArgsStr(arg_list, to_ignore):
    args_str=''
    for arg in sorted(arg_list.keys()):
        if str(arg) in to_ignore:
            continue
        elif isinstance(arg_list[arg], list):
            args_str += '_' + str(arg) + '-' + '-'.join([str(x) for x in sorted(arg_list[arg])])
        else:
            args_str += '_' + str(arg) + '-' + str(arg_list[arg])
    return args_str 

def submitJobs(script, subJobArgs, subJobList, argparser, dropArgs=None, subLog=None, wallTime='15', queue='localgrid', cores=1, jobLabel='', resubmission = False):
    args         = argparser.parse_args()
    args.isChild = True

    submitArgs   = getSubmitArgs(argparser, args, dropArgs)
    arg_string = getArgsStr(submitArgs, to_ignore=['isChild'])
    
    #Do not include isChild in arg_string

    logbase = os.path.join('log', os.path.basename(script).split('.')[0]+(('-'+subLog) if subLog else ''), arg_string)
    if not resubmission: clearLogs(logbase)
    logbase += '/Latest'
    script = os.path.realpath(script)

    # save arguments for later checks
    if not resubmission:
        with open(logbase+'/args.txt', 'w') as f:
            json.dump(args.__dict__, f, indent = 2)

    # # Clear current jobs folder
    # if args.batchSystem == 'HTCondor':
    #     os.system('rm jobs/*.sub')

    for i, subJob in enumerate(subJobList):
        for arg, value in zip(subJobArgs, subJob):
            if value: submitArgs[arg] = str(value)
            else:
                try:    submitArgs.pop(arg)
                except: pass
        
        args_str_for_command=' '
        for arg, value in submitArgs.iteritems():
            if value == False:
                continue
            elif isinstance(value, list):
                args_str_for_command += ' ' + '--' + arg + '=' + ' '.join([str(x) for x in sorted(value)])
            else:
                args_str_for_command += ' ' + '--' + arg + '=' + str(value)

        command = script + ' ' + args_str_for_command
        command = command.replace('=True','')
        
        logdir  = os.path.join(logbase, *(str(s) for s in subJob[:-1]))
        logfile = os.path.join(logdir, str(subJob[-1]) + ".log")

        try:    os.makedirs(logdir)
        except: pass

        if args.dryRun:     log.info('Dry-run: ' + command)
        # elif args.batchSystem == 'local': runLocal(command, logfile)
        elif args.batchSystem == 'HTCondor': 
            arguments = (os.getcwd(), command)
            launchOnCondor(logfile, script, arguments, i)
        
        else:               launchCream02(command, logfile, checkQueue=(i%100==0), wallTimeInHours=wallTime, queue=queue, cores=cores, jobLabel=jobLabel)

    print len(subJobList), 'jobs submitted'

from HNL.Tools.logger import successfullJob
def checkCompletedJobs(script, subJobList, argparser, subLog = None):
    failed_jobs = []
    args = argparser.parse_args()
    submitArgs   = getSubmitArgs(argparser, args)
    arg_string = getArgsStr(submitArgs, to_ignore=['isChild'])

    for i, subJob in enumerate(subJobList):
        logdir  = os.path.join('log', os.path.basename(script).split('.')[0]+(('-'+subLog) if subLog else ''), arg_string, 'Latest', *(str(s) for s in subJob[:-1]))
        if args.batchSystem != 'HTCondor':
            logfile = os.path.join(logdir, str(subJob[-1]) + ".log")
        else:
            logfile = os.path.join(logdir, str(subJob[-1]) + ".err")
        if not successfullJob(logfile): failed_jobs.append(subJob)
    
    if len(failed_jobs) != 0:
        print "FOLLOWING JOBS FAILED"
        for l in failed_jobs:
            print ' '.join(str(s) for s in l)
        
        return failed_jobs
    else:
        print "All jobs completed successfully!"
        return None

if __name__ == '__main__':
    launchCondor('a', 'b', 'c', 0)
