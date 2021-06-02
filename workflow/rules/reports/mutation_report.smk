rule mutation_report_overall:
	message: "Finding all Mutations and Deletions [Gene wise] (Overall)"
	input:
		metadata = rules.combine_clade_lineage.output.nextstrain
	output:
		overall_mutation = os.path.join("{base_path}/Analysis/{date}/reports", "mutation_count_report.xlsx"),
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'mutation_report_overall_error.log')
	run:
		try:
			genes = ['E', 'M', 'N', 'ORF1a', 'ORF1b', 'ORF3a', 'ORF6', 'ORF7a', 'ORF7b', 'ORF8', 'ORF9b', 'S']
			metadata = pandas.read_csv(input.metadata, delimiter = '\t', encoding = 'utf-8')
			writer = ExcelWriter(output.overall_mutation)

			temp = []
			for i in metadata['aaSubstitutions']:
				if(isinstance(i, str)):
					temp.append(i.split(','))
			aaSubstitution = list(itertools.chain(*temp))

			temp = []
			for i in metadata['aaDeletions']:
				if(isinstance(i, str)):
					temp.append(i.split(','))
			aaDeletions = list(itertools.chain(*temp))
			top_aaDeletions = dict(collections.Counter(aaDeletions))
			pandas.DataFrame.from_dict(data=[top_aaDeletions], orient='columns').transpose().to_excel(writer, 'deletions', header = True)

			for i in genes:
				gene_aaSubstitution = []
				for j in aaSubstitution:
					if(j.startswith(f'{i}')):
						gene_aaSubstitution.append(j)
				gene_subsitution_counter = dict(collections.Counter(gene_aaSubstitution))
				pandas.DataFrame.from_dict(data=[gene_subsitution_counter], orient='columns').transpose().to_excel(writer, i, header = True)

			writer.save()
		except Exception as e:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'mutation_report_state', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise


rule mutation_report_state:
	message: "Finding all Mutations and Deletions [Gene wise] (State wise)"
	input:
		sequences = rules.aggregate_alignments.output,
		metadata = rules.combine_clade_lineage.output.nextstrain
	output:
		state_wise_mutation = directory(os.path.join("{base_path}/Analysis/{date}/reports", "state_wise"))
	log:
		os.path.join('{base_path}', 'Analysis', '{date}', 'log', 'mutation_report_state_error.log')
	run:
		try:
			genes = ['E', 'M', 'N', 'ORF1a', 'ORF1b', 'ORF3a', 'ORF6', 'ORF7a', 'ORF7b', 'ORF8', 'ORF9b', 'S']
			metadata = pandas.read_csv(input.metadata, delimiter = '\t', encoding = 'utf-8')
			sequence = SeqIO.to_dict(SeqIO.parse(str(input.sequences), 'fasta'))
			all_states = pandas.unique(metadata['division']).tolist()

			for i in all_states:
				temp = []
				os.makedirs(os.path.join(output.state_wise_mutation, f"{i.replace(' ','_')}"), exist_ok = True)
				writer_state = ExcelWriter(os.path.join(output.state_wise_mutation, f"{i.replace(' ','_')}", f"{i.replace(' ','_')}_mutation_count_report.xlsx"))
				state_metadata = metadata.iloc[metadata.index[metadata['division'].isin([i])].tolist()]
				state_metadata.to_csv(os.path.join(output.state_wise_mutation, f"{i.replace(' ','_')}", f"{i.replace(' ','_')}_metadata.tsv"), sep = '\t', index = False)
				state_sequences = [sequence[i]  for i in state_metadata['strain']]
				SeqIO.write(state_sequences, os.path.join(output.state_wise_mutation, f"{i.replace(' ','_')}", f"{i.replace(' ','_')}_sequence.fasta"), 'fasta')

				temp = []
				for j in state_metadata['aaSubstitutions']:
					if(isinstance(j, str)):
						temp.append(j.split(','))
				aaSubstitution = list(itertools.chain(*temp))

				temp = []
				for j in state_metadata['aaDeletions']:
					if(isinstance(j, str)):
						temp.append(j.split(','))
				aaDeletions = list(itertools.chain(*temp))
				top_aaDeletions = dict(collections.Counter(aaDeletions))
				pandas.DataFrame.from_dict(data=[top_aaDeletions], orient='columns').transpose().to_excel(writer_state, 'deletions', header = True)

				for j in genes:
					gene_aaSubstitution = []
					for k in aaSubstitution:
						if(k.startswith(f'{j}')):
							gene_aaSubstitution.append(k)
					gene_subsitution_counter = dict(collections.Counter(gene_aaSubstitution))
					pandas.DataFrame.from_dict(data=[gene_subsitution_counter], orient='columns').transpose().to_excel(writer_state, j, header = True)

				writer_state.save()
		except Exception as e:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'mutation_report_state', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
