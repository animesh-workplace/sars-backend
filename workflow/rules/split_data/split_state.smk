rule split_state:
	message: "Splitting data state wise"
	input:
		sequence 	= rules.santize_data.output.sequence,
		metadata 	= rules.combine_clade_lineage.output.nextstrain,
	output:
		state_wise_path = directory("{base_path}/Analysis/{date}/reports/state_wise")
	log: "{base_path}/Analysis/{date}/log/split_state_error.log"
	run:
		try:
			shell(
				"""
					python workflow/scripts/split_data.py --date {wildcards.date} \
						--metadata {input.metadata} --sequence {input.sequence} \
						--basepath {wildcards.base_path} > {log} 2>&1
				"""
			)
		except Exception as e:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'split_state', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
