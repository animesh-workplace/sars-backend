rule lineage_substitution_deletion_report:
	message: "Finding all Mutations and Deletions and ordering it (Overall & State wise)"
	input:
		metadata 	= rules.combine_clade_lineage.output.nextstrain,
		split_state = rules.split_state.output.state_wise_path,
	output:
		lineage_substitution_deletion = "{base_path}/Analysis/{date}/reports/lineage_substitution_deletion_report.tsv"
	log: "{base_path}/Analysis/{date}/log/lineage_substitution_deletion_report_error.log"
	run:
		try:
			shell(
				"""
					python workflow/scripts/lineage_substitution_deletion_report.py --date {wildcards.date} \
						--metadata {input.metadata} --basepath {wildcards.base_path} > {log} 2>&1
				"""
			)
		except Exception as e:
			error_traceback = traceback.format_exc()
			if(config['websocket']):
				send_data_to_websocket('ERROR', 'lineage_substitution_deletion_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
