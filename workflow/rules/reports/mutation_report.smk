rule mutation_report:
	message: "Finding all Mutations and Deletions [Gene wise] (Overall & State wise)"
	input:
		split_state = rules.split_state.output.state_wise_path,
		metadata = rules.combine_clade_lineage.output.nextstrain
	output:
		overall_mutation = "{base_path}/Analysis/{date}/reports/mutation_count_report.xlsx"
	log: "{base_path}/Analysis/{date}/log/mutation_report_error.log"
	run:
		try:
			shell(
				"""
					python workflow/scripts/mutation_report.py \
						--metadata {input.metadata} \
						--output {output.overall_mutation}
				"""
			)

			print('Generating mutation report state wise')

			metadata = pandas.read_csv(input.metadata, delimiter = '\t', encoding = 'utf-8')
			all_states = pandas.unique(metadata['division']).tolist()

			for i in all_states:
				print(i)
				state_metadata_url = f"{wildcards.base_path}/Analysis/{wildcards.date}/reports/state_wise/{i.replace(' ','_')}/{i.replace(' ','_')}_metadata.tsv"
				state_output_url = f"{wildcards.base_path}/Analysis/{wildcards.date}/reports/state_wise/{i.replace(' ','_')}/{i.replace(' ','_')}_mutation_count_report.xlsx"
				shell(
					f"""
						python workflow/scripts/mutation_report.py \
							--metadata {state_metadata_url} \
							--output {state_output_url}
					"""
				)
		except Exception as e:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'mutation_report', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
