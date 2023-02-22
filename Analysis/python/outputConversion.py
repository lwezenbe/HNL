#
# Convert hist_of_list to table of yields
#
tex_translations_year = {
    '2016pre' : '2016 pre VFP',
    '2016post' : '2016 post VFP',
    '2016post-2016pre-2017-2018' : 'Full Run II',
    '2016pre-2016post-2017-2018' : 'Full Run II',
}

tex_translations_process = {
    'total'     : 'Total Pred. Bkgr.',
    'WZ'        : '\\WZ',
    'TT-T+X'    : '\\ttX',
    'XG'        : '\\VG',
    'triboson'  : 'Triboson',
    'ZZ-H'      : '\\ZZ',
    'non-prompt': 'Nonprompt',
}

def writeYieldTable(in_hist_dict, category, var, output_name, split_bkgr = False):
    #sort years
    years = [x for x in ['2016pre', '2016post', '2017', '2018'] if x in in_hist_dict.keys()] + [x for x in in_hist_dict if '-' in x]
    observed = 'signalregion' in in_hist_dict[years[0]][category][var]['data'].keys()

    #Get all samples in all years
    sample_names = {'signal' : set(), 'bkgr' : set()}
    for y in years:
        tmp_sig = {x for x in in_hist_dict[y][category][var]['signal'].keys()}
        if split_bkgr: tmp_bkgr = {x for x in in_hist_dict[y][category][var]['bkgr'].keys()}
        sample_names['signal'].update(tmp_sig)
        if split_bkgr: sample_names['bkgr'].update(tmp_bkgr)
    sample_names['signal'] = [x for x in sample_names['signal']]
    if split_bkgr:
        sample_names['bkgr'] = [tex_translations_process[x]  if x in tex_translations_process.keys() else x for x in sample_names['bkgr']]
    else:
        sample_names['bkgr'] = [] 
    sample_names['bkgr'] += ['total']

    total_n_samples = 0
    for sob in sample_names.keys():
        total_n_samples += len(sample_names[sob])
    if observed: 
        total_n_samples += 1
   
    from HNL.Tools.helpers import makeDirIfNeeded
    makeDirIfNeeded(output_name+'/'+category+'-yields.txt') 
    out_file = open(output_name+'/'+category+'-yields.txt', 'w')
    out_file.write('\\begin{table}[!h]\n')
    out_file.write('\\centering\n')
    out_file.write('\\begin{tabular}{l'+'|'.join(['c']*total_n_samples)+'}\n')
    out_file.write('\\hline\n')

    #Header
    process_line = 'Year & '
    if observed: process_line += 'Observed & '
    if len(sample_names['signal']) > 0:
        process_line += ' & '.join(sample_names['signal'])
    if len(sample_names['bkgr']) > 0:
        process_line += ' & '.join(sample_names['bkgr'])
    out_file.write(process_line + ' \\\\\n\\hline\n')

    #Yields per year
    for y in years:
        yield_line = tex_translations_year[y] if y in tex_translations_year.keys() else y
        if observed: yield_line += ' & %s \t'%float('%.1f' % in_hist_dict[y][category][var]['data']['signalregion']['nominal'].getHist().GetSumOfWeights())
        if len(sample_names['signal']) > 0:
            yield_line += ' & ' + ' & '.join(['%s \t'%float('%.1f' % in_hist_dict[y][category][var]['signal'][sig]['nominal'].getHist().GetSumOfWeights()) for sig in sample_names['signal']])
        if len(sample_names['bkgr']) > 0:
            yield_line += ' & '
            total_bkgr = 0.
            for bkgr in in_hist_dict[y][category][var]['bkgr'].keys():
                total_bkgr += in_hist_dict[y][category][var]['bkgr'][bkgr]['nominal'].getHist().GetSumOfWeights() 
            for bkgr in sample_names['bkgr']:
                if bkgr != 'total':
                    try:
                        yield_line += ' & %s \t'%float('%.1f' % in_hist_dict[y][category][var]['bkgr'][bkgr]['nominal'].getHist().GetSumOfWeights())
                    except:
                        yield_line += ' & %s \t'%float('%.1f' % 0.)
                else:
                    yield_line += ' & %s \t'%float('%.1f' % total_bkgr)
        yield_line += '\\\\\n'
        out_file.write(yield_line)
    out_file.write('\\hline\n')
    out_file.write('\\end{tabular}\n')
    out_file.write('\\end{table}\n')
    out_file.close()
