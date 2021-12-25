import os
import pandas
import logging
import argparse
from Bio import SeqIO
from mpire import WorkerPool

parser = argparse.ArgumentParser()
parser.add_argument('--date', help = 'Enter output file')
parser.add_argument('--basepath', help = 'Enter base path')
parser.add_argument('--metadata', help = 'Enter Nexstrain metadata')
parser.add_argument('--sequence', help = 'Enter Nexstrain sequences')
args = parser.parse_args()
date = args.date
base_path = args.basepath
metadata_url = args.metadata
sequence_url = args.sequence

log_path = f"{base_path}/Analysis/{date}/reports/state_wise/log/"
os.makedirs(log_path, exist_ok = True)
logging.basicConfig(filename = f"{log_path}/split_data.log", format = '%(asctime)s %(message)s', filemode = 'w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def split_data(state):
	folder_name = state.replace(' ','_')
	state_path = f"{base_path}/Analysis/{date}/reports/state_wise"
	os.makedirs(os.path.join(state_path, folder_name), exist_ok = True)
	state_metadata 	= metadata.iloc[metadata.index[metadata['division'].isin([state])].tolist()]
	state_sequences = [sequence[i]  for i in state_metadata['strain']]
	print(f'Writing {state}: {len(state_metadata)}')
	state_metadata.to_csv(os.path.join(state_path, f"{folder_name}/{folder_name}_metadata.tsv"), sep = '\t', index = False)
	SeqIO.write(state_sequences, os.path.join(state_path, f"{folder_name}/{folder_name}_sequence.fasta"), 'fasta')

print('Reading files')
metadata 	= pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)
sequence 	= SeqIO.to_dict(SeqIO.parse(sequence_url, 'fasta'))
print('Getting unique states')
states 		= pandas.unique(metadata['division']).tolist()

with WorkerPool(n_jobs = 50) as pool:
	output = pool.map(split_data, states)


