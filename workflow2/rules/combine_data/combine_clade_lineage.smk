rule combine_clade_lineage:
	message: "Creating a new metadata with clade and lineage definitions"
	input:
		metadata 		= rules.santize_data.output.metadata,
		sequence 		= rules.santize_data.output.sequence,
		clade_report 	= rules.clade_report.output.report,
		lineage_report 	= rules.lineage_report.output.report,
	output:
		nextstrain = "{base_path}/Analysis/{date}/nextstrain/nextstrain_metadata.tsv",
		insacog_datahub = "{base_path}/Analysis/{date}/nextstrain/insacog_datahub_metadata.tsv"
	log: "{base_path}/Analysis/{date}/log/combine_clade_lineage_error.log"
	run:
		try:
			nextstrain_labels = ['strain', 'virus', 'gisaid_epi_isl', 'genbank_accession', 'date', 'region', 'country', 'division', 'location', 'region_exposure', 'country_exposure', 'division_exposure', 'segment', 'length', 'host', 'age', 'sex', 'originating_lab', 'submitting_lab', 'authors', 'url', 'title', 'paper_url', 'date_submitted', 'purpose_of_sequencing']
			metadata = pandas.read_csv(input.metadata, delimiter = '\t', encoding = 'utf-8', low_memory = False)
			sequence = SeqIO.to_dict(SeqIO.parse(str(input.sequence), 'fasta'))

			nextclade_metadata = pandas.read_csv(input.clade_report, delimiter = '\t', encoding = 'utf-8', low_memory = False)
			nextclade_metadata.rename(columns = {'seqName': 'strain'}, inplace = True)

			pangolin_metadata = pandas.read_csv(input.lineage_report, delimiter = ',', encoding = 'utf-8', low_memory = False)
			pangolin_metadata.rename(columns = {'taxon': 'strain'}, inplace = True)

			nextclade_pangolin = pandas.merge(
				nextclade_metadata[['strain', 'clade', 'totalInsertions', 'totalMissing', 'totalNonACGTNs', 'nonACGTNs', 'substitutions', 'deletions', 'aaSubstitutions', 'aaDeletions']],
				pangolin_metadata[['strain', 'lineage', 'scorpio_call', 'note', 'pangoLEARN_version']],
				on = 'strain', how = 'inner'
			)

			region_type = pandas.read_csv('workflow/resources/indian_region.tsv', delimiter = '\t', encoding = 'utf-8').set_index('State').T.to_dict()

			# For Nextstrain Analysis
			nextstrain_metadata = pandas.DataFrame(columns = nextstrain_labels)
			nextstrain_metadata = nextstrain_metadata.assign(
				strain = metadata['Virus name'],
				lab_id = metadata['Sample ID given by the submitting lab'],
				last_vaccinated = metadata['Last vaccinated'],
				virus = metadata['Type'],
				gisaid_epi_isl = [f'EPI_ISL_{i}' for i in metadata.index],
				genbank_accession = ['?' for i in metadata.index],
				date = metadata['Collection date'],
				region = metadata['Location'],
				country = metadata['Country'],
				division = metadata['State'],
				location = metadata['District'],
				region_type = [region_type[i]['Region'] for i in metadata['State']],
				region_exposure = metadata['Location'],
				country_exposure = metadata['Country'],
				division_exposure = metadata['State'],
				segment = ['genome' for i in metadata.index],
				length = [len(sequence[i]) for i in metadata['Virus name']],
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

			# For INSACOG DataHub
			nextclade_pangolin.rename(columns = {'strain': 'Virus name'}, inplace = True)
			insacog_datahub_metadata = metadata.merge(nextclade_pangolin, on = 'Virus name', how = 'inner')
			insacog_datahub_metadata.to_csv(output.insacog_datahub, sep = '\t', index = False)

			database_entry = {}
			database_entry['map_data'] = []
			database_entry['metadata_link'] = output.insacog_datahub

			database_entry['states_covered'] 		= len(pandas.unique(insacog_datahub_metadata['State']))
			database_entry['genomes_sequenced'] 	= len(insacog_datahub_metadata)
			database_entry['lineages_catalogued'] 	= len(pandas.unique(insacog_datahub_metadata['lineage']))

			all_variants = []
			for i in insacog_datahub_metadata.index:
				if(isinstance(insacog_datahub_metadata.iloc[i]['aaSubstitutions'], str)):
					all_variants.append(insacog_datahub_metadata.iloc[i]['aaSubstitutions'].split(','))
				if(isinstance(insacog_datahub_metadata.iloc[i]['aaDeletions'], str)):
					all_variants.append(insacog_datahub_metadata.iloc[i]['aaDeletions'].split(','))
			all_variants = list(itertools.chain(*all_variants))
			unique_variants = pandas.unique(all_variants).tolist()

			database_entry['variants_catalogued'] = len(unique_variants)

			for (key,value) in dict(collections.Counter(insacog_datahub_metadata['State'].tolist())).items():
				database_entry['map_data'].append({
					"name": key,
					"value": value
				})

			send_data_to_websocket('SUCCESS_METADATA', 'combine_clade_lineage', database_entry | storage.fetch("tool_version"))
			storage.store("total_count", len(insacog_datahub_metadata))
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'combine_clade_lineage', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise

