#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
argParser.add_argument('--isTest',     action='store_true',      default=False,   help='Is this a test?')
argParser.add_argument('--flavor', action='store', default=None,  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l'])
args = argParser.parse_args()

if args.isTest:
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')
    if args.year is None: args.year = '2016'
    if args.flavor is None: args.flavor = 'tau'

#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
sample_manager = SampleManager(args.year, 'noskim', 'allsignal_'+str(args.year))
print sample_manager.sample_names


#
# Calculate the range for the histograms. These are as a function of the mass of the signal samples.
# This function looks at the names of all samples and returns an array with all values right the middle of those
# It assumes the samples are ordered by mass in the input list
#
from HNL.Tools.helpers import getMassRange
from HNL.Tools.histogram import Histogram

mass_range = getMassRange([sample_name for sample_name in sample_manager.sample_names if '-'+args.flavor+'-' in sample_name])

#
# Define the variables and axis name of the variable to fill and create efficiency objects
#
import numpy as np
var = {'HNLmass': (lambda c : c.HNLmass,        np.array(mass_range),   ('m_{N} [GeV]', 'Cross Section (pb)'))}

hist = Histogram('xsec', var['HNLmass'][0], var['HNLmass'][2], var['HNLmass'][1])

for sample in sample_manager.sample_list:
    if sample.name not in sample_manager.sample_names: continue
    if '-'+args.flavor+'-' not in sample.name: continue
    #
    # Load in sample and chain
    #
    chain = sample.initTree()

    chain.HNLmass = sample.getMass()
    chain.year = int(args.year)
    hist.fill(chain, sample.xsec)

from HNL.Plotting.plot import Plot
p = Plot([hist], sample.output, y_log=True)
p.drawHist(output_dir = os.path.expandvars('$CMSSW_BASE/src/HNL/Test/data/plotCrossSection'), draw_option="Hist")

if args.isTest:
    closeLogger(log)

