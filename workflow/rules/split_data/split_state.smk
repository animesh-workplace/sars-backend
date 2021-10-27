rule split_state:
	message: "Splitting data state wise"
	input:
		sequences 	= rules.clade_report.output.other,
		metadata 	= rules.combine_clade_lineage.output.nextstrain,
	output:
		state_wise_path = directory("{base_path}/Analysis/{date}/reports/state_wise")
	log: "{base_path}/Analysis/{date}/log/split_state_error.log"
	run:
		try:
			metadata = pandas.read_csv(input.metadata, delimiter = '\t', encoding = 'utf-8')
			sequence = SeqIO.to_dict(SeqIO.parse(os.path.join(input.sequences, 'combined_sequences.aligned.fasta'), 'fasta'))
			all_states = pandas.unique(metadata['division']).tolist()

			for i in all_states:
				os.makedirs(os.path.join(output.state_wise_path, f"{i.replace(' ','_')}"), exist_ok = True)

				state_metadata = metadata.iloc[metadata.index[metadata['division'].isin([i])].tolist()]
				state_metadata.to_csv(os.path.join(output.state_wise_path, f"{i.replace(' ','_')}/{i.replace(' ','_')}_metadata.tsv"), sep = '\t', index = False)

				state_sequences = [sequence[i]  for i in state_metadata['strain']]
				SeqIO.write(state_sequences, os.path.join(output.state_wise_path, f"{i.replace(' ','_')}/{i.replace(' ','_')}_sequence.fasta"), 'fasta')
		except Exception as e:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'split_state', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
