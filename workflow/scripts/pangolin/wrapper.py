import os
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--input', help='Input Fasta')
parser.add_argument('--output', help='Output Lineage')
args = parser.parse_args()
pangolin_input = args.input
pangolin_output = args.output

subprocess.run(f'pangolin {pangolin_input} --outfile {pangolin_output}', shell = True, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

# shell(
# 	"""
# 		pangolin {pangolin_input} --outfile {pangolin_output}
# 	"""
# )
