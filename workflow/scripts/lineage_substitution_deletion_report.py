import os
import pandas
import logging
import argparse
import itertools
from mpire import WorkerPool
from mpire.utils import make_single_arguments

parser = argparse.ArgumentParser()
parser.add_argument('--date', help = 'Enter output file')
parser.add_argument('--basepath', help = 'Enter base path')
parser.add_argument('--metadata', help = 'Enter Nexstrain metadata')
args = parser.parse_args()
date = args.date
base_path = args.basepath
metadata_url = args.metadata

logging.basicConfig(filename = f"{base_path}/Analysis/{date}/log/lsd_report_log", format = '%(asctime)s %(message)s', filemode = 'w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lsd_report(url):
	output_url = url['output']
	metadata_url = url['metadata']
	all_changes = []
	metadata = pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)
	if(not metadata['aaSubstitutions'].dropna().empty):
		all_changes = [{'date': metadata.iloc[index]['date'], 'strain': metadata.iloc[index]['strain'], 'lineage': metadata.iloc[index]['lineage'], 'mutation/deletion': mutation} for (index, mutations) in  metadata['aaSubstitutions'].dropna().str.split(',').to_dict().items() for mutation in mutations]
	if(not metadata['aaDeletions'].dropna().empty):
		all_changes = all_changes + [{'date': metadata.iloc[index]['date'], 'strain': metadata.iloc[index]['strain'], 'lineage': metadata.iloc[index]['lineage'], 'mutation/deletion': mutation} for (index, mutations) in  metadata['aaDeletions'].dropna().str.split(',').to_dict().items() for mutation in mutations]
	all_changes = all_changes + [{'date': metadata.iloc[index]['date'], 'strain': metadata.iloc[index]['strain'], 'lineage': metadata.iloc[index]['lineage'], 'mutation/deletion': ''} for index in metadata[metadata['aaSubstitutions'].isna()]['aaSubstitutions'].index.to_list() + metadata[metadata['aaDeletions'].isna()]['aaDeletions'].index.to_list()]
	pandas.DataFrame.from_dict(data = all_changes, orient = 'columns').to_csv(output_url, sep = '\t', header = True, index = False)
	print(url["name"])

metadata = pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)
states = pandas.unique(metadata['division']).tolist()
path_list = [
	{
		"name": f"Generating {state} Lineage Substitution Deletion report",
		"metadata": f"{base_path}/Analysis/{date}/reports/state_wise/{state.replace(' ','_')}/{state.replace(' ','_')}_metadata.tsv",
		"output": f"{base_path}/Analysis/{date}/reports/state_wise/{state.replace(' ','_')}/{state.replace(' ','_')}_lineage_substitution_deletion_report.tsv"
	} for state in states ]
path_list.append({
	"metadata": metadata_url,
	"name": "Generating Overall Lineage Substitution Deletion report",
	"output": f"{base_path}/Analysis/{date}/reports/lineage_substitution_deletion_report.tsv",
})

with WorkerPool(n_jobs = 50) as pool:
	output = pool.map(lsd_report, make_single_arguments(path_list, generator = False))
