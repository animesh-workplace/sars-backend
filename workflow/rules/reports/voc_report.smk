rule voc_report:
	message: "Get Specific VoC/VoI report"
	input:
		metadata = rules.combine_clade_lineage.output.nextstrain,
	output:
		voc_report = os.path.join("{base_path}/Analysis/{date}/reports", "voc_report.xlsx")
	run:
		with open("workflow/resources/voc_tracking.json") as f:
			voc_to_track = json.loads(f.read())

		metadata = pandas.read_csv(input.metadata, delimiter = '\t', encoding = 'utf-8', low_memory = False)
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
			voc_metadata[['strain', 'lab_id', 'division', 'location', 'date', 'lineage', 'clade', 'scorpio_call']].to_excel(voc_type_writer, f'{voc_type}', index = False)

		voc_type_writer.save()
