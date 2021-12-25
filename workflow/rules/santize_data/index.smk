rule santize_data:
	message: "Cleaning & Combining the data"
	input:
		rules.update.log
	output:
		metadata 		= "{base_path}/Analysis/{date}/combined_files/combined_metadata.tsv",
		sequence 		= "{base_path}/Analysis/{date}/combined_files/combined_sequences.fasta",
	log: "{base_path}/Analysis/{date}/log/santize_data_error.log"
	run:
		try:
			shell(
				"""
					python workflow/scripts/santize_data.py \
						--basepath {wildcards.base_path} \
						--date {wildcards.date} > {log} 2>&1
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			if(config['websocket']):
				send_data_to_websocket('ERROR', 'clean_data', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
