#########################
# Tools to use Combine  #
#########################

#
# Imports 
#
import os
from HNL.Tools.helpers import makeDirIfNeeded, tab

#
# Information about Combine release
#
release        = 'CMSSW_10_2_13'
arch           = 'slc7_amd64_gcc700'
version        = 'v8.0.1'

#
# Function to write out a data card, these data cards all contain 1 bin to be clear, readable and flexible
# and should be combined later on
#
def makeDataCard(bin_name, flavor, year, obs_yield, sig_name, bkgr_names, sig_yield=None, bkgr_yields= None, shapes=False):

    if not shapes and len(bkgr_yields) != len(bkgr_names):
        raise RuntimeError("length of background yields and names is inconsistent")

    if not shapes:
        out_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'dataCards', str(year), flavor, sig_name, 'cutAndCount',  bin_name+'.txt')
    else:
        out_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'dataCards', str(year), flavor, sig_name, 'shapes', bin_name+'.txt')
    makeDirIfNeeded(out_name)
    out_file = open(out_name, 'w')

    out_file.write('imax    1 number of bins \n')
    out_file.write('jmax    * number of processes\n')
    out_file.write('kmax    * \n')
    out_file.write('-'*400 + '\n')
    if shapes:
        shapes_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'shapes', str(year), flavor, sig_name, bin_name+'.txt')
        out_file.write('shapes * * \t' +shapes_path + ' $PROCESS $PROCESS_SYSTEMATIC')
    out_file.write('-'*400 + '\n')
    out_file.write('bin             '+bin_name+ ' \n')
    if shapes:
        # out_file.write('observation     -1 \n')   
        out_file.write('observation     '+str(obs_yield)+ ' \n') 
    else:
        out_file.write('observation     '+str(obs_yield)+ ' \n')
    out_file.write('-'*400 + '\n')
    out_file.write(tab(['bin', '']+ [bin_name]*(len(bkgr_names)+1)))
    out_file.write(tab(['process', '']+ bkgr_names + [sig_name]))
    out_file.write(tab(['process', '']+ [str(i) for i in xrange(1, len(bkgr_names)+1)] + ['0']))
    if shapes:
        out_file.write(tab(['rate', '']+ ['-1']*(len(bkgr_names)+1)))
    else:
        out_file.write(tab(['rate', '']+ ['%4.6f' % by if by >= 0 else 0.0 for by in bkgr_yields] + ['%4.6f' % sig_yield]))
    out_file.write('-'*400 + '\n')

    # For now no systematics, just lumi as example
    out_file.write(tab(['lumi_13TeV', 'lnN']+ [1.025]*(len(bkgr_names)+1)))

    out_file.close()

# def makeShape(list_of_process_names, list_of_values)

if __name__ == '__main__':
    makeDataCard('testbin', 'tau', 2016, 20, 6, [20, 23, 12, 1], ['DY', 'WJets', 'tt', 'WZ'])