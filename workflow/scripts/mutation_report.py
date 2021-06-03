import pandas
import argparse
import itertools
import collections
from pandas import ExcelWriter

parser = argparse.ArgumentParser()
parser.add_argument('--metadata', help='Enter Nexstrain metadata')
parser.add_argument('--output', help='Enter output file')
args = parser.parse_args()
metadata_url = args.metadata
output_url = args.output

genes = ['E', 'M', 'N', 'ORF1a', 'ORF1b', 'ORF3a', 'ORF6', 'ORF7a', 'ORF7b', 'ORF8', 'ORF9b', 'S']
metadata = pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8')
writer = ExcelWriter(output_url)

temp = []
for i in metadata['aaSubstitutions']:
	if(isinstance(i, str)):
		temp.append(i.split(','))
aaSubstitution = list(itertools.chain(*temp))

temp = []
for i in metadata['aaDeletions']:
	if(isinstance(i, str)):
		temp.append(i.split(','))
aaDeletions = list(itertools.chain(*temp))
top_aaDeletions = dict(collections.Counter(aaDeletions))
pandas.DataFrame.from_dict(data=[top_aaDeletions]).transpose().rename(columns={0:'Count'}).to_excel(writer, 'deletions', header = True)

for i in genes:
	gene_aaSubstitution = []
	for j in aaSubstitution:
		if(j.startswith(f'{i}')):
			gene_aaSubstitution.append(j)
	gene_subsitution_counter = dict(collections.Counter(gene_aaSubstitution))
	pandas.DataFrame.from_dict(data=[gene_subsitution_counter]).transpose().rename(columns={0:'Count'}).to_excel(writer, i, header = True)

writer.save()
