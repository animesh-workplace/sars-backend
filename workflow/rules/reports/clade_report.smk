rule partition_aligned_sequences:
	input:
		sequences = rules.aggregate_alignments.output.alignment
	output:
		split_sequences = directory(os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report"))
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'partition_aligned_sequences_error.log')
	params:
		sequences_per_group = 150
	run:
		try:
			shell(
				"""
				python workflow/scripts/partition-sequences.py \
					--sequences {input.sequences} \
					--output-dir {output.split_sequences} \
					--sequences-per-group {params.sequences_per_group} \
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'partition_aligned_sequences', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise

rule partition_clade_report:
	message: "Finding the clade definitions for each sequence and generating the report"
	input:
		rules.partition_aligned_sequences.output.split_sequences,
		os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report/{clade_cluster}.fasta"),
	output:
		os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report/clade_report_{clade_cluster}.tsv")
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'clade_report/{clade_cluster}_error.log')
	threads: 2
	run:
		try:
			shell(
				"""
					nextclade -i {input} -t {output} -j {threads}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'partition_clade_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise

def _get_all_clade_report(wildcards):
	checkpoint_output = os.path.join(wildcards.base_path, "Analysis", wildcards.date, "reports", "clade_report")
	print(checkpoint_output)
	return expand(
			os.path.join(wildcards.base_path, "Analysis", wildcards.date, "reports", "clade_report/clade_report_{i}.tsv"),
			i=glob_wildcards(os.path.join(checkpoint_output, "clade_report_{i}.tsv")).i
	)

rule clade_report:
	message: "Finding the nextstrain clade for each sequence and generating the report"
	input:
		alignments = _get_all_clade_report
	threads: 20
	output:
		clade_report = os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report.tsv")
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'clade_report_error.log')
	run:
		try:
			shell(
				"""
					touch {output.clade_report}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'lineage_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
