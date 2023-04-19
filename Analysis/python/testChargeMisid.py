from ROOT import gROOT
gROOT.SetBatch(True)
import glob
import os
from HNL.Analysis.analysisTypes import signal_couplingsquared
from HNL.Tools.helpers import getHistFromTree, makePathTimeStamped

era = 'UL'
year = '2018'
tag = 'nonpromptChargeMisidCheck'
region = 'highMassSR'
analysis = 'HNL'
selection = 'default'
strategy = 'MVA'
categoriesToPlot = 'analysis'

bkgr_list = {}
background_collection = {}

def getOutputName(st, y, tag=None):
    translated_tag = '' if tag is None else '-'+tag
    return os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'runAnalysis', analysis+translated_tag, '-'.join([strategy, selection, region, 'reco']), era+'-'+y, st)

def getSampleManager(y):
    skim_str = 'Reco'
    
    file_list = 'fulllist_'+era+str(y) 

    from HNL.Samples.sampleManager import SampleManager
    sm = SampleManager(era, y, skim_str, file_list, skim_selection=selection, region=region)
    return sm

sample_manager = getSampleManager(year)

bkgr_list = [getOutputName('bkgr', year, tag)+'/'+b for b in sample_manager.sample_outputs if os.path.isdir(getOutputName('bkgr', year, tag)+'/'+b)]

# Merge files if necessary
background_collection = []
for x in sample_manager.sample_outputs:
    if 'HNL' in x: continue
    if 'Data' in x: continue
    if not os.path.isdir(getOutputName('bkgr', year, tag)+'/'+x): continue
    background_collection.append(x)

background_collection += ['non-prompt', 'non-prompt-chargemisid', 'charge-misid']

from HNL.Analysis.analysisTypes import getBinning
bins = lambda c, v: getBinning(v, region, var_dict[v][1])

from HNL.Tools.outputTree import OutputTree
from HNL.EventSelection.eventCategorization import isLightLeptonFinalState

#Reset list_of_hist
import HNL.EventSelection.eventCategorization as cat
sorted_analysis_categories = cat.ANALYSIS_CATEGORIES.keys()
sorted_splitanalysis_categories = cat.ANALYSIS_SPLITOSSF_CATEGORIES.keys()
sorted_leadingflavor_categories = cat.LEADING_FLAVOR_CATEGORIES.keys()
sorted_trigger_categories = cat.TRIGGER_CATEGORIES.keys()
from HNL.Analysis.analysisTypes import getRelevantSuperCategories
sorted_super_categories = getRelevantSuperCategories(cat.SUPER_CATEGORIES.keys(), region)

category_dict = {}
if categoriesToPlot == 'analysis':
    category_dict['analysis'] = (sorted_analysis_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.ANALYSIS_CATEGORIES[y]])+')' for y in sorted_analysis_categories], {y :[str(x) for x in cat.ANALYSIS_CATEGORIES[y]] for y in sorted_analysis_categories})
if categoriesToPlot == 'splitanalysis':
    category_dict['splitanalysis'] = (sorted_splitanalysis_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.ANALYSIS_SPLITOSSF_CATEGORIES[y]])+')' for y in sorted_splitanalysis_categories], {y :[str(x) for x in cat.ANALYSIS_SPLITOSSF_CATEGORIES[y]] for y in sorted_splitanalysis_categories})
if categoriesToPlot == 'leadingflavor':
    category_dict['leadingflavor'] = (sorted_leadingflavor_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.LEADING_FLAVOR_CATEGORIES[y]])+')' for y in sorted_leadingflavor_categories], {y :[str(x) for x in cat.LEADING_FLAVOR_CATEGORIES[y]] for y in sorted_leadingflavor_categories})
if categoriesToPlot == 'super':
    category_dict['super'] = (sorted_super_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.SUPER_CATEGORIES[y]])+')' for y in sorted_super_categories], {y:[str(x) for x in cat.SUPER_CATEGORIES[y]] for y in sorted_super_categories})
if categoriesToPlot == 'trigger':
    category_dict['trigger'] = (sorted_trigger_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.TRIGGER_CATEGORIES[y]])+')' for y in sorted_trigger_categories], {y:[str(x) for x in cat.TRIGGER_CATEGORIES[y]] for y in sorted_trigger_categories})
category_dict['original'] = ([x for x in cat.CATEGORIES], ['(category=={0})'.format(x) for x in cat.CATEGORIES], {y : [str(y)] for y in cat.CATEGORIES})

import HNL.Analysis.analysisTypes as at
nl = 3 if region != 'ZZCR' else 4
var_dict = at.returnVariables(nl, True, region)


