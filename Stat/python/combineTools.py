#########################
# Tools to use Combine  #
#########################

#
# Imports 
#
import os
import glob
from HNL.Tools.helpers import makeDirIfNeeded, tab
import ROOT

#
# Information about Combine release
#
release        = 'CMSSW_10_2_13'
arch           = 'slc7_amd64_gcc700'
version        = 'v8.0.1'

#
# Information about displacement samples
#
displaced_mass_threshold = 20

coupling_dict = {'tau':'#tau', 'mu':'#mu', 'e':'e', '2l':'l'}


#
# Function to write out a data card, these data cards all contain 1 bin to be clear, readable and flexible
# and should be combined later on
#
from HNL.Samples.sample import Sample
def makeDataCard(bin_name, flavor, era, year, obs_yield, sig_name, bkgr_names, selection, region, final_state, nonprompt_from_sideband = True, sig_yield=None, bkgr_yields= None, shapes=False, is_test=False, majorana_str = 'Majorana', shapes_path = None):
    if not shapes and len(bkgr_yields) != len(bkgr_names):
        raise RuntimeError("length of background yields and names is inconsistent")

    from HNL.Samples.sample import Sample
    coupling_sq = Sample.getSignalCouplingSquared(sig_name)

    if not shapes:
        out_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'testArea' if is_test else '', 'dataCards', majorana_str, era+str(year), '-'.join([selection, region]), flavor, sig_name, 'cutAndCount',  bin_name+'.txt')
    else:
        out_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'testArea' if is_test else '', 'dataCards', majorana_str, era+str(year), '-'.join([selection, region]), flavor, sig_name, 'shapes', bin_name+'.txt')
    makeDirIfNeeded(out_name)
    out_file = open(out_name, 'w')

    out_file.write('# coupling squared = '+str(coupling_sq)+' \n \n')
    out_file.write('imax    1 number of bins \n')
    out_file.write('jmax    * number of processes\n')
    out_file.write('kmax    * \n')
    out_file.write('-'*400 + '\n')
    if shapes:
        if shapes_path is None:
            shapes_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'shapes', '-'.join([selection, region]), era+str(year), flavor, sig_name, majorana_str, bin_name+'.shapes.root')
        out_file.write('shapes * * \t' +shapes_path + ' $CHANNEL/$PROCESS $CHANNEL$SYSTEMATIC/$PROCESS \n')
    out_file.write('-'*400 + '\n')
    out_file.write('bin             '+bin_name.rsplit('-', 1)[0]+ ' \n')
    if shapes:
        out_file.write('observation     -1 \n')   
        # out_file.write('observation     '+str(obs_yield)+ ' \n') 
    else:
        out_file.write('observation     '+str(obs_yield)+ ' \n')
    out_file.write('-'*400 + '\n')
    out_file.write(tab(['bin', '']+ [bin_name.rsplit('-', 1)[0]]*(len(bkgr_names)+1)))
    out_file.write(tab(['process', '']+ bkgr_names + [sig_name], '50'))
    out_file.write(tab(['process', '']+ [str(i) for i in xrange(1, len(bkgr_names)+1)] + ['0']))
    if shapes:
        out_file.write(tab(['rate', '']+ ['-1']*(len(bkgr_names)+1)))
    else:
        out_file.write(tab(['rate', '']+ ['%4.6f' % by if by >= 0 else 0.0 for by in bkgr_yields] + ['%4.6f' % sig_yield]))
    out_file.write('-'*400 + '\n')

    from HNL.Systematics.systematics import insertSystematics
    insertSystematics(out_file, bkgr_names, sig_name, year, final_state, datadriven_processes = ['non-prompt'] if nonprompt_from_sideband else None)


    #autoMCstats
    if shapes:
        out_file.write('* autoMCStats 3 1 1')


    out_file.close()

def runCombineCommand(command, output = None):
    currentDir = os.getcwd()
    current_release = os.path.expandvars('$CMSSW_BASE')
    combine_release = os.path.expandvars('$CMSSW_BASE')+'/../'+release
    os.system('rm ' + combine_release +'/src/*root &> /dev/null') 
    os.chdir(combine_release+'/src')
    output_folder = output if output is not None else currentDir
    os.system('eval `scramv1 runtime -sh`; cd {0}; {1}'.format(output_folder, command))
    os.chdir(currentDir)

from ROOT import TGraph
def extractRawLimits(input_file_path):
    in_file = ROOT.TFile(input_file_path, 'read')
    tree = in_file.Get('limit')
    limits = {}
    try:
        if tree.GetEntries() < 5:
            limits = None
        for entry in xrange(tree.GetEntries()):
            tree.GetEntry(entry)
            limits[round(tree.quantileExpected, 3)] = tree.limit
        in_file.Close()
    except:
        limits = None
    return limits

def extractRawLimitsRange(in_file_paths, x_values):
    if len(in_file_paths) != len(x_values):
        raise RuntimeError("Size of in_file_paths and x_values is not the same")

    limits = {}
    for x, p in zip(x_values, in_file_paths):
        limits[x] = extractRawLimits(p)
    return limits

