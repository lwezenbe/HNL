import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--year',     action='store',       default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'tZq', 'TTT', 'HNLtauTest'])
submission_parser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino', 'tZq'])
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?')
submission_parser.add_argument('--systematics', action='store', nargs='*', default='JEC', type=str,  help='What region do you want to select for?')
submission_parser.add_argument('--signal', action='store', default=None, type=str,  help='What region do you want to select for?')
submission_parser.add_argument('--categories', action='store', nargs='*', default=None, type=str,  help='What categories do you want to select for?')
submission_parser.add_argument('--searchregions', action='store', nargs='*', default=None, type=str,  help='What search regions do you want to select for?')
submission_parser.add_argument('--methods', action='store', nargs='*', default=None, type=str,  help='What shape methods do you want to select for?')
submission_parser.add_argument('--oneplot', action='store_true', default=False,  help='What shape methods do you want to select for?')
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
    
    def __init__(self, path_to_shapes, systematic, sample_names, integral = False):
        self.path_to_shapes     = path_to_shapes
        self.systematic         = systematic
        self.sample_names       = sample_names
        self.integral           = integral

        shapes_name              = self.path_to_shapes.split('/')[-1].split('.')[0]
        self.category, self.x_name = shapes_name.rsplit('-', 1)
        if self.x_name != 'searchregion':     self.x_name = 'BDT output score'
    
        self.loadShapes()
        try:
            self.normalized_up      = self.up.Clone('Up')
            self.normalized_up.Divide(self.nominal) 
        except:
            self.normalized_up = None
            
        try:
            self.normalized_down    = self.down.Clone('Down')
            self.normalized_down.Divide(self.nominal) 
        except:
            self.normalized_down = None

        self.getStatHist()

    def loadShapes(self):
        from HNL.Tools.helpers import getObjFromFile
        self.nominal    = None
        self.up         = None
        self.down       = None
        for isample, sample in enumerate(self.sample_names):
            tmp_nominal    = getObjFromFile(self.path_to_shapes, self.category+'/'+sample)
            tmp_up         = getObjFromFile(self.path_to_shapes, self.category+self.systematic+'Up/'+sample)
            tmp_down       = getObjFromFile(self.path_to_shapes, self.category+self.systematic+'Down/'+sample)
            
            if tmp_nominal is not None:     
                if self.nominal is not None: 
                    self.nominal.Add(getObjFromFile(self.path_to_shapes, self.category+'/'+sample))
                else:
                    self.nominal = tmp_nominal.Clone()
            if tmp_up is not None:    
                if self.up is not None:      
                    self.up.Add(getObjFromFile(self.path_to_shapes, self.category+self.systematic+'Up/'+sample))
                else:
                    self.up = tmp_up.Clone()
            if tmp_down is not None:
                if self.down is not None:        
                    self.down.Add(getObjFromFile(self.path_to_shapes, self.category+self.systematic+'Down/'+sample))
                else:
                    self.down = tmp_down.Clone()

        if self.integral:
            from HNL.Tools.helpers import contractAllBins
            if self.nominal is not None:
                self.nominal = contractAllBins(self.nominal)
            if self.up is not None:
                self.up = contractAllBins(self.up)
            if self.down is not None:
                self.down = contractAllBins(self.down)

    def getStatHist(self):
        if self.nominal is None:
            self.stat_hist = None
        else:
             self.stat_hist          = self.nominal.Clone('Stat')
             for b in xrange(1, self.stat_hist.GetNbinsX()+1):
                 self.stat_hist.SetBinError(b, self.stat_hist.GetBinError(b)/self.stat_hist.GetBinContent(b))
                 self.stat_hist.SetBinContent(b, 1.)

#
# Function to plot the shapes and their ratio
#
def plotSystematic(syst_shapes, out_path, name_args = None, min_cutoff = None, max_cutoff = None):
    from HNL.Plotting.plot import Plot
    from HNL.Plotting.plottingTools import extraTextFormat
    extra_text = [extraTextFormat('Total Background')]
    extra_text.append(extraTextFormat(syst_shapes.systematic))
    from HNL.EventSelection.eventCategorization import ANALYSIS_CATEGORIES_TEX
    extra_text.append(extraTextFormat(ANALYSIS_CATEGORIES_TEX[syst_shapes.category.split('-', 1)[1]]))              #final states
  
    base_name = syst_shapes.systematic 
    if name_args is not None:
        base_name += '-'.join(name_args)

    if syst_shapes.nominal is None or syst_shapes.up is None or syst_shapes.down is None:
        return
 
    #Shapes themselves
    p = Plot(signal_hist = [syst_shapes.nominal], bkgr_hist = [syst_shapes.up, syst_shapes.down], tex_names = ['nominal', 'up', 'down'], name=base_name+"-Yields", x_name = syst_shapes.x_name, y_name = 'Events',
            extra_text = extra_text, year = args.year, era = args.era, color_palette='Syst')
    p.setLegend(x1=0.5)
    p.drawHist(out_path, bkgr_draw_option = 'Hist')

    #Normalized hist
    p = Plot(signal_hist = [syst_shapes.normalized_up, syst_shapes.normalized_down], bkgr_hist = syst_shapes.stat_hist, tex_names = ['up', 'down'], name=base_name+"-normalized", x_name = syst_shapes.x_name, y_name = 'Events', extra_text = extra_text, year = args.year, era = args.era, color_palette='Syst')
    p.setLegend(x1=0.5)
    p.drawHist(out_path, draw_option = 'Hist', bkgr_draw_option ='Hist', error_option = None, bkgr_error_option = 'E2', min_cutoff = min_cutoff, max_cutoff=max_cutoff)
    
    