categories_to_use = category_dict[categoriesToPlot][0]
category_conditions = category_dict[categoriesToPlot][1]
print "Preparing the hist list"
list_of_hist = {}
for c in categories_to_use:
    list_of_hist[c] = {}
    for v in var_dict:
        list_of_hist[c][v] = {'bkgr':{}}

print "Loading background histograms"
#for ib, b in enumerate(background_collection):
#    for c, cc in zip(categories_to_use, category_conditions):
#        for iv, v in enumerate(var_dict.keys()): 
#            list_of_hist[c][v]['bkgr'][b]

#searchregion_condition = ""
searchregion_condition = '('+'||'.join(['searchregion == {0}'.format(x) for x in range(17,26)])+')'
#print searchregion_condition

from HNL.Tools.histogram import Histogram
from HNL.Tools.helpers import getObjFromFile, progress, makeDirIfNeeded
for ib, b in enumerate(background_collection):
    progress(ib, len(background_collection))

    if b in ['non-prompt', 'non-prompt-chargemisid', 'charge-misid']: continue
    intree = OutputTree('events_{0}'.format('nominal'), getOutputName('bkgr', year, tag)+'/'+b+'/variables.root')                 
    for c, cc in zip(categories_to_use, category_conditions):
        for iv, v in enumerate(var_dict.keys()):
            #print '('+cc+'&&!isChargeFlipEvent&&isprompt&&!issideband&&'+searchregion_condition+')' 
            list_of_hist[c][v]['bkgr'][b] = Histogram(intree.getHistFromTree(v, 'tmp_'+b+v+str(c)+'p', bins(c, v), '('+cc+'&&!isChargeFlipEvent&&isprompt&&!issideband&&'+searchregion_condition+')', weight='weight'))
            
            #charge
            tmp_hist = Histogram(intree.getHistFromTree(v, 'tmp_'+b+'-chargemisid'+v+str(c)+'p', bins(c, v), '('+cc+'&&isChargeFlipEvent&&isprompt&&!issideband&&'+searchregion_condition+')', weight='weight'))
            if 'charge-misid' not in list_of_hist[c][v]['bkgr'].keys():
                list_of_hist[c][v]['bkgr']['charge-misid'] = tmp_hist
            else:
                list_of_hist[c][v]['bkgr']['charge-misid'].add(tmp_hist)
            del(tmp_hist)
            
            #nonprompt
            tmp_hist = Histogram(intree.getHistFromTree(v, 'tmp_'+b+v+str(c)+'np', bins(c, v), '('+cc+'&&!isChargeFlipEvent&&!isprompt&&!issideband&&'+searchregion_condition+')', weight='weight'))
            if 'non-prompt' not in list_of_hist[c][v]['bkgr'].keys():
                list_of_hist[c][v]['bkgr']['non-prompt'] = tmp_hist
            else:
                list_of_hist[c][v]['bkgr']['non-prompt'].add(tmp_hist)
            del(tmp_hist)
            
            #nonprompt charge misid
            tmp_hist = Histogram(intree.getHistFromTree(v, 'tmp_'+b+v+str(c)+'np-chargemisid', bins(c, v), '('+cc+'&&isChargeFlipEvent&&!isprompt&&!issideband&&'+searchregion_condition+')', weight='weight'))
            if 'non-prompt-chargemisid' not in list_of_hist[c][v]['bkgr'].keys():
                list_of_hist[c][v]['bkgr']['non-prompt-chargemisid'] = tmp_hist
            else:
                list_of_hist[c][v]['bkgr']['non-prompt-chargemisid'].add(tmp_hist)
            del(tmp_hist)


#
# Set output directory, taking into account the different options
#
from HNL.Tools.outputTree import cleanName
output_dir = os.path.join(os.getcwd(), 'data', 'Results', 'testChargeFlipNonprompt', analysis+'-'+tag if tag is not None else analysis, '-'.join([strategy, selection, region, era+str(year)]))

signal_or_background_str = 'bkgrOnly'
output_dir = os.path.join(output_dir, signal_or_background_str)    


output_dir = makePathTimeStamped(output_dir)

