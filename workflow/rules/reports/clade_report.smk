checkpoint partition_alignment:
	input:
		sequences = rules.aggregate_alignments.output.alignment
	output:
		split_sequences = directory(os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report/split_sequences/pre/"))
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'partition_alignment_error.log')
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
			send_data_to_websocket('ERROR', 'partition_sequences', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise

rule partitions_alignment_intermediate:
	message:
		"""
		partitions_alignment_intermediate: Copying sequence fastas {wildcards.clade_cluster}
		"""
	input:
		os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report/split_sequences/pre/{clade_cluster}.fasta")
	output:
		os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report/split_sequences/post/{clade_cluster}.fasta")
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'partitions_alignment_intermediate/{clade_cluster}_error.log')
	run:
		try:
			shell(
				"""
					cp {input} {output}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'partitions_alignment_intermediate', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise

rule split_clade_report:
	message:
		"""
		Generating Clade report for Cluster: {wildcards.clade_cluster}
		"""
	input:
		sequences = rules.partitions_alignment_intermediate.output,
	output:
		alignment = os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report/split_report/{clade_cluster}.tsv")
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'split_clade_report/{clade_cluster}_error.log')
	threads: 2
	run:
		try:
			shell(
				"""
					nextclade -i {input.sequences} -t {output.alignment} -j {threads}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'split_clade_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise

def _get_alignments(wildcards):
	checkpoint_output = checkpoints.partition_alignment.get(**wildcards).output[0]
	return expand(
			os.path.join(wildcards.base_path, "Analysis", wildcards.date, "reports", "clade_report/split_report/{i}.tsv"),
			i = glob_wildcards(os.path.join(checkpoint_output, "{i}.fasta")).i
	)

rule aggregate_split_clade_report:
	message: "Collecting clade reports"
	input:
		alignments = _get_alignments
	output:
		alignment = os.path.join("{base_path}", "Analysis", "{date}", "reports", "clade_report.tsv")
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'aggregate_alignments_error.log')
	run:
		try:
			shell(
				"""
					cat {input.alignments} > {output.alignment}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'aggregate_split_clade_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
