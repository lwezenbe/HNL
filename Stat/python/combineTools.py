#########################
# Tools to use Combine  #
#########################

#
# Imports 
#
import os
import glob
from HNL.Tools.helpers import makeDirIfNeeded, tab, getObjFromFile

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
def makeDataCard(bin_name, flavor, year, obs_yield, sig_name, bkgr_names, sig_yield=None, bkgr_yields= None, shapes=False, coupling_sq = 1e-4):

    if not shapes and len(bkgr_yields) != len(bkgr_names):
        raise RuntimeError("length of background yields and names is inconsistent")

    if not shapes:
        out_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'dataCards', str(year), flavor, sig_name, 'cutAndCount',  bin_name+'.txt')
    else:
        out_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'dataCards', str(year), flavor, sig_name, 'shapes', bin_name+'.txt')
    makeDirIfNeeded(out_name)
    out_file = open(out_name, 'w')

    out_file.write('# coupling squared = '+str(coupling_sq)+' \n \n')
    out_file.write('imax    1 number of bins \n')
    out_file.write('jmax    * number of processes\n')
    out_file.write('kmax    * \n')
    out_file.write('-'*400 + '\n')
    if shapes:
        shapes_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'shapes', str(year), flavor, sig_name, bin_name+'.shapes.root')
        out_file.write('shapes * * \t' +shapes_path + ' $PROCESS $PROCESS_SYSTEMATIC')
    out_file.write('-'*400 + '\n')
    out_file.write('bin             '+bin_name+ ' \n')
    if shapes:
        out_file.write('observation     -1 \n')   
        # out_file.write('observation     '+str(obs_yield)+ ' \n') 
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


    #autoMCstats
    if shapes:
        out_file.write('* autoMCStats 3 1 1')


    out_file.close()

def runCombineCommand(command, output = None):
    currentDir = os.getcwd()
    current_release = os.path.expandvars('$CMSSW_BASE')
    print current_release
    combine_release = os.path.expandvars('$CMSSW_BASE')+'/../'+release
    os.system('rm ' + combine_release +'/src/*root &> /dev/null') 
    os.chdir(combine_release+'/src')
    os.system('(eval `scramv1 runtime -sh`; ' + command + ')')
    if len(glob.glob('*.root'))!=0:
        if output is None:
            os.system('mv *.root '+current_release +'/src/HNL/Stat/data/output/tmp/')
            print 'output saved to '+current_release +'/src/HNL/Stat/data/output/tmp'
        else:
            os.system('mv *.root '+output)
            print 'output saved to '+output
    else:
        print 'No combine .root output was saved. If this is not what you expect, please check your input.'
    os.chdir(currentDir)

from ROOT import TGraph
def extractRawLimits(input_file_path):
    tree = getObjFromFile(input_file_path, 'limit')
    limits = {}
    for entry in xrange(tree.GetEntries()):
        tree.GetEntry(entry)
        limits[tree.quantileExpected] = tree.limit
    return limits

def extractScaledLimitsPromptHNL(input_file_path, coupling):
    tree = getObjFromFile(input_file_path, 'limit')
    exclusion_coupling = {}
    try:
        for entry in xrange(tree.GetEntries()):
            tree.GetEntry(entry)
            exclusion_coupling[round(tree.quantileExpected, 3)] = tree.limit * coupling**2
        return exclusion_coupling
    except:
        return None

def makeGraphs(x_values, couplings, limits = None, input_paths = None):
    if limits is None and input_paths is None:
        raise RuntimeError('Invalid input: both "limits" and "input_paths" are None in CombineTools.makeGraphs')

    npoints = len(x_values)
    graphs = {
        'expected': TGraph(npoints),
        '1sigma': TGraph(npoints*2),
        '2sigma': TGraph(npoints*2)
    }

    if limits is None:
        limits = {}
        for i, (m, p) in enumerate(zip(x_values, input_paths)):
            limits[m] = extractScaledLimitsPromptHNL(p, couplings[i])

    for i, m in enumerate(x_values):
        graphs['2sigma'].SetPoint(i, m, limits[m][0.975])
        graphs['1sigma'].SetPoint(i, m, limits[m][0.84])
        graphs['expected'].SetPoint(i, m, limits[m][0.5])
        graphs['1sigma'].SetPoint(npoints*2-1-i, m, limits[m][0.16])
        graphs['2sigma'].SetPoint(npoints*2-1-i, m, limits[m][0.025])

    return [graphs['expected'], graphs['1sigma'], graphs['2sigma']]


if __name__ == '__main__':
    makeDataCard('testbin', 'tau', 2016, 20, 6, [20, 23, 12, 1], ['DY', 'WJets', 'tt', 'WZ'])
