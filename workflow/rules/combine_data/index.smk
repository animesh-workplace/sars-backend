rule combine_data:
	message: "Collecting all fixed data and combining them"
	input:
		rules.update.log
	output:
		metadata = os.path.join('{base_path}', 'Analysis', '{date}', 'combined_files', 'combined_metadata.tsv'),
		sequences = os.path.join('{base_path}', 'Analysis', '{date}', 'combined_files', 'combined_sequences.fasta'),
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'combine_data_error.log')
	run:
		try:
			# Initializing all required data
			metadata_labels = ['Virus name', 'Type', 'Passage details/history', 'Collection date', 'Country', 'State', 'District', 'Location', 'Additional location information', 'Host', 'Additional host information', 'Gender', 'Patient age', 'Patient status', 'Specimen source', 'Outbreak', 'Last vaccinated', 'Treatment', 'Sequencing technology', 'Assembly method', 'Coverage', 'Originating lab', 'Originating lab address', 'Submitting lab', 'Submitting lab address', 'Sample ID given by the submitting lab', 'Authors']
			combined_metadata = pandas.DataFrame()
			combined_sequences = []
			combined_sequences_label = []
			ignore_dir = ['combined_files']
			ignore_file = ['template_metadata.csv']

			# Create path and folder for all combined files
			upload_date = config['analysis_time'].split('_')[0]
			path_for_files = os.path.join(config['base_path'], 'Analysis', upload_date, 'combined_files')
			os.makedirs(path_for_files, exist_ok = True)

			# Traversing all paths and combining all sequences and metadata
			for path, dirs, files in os.walk(config['base_path']):
				if(not (sum(list(map(lambda x: (x in ignore_dir), path.split('/')))) or sum(list(map(lambda x: (x in ignore_file), files))))):
					if(files):
						for i in files:
							type = i.split('_')[0]
							if(type == 'fixed'):
								metadata_url = os.path.join(path, i)
								metadata = pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)
								if(not len(metadata.keys().tolist()) >= 27):
									metadata = pandas.read_csv(metadata_url, delimiter = ',', encoding = 'utf-8', low_memory = False)
								combined_metadata = pandas.concat([combined_metadata, metadata])
							elif(type == 'sequence'):
								for j in SeqIO.parse(os.path.join(path, i), 'fasta'):
									if(not j.id in combined_sequences_label):
										combined_sequences.append(j)
										combined_sequences_label.append(j.id)

			combined_metadata['Virus name'].replace('', numpy.nan, inplace = True)
			combined_metadata.dropna(subset = ['Virus name'], inplace = True)
			combined_metadata = combined_metadata[combined_metadata['Virus name'].str.strip().astype(bool)]
			combined_metadata.reset_index(drop = True, inplace = True)
			combined_metadata.drop_duplicates(subset = ['Virus name'], ignore_index = True, inplace = True)

			# For download button
			combined_metadata[metadata_labels].to_csv(output.metadata, sep = '\t', index = False)
			SeqIO.write(combined_sequences, output.sequences, 'fasta')
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'combine_data', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
