rule top_mutation:
	message: "Finding all Mutations and Deletions [Gene wise] (Overall & State wise)"
	input:
		sequences = rules.aggregate_alignments.output,
		metadata = rules.combine_clade_pangolin.output.nextstrain
	output:
		overall_mutation = os.path.join("{base_path}/combined_files/{date}/Analysis", "top_mutation.xlsx"),
		state_wise_mutation = directory(os.path.join("{base_path}/combined_files/{date}/Analysis", "state_wise"))
	run:
		try:
			genes = ['E', 'M', 'N', 'ORF1a', 'ORF1b', 'ORF3a', 'ORF6', 'ORF7a', 'ORF7b', 'ORF8', 'ORF9b', 'S']
			metadata = pandas.read_csv(input.metadata, delimiter = '\t', encoding = 'utf-8')
			sequence = SeqIO.to_dict(SeqIO.parse(str(input.sequences), 'fasta'))
			all_states = pandas.unique(metadata['division']).tolist()
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

			os.makedirs(os.path.join(output.state_wise_mutation, 'metadata'), exist_ok = True)
			os.makedirs(os.path.join(output.state_wise_mutation, 'mutations'), exist_ok = True)

			for i in all_states:
				writer_state = ExcelWriter(os.path.join(output.state_wise_mutation, 'mutations', f"{i.replace(' ','_')}_mutations.xlsx"))
				temp = []
				os.makedirs(os.path.join(output.state_wise_mutation, 'metadata', f"{i.replace(' ','_')}"), exist_ok = True)
				state_metadata = metadata.iloc[metadata.index[metadata['division'].isin([i])].tolist()]
				state_metadata.to_csv(os.path.join(output.state_wise_mutation, 'metadata', f"{i.replace(' ','_')}", f"{i.replace(' ','_')}_metadata.tsv"), sep = '\t', index = False)
				state_sequences = [sequence[i]  for i in state_metadata['strain']]
				SeqIO.write(state_sequences, os.path.join(output.state_wise_mutation, 'metadata', f"{i.replace(' ','_')}", f"{i.replace(' ','_')}_sequence.fasta"), 'fasta')

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
			send_data_to_websocket('ERROR', 'top_mutation', traceback.format_exc())
			raise
