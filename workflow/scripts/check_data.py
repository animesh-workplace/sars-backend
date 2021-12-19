import numpy
import pandas
import argparse
from tqdm import tqdm
from Bio import SeqIO
from datetime import date
from pandas import ExcelWriter

parser = argparse.ArgumentParser()
parser.add_argument('--fasta', help='Enter Fasta file')
parser.add_argument('--metadata', help='Enter NIBMG Datahub metadata')
args 			= parser.parse_args()
fasta_url 		= args.fasta
metadata_url 	= args.metadata

writer 	= ExcelWriter(f'Matching_output_{str(date.today())}.xlsx')

sequences 	= SeqIO.to_dict(SeqIO.parse(fasta_url, 'fasta'))
metadata 	= pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)

matched 	= []
unmatched 	= []
multimatch 	= []

sequence_ids = list(sequences.keys())

for i in tqdm(sequence_ids):
	match = [j for j in metadata['strain'].tolist() if(i in j)]
	if(len(match) == 0):
		unmatched.append(i)
	elif(len(match) == 1):
		matched.append({
			"search query": i,
			"matched term": match[0]
		})
	else:
		multimatch.append(i)

pandas.DataFrame(unmatched, columns = ['Unmatched']).to_excel(writer, 'Unmatched_metadata', index = False, header = True)
pandas.DataFrame(multimatch, columns = ['Multimatch']).to_excel(writer, 'Multi_Matched_metadata', index = False, header = True)
pandas.DataFrame(matched).to_excel(writer, 'Matched_metadata', index = False, header = True)


matched 	= []
unmatched 	= []

for i in tqdm(metadata['strain']):
	try:
		temp = sequences[i]
		matched.append(i)
	except KeyError:
		unmatched.append(i)

pandas.DataFrame(unmatched, columns = ['Unmatched']).to_excel(writer, 'Unmatched_Sequences', index = False, header = True)
pandas.DataFrame(matched).to_excel(writer, 'Matched_Sequences', index = False, header = True)

writer.save()