#
# Create variable plots for each category
#
print "Creating variable plots"
from HNL.EventSelection.eventCategorization import CATEGORY_NAMES
from HNL.Plotting.plot import Plot
# for c in list_of_hist.keys():
for c in category_dict[categoriesToPlot][0]:
    if categoriesToPlot == 'original':
        c_name = CATEGORY_NAMES[float(c)]
    elif categoriesToPlot == 'analysis':
        from HNL.EventSelection.eventCategorization import ANALYSIS_CATEGORIES_TEX
        c_name = ANALYSIS_CATEGORIES_TEX[c] 
    elif categoriesToPlot == 'splitanalysis':
        from HNL.EventSelection.eventCategorization import ANALYSIS_SPLITOSSF_CATEGORIES_TEX
        c_name = ANALYSIS_SPLITOSSF_CATEGORIES_TEX[c] 
    elif categoriesToPlot == 'leadingflavor':
        from HNL.EventSelection.eventCategorization import LEADING_FLAVOR_CATEGORIES_TEX
        c_name = LEADING_FLAVOR_CATEGORIES_TEX[c] 
    elif categoriesToPlot == 'trigger':
        from HNL.EventSelection.eventCategorization import TRIGGER_CATEGORIES_TEX
        c_name = TRIGGER_CATEGORIES_TEX[c] 
    else:
        from HNL.EventSelection.eventCategorization import SUPER_CATEGORIES_TEX
        c_name = SUPER_CATEGORIES_TEX[c] 

    from HNL.Plotting.plottingTools import extraTextFormat
    extra_text = [extraTextFormat(c_name, xpos = 0.2, ypos = 0.74, textsize = None, align = 12)]  #Text to display event type in plot
    # Plots that display chosen for chosen signal masses and backgrounds the distributions for the different variables
    # S and B in same canvas for each variable
    

    #Print the fraction
    print 'Fraction of {0} charge flip nonprompt events:  {1}'.format(c_name, list_of_hist[c]['LT']['bkgr']['non-prompt-chargemisid'].getHist().GetSumOfWeights()/(list_of_hist[c]['LT']['bkgr']['non-prompt-chargemisid'].getHist().GetSumOfWeights()+list_of_hist[c]['LT']['bkgr']['non-prompt'].getHist().GetSumOfWeights()))    

    for v in var_dict.keys():
        bkgr_legendnames = []
        # Make list of background histograms for the plot object (or None if no background)
        bkgr_hist = []
        for bk in list_of_hist[c][v]['bkgr'].keys():
            bkgr_hist.append(list_of_hist[c][v]['bkgr'][bk])
            bkgr_legendnames.append(bk)

        from HNL.Plotting.plottingDicts import sample_tex_names
        #Clean bkgr names
        bkgr_legendnames = [sample_tex_names[x] if x in sample_tex_names.keys() else x for x in bkgr_legendnames]


        legend_names = bkgr_legendnames

        #Create specialized signal region plots if this is the correct variable
        if v == 'searchregion':
            #Wanneer plots
            if region in signal_regions:
                from HNL.EventSelection.searchRegions import plotLowMassRegions, plotHighMassRegions, plotLowMassRegionsLoose
                # else:
                #     signal_names = [s + ' V^{2}=' + str(signal_couplingsquared[s.split('-')[1]][int(s.split('-m')[-1])])  for s in signal_names]
                  
                if region == 'lowMassSRloose':
                    plotLowMassRegionsLoose(None, bkgr_hist, None, legend_names, 
                        out_path = os.path.join(output_dir, 'Yields', 'SearchRegions', c, '-'.join(searchregion) if searchregion is not None else ''), extra_text = [x for x in extra_text], year = year, era = era, observed_hist = None)
                if region == 'highMassSR':
                    plotHighMassRegions(None, bkgr_hist, None, legend_names, 
                        out_path = os.path.join(output_dir, 'Yields', 'SearchRegions', c, '-'.join(searchregion) if searchregion is not None else ''), extra_text = [x for x in extra_text], year = year, era = era, observed_hist = None, final_state = c)

        else:

            # Create plot object (if signal and background are displayed, also show the ratio)
            p = Plot(None, legend_names, c+'-'+v, bkgr_hist = bkgr_hist, observed_hist = None, syst_hist = None, y_log = True, extra_text = [x for x in extra_text], draw_ratio = False, year = year, era=era,
                    color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau' if not analysis == 'tZq' else 'tZq', x_name = var_dict[v][2][0], y_name = var_dict[v][2][1])

            # Draw
            #p.drawHist(output_dir = os.path.join(output_dir, 'Variables' if v != 'searchregion' else 'Yields/SearchRegions', c), normalize_signal = True, draw_option='EHist', min_cutoff = 1)
            if '-' in v:
                p.draw2D(output_dir = os.path.join(output_dir+'/2D', 'Variables' if v != 'searchregion' else 'Yields/SearchRegions', c))
            else:
                normalize_signal = None
                if 'analysis' in categoriesToPlot:
                    normalize_signal = 'med'
                else:
                    normalize_signal = 'bkgr'
                p.drawHist(output_dir = os.path.join(output_dir, 'Variables' if v != 'searchregion' else 'Yields/SearchRegions', c), draw_option='EHist', min_cutoff = 1)
