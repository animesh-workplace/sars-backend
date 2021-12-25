rule voc_id_report:
	message: "Get Specific VoC/VoI IDs report (Overall & State wise)"
	input:
		metadata 		= rules.combine_clade_lineage.output.nextstrain,
		split_state 	= rules.split_state.output.state_wise_path,
	output:
		voc_report = "{base_path}/Analysis/{date}/reports/voc_id_report.xlsx"
	log: "{base_path}/Analysis/{date}/log/voc_report_error.log"
	run:
		try:
			shell(
				"""
					python workflow/scripts/voc_report.py --date {wildcards.date} \
						--metadata {input.metadata} --basepath {wildcards.base_path} > {log} 2>&1
				"""
			)
		except Exception as e:
			error_traceback = traceback.format_exc()
			if(config['websocket']):
				send_data_to_websocket('ERROR', 'voc_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
