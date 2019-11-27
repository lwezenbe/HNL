#! /usr/bin/env python
import pylint.lint
import os

#
# Runs pylint on the whole ttg package, but exclude dirs and files which are from external sources
#
skipDirs  = ['documents', 'log', '.git', 'virenv', 'utils', 'SkimTuples']
skipFiles = ['__init__.py', 'diffNuisances.py', 'tdrstyle.py', 'CMS_lumi.py']

pyFiles = []
topDir  = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src/HNL')
for root, dirs, files in os.walk(topDir, topdown=True):
    dirs[:]  = [d for d in dirs  if d not in skipDirs]
    pyFiles += [os.path.join(root, f) for f in files if f[-3:] == '.py' and f not in skipFiles]

pyFiles = [f for f in pyFiles if not os.path.islink(f)] # skip symbolic links
pylint.lint.Run(pyFiles + ['--rcfile='+ os.path.expandvars('$CMSSW_BASE') + '/src/HNL/Tools/codeReview/.pylintrc'])
# possibly extend this with pytest in the future
