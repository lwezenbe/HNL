RELEASE=CMSSW_10_2_20
BRANCH=master

#If the release is already available using cmsenv, use it, otherwise set up a new one
if [[ $CMSSW_BASE == *$RELEASE ]] && [[ -d $CMSSW_BASE ]]; then
  echo "Setting up HNL framework in current release: $CMSSW_BASE"
  cd $CMSSW_BASE/src
else
  scram project CMSSW $RELEASE
  cd $RELEASE/src
  eval `scram runtime -sh`
  echo "Creating release for HNL framework: $CMSSW_BASE"
fi

cmsenv
git clone https://github.com/cms-tau-pog/TauIDSFs TauPOG/TauIDSFs
cd TauPOG
scram b -j10

cd -
git clone https://github.com/lwezenbe/HNL
cd HNL
scram b -j 10
echo "Setup finished"
