checkpoint partition_sequences:
	message:
		"""
			Splitting sequences into {params.sequences_per_group} per group for faster clade reports
		"""
	input:
		update = rules.update.log,
		sequences = rules.combine_fixed_data.output.sequences
	output:
		split_sequences = directory("{base_path}/Analysis/{date}/alignment/split_sequences/pre/")
	log: "{base_path}/Analysis/{date}/log/alignment/partition_sequences_error.log"
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

rule partitions_intermediate:
	message:
		"""
			Copying sequence fastas for cluster: {wildcards.cluster}
		"""
	input: "{base_path}/Analysis/{date}/alignment/split_sequences/pre/{cluster}.fasta"
	output: "{base_path}/Analysis/{date}/alignment/split_sequences/post/{cluster}.fasta"
	log: os.path.join("{base_path}/Analysis/{date}/log/alignment/partitions_intermediate/{cluster}_error.log")
	run:
		try:
			shell(
				"""
					cp {input} {output}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'partitions_intermediate', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise

rule align:
	message:
		"""
			Aligning sequences to {input.reference}
			  - gaps relative to reference are considered real
			Cluster:  {wildcards.cluster}
		"""
	input:
		sequences = rules.partitions_intermediate.output,
		reference = 'workflow/resources/data/reference.fasta'
	output:
		alignment = os.path.join("{base_path}", "Analysis", "{date}", "alignment", "split_alignments/{cluster}.fasta"),
		alignment_other = directory("{base_path}/Analysis/{date}/reports/clade_report/split_extra/split_{cluster}")
	log: "{base_path}/Analysis/{date}/log/alignment/align/{cluster}_error.log"
	threads: 2
	run:
		try:
			shell(
				"""
				nextalign \
					--sequences {input.sequences} --reference {input.reference} --jobs {threads} \
					--genemap workflow/resources/data/genemap.gff --output-fasta {output.alignment} \
					--output-dir {output.alignment_other}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'align', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise

def _get_alignments(wildcards):
	checkpoint_output = checkpoints.partition_sequences.get(**wildcards).output[0]
	return expand(
			os.path.join(wildcards.base_path, "Analysis", wildcards.date, "alignment/split_alignments/{i}.fasta"),
			i=glob_wildcards(os.path.join(checkpoint_output, "{i}.fasta")).i
	)

rule aggregate_alignments:
	message:
		"""
			Collecting alignments
		"""
	input:
		alignments = _get_alignments
	output:
		alignment = os.path.join("{base_path}", "Analysis", "{date}", "alignment", "combined_sequences_aligned.fasta")
	log: "{base_path}/Analysis/{date}/log/alignment/align/aggregate_alignments_error.log"
	run:
		try:
			shell(
				"""
					cat {input.alignments} > {output.alignment}
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'aggregate_alignments', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
