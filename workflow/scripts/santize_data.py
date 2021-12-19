import os
import gc
import arrow
import pandas
import logging
import fuzzyset
import itertools
from Bio import SeqIO
from mpire import WorkerPool

logging.basicConfig(filename = "additional.log", format = '%(asctime)s %(message)s', filemode = 'w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

rgsl_users = os.listdir("Uploaded_data")

def sanitize_data(rgsl):
	metadata_labels           = ['Virus name', 'Type', 'Passage details/history', 'Collection date', 'Country', 'State', 'District', 'Location', 'Additional location information', 'Host', 'Additional host information', 'Gender', 'Patient age', 'Patient status', 'Specimen source', 'Outbreak', 'Last vaccinated', 'Treatment', 'Sequencing technology', 'Assembly method', 'Coverage', 'Originating lab', 'Originating lab address', 'Submitting lab', 'Submitting lab address', 'Sample ID given by the submitting lab', 'Authors']
	combined_metadata         = pandas.DataFrame()
	indian_state_info 		  = pandas.read_csv("indian_state_district.tsv", delimiter = '\t', encoding = "utf-8", low_memory = False)
	combined_sequences        = []
	combined_sequences_label  = []
	fs_state          		  = fuzzyset.FuzzySet(pandas.unique(indian_state_info['State']), False, 3, 4)
	fs_gender         		  = fuzzyset.FuzzySet(['Male', 'Female', 'Transgender', 'Unknown'], False, 3, 4)

	for (path, dirs, files) in os.walk(f"Uploaded_data/{rgsl}"):
		if(files):
			for i in files:
				save_url        = f"Fixed_data/{rgsl}/"
				file_type       = i.split('_')[0]
				os.makedirs(save_url, exist_ok = True)
				if(file_type == 'metadata'):
					file_id          = i.split('_')[1].split('.')[0]
					metadata_name   = f'metadata_{file_id}.tsv'
					sequence_name   = f'sequence_{file_id}.fasta'
					metadata_url    = os.path.join(path, metadata_name)
					sequence_url    = os.path.join(path, sequence_name)
					if(os.path.isfile(metadata_url)):
							metadata = pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)
					else:
							print(f'{metadata_url} doesnot exist')
					if(os.path.isfile(sequence_url)):
							sequence = SeqIO.to_dict(SeqIO.parse(sequence_url, 'fasta'))
					else:
							print(f'{sequence_url} doesnot exist')
					metadata_ids = set(metadata['Virus name'].map(str).str.strip())
					sequence_ids = set([str(key).strip() for key in sequence.keys()])
					if(metadata_ids - sequence_ids):
							for ids in (metadata_ids - sequence_ids):
									logger.info(f'Metadata: {metadata_url} has additional ID: {ids}')
					if(sequence_ids - metadata_ids):
							for ids in (metadata_ids - sequence_ids):
									logger.info(f'Sequence: {sequence_url} has additional ID: {ids}')

					fixed_gender            = [ 'Unknown' if(j!=j or len(fs_gender.get(j)) > 1) else fs_gender.get(j)[0][1] for j in metadata['Gender'] ]
					fixed_state_name        = [ fs_state.get(j)[0][1]  for j in metadata['State'] ]
					fixed_collection_date   = [ arrow.get(j, ['YYYY-MM-DD', 'DD-MM-YYYY', 'YYYY/MM/DD', 'DD/MM/YYYY', 'MM-DD-YYYY']).date() for j in metadata['Collection date'] ]

					metadata['State']               = fixed_state_name
					metadata['Country']             = 'India'
					metadata['Location']            = 'Asia'
					metadata['Virus name']          = metadata['Virus name'].map(str).str.strip()
					metadata['Submitting lab']      = rgsl.split('_')[-1]
					metadata['Submission date'] 	= metadata['Collection date']

					combined_metadata = pandas.concat([combined_metadata, metadata[metadata_labels]])
					for (key, value) in sequence.items():
							gc.disable()
							if(not key in combined_sequences_label):
									combined_sequences.append(value)
									combined_sequences_label.append(key)
							gc.enable()

					metadata.to_csv(os.path.join(save_url, f"fixed_{metadata_name}"), sep = '\t', index = False)
					SeqIO.write([seq for (key, seq) in sequence.items()], os.path.join(save_url, f"fixed_{sequence_name}"), 'fasta')
	print(f"Fixed metadata of {rgsl.split('_')[-1]}")
	return (combined_metadata, combined_sequences)

with WorkerPool(n_jobs = 50) as pool:
	output = pool.map(sanitize_data, rgsl_users)

print('Combining all metadata and sequences')
combined_metadata  = pandas.DataFrame()
combined_sequences = []
for i in output:
	combined_metadata = pandas.concat([combined_metadata, i[0]])
	combined_sequences.append(i[1])

combined_sequences = list(itertools.chain(*combined_sequences))

combined_metadata.reset_index(drop = True, inplace = True)
combined_metadata.drop_duplicates(subset = ['Virus name'], ignore_index = True, inplace = True)
combined_metadata.to_csv('combined_metadata.tsv', sep = '\t', index = False)
SeqIO.write(combined_sequences, 'combined_sequences.fasta', 'fasta')