def makeGraph(flavor, in_name, masses):
    min_mass = min(masses)
    max_mass = max(masses)
    from array import array
    import json
    import os
    import_path = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Stat', 'data', 'StateOfTheArt', 'stateOfTheArt.json'))
    with open(import_path, 'r') as openfile:
        json_dict = json.load(openfile)
    masses_to_keep = array('f', sorted([float(m) for m in json_dict[flavor][in_name] if float(m) >= min_mass and float(m) <= max_mass]))
    appropriate_couplings = array('f', [json_dict[flavor][in_name][str(m)] for m in masses_to_keep])
    from ROOT import TGraph
    out_graph = TGraph(len(masses_to_keep), masses_to_keep, appropriate_couplings)
    return out_graph

legend_names = {
    'expected_17012_prompt' : 'expected (EXO-17-012)',
    'observed_17012_prompt' : 'EXO-17-012 (prompt)',
    'observed_17012_displaced' : 'EXO-17-012',
    'delphi_prompt' : 'DELPHI'
}
def makeGraphList(flavor, in_names, masses):
    graph_list = []
    graph_legend = []
    for name in in_names:
        graph_list.append(makeGraph(flavor, name, masses))
        graph_legend.append(legend_names[name])
    return graph_list, graph_legend   
    

def createDictEntry(in_dict, entry_name, masses, couplings):
    in_dict[entry_name] = {}
    for m, c in zip(masses, couplings):
        in_dict[entry_name][m] = c 
    return in_dict


