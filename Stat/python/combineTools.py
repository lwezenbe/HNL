#########################
# Tools to use Combine  #
#########################

#
# Imports 
#
import os
from HNL.Tools.helpers import makeDirIfNeeded

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
def makeDataCard(bin_name, flavor, year, obs_yield, sig_yield, bkgr_yields, bkgr_names):

    if len(bkgr_yields) != len(bkgr_names):
        raise RuntimeError("length of background yields and names is inconsistent")

    def tab(entries, column='12'):
        return ''.join(['%25s' % entries[0]] + [(('%'+column+'s') % i) for i in entries[1:]]) + '\n'

    out_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'dataCards', str(year), flavor, bin_name+'.txt')
    makeDirIfNeeded(out_name)
    out_file = open(out_name, 'w')

    out_file.write('imax    1 number of bins \n')
    out_file.write('jmax    * number of processes\n')
    out_file.write('kmax    * \n')
    out_file.write('-'*400 + '\n')
    out_file.write('-'*400 + '\n')
    out_file.write('bin             '+bin_name+ ' \n')
    out_file.write('observation     '+str(obs_yield)+ ' \n')
    out_file.write('-'*400 + '\n')
    out_file.write(tab(['bin', '']+ [bin_name]*(len(bkgr_yields)+1)))
    out_file.write(tab(['process', '']+ bkgr_names + ['HNL-'+flavor]))
    out_file.write(tab(['process', '']+ [str(i) for i in xrange(1, len(bkgr_yields)+1)] + ['0']))
    out_file.write(tab(['rate', '']+ bkgr_yields + [sig_yield]))
    out_file.write('-'*400 + '\n')

    # For now no systematics, just lumi as example
    out_file.write(tab(['lumi_13TeV', 'lnN']+ [1.025]*(len(bkgr_yields)+1)))



    out_file.close()

if __name__ == '__main__':
    makeDataCard('testbin', 'tau', 2016, 20, 6, [20, 23, 12, 1], ['DY', 'WJets', 'tt', 'WZ'])