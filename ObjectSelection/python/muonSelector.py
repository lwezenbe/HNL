

def isLooseMuon(chain, index):
    if abs(chain._lEta[index]) >= 2.4:          return False
    if chain._lPt[index] < 5:                   return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._relIso[index] >= 0.6:                    return False
    #PF Muon and (tracker or global) Muon requirements already in ntuplizer
    return True

def isFOMuon(chain, index):
    if not isLooseMuon(chain, index):           return False
    if chain._3dIPSig[index] >= 4:              return False 
    if not chain._lPOGMedium[index]:            return False
    return True

def isTightMuon(chain, index):
    if not isFOMuon(chain, index):              return False
    if chain._relIso[index] >= 0.1:                    return False
    return True
