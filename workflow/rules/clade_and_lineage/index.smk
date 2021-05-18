rule get_pangolin:
	message: "Finding the pangolin lineage for each sequence"
	input: rules.aggregate_alignments.output
	threads: 20
	output:
		lineage_report = os.path.join("{base_path}", "combined_files", "{date}", "lineage_report.csv")
	run:
		try:
			shell(
				"""
					pangolin {input} --outfile {output.lineage_report} > pangolin_output1 2> pangolin_output2
				"""
			)
		except:
			send_data_to_websocket('ERROR', 'get_pangolin', 'Error occured while getting pangolin lineage')

rule get_clade:
	message: "Finding the clade definitions for each sequence"
	input: rules.aggregate_alignments.output
	threads: 20
	output:
		clade_label = os.path.join("{base_path}", "combined_files", "{date}", "clade_label.tsv")
	run:
		try:
			shell(
				"""
					nextclade -i {input} -t {output.clade_label} -j {threads}
				"""
			)
		except:
			send_data_to_websocket('ERROR', 'get_clade', 'Error occured while getting clade definitions from nextclade')

rule combine_clade_pangolin:
	message: "Creating a new metadata with clade and lineage definitions"
	input:
		lineage = rules.get_pangolin.output.lineage_report,
		clade = rules.get_clade.output.clade_label,
		metadata = rules.combine_data.output.metadata,
		sequences = rules.combine_data.output.sequences,
	output:
		nextstrain = os.path.join("{base_path}", "combined_files", "{date}", "nextstrain_metadata.tsv")
	run:
		try:
			nextstrain_labels = ['strain', 'virus', 'gisaid_epi_isl', 'genbank_accession', 'date', 'region', 'country', 'division', 'location', 'region_exposure', 'country_exposure', 'division_exposure', 'segment', 'length', 'host', 'age', 'sex', 'originating_lab', 'submitting_lab', 'authors', 'url', 'title', 'paper_url', 'date_submitted', 'purpose_of_sequencing']
			metadata = pandas.read_csv(input.metadata, delimiter = '\t', encoding = 'utf-8', low_memory = False)
			sequence = SeqIO.to_dict(SeqIO.parse(input.sequences, 'fasta'))

			nextclade_metadata = pandas.read_csv(input.clade, delimiter = '\t', encoding = 'utf-8', low_memory = False)
			nextclade_metadata.rename(columns = {'seqName': 'strain'}, inplace = True)

			pangolin_metadata = pandas.read_csv(input.lineage, delimiter = ',', encoding = 'utf-8', low_memory = False)
			pangolin_metadata.rename(columns = {'taxon': 'strain'}, inplace = True)

			nextclade_pangolin = pandas.merge(
				nextclade_metadata[['strain', 'clade', 'totalInsertions', 'totalMissing', 'totalNonACGTNs', 'nonACGTNs', 'substitutions', 'deletions', 'aaSubstitutions', 'aaDeletions']],
				pangolin_metadata[['strain', 'lineage', 'note', 'pangoLEARN_version']],
				on = 'strain', how = 'inner'
			)

			# For Nextstrain Analysis
			nextstrain_metadata = pandas.DataFrame(columns = nextstrain_labels)
			nextstrain_metadata = nextstrain_metadata.assign(
				strain = metadata['Virus name'],
				virus = metadata['Type'],
				gisaid_epi_isl = [f'EPI_ISL_{i}' for i in metadata.index],
				genbank_accession = ['?' for i in metadata.index],
				date = metadata['Collection date'],
				region = metadata['Location'],
				country = metadata['Country'],
				division = metadata['State'],
				location = metadata['District'],
				region_exposure = metadata['Location'],
				country_exposure = metadata['Country'],
				division_exposure = metadata['State'],
				segment = ['genome' for i in metadata.index],
				host = metadata['Host'],
				age = metadata['Patient age'],
				sex = metadata['Gender'],
				originating_lab = metadata['Originating lab'],
				submitting_lab = metadata['Submitting lab'],
				authors = metadata['Authors'],
				url = ['?' for i in metadata.index],
				title = ['?' for i in metadata.index],
				paper_url = ['?' for i in metadata.index],
				date_submitted = metadata['Collection date'],
				purpose_of_sequencing = ['?' for i in metadata.index]
			)

			nextstrain_metadata = nextstrain_metadata.merge(nextclade_pangolin, on = 'strain', how = 'inner')
			nextstrain_metadata.to_csv(output.nextstrain, sep = '\t', index = False)
		except:
			send_data_to_websocket('ERROR', 'combine_clade_pangolin', 'Error occured while combining clade and lineage information')
