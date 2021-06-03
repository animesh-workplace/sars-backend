import json
import pandas
import argparse
from pandas import ExcelWriter

parser = argparse.ArgumentParser()
parser.add_argument('--metadata', help='Enter Nexstrain metadata')
parser.add_argument('--output', help='Enter output file')
args = parser.parse_args()
metadata_url = args.metadata
output_url = args.output

with open("workflow/resources/voc_tracking.json") as f:
	voc_to_track = json.loads(f.read())

metadata = pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)
voc_type_writer = ExcelWriter(output_url)

for voc_type, entries in voc_to_track.items():
	voc_metadata = pandas.DataFrame()
	for i in entries:
		if('pangolin' in list(i.keys())):
			voc_metadata = pandas.concat([ voc_metadata, metadata.loc[metadata['lineage'].isin(i['pangolin'])] ])
		if('nextstrain' in list(i.keys())):
			voc_metadata = pandas.concat([ voc_metadata, metadata.loc[metadata['clade'].isin(i['nextstrain'])] ])

	voc_metadata.reset_index(drop = True, inplace = True)
	voc_metadata.drop_duplicates(subset = ['strain'], ignore_index = True, inplace = True)
	voc_metadata[['strain', 'lab_id', 'division', 'location', 'date', 'lineage', 'clade', 'scorpio_call']].to_excel(voc_type_writer, f'{voc_type}', index = False)

voc_type_writer.save()
