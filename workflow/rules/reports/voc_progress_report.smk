rule voc_progress_report:
	message: "Get Specific VoC/VoI Monthly Progress report (State wise & District wise)"
	input:
		split_state = rules.split_state.output.state_wise_path,
		metadata = rules.combine_clade_lineage.output.nextstrain
	output:
		voc_report = "{base_path}/Analysis/{date}/reports/voc_state_monthly_report.xlsx"
	log: "{base_path}/Analysis/{date}/log/voc_progress_report_error.log"
	run:
		try:
			print('Generating VoC/VoI Monthly Progress report State wise')
			shell(
				"""
					python workflow/scripts/voc_progress_report.py \
						--metadata {input.metadata} \
						--output {output.voc_report} \
						--type division
				"""
			)

			print('Generating VoC/VoI Monthly Progress report District wise')
			metadata = pandas.read_csv(input.metadata, delimiter = '\t', encoding = 'utf-8')
			all_states = pandas.unique(metadata['division']).tolist()

			for i in all_states:
				print(i)
				state_metadata_url = f"{wildcards.base_path}/Analysis/{wildcards.date}/reports/state_wise/{i.replace(' ','_')}/{i.replace(' ','_')}_metadata.tsv"
				state_output_url = f"{wildcards.base_path}/Analysis/{wildcards.date}/reports/state_wise/{i.replace(' ','_')}/{i.replace(' ','_')}_voc_district_monthly_report.xlsx"
				shell(
					f"""
						python workflow/scripts/voc_progress_report.py \
							--metadata {state_metadata_url} \
							--output {state_output_url} \
							--type location
					"""
				)
		except Exception as e:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'voc_progress_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
