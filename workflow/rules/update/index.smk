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
			nextstrain_path = f"{os.environ.get('MODULE_PREFIX')}/modules_source/nextstrain/v1.0.0_a9/package"
			shell(
				f"""
					curl -fsSL 'https://github.com/nextstrain/nextclade/releases/latest/download/nextalign-Linux-x86_64' -o {nextstrain_path}/nextalign && chmod +x {nextstrain_path}/nextalign
					curl -fsSL 'https://github.com/nextstrain/nextclade/releases/latest/download/nextclade-Linux-x86_64' -o {nextstrain_path}/nextclade && chmod +x {nextstrain_path}/nextclade
					nextclade --version
					nextalign --version
					nextclade dataset get --name='sars-cov-2' --output-dir='workflow/resources/data'
				"""
			)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'update', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
