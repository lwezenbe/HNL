#
#       Defines jet WP and b-tagging
#

def isGoodJet(chain, index):
    if chain._jetPt[index] < 25:        return False
    if abs(chain._jetEta[index]) > 2.4: return False
    if not chain._jetIsLoose[index]:    return False
    return True


from bTagWP import getBTagWP, readBTagValue
def isBJet(chain, index, algo, wp):
    if readBTagValue(chain, index, algo) < getBTagWP(chain.year, wp, algo): return False
    return True
    

