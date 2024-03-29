#
# Logger module
#
import logging, sys, ROOT, os
ROOT.gErrorIgnoreLevel = ROOT.kWarning


SUCCESS_MESSAGE = "JOB SUCCESSFULLY COMPLETED. NO NEED TO RESUBMIT"
OTHER_ERRORS = ["SysError in <TFile::Flush>", "Input/output error"]
L1_ERRORS = ["Error in <TBasket::ReadBasketBuffers>"]

def getLogger(level='INFO', logFile=None):
    # If it already exist, return it
    logger = logging.getLogger('main')
    if logger.handlers:
        return logger

    # add TRACE (numerical level 5, less than DEBUG) to logging (similar to apache) 
    # see default levels at https://docs.python.org/2/library/logging.html#logging-levels
    logging.TRACE = 5
    logging.addLevelName(logging.TRACE, 'TRACE')

    logging.Logger.trace = lambda inst, msg, *args, **kwargs: inst.log(logging.TRACE, msg, *args, **kwargs)
    logging.trace        = lambda msg, *args, **kwargs: logging.log(logging.TRACE, msg, *args, **kwargs)

    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % level)

    logger.setLevel(numeric_level)
    formatter = logging.Formatter('%(asctime)s %(module)20s %(levelname)7s - %(message)s')
    if logFile:
        # create the logging file handler
        fileHandler = logging.FileHandler(logFile, mode='w')
        fileHandler.setFormatter(formatter)
        # add handler to logger object
        logger.addHandler(fileHandler)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # log the exceptions to the logger
    def excepthook(*args):
        logger.error("Uncaught exception:", exc_info=args)

    sys.excepthook = excepthook
    logger.info('Command: ' + ' '.join(sys.argv))
    return logger

def closeLogger(logger):
    logger.info(SUCCESS_MESSAGE)

def logLevel(logger, level):
    return logger.getEffectiveLevel() <= logging.getLevelName(level)

def successfullJob(fname, level = 0):
    try:
        lines = [line.split('%')[0].strip() for line in open(fname)] 
    except:
        return False
    for line in lines:
        if level == 1:
            for err in L1_ERRORS:
                if err in line: return False
        for err in OTHER_ERRORS:
            if err in line: return False
     
        passed = SUCCESS_MESSAGE in line

#        failed = 'Bus error' in line
#        if failed: return False
#        else: continue

        if not passed: continue
        else: return True
#    return True
    return False

from HNL.Tools.helpers import makeDirIfNeeded
def clearLogs(base):
#    last_base = base.replace('Latest', 'Previous')
#    makeDirIfNeeded(last_base+'/x')
#    os.system('rm -r '+last_base+'/*')
#    os.system('scp -r '+base+'/* '+last_base+'/.')
    os.system('rm -r '+base)
