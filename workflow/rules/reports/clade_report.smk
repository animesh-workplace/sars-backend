checkpoint partition_alignment:
	message:
		"""
			Splitting alignments into {params.alignment_per_group} per group for faster clade reports
		"""
	input:
		alignment = rules.aggregate_alignments.output.alignment
	output:
		split_alignment = directory(os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report/split_alignment/pre/"))
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'clade_report/partition_alignment_error.log')
	params:
		alignment_per_group = 150
	run:
		try:
			shell(
				"""
				python workflow/scripts/partition-sequences.py \
					--sequences {input.alignment} \
					--output-dir {output.split_alignment} \
					--sequences-per-group {params.alignment_per_group} \
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'partition_alignment', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise

rule partition_alignment_intermediate:
	message:
		"""
			Copying sequence fasta for cluster: {wildcards.clade_cluster}
		"""
	input:
		os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report/split_alignment/pre/{clade_cluster}.fasta")
	output:
		os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report/split_alignment/post/{clade_cluster}.fasta")
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'clade_report/partitions_alignment_intermediate/{clade_cluster}_error.log')
	run:
		try:
			shell(
				"""
					cp {input} {output}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'partition_alignment_intermediate', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise

rule split_clade_report:
	message:
		"""
			Generating clade report for cluster:
				- using nextclade
			Cluster: {wildcards.clade_cluster}
		"""
	input:
		split_alignment = rules.partition_alignment_intermediate.output,
	output:
		split_report = os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report/split_report/{clade_cluster}.tsv")
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'clade_report/split_clade_report/{clade_cluster}_error.log')
	threads: 2
	run:
		try:
			shell(
				"""
					nextclade -i {input.split_alignment} -t {output.split_report} -j {threads}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'split_clade_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise

def _get_split_clade_report(wildcards):
	checkpoint_output = checkpoints.partition_alignment.get(**wildcards).output[0]
	return expand(
			os.path.join(wildcards.base_path, "Analysis", wildcards.date, "reports", "clade_report/split_report/{i}.tsv"),
			i = glob_wildcards(os.path.join(checkpoint_output, "{i}.fasta")).i
	)

rule clade_report:
	message:
		"""
			Collecting clade reports
		"""
	input:
		split_clade_report = _get_split_clade_report
	output:
		clade_report = os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report.tsv")
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'clade_report/aggregate_split_clade_report_error.log')
	run:
		try:
			combined_clade_report = pandas.DataFrame()
			for report_url in input.split_clade_report:
				clade_report = pandas.read_csv(report_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)
				combined_clade_report = pandas.concat([combined_clade_report, clade_report])
			combined_clade_report.to_csv(output.clade_report, sep = '\t', index = False)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'aggregate_split_clade_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
