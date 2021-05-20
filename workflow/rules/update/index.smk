rule update:
	message: "Updating nextclade and pangolin"
	output:
		os.path.join('{base_path}', 'combined_files', '{date}', 'log', 'update_log')
	run:
		try:
			shell(
				"""
					pangolin --update
					# npm update --global @neherlab/nextclade
					touch {output}
				"""
			)
		except:
			send_data_to_websocket('ERROR', 'update', traceback.format_exc())
			raise
