# Release: take CMSSW_10_6_X as default (works for both UL and older reprocessings), fall back to CMSSW_10_2_X on T2_BE_IIHE
if [[ $SCRAM_ARCH == *slc6* ]]; then
  RELEASE=CMSSW_10_2_22
else
  RELEASE=CMSSW_10_6_12
fi

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

#setup of correctionlibtool
cd -
git clone --recursive git@github.com:cms-nanoAOD/correctionlib.git
cd correctionlib
make PYTHON=python2
make install PREFIX=../HNL/Weights/python/correctionlib
scram b -j10

cd -
python3 -m pip install git+https://github.com/cms-nanoAOD/correctionlib.git
git clone https://github.com/lwezenbe/HNL
cd HNL
scram b -j 10
python Stat/python/combineSetup.py

pip install PyPdf2 --user

echo "Setup finished"
