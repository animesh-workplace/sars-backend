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
		shell(
			"""
				python workflow/scripts/santize_data.py \
					--basepath {wildcards.base_path} \
					--date {wildcards.date}
			"""
		)

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
