rule align:
	message:
		"""
			Aligning sequences to {input.reference}
			  - gaps relative to reference are considered real
		"""
	input:
		update = rules.update.log,
		sequences = rules.combine_fixed_data.output.sequences,
		reference = 'workflow/resources/data/reference.fasta',
	output:
		alignment = os.path.join("{base_path}", "Analysis", "{date}", "alignment", "combined_sequences_aligned.fasta"),
		alignment_other = directory("{base_path}/Analysis/{date}/alignment/extra/")
	log: "{base_path}/Analysis/{date}/log/alignment/align_error.log"
	threads: 20
	run:
		try:
			shell(
				"""
				nextalign \
					--sequences {input.sequences} --reference {input.reference} --jobs {threads} \
					--genemap workflow/resources/data/genemap.gff --output-fasta {output.alignment} \
					--output-dir {output.alignment_other} --genes=E,M,N,ORF1a,ORF1b,ORF3a,ORF6,ORF7a,ORF7b,ORF8,ORF9b,S
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'align', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
