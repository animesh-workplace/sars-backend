import os
import json
import pandas
import logging
import argparse
from mpire import WorkerPool
from pandas import ExcelWriter
from mpire.utils import make_single_arguments

parser = argparse.ArgumentParser()
parser.add_argument('--date', help='Enter output file')
parser.add_argument('--basepath', help='Enter base path')
parser.add_argument('--metadata', help='Enter Nexstrain metadata')
args = parser.parse_args()
date = args.date
base_path = args.basepath
metadata_url = args.metadata

logging.basicConfig(filename=f"{base_path}/Analysis/{date}/log/voc_report", format='%(asctime)s %(message)s', filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

with open("workflow/resources/voc_tracking.json") as f:
    voc_to_track = json.loads(f.read())


def voc_report(url):
    output_url = url['output']
    metadata_url = url['metadata']
    metadata = pandas.read_csv(metadata_url, delimiter='\t', encoding='utf-8', low_memory=False)
    voc_type_writer = ExcelWriter(output_url)

    for voc_type, entries in voc_to_track.items():
        voc_metadata = pandas.DataFrame()
        for i in entries:
            if('pangolin' in list(i.keys())):
                for (key, value) in i['pangolin'].items():
                    if(key == 'exact'):
                        voc_metadata = pandas.concat([voc_metadata, metadata.loc[metadata['lineage'].isin(value)]])
                    elif(key == 'contains'):
                        voc_metadata = pandas.concat([voc_metadata, metadata.loc[metadata['lineage'].str.contains(value)]])

            if('nextstrain' in list(i.keys())):
                for (key, value) in i['nextstrain'].items():
                    if(key == 'exact'):
                        voc_metadata = pandas.concat([voc_metadata, metadata.loc[metadata['clade'].isin(value)]])
                    elif(key == 'contains'):
                        voc_metadata = pandas.concat([voc_metadata, metadata.loc[metadata['clade'].str.contains(value)]])

        voc_metadata.reset_index(drop=True, inplace=True)
        voc_metadata.drop_duplicates(subset=['strain'], ignore_index=True, inplace=True)
        voc_metadata[['strain', 'lab_id', 'division', 'location', 'date', 'lineage', 'clade', 'scorpio_call']].to_excel(voc_type_writer, f'{voc_type}', index=False)

    voc_type_writer.save()
    print(url["name"])


metadata = pandas.read_csv(metadata_url, delimiter='\t', encoding='utf-8', low_memory=False)
states = pandas.unique(metadata['division']).tolist()
path_list = [
    {
        "name": f"Generating {state} VoC/VoI report",
        "metadata": f"{base_path}/Analysis/{date}/reports/state_wise/{state.replace(' ','_')}/{state.replace(' ','_')}_metadata.tsv",
                "output": f"{base_path}/Analysis/{date}/reports/state_wise/{state.replace(' ','_')}/{state.replace(' ','_')}_voc_id_report.xlsx"
    } for state in states]
path_list.append({
    "metadata": metadata_url,
    "name": "Generating Overall VoC/VoI report",
    "output": f"{base_path}/Analysis/{date}/reports/voc_id_report.xlsx",
})

with WorkerPool(n_jobs=50) as pool:
    output = pool.map(voc_report, make_single_arguments(path_list, generator=False))
