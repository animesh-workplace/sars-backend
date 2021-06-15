rule clean_data:
	message: "Cleaning the data"
	input:
		rules.update.log
	output: directory("{base_path}/Fixed_data/{date}")
	log: "{base_path}/Fixed_data/{date}/log/clean_data_error.log"
	run:
		try:
			indian_state_info = pandas.read_csv("workflow/resources/indian_state_district.tsv", delimiter = '\t', encoding = "utf-8", low_memory = False)
			fs_state = fuzzyset.FuzzySet(pandas.unique(indian_state_info['State']), False, 3, 4)
			fs_gender = fuzzyset.FuzzySet(['Male', 'Female', 'Transgender', 'Unknown'], False, 3, 4)
			rgsl_users = os.listdir(f"{wildcards.base_path}/Uploaded_data")
			for rgsl in rgsl_users:
				print(f"Fixing metadata of {rgsl.split('_')[-1]}")
				for path, dirs, files in os.walk(f"{wildcards.base_path}/Uploaded_data/{rgsl}"):
					if(files):
						for i in files:
							file_url = os.path.join(path, i)
							save_url = f"{wildcards.base_path}/Fixed_data/{wildcards.date}/{rgsl}/"
							file_type = i.split('_')[0]
							if(file_type == 'sequence'):
								shell(
									f"""
										mkdir -p {wildcards.base_path}/Fixed_data/{wildcards.date}/{rgsl}/
										cp -r {file_url} {save_url}
									"""
								)
							elif(file_type == 'metadata'):
								shell(
									f"""
										mkdir -p {wildcards.base_path}/Fixed_data/{wildcards.date}/{rgsl}/
									"""
								)
								metadata = pandas.read_csv(file_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)
								fixed_state_name = [fs_state.get(i)[0][1]  for i in metadata['State']]
								metadata['State'] = fixed_state_name

								fixed_collection_date = [arrow.get(i, ['YYYY-MM-DD', 'DD-MM-YYYY', 'YYYY/MM/DD', 'DD/MM/YYYY', 'MM-DD-YYYY']).date() for i in metadata['Collection date']]
								metadata['Collection date'] = fixed_collection_date

								fixed_gender = [ 'Unknown' if(i!=i or len(fs_gender.get(i)) > 1) else fs_gender.get(i)[0][1] for i in metadata['Gender'] ]
								metadata['Gender'] = fixed_gender

								metadata['Submitting lab'] = rgsl.split('_')[-1]
								metadata['Submission date'] = metadata['Collection date']
								metadata['Location'] = 'Asia'
								metadata['Country'] = 'India'

								# fixed_district = []
								# for i in metadata.index:
									# state = metadata.iloc[i]['State']
									# districts = indian_state_info.loc[indian_state_info['State'] == state]['District'].tolist()
									# fs_district = fuzzyset.FuzzySet(districts, False, 3, 4)
									# print(metadata.iloc[i]['District'])
									# print('Unknown' if(len(fs_district.get(metadata.iloc[i]['District'])) == len(districts)) else fs_district.get(metadata.iloc[i]['District'])[0][1])
									# print(fs_district.get(metadata.iloc[i]['District']))
									# fixed_district.append('Unknown' if(len(fs_district.get(metadata.iloc[i]['District'])) == len(districts)) else fs_district.get(metadata.iloc[i]['District'])[0][1])

								# metadata['District'] = fixed_district

								metadata.to_csv(os.path.join(save_url, f"fixed_{i}"), sep = '\t', index = False)

		except:
			error_traceback = traceback.format_exc()
			send_data_to_websocket('ERROR', 'clean_data', error_traceback)
			pathlib.Path(str(log)).write_text(error_traceback)
			raise