def extractScaledLimitsPromptHNL(input_file_path, coupling):
    in_file = ROOT.TFile(input_file_path, 'read')
    tree = in_file.Get('limit')
    exclusion_coupling = {}
    try:
        for entry in xrange(tree.GetEntries()):
            tree.GetEntry(entry)
            exclusion_coupling[round(tree.quantileExpected, 3)] = tree.limit * coupling
        in_file.Close()
        return exclusion_coupling
    except:
        in_file.Close()
        return None

def linearExtrapolationX(x1, x2, y1, y2, target_y = 1.):
    return (((target_y-y1) / (y2-y1)) * (x2-x1)) + x1

def inverseExtrapolationY(x1, y1, x):
    return (x1*y1)/x

def extrapolateExclusionLimit(limits, quantile):
    x_values = sorted(limits.keys())
    x_values = [x for x in x_values if limits[x] is not None]

    limit_candidates = []
    last_val = None
    for ix, x in enumerate(x_values):
        new_val = limits[x][quantile]
        if last_val is None:    
            last_val = new_val
        elif x != x_values[-1]:
            if last_val < 1. and new_val > 1.:
                limit_candidates.append(x_values[ix-1])
                last_val = new_val
            if last_val > 1. and new_val < 1.:
                limit_candidates.append(x_values[ix-1])
                last_val = new_val
        else:
            last_val = new_val
            continue
    
    if len(limit_candidates) == 0:
        print 'Found no suitable coupling point, please extend range'
        return None
    if len(limit_candidates) > 1:
        print 'Multiple coupling points found, please investigate'
        return None

    x1 = limit_candidates[0]
    x2 = x_values[limit_candidates.index(x1)+1]
    y1 = limits[x1][quantile]
    y2 = limits[x2][quantile]
    return linearExtrapolationX(x1, x2, y1, y2) 

def extractScaledLimitsDisplacedHNL(input_file_paths, couplings):
    limits = extractRawLimitsRange(input_file_paths, couplings)

    #Gather all points in between which the coupling strength crosses one
    out_limits = {}
    out_limits[0.5] = extrapolateExclusionLimit(limits, 0.5)
    out_limits[0.16] = extrapolateExclusionLimit(limits, 0.16)
    out_limits[0.84] = extrapolateExclusionLimit(limits, 0.84)
    out_limits[0.025] = extrapolateExclusionLimit(limits, 0.025)
    out_limits[0.975] = extrapolateExclusionLimit(limits, 0.975)
    return out_limits    

def makeGraphs(x_values, limits):
    passed_masses = x_values
    npoints = len(passed_masses)

    graphs = {
        'expected': TGraph(npoints),
        '1sigma': TGraph(npoints*2),
        '2sigma': TGraph(npoints*2)
    }


    for i, m in enumerate(passed_masses):
        try:
            graphs['2sigma'].SetPoint(i, m, limits[m][0.975])
            graphs['1sigma'].SetPoint(i, m, limits[m][0.84])
            graphs['expected'].SetPoint(i, m, limits[m][0.5])
            graphs['1sigma'].SetPoint(npoints*2-1-i, m, limits[m][0.16])
            graphs['2sigma'].SetPoint(npoints*2-1-i, m, limits[m][0.025])
        except:
            pass

    return [graphs['expected'], graphs['1sigma'], graphs['2sigma']]

def saveGraphs(graphs, outpath):
    makeDirIfNeeded(outpath)
    out_file = ROOT.TFile(outpath, 'recreate')
    graphs[0].Write('expected_central')
    graphs[1].Write('expected_1sigma')
    graphs[2].Write('expected_2sigma')
    out_file.Close()

def drawSignalStrengthPerCouplingDisplaced(input_file_paths, couplings, out_path, out_name, year, flavor):
    limits = extractRawLimitsRange(input_file_paths, couplings)

    cleaned_couplings = [c for c in couplings if limits[c] is not None]
    
    graphs = makeGraphs(cleaned_couplings, limits)
    from HNL.Plotting.plot import Plot
    p = Plot(graphs, name=out_name, y_log = True, x_log=True, x_name = '|V_{'+coupling_dict[flavor]+' N}|^{2}', y_name = 'Signal Strength', era = 'UL', year = year)
    p.drawBrazilian(output_dir = out_path)
   
def drawSignalStrengthPerCouplingPrompt(input_file_path, coupling, out_path, out_name, year, flavor):
    limits = {}
    limits[coupling] = extractRawLimits(input_file_path)
    for probe_coupling in [0.01*coupling, 0.05*coupling, 0.1*coupling, 0.5*coupling, 5*coupling, 10*coupling, 50*coupling, 100*coupling]:
        limits[probe_coupling] = {}
        for quantile in [0.025, 0.16, 0.5, 0.84, 0.975]:
            limits[probe_coupling][quantile] = inverseExtrapolationY(coupling, limits[coupling][quantile], probe_coupling) 

    sorted_couplings = sorted(limits.keys())
    graphs = makeGraphs(sorted_couplings, limits)
    from HNL.Plotting.plot import Plot
    p = Plot(graphs, name=out_name, y_log = True, x_log=True, x_name = '|V_{'+coupling_dict[flavor]+' N}|^{2}', y_name = 'Signal Strength', era = 'UL', year = year)
    p.drawBrazilian(output_dir = out_path)
 

if __name__ == '__main__':
    makeDataCard('testbin', 'tau', 2016, 20, 6, [20, 23, 12, 1], ['DY', 'WJets', 'tt', 'WZ'])
