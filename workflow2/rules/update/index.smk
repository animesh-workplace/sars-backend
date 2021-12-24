rule update:
	message: "Updating nextclade and pangolin"
	log: "{base_path}/Analysis/{date}/log/update_error.log"
	run:
		try:
			print("Updating Pangolin")
			shell(
				"""
					pangolin --update
					pangolin --update-data
				"""
			)
			print("Updating Nextclade")
			shell(
				f"""
					curl -fsSL 'https://github.com/nextstrain/nextclade/releases/latest/download/nextalign-Linux-x86_64' -o /bin/nextalign && chmod +x /bin/nextalign
					curl -fsSL 'https://github.com/nextstrain/nextclade/releases/latest/download/nextclade-Linux-x86_64' -o /bin/nextclade && chmod +x /bin/nextclade
					nextclade --version
					nextalign --version
					nextclade dataset get --name 'sars-cov-2' --output-dir 'workflow/resources/data'
				"""
			)
			from scorpio import __version__ as scorpio_version
			from pangolin import __version__ as pangolin_version
			from pangoLEARN import __version__ as pangolearn_version
			from constellations import __version__ as constellation_version
			from pango_designation import __version__ as pango_designation_version
			nextclade_version = subprocess.run('nextclade --version', shell = True, capture_output = True, text = True).stdout.split('\n')[0]
			storage.store("tool_version", {
				'scorpio_version': f"Scorpio version: {scorpio_version}",
				'pangolin_version': f"Pangolin version: {pangolin_version}",
				'nextclade_version': f"Nextclade version: {nextclade_version}",
				'pangolearn_version': f"PangoLearn version: {pangolearn_version}",
				'constellation_version': f"Constellation version: {constellation_version}",
				'pango_designation_version': f"PangoDesignation version: {pango_designation_version}",
			})
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'update', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
