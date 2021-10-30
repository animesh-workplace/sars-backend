rule lineage_report:
	message: "Finding the pangolin lineage for each sequence and generating the report"
	input:
		alignment_path 	= rules.clade_report.output.other,
		clade_report 	= rules.clade_report.log,
	threads: 20
	output:
		lineage_report = "{base_path}/Analysis/{date}/reports/lineage_report.csv"
	log: "{base_path}/Analysis/{date}/log/lineage_report_error.log"
	run:
		try:
			shell(
				"""
					pangolin {input.alignment_path}/combined_sequences.aligned.fasta \
					--outfile {output.lineage_report} -t {threads} > {log} 2>&1
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'lineage_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
