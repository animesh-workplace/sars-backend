rule specific_voc:
	message: "Get Specific VoC/VoI report"
	input:
		metadata = rules.combine_clade_pangolin.output.nextstrain,
		overall_mutation = rules.top_mutation.output.overall_mutation
	output:
		voc_report = os.path.join("{base_path}/combined_files/{date}/Analysis", "specific_voc_report.xlsx")
	run:
		voc_to_track = {
			'UK': 		[
				{ 'pangolin'	: ['B.1.1.7'] },
				{ 'nextstrain'	: ['20I/501Y.V1'] }
			],
			'SA': 		[
				{ 'pangolin' 	: ['B.1.315'] },
				{ 'nextstrain' 	: ['20H/501Y.V2'] }
			],
			'Brazil':	[
				{ 'pangolin' 	: ['P.1'] },
				{ 'nextstrain' 	: ['20J/501Y.V3'] }
			],
			'B.1.617':		[
				{ 'pangolin' : ['B.1.617'] }
			],
			'B.1.617.1':		[
				{ 'pangolin' : ['B.1.617.1'] }
			],
			'B.1.617.2':		[
				{ 'pangolin' : ['B.1.617.2'] }
			],
			'B.1.617.3':		[
				{ 'pangolin' : ['B.1.617.3'] }
			],
			'B.1.617_combined':		[
				{ 'pangolin' : ['B.1.617', 'B.1.617.1', 'B.1.617.2', 'B.1.617.3'] }
			],
			'B.1.618':		[
				{ 'pangolin': ['B.1.618'] }
			],
		}
		metadata = pandas.read_csv(input.metadata, delimiter = '\t', encoding = 'utf-8', low_memory = False)
		# os.makedirs(os.path.join("{base_path}/combined_files/{date}/Analysis"), exist_ok = True)
		voc_type_writer = ExcelWriter(output.voc_report)

		for voc_type, entries in voc_to_track.items():
			voc_metadata = pandas.DataFrame()
			for i in entries:
				if('pangolin' in list(i.keys())):
					voc_metadata = pandas.concat([ voc_metadata, metadata.loc[metadata['lineage'].isin(i['pangolin'])] ])
				if('nextstrain' in list(i.keys())):
					voc_metadata = pandas.concat([ voc_metadata, metadata.loc[metadata['clade'].isin(i['nextstrain'])] ])

			voc_metadata.reset_index(drop = True, inplace = True)
			voc_metadata.drop_duplicates(subset = ['strain'], ignore_index = True, inplace = True)
			voc_metadata[['strain', 'lab_id', 'division', 'location', 'date', 'lineage', 'clade']].to_excel(voc_type_writer, f'{voc_type}', index = False)

		voc_type_writer.save()
