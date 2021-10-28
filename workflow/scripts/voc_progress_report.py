import os
import json
import pandas
import argparse
import collections
from pandas import ExcelWriter

parser = argparse.ArgumentParser()
parser.add_argument('--output', help = 'Enter output file')
parser.add_argument('--metadata', help = 'Enter Nexstrain metadata')
parser.add_argument('--type', help = 'Enter division or location, where division is state and location is district')
args = parser.parse_args()
metadata_url = args.metadata
output_url = args.output
type_of_table = args.type

with open("workflow/resources/voc_tracking.json") as f:
	voc_to_track = json.loads(f.read())

metadata = pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)
index_keys = metadata[type_of_table].unique().tolist()
metadata['date'] = pandas.to_datetime(metadata['date'], format="%Y-%m-%d")
month_values = sorted(metadata['date'])
month_keys = [i.strftime('%b-%Y') for i in month_values]
month_keys = pandas.DataFrame(month_keys)[0].unique().tolist()

metadata = metadata.assign(collection_month = metadata['date'].dt.strftime('%b-%Y'))
district_month_wise_sampling = pandas.DataFrame(index = index_keys, columns = month_keys)
writer = ExcelWriter(output_url)

for i in month_keys:
	temp_metadata = metadata.iloc[metadata.index[metadata['collection_month'] == i].tolist()]
	for index,j in dict(collections.Counter(temp_metadata[type_of_table])).items():
		district_month_wise_sampling.loc[index][i] = j

district_month_wise_sampling.to_excel(writer,f'sample_data({type_of_table}_vs_month)')
month_wise_mutation_count = pandas.DataFrame(index = list(voc_to_track.keys()), columns = month_keys)
month_wise_mutation_percent = pandas.DataFrame(index = list(voc_to_track.keys()), columns = month_keys)
month_wise_mutation_combined = pandas.DataFrame(index = list(voc_to_track.keys()), columns = month_keys)
voc_df = pandas.DataFrame(index = index_keys, columns = list(voc_to_track.keys()))

for voc_type, entries in voc_to_track.items():
	voc_metadata = pandas.DataFrame()
	for i in entries:
		if('pangolin' in list(i.keys())):
			voc_metadata = pandas.concat([ voc_metadata, metadata.loc[metadata['lineage'].isin(i['pangolin'])] ])
		if('nextstrain' in list(i.keys())):
			voc_metadata = pandas.concat([ voc_metadata, metadata.loc[metadata['clade'].isin(i['nextstrain'])] ])

	voc_metadata.reset_index(drop = True, inplace = True)
	voc_metadata.drop_duplicates(subset = ['strain'], ignore_index = True, inplace = True)

	for index,k in dict(collections.Counter(voc_metadata['collection_month'])).items():
		month_wise_mutation_count.loc[voc_type][index] = k	

	for index,k in dict(collections.Counter(voc_metadata[type_of_table])).items():
		voc_df.loc[index][voc_type] = k

	final_df_month_count = pandas.DataFrame(index = index_keys, columns = month_keys)
	final_df_month_percent = pandas.DataFrame(index = index_keys, columns = month_keys)
	final_df_month_combined = pandas.DataFrame(index = index_keys, columns = month_keys)	

	for i in month_keys:
		voc_metadata_monthly = voc_metadata.iloc[voc_metadata.index[voc_metadata['collection_month'] == i].tolist()]
		for index,k in dict(collections.Counter(voc_metadata_monthly[type_of_table])).items():
			final_df_month_count.loc[index][i] = k
			final_df_month_percent.loc[index][i] = round((k/district_month_wise_sampling.loc[index, i])*100, 2)
			final_df_month_combined.loc[index][i] = f"{final_df_month_count.loc[index][i]} ({final_df_month_percent.loc[index][i]}%)"

	final_df_month_count.to_excel(writer, f'{voc_type}_count')
	final_df_month_percent.to_excel(writer, f'{voc_type}_percent')
	final_df_month_combined.to_excel(writer, f'{voc_type}_combined')

for i in month_keys:
	month_wise_mutation_percent[i] = round((pandas.to_numeric(month_wise_mutation_count[i])/len(metadata.index[metadata['collection_month'] == i].tolist()))*100, 2)

voc_df.to_excel(writer, "voc_distribution_state")
month_wise_mutation_count.to_excel(writer, "month_wise_mutation_count")
month_wise_mutation_percent.to_excel(writer, "month_wise_mutation_percent")
writer.save()
