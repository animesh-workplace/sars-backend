checkpoint partition_sequences:
	input:
		sequences = rules.combine_data.output.sequences
	output:
		split_sequences = directory(os.path.join("{base_path}", "combined_files", "{date}", "alignment", "split_sequences/pre/"))
	params:
		sequences_per_group = 150
	run:
		try:
			shell(
				"""
				python workflow/scripts/partition-sequences.py \
					--sequences {input.sequences} \
					--sequences-per-group {params.sequences_per_group} \
					--output-dir {output.split_sequences}
				"""
			)
		except:
			send_data_to_websocket('ERROR', 'partition_sequences', 'Error occured while paritioning sequences')

rule partitions_intermediate:
	message:
		"""
		partitions_intermediate: Copying sequence fastas
		{wildcards.cluster}
		"""
	input:
		os.path.join("{base_path}", "combined_files", "{date}", "alignment", "split_sequences/pre/{cluster}.fasta")
	output:
		os.path.join("{base_path}", "combined_files", "{date}", "alignment", "split_sequences/post/{cluster}.fasta")
	run:
		try:
			shell(
				"""
					cp {input} {output}
				"""
			)
		except:
			send_data_to_websocket('ERROR', 'partitions_intermediate', 'Error occured while partitioning intermediates')

rule align:
	message:
		"""
		Aligning sequences to {input.reference}
		  - gaps relative to reference are considered real
		Cluster:  {wildcards.cluster}
		"""
	input:
		sequences = rules.partitions_intermediate.output,
		reference = 'workflow/resources/reference_seq.fasta'
	output:
		alignment = os.path.join("{base_path}", "combined_files", "{date}", "alignment", "split_alignments/{cluster}.fasta")
	threads: 2
	run:
		try:
			shell(
				"""
				augur align \
					--sequences {input.sequences} \
					--reference-sequence {input.reference} \
					--output {output.alignment} \
					--nthreads {threads} \
					--remove-reference \
				"""
			)
		except:
			send_data_to_websocket('ERROR', 'align', 'Error occured while aligning sequences')

def _get_alignments(wildcards):
	checkpoint_output = checkpoints.partition_sequences.get(**wildcards).output[0]
	return expand(
			os.path.join(wildcards.base_path, "combined_files", wildcards.date, "alignment", "split_alignments/{i}.fasta"),
			i=glob_wildcards(os.path.join(checkpoint_output, "{i}.fasta")).i
	)

rule aggregate_alignments:
	message: "Collecting alignments"
	input:
		alignments = _get_alignments
	output:
		alignment = os.path.join("{base_path}", "combined_files", "{date}", "alignment", "aligned.fasta")
	run:
		try:
			shell(
				"""
					cat {input.alignments} > {output.alignment}
				"""
			)
		except:
			send_data_to_websocket('ERROR', 'aggregate_alignments', 'Error occured while combining aligned sequences')