#
# Function to plot the shapes and their ratio
#
def plotMultipleSystematic(syst_shapes, out_path, name_args = None, min_cutoff = None, max_cutoff = None):
    syst = syst_shapes.keys()
    from HNL.Plotting.plot import Plot
    from HNL.Plotting.plottingTools import extraTextFormat
    extra_text = [extraTextFormat('Total Background')]
    extra_text.append(extraTextFormat(syst_shapes[syst[0]].systematic))
    from HNL.EventSelection.eventCategorization import ANALYSIS_CATEGORIES_TEX
    extra_text.append(extraTextFormat(ANALYSIS_CATEGORIES_TEX[syst_shapes[syst[0]].category.split('-', 1)[1]]))              #final states
  
    base_name = 'shapes' 
    if name_args is not None:
        base_name += '-'+'-'.join(name_args)

    if syst_shapes[syst[0]].nominal is None: return

    #Shapes themselves
    bkgr_hist = []
    tex_names = ['nominal']
    for s in syst:
        if syst_shapes[s].up is None or syst_shapes[s].down is None: continue
        bkgr_hist.extend([syst_shapes[s].up, syst_shapes[s].down])
        tex_names.extend([s+'_up', s+'_down'])
    
    p = Plot(signal_hist = [syst_shapes[syst[0]].nominal], bkgr_hist = bkgr_hist, tex_names = tex_names, name=base_name+"-Yields", x_name = syst_shapes[syst[0]].x_name, y_name = 'Events',
            extra_text = extra_text, year = args.year, era = args.era, color_palette='StackTauPOG')
    p.setLegend(x1=0.5, textsize=0.01)
    p.drawHist(out_path, bkgr_draw_option = 'Hist')

    #Normalized hist
    bkgr_hist = []
    tex_names = []
    for s in syst:
        if syst_shapes[s].up is None or syst_shapes[s].down is None: continue
        bkgr_hist.extend([syst_shapes[s].normalized_up, syst_shapes[s].normalized_down])
        tex_names.extend([s+'_up', s+'_down'])
    p = Plot(signal_hist = bkgr_hist, bkgr_hist = syst_shapes[syst[0]].stat_hist, tex_names = tex_names, name=base_name+"-normalized", x_name = syst_shapes[syst[0]].x_name, y_name = 'Events', extra_text = extra_text, year = args.year, era = args.era, color_palette='StackTauPOG')
    p.setLegend(x1=0.5, textsize=0.015)
    p.drawHist(out_path, draw_option = 'Hist', bkgr_draw_option ='Hist', error_option = None, bkgr_error_option = 'E2', min_cutoff = min_cutoff, max_cutoff=max_cutoff)
    
#
# Actually start the code
#
import os
flavor = args.signal.split('-')[1]
for cat in args.categories:
    for sr in args.searchregions:
        for im, m in enumerate(args.methods):
            syst_shapes = {}
            for isyst, syst in enumerate(args.systematics):
                path_to_shapes = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Stat', 'data', 'shapes', args.selection+'-'+args.region, args.era+args.year, flavor, args.signal, 'Majorana', '-'.join([sr, cat, m])+'.shapes.root'))
                print cat, sr, m, syst
                syst_shapes[syst] = SystShape(path_to_shapes, syst, [x for x in sm.sample_outputs if not 'HNL' in x and not 'Data' in x])
    
                if not args.oneplot:
                    out_path = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Stat', 'data', 'Results', 'shapeStudy', args.selection+'-'+args.region, args.era+args.year, flavor, args.signal, syst))
                    plotSystematic(syst_shapes[syst], out_path, name_args=[sr, cat, m])

            if args.oneplot:
                out_path = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Stat', 'data', 'Results', 'shapeStudy', args.selection+'-'+args.region, args.era+args.year, flavor, args.signal, '-'.join(syst_shapes.keys())))
                plotMultipleSystematic(syst_shapes, out_path, name_args=[sr, cat, m])

                #Total yield version as well
            if im == len(args.methods)-1:
                for isyst, syst in enumerate(args.systematics):
                    path_to_shapes = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Stat', 'data', 'shapes', args.selection+'-'+args.region, args.era+args.year, flavor, args.signal, 'Majorana', '-'.join([sr, cat, m])+'.shapes.root'))
                    print cat, sr, 'SingleBin', syst
                    syst_shapes[syst] = SystShape(path_to_shapes, syst, [x for x in sm.sample_outputs if not 'HNL' in x and not 'Data' in x], integral=True)
        
                    if not args.oneplot:
                        out_path = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Stat', 'data', 'Results', 'shapeStudy', args.selection+'-'+args.region, args.era+args.year, flavor, args.signal, syst))
                        plotSystematic(syst_shapes[syst], out_path, name_args=[sr, cat, 'SingleBin'])
    
                if args.oneplot:
                    out_path = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Stat', 'data', 'Results', 'shapeStudy', args.selection+'-'+args.region, args.era+args.year, flavor, args.signal, '-'.join(syst_shapes.keys())))
                    plotMultipleSystematic(syst_shapes, out_path, name_args=[sr, cat, 'SingleBin'], min_cutoff=0.98, max_cutoff = 1.02)

