#
# Code to check HEM failure impact on control regions, uses output from runAnalysis
#

import os
input_file_name = lambda region : os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Analysis', 'data', 'runAnalysis', 'HNL-HEMcheck', region, 'UL-2018', 'data', 'Data', 'variables-Data-UL2018-signal.root'))
#input_file_name = lambda region : os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Analysis', 'data', 'runAnalysis', 'HNL', region, 'UL-2018', 'data', 'Data', 'variables-Data-UL2018-signal.root'))
output_file_name = lambda region, category : os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Test', 'data', 'Results', 'HEMcheck', region, category))

region_dict = {
    #'WZCR' : ['MVA', 3],
    'ZZCR' :['cutbased', 4],
#    'ConversionCR' : ['MVA', 3]
}

#Define the 4 regions
condition_a = 'objectInHEM&&isPreHEMrun'
condition_b = 'objectInHEM&&!isPreHEMrun'
condition_c = '!objectInHEM&&isPreHEMrun'
condition_d = '!objectInHEM&&!isPreHEMrun'


from HNL.EventSelection.eventCategorization import SUPER_CATEGORIES, SUPER_CATEGORIES_TEX
categories = {}
for super_cat in SUPER_CATEGORIES:
    categories[super_cat] = '('+'||'.join(['category=={0}'.format(x) for x in SUPER_CATEGORIES[super_cat]])+')'

from HNL.Tools.outputTree import OutputTree
for region in region_dict:
    import HNL.Analysis.analysisTypes as at
    var = at.returnVariables(region_dict[region][1], True, region)

    for c in categories.keys():
        if c!= 'Other': continue
        from HNL.Plotting.plottingTools import extraTextFormat
        extra_text = extraTextFormat(SUPER_CATEGORIES_TEX[c], xpos = 0.2, ypos = 0.74, textsize = None, align = 12)
        for v in var.keys():
            input_tree = OutputTree('events_nominal', input_file_name('{0}-default-{1}-reco'.format(region_dict[region][0], region)))
            from HNL.Analysis.analysisTypes import getBinning
            # run < 319072 && with objects in affected region
            shapes_a = input_tree.getHistFromTree(v, 'shapes_a_{0}_{1}'.format(v, c), getBinning(v, region, var[v][1]), categories[c]+'&&'+condition_a)
            # run >= 319072 && with objects in affected region
            shapes_b = input_tree.getHistFromTree(v, 'shapes_a_{0}_{1}'.format(v, c), getBinning(v, region, var[v][1]), categories[c]+'&&'+condition_b)
            # run < 319072 && without objects in affected region
            shapes_c = input_tree.getHistFromTree(v, 'shapes_a_{0}_{1}'.format(v, c), getBinning(v, region, var[v][1]), categories[c]+'&&'+condition_c)
            # run >= 319072 && without objects in affected region
            shapes_d = input_tree.getHistFromTree(v, 'shapes_a_{0}_{1}'.format(v, c), getBinning(v, region, var[v][1]), categories[c]+'&&'+condition_d)

            
            from HNL.Plotting.plot import Plot
            #A vs B
            extra_text_ab = [extra_text, extraTextFormat('Contains objects in HEM region')]
            p = Plot(shapes_a, ['Run < 319072', 'Run >= 319072'], c+'-'+v+'-AB', bkgr_hist = shapes_b, draw_ratio = True, era ='UL', year='2018', extra_text = [x for x in extra_text_ab], x_name = var[v][2][0], y_name = var[v][2][1], color_palette='Black', color_palette_bkgr = 'Stack')
            p.drawHist(output_file_name(region, c), normalize_signal = 'bkgr')
            #C vs D
            extra_text_cd = [extra_text, extraTextFormat('Does not contain objects in HEM region')]
            p = Plot(shapes_c, ['Run < 319072', 'Run >= 319072'], c+'-'+v+'-CD', bkgr_hist = shapes_d, draw_ratio = True, era ='UL', year='2018', extra_text = [x for x in extra_text_cd], x_name = var[v][2][0], y_name = var[v][2][1], color_palette='Black', color_palette_bkgr = 'Stack')
            p.drawHist(output_file_name(region, c), normalize_signal = 'bkgr')
    
 
