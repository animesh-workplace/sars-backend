rule update:
	message: "Updating nextclade and pangolin"
	output:
		os.path.join('{base_path}', 'combined_files', '{date}', 'update_log')
	run:
		shell(
			"""
				pangolin --update
				# npm update --global @neherlab/nextclade
				touch {output}
			"""
		)
