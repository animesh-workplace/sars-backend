rule mutation_report:
	message: "Finding all Mutations and Deletions [Gene wise] (Overall & State wise)"
	input:
		split_state = rules.split_state.output.state_wise_path,
		metadata = rules.combine_clade_lineage.output.nextstrain
	output:
		overall_mutation = "{base_path}/Analysis/{date}/reports/mutation_count_report.xlsx"
	log: "{base_path}/Analysis/{date}/log/mutation_report_error.log"
	run:
		try:
			shell(
				"""
					python workflow/scripts/mutation_report.py --date {wildcards.date} \
						--metadata {input.metadata} --basepath {wildcards.base_path} > {log} 2>&1
				"""
			)
		except Exception as e:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'mutation_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
