rule clean_data:
	message: "Cleaning the data"
	input:
		rules.update.log
	output:
		metadata = "{base_path}/Analysis/{date}/combined_files/combined_metadata.tsv",
		sequences = "{base_path}/Analysis/{date}/combined_files/combined_sequences.fasta",
		download_zip = "{base_path}/Download/INSACOG_data_{date}.zip",
		fixed_directory = directory("{base_path}/Fixed_data/{date}"),
	log: "{base_path}/Fixed_data/{date}/log/clean_data_error.log"
	run:
		# try:
		rgsl_users = os.listdir(f"{wildcards.base_path}/Uploaded_data")
		with WorkerPool(n_jobs = 50) as pool:
			output = pool.map(sanitize_data, rgsl_users)

		print('Combining all metadata and sequences')
		combined_metadata  = pandas.DataFrame()
		combined_sequences = []
		for i in output:
			combined_metadata = pandas.concat([combined_metadata, i[0]])
			combined_sequences.append(i[1])

		combined_sequences = list(itertools.chain(*combined_sequences))
		combined_metadata['Virus name'].replace('', numpy.nan, inplace = True)
		combined_metadata.dropna(subset = ['Virus name'], inplace = True)
		combined_metadata.reset_index(drop = True, inplace = True)
		combined_metadata.drop_duplicates(subset = ['Virus name'], ignore_index = True, inplace = True)
		combined_metadata.to_csv(output.metadata, sep = '\t', index = False)
		SeqIO.write(combined_sequences, 'output.sequences', 'fasta')

		print("Creating zip")
		zip_obj_download = ZipFile(output.download_zip, "w", compression = ZIP_DEFLATED, compresslevel = 9)
		zip_obj_download.write(output.sequences, arcname = "combined_sequences.fasta")
		zip_obj_download.write(output.metadata, arcname = "combined_metadata.tsv")
		zip_obj_download.close()

		storage.store("total_count", len(combined_metadata))
		send_data_to_websocket('SUCCESS_ZIP', 'combine_data', None)
		# except:
		# 	error_traceback = traceback.format_exc()
		# 	send_data_to_websocket('ERROR', 'clean_data', error_traceback)
		# 	pathlib.Path(str(log)).write_text(error_traceback)
		# 	raise
