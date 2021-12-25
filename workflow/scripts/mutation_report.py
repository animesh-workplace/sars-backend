import os
import pandas
import logging
import argparse
import itertools
import collections
from mpire import WorkerPool
from pandas import ExcelWriter
from mpire.utils import make_single_arguments

parser = argparse.ArgumentParser()
parser.add_argument('--date', help = 'Enter output file')
parser.add_argument('--basepath', help = 'Enter base path')
parser.add_argument('--metadata', help = 'Enter Nexstrain metadata')
args = parser.parse_args()
date = args.date
base_path = args.basepath
metadata_url = args.metadata

logging.basicConfig(filename = f"{base_path}/Analysis/{date}/log/mutation_report_log", format = '%(asctime)s %(message)s', filemode = 'w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def mutation_report(url):
	output_url = url['output']
	metadata_url = url['metadata']
	genes = ['E', 'M', 'N', 'ORF1a', 'ORF1b', 'ORF3a', 'ORF6', 'ORF7a', 'ORF7b', 'ORF8', 'ORF9b', 'S']
	metadata = pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)
	writer = ExcelWriter(output_url)

	if(not metadata['aaSubstitutions'].dropna().empty):
		aaSubstitution = metadata['aaSubstitutions'].dropna().str.split(',').dropna().explode().to_list()
	else:
		aaSubstitution = []
	if(not metadata['aaDeletions'].dropna().empty):
		aaDeletions = metadata['aaDeletions'].dropna().str.split(',').dropna().explode().to_list()
	else:
		aaDeletions = []
	top_aaDeletions = dict(collections.Counter(aaDeletions))
	pandas.DataFrame.from_dict(data = [top_aaDeletions]).transpose().rename(columns = {0:'Count'}).to_excel(writer, 'deletions', header = True)

	for i in genes:
		gene_aaSubstitution = []
		for j in aaSubstitution:
			if(j.startswith(f'{i}')):
				gene_aaSubstitution.append(j)
		gene_subsitution_counter = dict(collections.Counter(gene_aaSubstitution))
		pandas.DataFrame.from_dict(data = [gene_subsitution_counter]).transpose().rename(columns = {0:'Count'}).to_excel(writer, i, header = True)

	writer.save()
	print(url["name"])


metadata = pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)
states = pandas.unique(metadata['division']).tolist()
path_list = [
	{
		"name": f"Generating {state} mutation report",
		"metadata": f"{base_path}/Analysis/{date}/reports/state_wise/{state.replace(' ','_')}/{state.replace(' ','_')}_metadata.tsv",
		"output": f"{base_path}/Analysis/{date}/reports/state_wise/{state.replace(' ','_')}/{state.replace(' ','_')}_mutation_count_report.xlsx"
	} for state in states ]
path_list.append({
	"metadata": metadata_url,
	"name": "Generating Overall mutation report",
	"output": f"{base_path}/Analysis/{date}/reports/mutation_count_report.xlsx",
})

with WorkerPool(n_jobs = 50) as pool:
	output = pool.map(mutation_report, make_single_arguments(path_list, generator = False))