if __name__ == '__main__':
    
    out_dict = {}
    #
    #Electrons
    #
    out_dict['e'] = {}
    #expected_17012_prompt
    out_dict['e'] = createDictEntry(out_dict['e'], 'expected_17012_prompt', [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 85.0, 90.0, 100.0, 130.0, 150.0, 200.0, 400.0, 600.0, 800.0, 1000.0, 1200.0], [4.5156248234e-05, 1.4726561858e-05, 1.11328117782e-05, 1.12109373731e-05, 1.03515621959e-05, 9.5703126135e-06, 1.05468743641e-05, 1.03515621959e-05, 9.41406233324e-06, 1.07421874418e-05, 1.08203121272e-05, 1.05078124761e-05, 9.5703126135e-06, 1.07421874418e-05, 1.29296868181e-05, 1.79687503987e-05, 3.67187494703e-05, 0.000335937482305, 0.00112499995157, 0.00412109354511, 0.00478515634313, 0.00505859358236, 0.00964843761176, 0.0140234371647, 0.017578125, 0.0690625011921, 0.199062496424, 0.476249992847, 1.01625001431, 1.88812494278])
    
    out_dict['e'] = createDictEntry(out_dict['e'], 'observed_17012_prompt', [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 85.0, 90.0, 100.0, 130.0, 150.0, 200.0, 400.0, 600.0, 800.0, 1000.0, 1200.0], [4.43193603132e-05, 1.50110681716e-05, 1.11232584459e-05, 1.14097947517e-05, 1.0263481272e-05, 9.67611958913e-06, 1.06075258373e-05, 1.04734272099e-05, 9.41548296396e-06, 1.08572457975e-05, 1.11794370241e-05, 1.12819743663e-05, 1.20661316032e-05, 1.60735453392e-05, 2.19736612053e-05, 3.3227403037e-05, 6.70456283842e-05, 0.000564675719943, 0.00186337635387, 0.00629086466506, 0.00622035656124, 0.00652450788766, 0.0109739722684, 0.0142639838159, 0.0135632818565, 0.0523753352463, 0.167424604297, 0.428148448467, 0.949388027191, 1.83976852894])
    
    out_dict['e'] = createDictEntry(out_dict['e'], 'observed_17012_displaced', [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 85.0, 90.0, 100.0, 130.0, 150.0, 200.0, 400.0, 600.0, 800.0, 1000.0, 1200.0], [0.0135784, 0.00151879, 0.000447416, 0.000223742, 0.00011303, 7.23346e-05, 5.10346e-05, 3.77547e-05, 2.72229e-05, 2.33201e-05, 1.8688e-05, 1.75216e-05, 1.20661e-05, 1.60735453392e-05, 2.19736612053e-05, 3.3227403037e-05, 6.70456283842e-05, 0.000564675719943, 0.00186337635387, 0.00629086466506, 0.00622035656124, 0.00652450788766, 0.0109739722684, 0.0142639838159, 0.0135632818565, 0.0523753352463, 0.167424604297, 0.428148448467, 0.949388027191, 1.83976852894])
    
    d_p_m = [0.260273972602739, 0.292237442922374, 0.342465753424657, 0.390410958904109, 0.447488584474885, 0.481735159817351, 0.534246575342466, 0.591324200913242, 0.625570776255707, 0.652968036529680, 0.694063926940639, 0.732876712328766, 0.776255707762557, 0.815068493150685, 0.860730593607306, 0.915525114155251, 0.972602739726027, 1.038812785388127, 1.098173515981735, 1.166666666666666, 1.230593607305935, 1.280821917808219, 1.331050228310502, 1.381278538812785, 1.456621004566209, 1.513698630136986, 1.586757990867580, 1.630136986301369, 1.666666666666666, 1.712328767123287, 1.751141552511415, 1.785388127853881, 1.815068493150684, 1.837899543378995, 1.856164383561643, 1.872146118721461, 1.888127853881278, 1.901826484018265]
    d_p_l = [-2.00000000000000, -2.19424460431654, -2.49640287769784, -2.78417266187050, -3.11510791366906, -3.33812949640287, -3.63309352517985, -3.95683453237410, -4.14388489208633, -4.30935251798561, -4.47482014388489, -4.59712230215827, -4.68345323741007, -4.72661870503597, -4.75539568345323, -4.74820143884892, -4.73381294964028, -4.72661870503597, -4.72661870503597,  -4.70503597122302, -4.68345323741007, -4.67625899280575, -4.66187050359712, -4.63309352517985, -4.60431654676259, -4.60431654676259, -4.60431654676259, -4.59712230215827, -4.56115107913669, -4.48920863309352, -4.38129496402877, -4.20143884892086, -3.98561151079136, -3.73381294964028, -3.50359712230215, -3.20863309352517, -2.92805755395683, -2.64748201438848]
    
    import math
    from array import array
    delphi_prompt_masses = array('f', [math.pow(10.0, x) for x in d_p_m])
    delphi_prompt_couplings = array('f', [math.pow(10.0, x) for x in d_p_l]) 
    out_dict['e'] = createDictEntry(out_dict['e'], 'delphi_prompt', delphi_prompt_masses, delphi_prompt_couplings)
    
    #
    #Muons
    #
    out_dict['mu'] = {}
    
    #expected_17012_prompt
    out_dict['mu'] = createDictEntry(out_dict['mu'], 'expected_17012_prompt', [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 85.0, 90.0, 95.0, 100.0, 130.0, 150.0, 200.0, 400.0, 600.0, 800.0, 1000.0, 1200.0], [4.5156248234e-05, 1.80468741746e-05, 1.31640617838e-05, 1.27734374473e-05, 1.13671876534e-05, 1.08593749246e-05, 1.12890620585e-05, 1.09765624074e-05, 1.01953119156e-05, 1.04687496787e-05, 1.08984368126e-05, 1.08984368126e-05, 1.32421873786e-05, 1.52734373842e-05, 1.60156250786e-05, 1.66406243807e-05, 2.69531246886e-05, 0.000129296866362, 0.000585937465075, 0.00215820316225, 0.00245117186569, 0.00294921873137, 0.00375976553187, 0.00703124981374, 0.0102734370157, 0.0128124998882, 0.0448437482119, 0.12031249702, 0.291249990463, 0.609687507153, 1.14906251431])
    
    out_dict['mu'] = createDictEntry(out_dict['mu'], 'observed_17012_prompt', [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 85.0, 90.0, 95.0, 100.0, 130.0, 150.0, 200.0, 400.0, 600.0, 800.0, 1000.0, 1200.0], [5.53294485144e-05, 2.13486309804e-05, 1.54980734806e-05, 1.51253434524e-05, 1.35940999826e-05, 1.29579138957e-05, 1.36955950438e-05, 1.34053416332e-05, 1.23575791804e-05, 1.29577347252e-05, 1.33568382807e-05, 1.3231740013e-05, 1.48506314872e-05, 1.76592966454e-05, 1.8759708837e-05, 1.80472998181e-05, 2.77738545265e-05, 0.000156183625222, 0.000742154952604, 0.00241651013494, 0.00289491401054, 0.00345642818138, 0.00431929342449, 0.00716542685404, 0.00796568952501, 0.0088823242113, 0.0301447957754, 0.0835229083896, 0.206450402737, 0.44104334712, 0.847843885422])
    
    out_dict['mu'] = createDictEntry(out_dict['mu'], 'observed_17012_displaced', [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 85.0, 90.0, 95.0, 100.0, 130.0, 150.0, 200.0, 400.0, 600.0, 800.0, 1000.0, 1200.0], [0.0163199, 0.00182936, 0.00059415, 0.000280499, 0.000149561, 0.000103852, 6.81653e-05, 4.97358e-05, 3.52154e-05, 3.12335e-05, 2.46796e-05, 2.13769e-05, 1.48506e-05, 1.76592966454e-05, 1.8759708837e-05, 1.80472998181e-05, 2.77738545265e-05, 0.000156183625222, 0.000742154952604, 0.00241651013494, 0.00289491401054, 0.00345642818138, 0.00431929342449, 0.00716542685404, 0.00796568952501, 0.0088823242113, 0.0301447957754, 0.0835229083896, 0.206450402737, 0.44104334712, 0.847843885422])
    
    d_p_m = [0.260273972602739, 0.292237442922374, 0.342465753424657, 0.390410958904109, 0.447488584474885, 0.481735159817351, 0.534246575342466, 0.591324200913242, 0.625570776255707, 0.652968036529680, 0.694063926940639, 0.732876712328766, 0.776255707762557, 0.815068493150685, 0.860730593607306, 0.915525114155251, 0.972602739726027, 1.038812785388127, 1.098173515981735, 1.166666666666666, 1.230593607305935, 1.280821917808219, 1.331050228310502, 1.381278538812785, 1.456621004566209, 1.513698630136986, 1.586757990867580, 1.630136986301369, 1.666666666666666, 1.712328767123287, 1.751141552511415, 1.785388127853881, 1.815068493150684, 1.837899543378995, 1.856164383561643, 1.872146118721461, 1.888127853881278, 1.901826484018265]
    d_p_l = [-2.00000000000000, -2.19424460431654, -2.49640287769784, -2.78417266187050, -3.11510791366906, -3.33812949640287, -3.63309352517985, -3.95683453237410, -4.14388489208633, -4.30935251798561, -4.47482014388489, -4.59712230215827, -4.68345323741007, -4.72661870503597, -4.75539568345323, -4.74820143884892, -4.73381294964028, -4.72661870503597, -4.72661870503597,  -4.70503597122302, -4.68345323741007, -4.67625899280575, -4.66187050359712, -4.63309352517985, -4.60431654676259, -4.60431654676259, -4.60431654676259, -4.59712230215827, -4.56115107913669, -4.48920863309352, -4.38129496402877, -4.20143884892086, -3.98561151079136, -3.73381294964028, -3.50359712230215, -3.20863309352517, -2.92805755395683, -2.64748201438848]
    
    import math
    from array import array
    delphi_prompt_masses = array('f', [math.pow(10.0, x) for x in d_p_m])
    delphi_prompt_couplings = array('f', [math.pow(10.0, x) for x in d_p_l]) 
    out_dict['mu'] = createDictEntry(out_dict['mu'], 'delphi_prompt', delphi_prompt_masses, delphi_prompt_couplings)
    
    import json
    jd = json.dumps(out_dict, sort_keys=True, indent=4)
    with open('stateOfTheArt.json', 'w') as outf:
        outf.write(jd)
