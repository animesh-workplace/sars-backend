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
			nextstrain_path = f"{os.environ.get('MODULE_PREFIX')}/modules/nextstrain/v1.0.0_a9"
			if(os.path.exists(f"{nextstrain_path}/source")):
				shell(
					f"""
						git -C {nextstrain_path}/source pull
						cp -rf {nextstrain_path}/source/data/sars-cov-2/. workflow/resources/data/
					"""
				)
			else:
				shell(
					f"""
						git clone https://github.com/nextstrain/nextclade.git {nextstrain_path}/source
						cp -r {nextstrain_path}/source/data/sars-cov-2/ workflow/resources/data
					"""
				)
		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'update', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
