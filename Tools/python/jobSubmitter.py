import os
import time
import subprocess

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
def makeCondorFile(logfile, script):
    submit_file_name = makePathTimeStamped(os.path.join('jobs', os.path.basename(script).split('.')[0]))
    submit_file_name += '.sub'
    submit_file = open(submit_file_name, 'w') 
    submit_file.write('Universe     = vanilla \n')
    submit_file.write('Executable   = '+os.path.expandvars('$CMSSW_BASE/src/HNL/Tools/scripts/runOnCream02.sh')+' \n')
    submit_file.write('Log          = '+logfile+ '\n')
    submit_file.write('Output       = '+logfile.split('.log')[0]+'.out \n')
    submit_file.write('Error        = '+logfile.split('.log')[0]+'.err \n')
    submit_file.close()
    return submit_file_name

def launchOnCondor(submit_file_name, arguments):
    submit_file = open(submit_file_name, 'a')
    submit_file.write('Arguments        = '+ arguments +'\n')
    submit_file.write('Queue \n')

    print 'condor_submit '+submit_file_name
    try:    out = system('condor_submit '+submit_file_name)
    except: out = 'failed'
    print out

from HNL.Tools.logger import clearLogs
import json
def submitJobs(script, subJobArgs, subJobList, argParser, dropArgs=None, subLog=None, wallTime='15', queue='localgrid', cores=1, jobLabel='', resubmission = False):
    logbase = os.path.join('log', os.path.basename(script).split('.')[0]+(('-'+subLog) if subLog else ''))
    if not resubmission: clearLogs(logbase)
    logbase += '/Latest'

    # save arguments in case you need to resubmit
    if not resubmission:
        args         = argParser.parse_args()
        with open(logbase+'/args.txt', 'w') as f:
            json.dump(args.__dict__, f, indent = 2)

    args.isChild = True
    
    #changedArgs looks at all the arguments you gave in the original command. The getattr() skips things like args.sample and so on that have a default of None here but will add those anyway
    #when looping over the subjobs in the zip(subJobArgs, subJob) 
    changedArgs  = [arg for arg in vars(args) if getattr(args, arg) and argParser.get_default(arg) != getattr(args, arg)]
    submitArgs   = {arg: getattr(args, arg) for arg in changedArgs if (not dropArgs or arg not in dropArgs)}

    for i, subJob in enumerate(subJobList):
        for arg, value in zip(subJobArgs, subJob):
            if value: submitArgs[arg] = str(value)
            else:
                try:    submitArgs.pop(arg)
                except: pass
        
        command = script + ' ' + ' '.join(['--' + arg + '=' + str(value) for arg, value in submitArgs.iteritems() if value != False])
        command = command.replace('=True','')
        
        logdir  = os.path.join(logbase, *(str(s) for s in subJob[:-1]))
        logfile = os.path.join(logdir, str(subJob[-1]) + ".log")

        try:    os.makedirs(logdir)
        except: pass

        if args.dryRun:     log.info('Dry-run: ' + command)
        elif args.batchSystem == 'local': runLocal(command, logfile)
        elif args.batchSystem == 'HTCondor': 
            arguments = "dir='" + os.getcwd() + "' command='" + command + "'"
            submit_file_name = makeCondorFile(logfile, script)
            launchOnCondor(submit_file_name, arguments)
        
        else:               launchCream02(command, logfile, checkQueue=(i%100==0), wallTimeInHours=wallTime, queue=queue, cores=cores, jobLabel=jobLabel)

    print len(subJobList), 'jobs submitted'

from HNL.Tools.logger import successfullJob
def checkCompletedJobs(script, subJobList, subLog = None):
    failed_jobs = []
    for i, subJob in enumerate(subJobList):
        logdir  = os.path.join('log', os.path.basename(script).split('.')[0]+(('-'+subLog) if subLog else ''), 'Latest', *(str(s) for s in subJob[:-1]))
        logfile = os.path.join(logdir, str(subJob[-1]) + ".log")
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
    launchCondor('a', 'b', 'c')
