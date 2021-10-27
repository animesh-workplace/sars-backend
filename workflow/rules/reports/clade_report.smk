rule clade_report:
	message:
		"""
			Generating clade report for cluster:
				- using nextclade
		"""
	input:
		update 		= rules.update.log,
		qc 			= 'workflow/resources/data/qc.json',
		tree 		= 'workflow/resources/data/tree.json',
		primers 	= 'workflow/resources/data/primers.csv',
		genemap 	= 'workflow/resources/data/genemap.gff',
		sequences 	= rules.combine_fixed_data.output.sequences,
		reference 	= 'workflow/resources/data/reference.fasta',
	output:
		other 	= directory("{base_path}/Analysis/{date}/alignment/"),
		report 	= "{base_path}/Analysis/{date}/reports/clade_report.tsv",
	log: "{base_path}/Analysis/{date}/log/clade_report_error.log"
	threads: 20
	run:
		try:
			shell(
				"""
					nextclade run --input-fasta {input.sequences} --output-tsv {output.report} --jobs {threads} \
					--input-root-seq {input.reference} --input-tree {input.tree} \
					--input-qc-config {input.qc} --input-pcr-primers {input.primers} \
					--input-gene-map {input.genemap} --output-dir {output.other}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'split_clade_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
