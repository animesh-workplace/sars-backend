rule clade_report:
	message:
		"""
			Generating clade report for cluster:
				- using nextclade
		"""
	input:
		alignment = rules.align.output.alignment,
	output:
		report = "{base_path}/Analysis/{date}/reports/clade_report.tsv",
		other = directory("{base_path}/Analysis/{date}/reports/clade_report/")
	log: "{base_path}/Analysis/{date}/log/clade_report_error.log"
	threads: 20
	run:
		try:
			shell(
				"""
					nextclade --input-fasta {input.alignment} --output-tsv {output.report} --jobs {threads} \
					--input-root-seq workflow/resources/data/reference.fasta --input-tree workflow/resources/data/tree.json \
					--input-qc-config workflow/resources/data/qc.json --input-pcr-primers workflow/resources/data/primers.csv \
					--input-gene-map workflow/resources/data/genemap.gff --output-dir {output.other}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'split_clade_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
