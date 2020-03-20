#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
argParser.add_argument('--isTest',     action='store_true',      default=False,   help='Is this a test?')
args = argParser.parse_args()

if args.isTest:
    args.year = '2016'

#
# Load in the sample list 
#
from HNL.Samples.sample import createSampleList, getSampleFromList
list_location = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/signallist_'+str(args.year)+'.conf')
sample_list = createSampleList(list_location)

#
# Calculate the range for the histograms. These are as a function of the mass of the signal samples.
# This function looks at the names of all samples and returns an array with all values right the middle of those
# It assumes the samples are ordered by mass in the input list
#
from HNL.Tools.helpers import getMassRange
from HNL.Tools.histogram import Histogram

mass_range = getMassRange(list_location)

#
# Define the variables and axis name of the variable to fill and create efficiency objects
#
import numpy as np
var = {'HNLmass': (lambda c : c.HNLmass,        np.array(mass_range),   ('m_{N} [GeV]', 'Cross Section (pb)'))}

hist = Histogram('xsec', var['HNLmass'][0], var['HNLmass'][2], var['HNLmass'][1])

for sample in sample_list:
    #
    # Load in sample and chain
    #
    chain = sample.initTree()

    chain.HNLmass = float(sample.name.rsplit('-', 1)[1])
    chain.year = int(args.year)
    hist.fill(chain, sample.xsec)

from HNL.Plotting.plot import Plot
p = Plot([hist], sample.output, y_log=True)
p.drawHist(output_dir = os.path.expandvars('$CMSSW_BASE/src/HNL/Test/data/plotCrossSection'), draw_option="Hist")
