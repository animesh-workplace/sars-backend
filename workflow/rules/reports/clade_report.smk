rule clade_report:
	message: "Finding the clade definitions for each sequence and generating the report"
	input: rules.aggregate_alignments.output
	threads: 20
	output:
		clade_report = os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report.tsv")
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'clade_report_error.log')
	run:
		try:
			shell(
				"""
					nextclade -i {input} -t {output.clade_report} -j {threads}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'clade_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
