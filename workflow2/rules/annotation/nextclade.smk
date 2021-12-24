rule clade_report:
	message: "Finding the nextclade for each sequence and generating the report"
	input:
		dataset		= 'workflow/resources/data',
		sequence 	= rules.santize_data.output.sequence,
	output:
		other 	= directory("{base_path}/Analysis/{date}/alignment/"),
		report 	= "{base_path}/Analysis/{date}/reports/clade_report.tsv",
	log: "{base_path}/Analysis/{date}/log/clade_report_error.log"
	threads: 10
	run:
		try:
			shell(
				"""
					nextclade run --input-fasta {input.sequence} --output-tsv {output.report} --jobs {threads} \
					--input-dataset {input.dataset} --output-dir {output.other} > {log} 2>&1
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'split_clade_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
