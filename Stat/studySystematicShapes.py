import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--year',     action='store',       default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'tZq', 'TTT', 'HNLtauTest'])
submission_parser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino', 'tZq'])
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?')
submission_parser.add_argument('--systematic', action='store', default='JEC', type=str,  help='What region do you want to select for?')
submission_parser.add_argument('--signal', action='store', default='JEC', type=str,  help='What region do you want to select for?')
submission_parser.add_argument('--shapes_file', action='store', default=None, type=str,  help='What region do you want to select for?')
args = argParser.parse_args()

#
# Load in sample list
#
from HNL.Samples.sampleManager import SampleManager
sm = SampleManager(args.era, args.year, 'Reco', 'fulllist_{0}{1}'.format(args.era, args.year), skim_selection=args.selection, region=args.region)

#
# Systematic bookkeeping
#
class SystShape:
    
    def __init__(self, path_to_shapes, systematic, sample_names):
        print path_to_shapes
        self.path_to_shapes     = path_to_shapes
        self.systematic         = systematic
        self.sample_names       = sample_names

        shapes_name              = self.path_to_shapes.split('/')[-1].split('.')[0]
        self.category, self.x_name = shapes_name.rsplit('-', 1)
        if self.x_name != 'searchregion':     self.x_name = 'BDT output score'
    
        self.loadShapes()
        self.normalized_up      = self.up.Clone('Up')
        self.normalized_up.Divide(self.nominal) 
        self.normalized_down    = self.down.Clone('Down')
        self.normalized_down.Divide(self.nominal) 

        self.getStatHist()


    def loadShapes(self):
        from HNL.Tools.helpers import getObjFromFile
        for isample, sample in enumerate(self.sample_names):
            print sample
            if isample == 0:
                self.nominal    = getObjFromFile(path_to_shapes, self.category+'/'+sample)
                self.up         = getObjFromFile(path_to_shapes, self.category+self.systematic+'Up/'+sample)
                self.down       = getObjFromFile(path_to_shapes, self.category+self.systematic+'Down/'+sample)
            else:
                self.nominal.Add(getObjFromFile(path_to_shapes, self.category+'/'+sample))
                self.up.Add(getObjFromFile(path_to_shapes, self.category+self.systematic+'Up/'+sample))
                self.down.Add(getObjFromFile(path_to_shapes, self.category+self.systematic+'Down/'+sample))


    def getStatHist(self):
        self.stat_hist          = self.nominal.Clone('Stat')
        for b in xrange(1, self.stat_hist.GetNbinsX()+1):
            self.stat_hist.SetBinError(b, self.stat_hist.GetBinError(b)/self.stat_hist.GetBinContent(b))
            self.stat_hist.SetBinContent(b, 1.)

#
# Function to plot the shapes and their ratio
#
def plotSystematic(syst_shapes, out_path):
    from HNL.Plotting.plot import Plot
    from HNL.Plotting.plottingTools import extraTextFormat
    extra_text = [extraTextFormat('Total Background')]
    extra_text.append(extraTextFormat(syst_shapes.systematic))
    from HNL.EventSelection.eventCategorization import ANALYSIS_CATEGORIES_TEX
    extra_text.append(extraTextFormat(ANALYSIS_CATEGORIES_TEX[syst_shapes.category.split('-', 1)[1]]))              #final states
    
    #Shapes themselves
    p = Plot(signal_hist = [syst_shapes.nominal], bkgr_hist = [syst_shapes.up, syst_shapes.down], tex_names = ['nominal', 'up', 'down'], name=syst_shapes.systematic+"-Yields", x_name = syst_shapes.x_name, y_name = 'Events',
            extra_text = extra_text, year = args.year, era = args.era, color_palette='Syst')
    p.setLegend(x1=0.5)
    p.drawHist(out_path, bkgr_draw_option = 'Hist')

    #Normalized hist
    p = Plot(signal_hist = [syst_shapes.normalized_up, syst_shapes.normalized_down], bkgr_hist = syst_shapes.stat_hist, tex_names = ['up', 'down'], name=syst_shapes.systematic+"-normalized", x_name = syst_shapes.x_name, y_name = 'Events', extra_text = extra_text, year = args.year, era = args.era, color_palette='Syst')
    p.setLegend(x1=0.5)
    p.drawHist(out_path, draw_option = 'Hist', bkgr_draw_option ='Hist', error_option = None, bkgr_error_option = 'E2')
    
    
    
#
# Actually start the code
#
import os
flavor = args.signal.split('-')[1]
path_to_shapes = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Stat', 'data', 'shapes', args.selection+'-'+args.region, args.era+args.year, flavor, args.signal, args.shapes_file+'.shapes.root'))
syst_shapes = SystShape(path_to_shapes, args.systematic, [x for x in sm.sample_outputs if not 'HNL' in x and not 'Data' in x])
out_path = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Stat', 'data', 'Results', 'shapeStudy', args.selection+'-'+args.region, args.era+args.year, flavor, args.signal))
plotSystematic(syst_shapes, out_path)
