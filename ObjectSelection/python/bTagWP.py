
WP_prelegacy = { ('2016', 'loose', 'CSV') : 0.2217,
        ('2016', 'medium', 'CSV') : 0.6321,
        ('2016', 'tight', 'CSV') : 0.8953,

        ('2016', 'loose', 'AN2017014') : 0.5426,
        ('2017', 'loose', 'AN2017014') : 0.5803,              #This number was copied from ewkino, 2017 was not used in AN2017014
        ('2018', 'loose', 'AN2017014') : 0.5803,              #This number was copied from ewkino, 2018 was not used in AN2017014
        
        ('2017', 'loose', 'CSV') : 0.1522,
        ('2017', 'medium', 'CSV') : 0.4941,
        ('2017', 'tight', 'CSV') : 0.8001,

        ('2018', 'loose', 'CSV') : 0.1241,
        ('2018', 'medium', 'CSV') : 0.4184,
        ('2018', 'tight', 'CSV') : 0.7527,

        ('2016', 'loose', 'Deep') : 0.0614,
        ('2016', 'medium', 'Deep') : 0.3093,
        ('2016', 'tight', 'Deep') : 0.7221,

        ('2017', 'loose', 'Deep') : 0.0521,
        ('2017', 'medium', 'Deep') : 0.3033,
        ('2017', 'tight', 'Deep') : 0.7489,

        ('2018', 'loose', 'Deep') : 0.0494,
        ('2018', 'medium', 'Deep') : 0.2770,
        ('2018', 'tight', 'Deep') : 0.7264
        }

WP_UL = { ('2016pre', 'loose', 'CSV') : 0.1355,
        ('2016pre', 'medium', 'CSV') : 0.4506,
        ('2016pre', 'tight', 'CSV') : 0.7738,
        
        ('2016post', 'loose', 'CSV') : 0.1918,
        ('2016post', 'medium', 'CSV') : 0.5847,
        ('2016post', 'tight', 'CSV') : 0.8767,
        
        ('2017', 'loose', 'CSV') : 0.1355,
        ('2017', 'medium', 'CSV') : 0.4506,
        ('2017', 'tight', 'CSV') : 0.7738,

        ('2018', 'loose', 'CSV') : 0.1208,
        ('2018', 'medium', 'CSV') : 0.4168,
        ('2018', 'tight', 'CSV') : 0.7665,

        ('2016pre', 'loose', 'AN2017014') : 0.5426,
        ('2016post', 'loose', 'AN2017014') : 0.5426,
        ('2017', 'loose', 'AN2017014') : 0.5803,              #This number was copied from ewkino, 2017 was not used in AN2017014
        ('2018', 'loose', 'AN2017014') : 0.5803,              #This number was copied from ewkino, 2018 was not used in AN2017014

        ('2016pre', 'loose', 'Deep') : 0.0532,
        ('2016pre', 'medium', 'Deep') : 0.3040,
        ('2016pre', 'tight', 'Deep') : 0.7476,

        ('2016post', 'loose', 'Deep') : 0.0480,
        ('2016post', 'medium', 'Deep') : 0.2489,
        ('2016post', 'tight', 'Deep') : 0.6377,

        ('2017', 'loose', 'Deep') : 0.0532,
        ('2017', 'medium', 'Deep') : 0.3040,
        ('2017', 'tight', 'Deep') : 0.7476,

        ('2018', 'loose', 'Deep') : 0.0490,
        ('2018', 'medium', 'Deep') : 0.2783,
        ('2018', 'tight', 'Deep') : 0.7100
        }

WP = {
    'prelegacy' : WP_prelegacy,
    'UL'        : WP_UL
}

def getBTagWP(era, year, working_point, algo = 'Deep'):
    return WP[era][year, working_point, algo]

def readBTagValue(chain, jet, algo = 'Deep'):
    if algo == 'Deep':
        return chain._jetDeepFlavor_b[jet] + chain._jetDeepFlavor_bb[jet] + chain._jetDeepFlavor_lepb[jet]
        # return chain._jetDeepFlavor[jet]
    elif algo == 'CSV':
        return chain._jetDeepCsv[jet]
    elif algo == 'AN2017014':
        return chain._jetCsvV2[jet]
    else:
        print 'Unknown b-tagging algorithm'

def slidingDeepFlavorThreshold(era, year, pt, algo='Deep' ):
    minPt = 20.
    maxPt = 45.
    looseWP = getBTagWP(era, year, 'loose', algo)
    mediumWP = getBTagWP(era, year, 'medium', algo)
    if( pt < minPt ):
        return mediumWP
    elif( pt > maxPt ):
        return looseWP
    else:
        return ( mediumWP - ( mediumWP - looseWP ) / ( maxPt - minPt ) * ( pt - minPt ) )

def returnBTagValueBySelection(chain, jet, selection = None):
    if selection is None: selection = chain.obj_sel['jet_algo']

    if selection in ['HNL', 'HNLLowPt', 'TTT', 'Luka']:
        return readBTagValue(chain, jet, 'Deep')
    else:
        return readBTagValue(chain, jet, 'AN2017014')

def passBtag(chain, jet, workingpoint, algo):
    return readBTagValue(chain, jet, algo) > getBTagWP(chain.era, chain.year, workingpoint, algo)

def getAllAlgorithms(era, year):
    all_algos = {a[2] for a in WP[era].keys() if a[2] != 'AN2017014'}
    return [k for k in all_algos]

def getFlavor(chain, jet_index):
    if abs(chain._jetHadronFlavor[jet_index]) == 5: return 'b'
    elif abs(chain._jetHadronFlavor[jet_index]) == 4: return 'c'
    else: return 'other'