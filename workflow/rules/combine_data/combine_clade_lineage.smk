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

			nextstrain_metadata['date'] = pandas.to_datetime(nextstrain_metadata['date'], format="%Y-%m-%d")
			nextstrain_metadata = nextstrain_metadata.assign(collection_month = nextstrain_metadata['date'].dt.strftime('%b-%Y'), WHO_label = "Others")
			nextstrain_metadata = nextstrain_metadata.merge(nextclade_pangolin, on = 'strain', how = 'inner')

			with open("workflow/resources/voc_tracking_frontend.json") as f:
				voc_to_track = json.loads(f.read())

			for voc_type, entries in voc_to_track.items():
				for i in entries:
					if('pangolin' in list(i.keys())):
						for (key, value) in i['pangolin'].items():
							if(key == 'exact'):
								nextstrain_metadata['WHO_label'][nextstrain_metadata['lineage'].isin(value)] = voc_type
							elif(key == 'contains'):
								nextstrain_metadata['WHO_label'][nextstrain_metadata['lineage'].str.contains(value)] = voc_type

					if('nextstrain' in list(i.keys())):
						for (key, value) in i['nextstrain'].items():
							if(key == 'exact'):
								nextstrain_metadata['WHO_label'][nextstrain_metadata['lineage'].isin(value)] = voc_type
							elif(key == 'contains'):
								nextstrain_metadata['WHO_label'][nextstrain_metadata['lineage'].str.contains(value)] = voc_type

			nextstrain_metadata.to_csv(output.nextstrain, sep = '\t', index = False)

			# For INSACOG DataHub
			nextclade_pangolin.rename(columns = {'strain': 'Virus name'}, inplace = True)
			insacog_datahub_metadata = metadata.merge(nextclade_pangolin, on = 'Virus name', how = 'inner')
			insacog_datahub_metadata.to_csv(output.insacog_datahub, sep = '\t', index = False)

			# Removing NIV sequences
			frontend_metadata = insacog_datahub_metadata[~insacog_datahub_metadata['Submitting lab'].isin(['NIV'])]
			frontend_nextstrain_metadata = nextstrain_metadata[~nextstrain_metadata['submitting_lab'].isin(['NIV']) & ~nextstrain_metadata['lineage'].isin(['None'])]

			database_entry = {}
			database_entry['map_data'] = []
			database_entry['metadata_link'] = output.insacog_datahub

			database_entry['states_covered'] 		= len(pandas.unique(frontend_metadata['State']))
			database_entry['genomes_sequenced'] 	= len(frontend_metadata)
			database_entry['lineage_graph_data']	= { 'month_data': {}, 'lineage': [] }
			database_entry['lineages_catalogued'] 	= len(pandas.unique(frontend_metadata['lineage']))

			# Calculation of all variants
			if(not frontend_metadata['aaSubstitutions'].dropna().empty):
				all_variants = [mutations for (index, mutations) in  frontend_metadata['aaSubstitutions'].dropna().str.split(',').to_dict().items()]
			if(not frontend_metadata['aaDeletions'].dropna().empty):
				all_variants = all_variants + [mutations for (index, mutations) in  frontend_metadata['aaDeletions'].dropna().str.split(',').to_dict().items()]
			all_variants = list(itertools.chain(*all_variants))
			unique_variants = pandas.unique(all_variants).tolist()

			database_entry['variants_catalogued'] = len(unique_variants)

			# Calculation of State wise distribution
			for (key,value) in dict(collections.Counter(frontend_metadata['State'].tolist())).items():
				database_entry['map_data'].append({
					"name": key,
					"value": value
				})

			# Calculation of lineage distribution
			month_values = sorted(frontend_nextstrain_metadata['date'])
			month_keys = [i.strftime('%b-%Y') for i in month_values]
			month_keys = pandas.DataFrame(month_keys)[0].unique().tolist()
			month_wise_mutation_percent = pandas.DataFrame(index = list(pandas.unique(frontend_nextstrain_metadata['WHO_label'])), columns = month_keys)

			month_count = dict(collections.Counter(frontend_nextstrain_metadata['collection_month']))
			lineage_wise_count = pandas.crosstab(frontend_nextstrain_metadata.WHO_label, frontend_nextstrain_metadata.collection_month)

			for i in month_keys:
				month_wise_mutation_percent[i] = round((lineage_wise_count[i]/month_count[i])*100, 2)

			for i in month_wise_mutation_percent.T['Jan-2021':].index:
				database_entry['lineage_graph_data']['month_data'][i] = month_count[i]

			temp = {}
			for (key, value) in month_wise_mutation_percent.T['Jan-2021':].to_dict(orient = 'list').items():
				temp[key] = { 'name': key, 'value': value }

			order_lineage = ['Omicron', 'Delta', 'Alpha', 'Beta', 'Gamma', 'Kappa', 'Eta', 'Iota', 'Epsilon', 'Zeta', 'Others']
			for i in order_lineage:
				database_entry['lineage_graph_data']['lineage'].append(temp[i])

			storage.store("total_count", len(insacog_datahub_metadata))
			storage.store("frontend_count", len(frontend_metadata))
			if(config['websocket']):
				send_data_to_websocket('SUCCESS_METADATA', 'combine_clade_lineage', database_entry | storage.fetch("tool_version"))
		except:
			error_traceback = traceback.format_exc()
			if(config['websocket']):
				send_data_to_websocket('ERROR', 'combine_clade_lineage', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise

