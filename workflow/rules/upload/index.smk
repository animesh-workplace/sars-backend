rule upload_to_ondedrive:
	message: "Uploading Files to Onedrive"
	input:
		rules.voc_id_report.output,
		rules.mutation_report.output,
		rules.voc_progress_report.output,
		rules.lineage_substitution_deletion_report.output,
	log: "{base_path}/Analysis/{date}/log/upload_error.log"
	run:
		try:
			print("Copying files onto OneDrive")
			shell(
				f"""
					mkdir -p OneDrive/{wildcards.date}/reports
					cp -rv {wildcards.base_path}/Analysis/{wildcards.date}/reports/state_wise OneDrive/{wildcards.date}/reports/
					cp -rv {wildcards.base_path}/Analysis/{wildcards.date}/reports/*.tsv OneDrive/{wildcards.date}/reports/
					cp -rv {wildcards.base_path}/Analysis/{wildcards.date}/reports/*.csv OneDrive/{wildcards.date}/reports/
					cp -rv {wildcards.base_path}/Analysis/{wildcards.date}/reports/*.xlsx OneDrive/{wildcards.date}/reports/
					cp -rv {wildcards.base_path}/Analysis/{wildcards.date}/alignment OneDrive/{wildcards.date}/
					cp -rv {wildcards.base_path}/Analysis/{wildcards.date}/log OneDrive/{wildcards.date}/
					cp -rv {wildcards.base_path}/Analysis/{wildcards.date}/nextstrain OneDrive/{wildcards.date}/
					cp -rv {wildcards.base_path}/Analysis/{wildcards.date}/combined_files OneDrive/{wildcards.date}/
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			if(config['websocket']):
				send_data_to_websocket('ERROR', 'update', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
