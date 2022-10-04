import os

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--year',     action='store',       default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--sample',   action='store',            default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'tZq', 'TTT', ])
submission_parser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino', 'tZq'])
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?')
submission_parser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
submission_parser.add_argument('--systematics',  action='store',      default='nominal',               help='Choose level of systematics.', choices = ['nominal', 'limited', 'full'])
submission_parser.add_argument('--firstrun',  action='store_true',      default='False',               help='Something to make sure we dont overwrite the backup.')

args = argParser.parse_args()

year = args.year

def getSampleManager(y):
    from HNL.Samples.sampleManager import SampleManager
    skim_str = 'Reco'
    file_list = 'fulllist_'+args.era+str(y) if args.customList is None else args.customList

    sm = SampleManager(args.era, y, skim_str, file_list, skim_selection=args.selection, region=args.region)
    return sm


def getOutputName(st, y):
    return os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'runAnalysis', args.analysis, '-'.join([args.strategy, args.selection, args.region, 'reco']), args.era+'-'+y, st)

def getSystToRun(year, proc):
    from HNL.Systematics.systematics import SystematicJSONreader
    sjr = SystematicJSONreader(datadriven_processes = ['non-prompt'])
    syst_to_run = ['nominal']
    if args.systematics == 'full': syst_to_run += sjr.getReruns(year, proc, split_syst=True)
    return syst_to_run

def makeBranches(branches):
    from HNL.Tools.makeBranches import cType
    branches = [tuple(branch.split('/')) for branch in branches] 

    from ROOT import gROOT
    gROOT.ProcessLine('struct newVars {' + ';'.join([cType[t] + ' ' + name for name, t in branches]) + ';};')
    
    from ROOT import newVars
    newVars = newVars()
    return newVars

sample_manager = getSampleManager(year)
sample = sample_manager.getSample(args.sample)

original_chain = sample.initTree()
original_chain.GetEntry(5)
original_chain.year = year
original_chain.era = args.era
original_weight = original_chain._weight

syst_to_run = getSystToRun(year, sample.output)

from HNL.Tools.outputTree import OutputTree
from ROOT import TFile, AddressOf, addressof
from HNL.Tools.helpers import getObjFromFile, progress, makeDirIfNeeded

from HNL.Weights.lumiweight import LumiWeight
from HNL.Systematics.systematics import SystematicJSONreader

sjr = SystematicJSONreader(['non-prompt'])

out_file_path = os.path.join(getOutputName('bkgr', year), sample.output, 'variables-{0}-v2.root'.format(args.sample))
out_file = TFile(out_file_path, 'recreate')
original_path = os.path.join(getOutputName('bkgr', year), sample.output, 'variables-{0}.root'.format(args.sample))

branches_to_change = ['lumiWeight/F', 'weight/F']
for x in sjr.getWeights(year, sample.output, split_syst = True):
    branches_to_change.append(x+'/F')
new_vars = makeBranches(branches_to_change)

lw = LumiWeight(sample, sample_manager)
for isyst, syst in enumerate(syst_to_run):
    print 'running', syst
    in_tree = OutputTree('events_{0}'.format(syst), original_path)    

    out_file.cd()
    out_tree = in_tree.tree.CloneTree(0)
    out_tree.SetBranchAddress('lumiWeight', AddressOf(new_vars, 'lumiWeight'))
    out_tree.SetBranchAddress('weight', AddressOf(new_vars, 'weight'))
    out_tree.SetBranchAddress('btagWeight_lightcorrelatedUp', AddressOf(new_vars, 'btagWeight_lightcorrelatedUp'))
    for x in sjr.getWeights(year, sample.output, split_syst = True):
        out_tree.SetBranchAddress(str(x), AddressOf(new_vars, str(x)))

    for entry in xrange(in_tree.tree.GetEntries()):
        progress(entry, in_tree.tree.GetEntries())
        in_tree.tree.GetEntry(entry)
        in_tree.tree.original_weight = original_weight
        new_lumi_weight = lw.getLumiWeight(in_tree.tree)
        ratio = new_lumi_weight/in_tree.tree.lumiWeight

        new_vars.lumiWeight = new_lumi_weight
        new_vars.weight = in_tree.tree.weight*ratio
        for x in sjr.getWeights(year, sample.output, split_syst = True):
            setattr(new_vars, x, getattr(in_tree.tree, x)*ratio)
    
        #print in_tree.tree.weight, new_vars.weight    
        out_tree.Fill()
        #print out_tree.weight 
    out_tree.Write()

out_file.Close()

if args.firstrun:
    backup_path = original_path.rsplit('/', 1)[0]+'/backup/'+ original_path.rsplit('/', 1)[1]
    makeDirIfNeeded(backup_path)
    os.system('mv '+original_path+' '+backup_path)
    os.system('mv '+out_file_path+' '+original_path)
