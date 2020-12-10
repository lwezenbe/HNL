
WP = { (2016, 'loose', 'CSV') : 0.2217,
        (2016, 'medium', 'CSV') : 0.6321,
        (2016, 'tight', 'CSV') : 0.8953,

        (2016, 'loose', 'AN2017014') : 0.5426,
        
        (2017, 'loose', 'CSV') : 0.1522,
        (2017, 'medium', 'CSV') : 0.4941,
        (2017, 'tight', 'CSV') : 0.8001,

        (2018, 'loose', 'CSV') : 0.1241,
        (2018, 'medium', 'CSV') : 0.4184,
        (2018, 'tight', 'CSV') : 0.7527,

        (2016, 'loose', 'Deep') : 0.0614,
        (2016, 'medium', 'Deep') : 0.3093,
        (2016, 'tight', 'Deep') : 0.7221,

        (2017, 'loose', 'Deep') : 0.0521,
        (2017, 'medium', 'Deep') : 0.3033,
        (2017, 'tight', 'Deep') : 0.7489,

        (2018, 'loose', 'Deep') : 0.0494,
        (2018, 'medium', 'Deep') : 0.2770,
        (2018, 'tight', 'Deep') : 0.7264
        }

def getBTagWP(year, working_point, algo = 'Deep'):
    return WP[year, working_point, algo]

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

def slidingDeepFlavorThreshold(year, pt, algo='Deep' ):
    minPt = 20.
    maxPt = 45.
    looseWP = getBTagWP(year, 'loose', algo)
    mediumWP = getBTagWP(year, 'medium', algo)
    if( pt < minPt ):
        return mediumWP
    elif( pt > maxPt ):
        return looseWP
    else:
        return ( mediumWP - ( mediumWP - looseWP ) / ( maxPt - minPt ) * ( pt - minPt ) )
