rule compress_santize_data:
	message: "Compressing the santized data"
	input:
		rules.update.log,
		metadata = rules.santize_data.output.metadata,
		sequence = rules.santize_data.output.sequence,
	output:
		download_zip = "{base_path}/Download/INSACOG_data_{date}.zip",
	log: "{base_path}/Analysis/{date}/log/santize_data_error.log"
	run:
		try:
			print("Creating zip")
			os.makedirs(f"{wildcards.base_path}/Download/", exist_ok = True)
			zip_obj_download = ZipFile(output.download_zip, "w", compression = ZIP_DEFLATED, compresslevel = 9)
			zip_obj_download.write(input.sequence, arcname = "combined_sequences.fasta")
			zip_obj_download.write(input.metadata, arcname = "combined_metadata.tsv")
			zip_obj_download.close()
			if(config['websocket']):
				send_data_to_websocket('SUCCESS_ZIP', 'combine_data', None)
		except:
			error_traceback = traceback.format_exc()
			if(config['websocket']):
				send_data_to_websocket('ERROR', 'clean_data', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
