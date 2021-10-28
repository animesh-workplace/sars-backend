import os
import pandas
import argparse
import itertools

parser = argparse.ArgumentParser()
parser.add_argument('--metadata', help = 'Enter Nexstrain metadata')
parser.add_argument('--output', help = 'Enter output file')
args = parser.parse_args()
metadata_url = args.metadata
output_url = args.output

metadata = pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)

new_dict = []
for i in metadata.index:
	all_changes = []
	if(isinstance(metadata.iloc[i]['aaSubstitutions'], str)):
		all_changes.append(metadata.iloc[i]['aaSubstitutions'].split(','))
	if(isinstance(metadata.iloc[i]['aaDeletions'], str)):
		all_changes.append(metadata.iloc[i]['aaDeletions'].split(','))
	if(len(all_changes) > 0):
		all_changes = list(itertools.chain(*all_changes))
		p = [new_dict.append({
				'date': metadata.iloc[i]['date'],
				'strain': metadata.iloc[i]['strain'],
				'state': metadata.iloc[i]['division'],
				'lineage':	metadata.iloc[i]['lineage'],
				'mutation/deletion': j,
			}) for j in all_changes]
	else:
		p = new_dict.append({
				'date': metadata.iloc[i]['date'],
				'strain': metadata.iloc[i]['strain'],
				'state': metadata.iloc[i]['division'],
				'lineage':	metadata.iloc[i]['lineage'],
				'mutation/deletion': '',
			})

pandas.DataFrame.from_dict(data = new_dict, orient = 'columns').to_csv(output_url, sep = '\t', header = True, index = False)
