import Interface

f = open('./first_model/results-part2-copy.txt', 'a')
Interface.mergeFilesNoMeanName(f, './first_model/new_results_name.txt', 'first_model')

