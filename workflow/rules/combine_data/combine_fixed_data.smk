rule combine_fixed_data:
	message: "Collecting all fixed data and combining them"
	input:
		cleaned_data = rules.clean_data.output,
		update_log = rules.update.log
	output:
		metadata = "{base_path}/Analysis/{date}/combined_files/combined_metadata.tsv",
		sequences = "{base_path}/Analysis/{date}/combined_files/combined_sequences.fasta",
		download_zip = "{base_path}/Download/INSACOG_data_{date}.zip"
	log: "{base_path}/Analysis/{date}/log/combine_data_error.log"
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
			path_for_files = f"{wildcards.base_path}/Analysis/{wildcards.date}/combined_files"
			os.makedirs(path_for_files, exist_ok = True)

			# Traversing all paths and combining all sequences and metadata
			for path, dirs, files in os.walk(str(input.cleaned_data)):
				if(not (sum(list(map(lambda x: (x in ignore_dir), path.split('/')))) or sum(list(map(lambda x: (x in ignore_file), files))))):
					if(files):
						for i in files:
							file_type = i.split('_')[0]
							if(file_type == 'fixed'):
								metadata_url = os.path.join(path, i)
								metadata = pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)
								if(not len(metadata.keys().tolist()) >= 27):
									metadata = pandas.read_csv(metadata_url, delimiter = ',', encoding = 'utf-8', low_memory = False)
								combined_metadata = pandas.concat([combined_metadata, metadata])
							elif(file_type == 'sequence'):
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

			print("Creating zip")
			zip_obj_download = ZipFile(output.download_zip, "w", compression = ZIP_DEFLATED, compresslevel = 9)
			zip_obj_download.write(output.sequences, arcname="combined_sequences.fasta")
			zip_obj_download.write(output.metadata, arcname="combined_metadata.tsv")
			zip_obj_download.close()

			send_data_to_websocket('SUCCESS_ZIP', 'combine_data', None)
			storage.store("total_count", len(combined_metadata))
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'combine_data', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
