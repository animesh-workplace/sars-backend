rule lineage_report:
	message: "Finding the pangolin lineage for each sequence and generating the report"
	input: rules.aggregate_alignments.output
	threads: 20
	output:
		lineage_report = os.path.join("{base_path}", "Analysis", "{date}", "reports", "lineage_report.csv")
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'lineage_report_error.log')
	run:
		try:
			shell(
				"""
					pangolin {input} --outfile {output.lineage_report} -t {threads}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'lineage_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise