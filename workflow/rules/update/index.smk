rule update:
	message: "Updating nextclade and pangolin"
	log: "{base_path}/Analysis/{date}/log/update_error.log"
	run:
		try:
			shell(
				"""
					pangolin --update
					pangolin --update-data
					# npm update --global @neherlab/nextclade
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'update', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
