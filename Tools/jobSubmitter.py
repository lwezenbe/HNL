import os, time, subprocess
from logger import getLogger
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
def launchCream02(command, logfile, checkQueue=False, name=None, wallTimeInHours='12'):
    if checkQueue: checkQueueOnCream02()
    log.info('Launching ' + command + ' on cream02')
    qsubOptions = ['-v dir=' + os.getcwd() + ',command="' + command + '"',
                   '-q localgrid@cream02',
                   '-o ' + logfile,
                   '-e ' + logfile,
                   '-l walltime='+wallTimeInHours+':00:00']
    if name:
      qsubOptions.append('-N ' + name)
    try:    out = system('qsub ' + ' '.join(qsubOptions) + ' /user/lwezenbe/private/PhD/Code/TauStudy/scripts/runOnCream02.sh')
    except: out = 'failed'
    if not out.count('.cream02.iihe.ac.be'):
        time.sleep(10)
        launchCream02(command, logfile, checkQueue, name)

def runLocal(command, logfile):
    print('starting wait')
    print(int(system('ps uaxw | grep python | grep $USER |grep -c -v grep')))
    while(int(system('ps uaxw | grep python | grep $USER |grep -c -v grep')) > 8): 
        print('WAIT')
        time.sleep(20)
    print('passed waiting phase')
    log.info('Launching ' + command + ' on local machine')
    system(command + ' &> ' + logfile + ' &')
