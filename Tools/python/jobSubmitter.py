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
def launchCream02(command, logfile, checkQueue=False, name=None, wallTimeInHours='12', queue='localgrid', cores=1, jobLabel=None):
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
    while(int(system('ps uaxw | grep python | grep $USER |grep -c -v grep')) > 8): time.sleep(20)
    log.info('Launching ' + command + ' on local machine')
    system(command + ' &> ' + logfile + ' &')

def submitJobs(script, subJobArgs, subJobList, argParser, dropArgs=None, subLog=None, wallTime='15', queue='localgrid', cores=1, jobLabel=''):
    args         = argParser.parse_args()
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
        
        logdir  = os.path.join('log', os.path.basename(script).split('.')[0]+(('-'+subLog) if subLog else ''), *(str(s) for s in subJob[:-1]))
        logfile = os.path.join(logdir, str(subJob[-1]) + ".log")

        try:    os.makedirs(logdir)
        except: pass
        
        if args.dryRun:     log.info('Dry-run: ' + command)
        elif args.runLocal: runLocal(command, logfile)
        else:               launchCream02(command, logfile, checkQueue=(i%100==0), wallTimeInHours=wallTime, queue=queue, cores=cores, jobLabel=jobLabel)

