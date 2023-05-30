import numpy as np
# https://lathomas.web.cern.ch/lathomas/METStuff/XYCorrections/XYMETCorrection_withUL17andUL18andUL16.h
def ULMETXYCorrection(met, met_phi, npv, runnb, year, era, isMC):
    if npv > 100: npv = 100

    if era != 'UL':
        return 1.

    if year=="2017":
        if isMC:
            METxcorr = -(-0.300155*npv +1.90608)
            METycorr = -(0.300213*npv +-2.02232)
        else:
            if runnb >=297020 and runnb <=299329:           #2017B
                METxcorr = -(-0.211161*npv +0.419333)
                METycorr = -(0.251789*npv +-1.28089)
            elif runnb >=299337 and runnb <=302029:         #2017C
                METxcorr = -(-0.185184*npv +-0.164009)
                METycorr = -(0.200941*npv +-0.56853)
            elif runnb >=302030 and runnb <=303434:         #2017D
                METxcorr = -(-0.201606*npv +0.426502)
                METycorr = -(0.188208*npv +-0.58313)
            elif runnb >=303435 and runnb <=304826:         #2017E
                METxcorr = -(-0.162472*npv +0.176329)
                METycorr = -(0.138076*npv +-0.250239)
            elif runnb >=304911 and runnb <=306462:         #2017F
                METxcorr = -(-0.210639*npv +0.72934)
                METycorr = -(0.198626*npv +1.028)

    if year == "2018":
        if isMC:
            METxcorr = -(0.183518*npv +0.546754)
            METycorr = -(0.192263*npv +-0.42121)
        else:
            if runnb >=315252 and runnb <=316995 :          #2018A
                METxcorr = -(0.263733*npv +-1.91115)
                METycorr = -(0.0431304*npv +-0.112043)
            elif runnb >=316998 and runnb <=319312:         #2018B
                METxcorr = -(0.400466*npv +-3.05914)
                METycorr = -(0.146125*npv +-0.533233)
            elif runnb >=319313 and runnb <=320393:         #2018C
                METxcorr = -(0.430911*npv +-1.42865)
                METycorr = -(0.0620083*npv +-1.46021)
            elif runnb >=320394 and runnb <=325273:         #2018D
                METxcorr = -(0.457327*npv +-1.56856)
                METycorr = -(0.0684071*npv +-0.928372)

    if year =="2016pre":
        if isMC:
            METxcorr = -(-0.188743*npv +0.136539)
            METycorr = -(0.0127927*npv +0.117747)
        else:
            if runnb >=272007 and runnb <=275376:           #2016B
                METxcorr = -(-0.0214894*npv +-0.188255)
                METycorr = -(0.0876624*npv +0.812885)
            if runnb >=275657 and runnb <=276283:           #2016C
                METxcorr = -(-0.032209*npv +0.067288)
                METycorr = -(0.113917*npv +0.743906)
            if runnb >=276315 and runnb <=276811:           #2016D
                METxcorr = -(-0.0293663*npv +0.21106)
                METycorr = -(0.11331*npv +0.815787)
            if runnb >=276831 and runnb <=277420:           #2016E
                METxcorr = -(-0.0132046*npv +0.20073)
                METycorr = -(0.134809*npv +0.679068)
            if ((runnb >=277772 and runnb <=278768) or runnb==278770):      #2016F
                METxcorr = -(-0.0543566*npv +0.816597)
                METycorr = -(0.114225*npv +1.17266)
    
    if year =="2016post":
        if isMC:
            METxcorr = -(-0.153497*npv +-0.231751)
            METycorr = -(0.00731978*npv +0.243323)
        else:
            if ((runnb >=278801 and runnb <=278808) or runnb==278769):      #2016F
                METxcorr = -(0.134616*npv +-0.89965)
                METycorr = -(0.0397736*npv +1.0385)
            if runnb >=278820 and runnb <=280385:           #2016G
                METxcorr = -(0.121809*npv +-0.584893)
                METycorr = -(0.0558974*npv +0.891234)
            if runnb >=280919 and runnb <=284044:           #2016H
                METxcorr = -(0.0868828*npv +-0.703489)
                METycorr = -(0.0888774*npv +0.902632)

    corrMETx=met*np.cos(met_phi) + METxcorr
    corrMETy=met*np.sin(met_phi) + METycorr
   
    import math 
    corr_met = np.sqrt(corrMETx**2 +corrMETy**2)
    if corrMETx == 0 and corrMETy > 0:
        corr_metphi = math.pi
    elif corrMETx == 0 and corrMETy < 0:
        corr_metphi = -math.pi
    elif corrMETx > 0:
        corr_metphi = math.atan2(corrMETy, corrMETx)
    elif corrMETx < 0 and corrMETy > 0:
        corr_metphi = math.atan2(corrMETy, corrMETx)
    elif corrMETx < 0 and corrMETy < 0:
        corr_metphi = math.atan2(corrMETy, corrMETx)

    return corr_met, corr_metphi 
