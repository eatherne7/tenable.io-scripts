import sys
import requests
import json
import time

global access_key, secret_key, headers,output_file
access_key = '<your access key>'
secret_key = '<your secret>'
headers = {
	'X-ApiKeys': 'accessKey=' + access_key + '; secretKey=' + secret_key,
	"accept": "application/json",
	"content-type": "application/json"
}
output_file = '<your output filename>'

def exportAssets():
	print("[+] Initiating export of all assets...")
	url = "https://cloud.tenable.com/assets/export"
	payload = { "chunk_size": 10000 }
	response = requests.post(url, json=payload, headers=headers)
	data = json.loads(response.text)
	try:
		export_uuid = data["export_uuid"]
		print(f"    [-] Export UUID = {export_uuid}")
		return export_uuid
	except:
		print("Error requesting initial export")
		sys.exit(1)

def exportStatus(export_uuid):
	print(f"[+] Checking status of export {export_uuid}...")
	print("    [-] Export is process, waiting for completion...")
	url = f"https://cloud.tenable.com/assets/export/{export_uuid}/status"

	while True:
		response = requests.get(url, headers=headers)
		data = response.json()
		status = data.get("status")

		if status == "PROCESSING":
		    time.sleep(5)
		else:
			if status == "FINISHED":
				print(f"    [-] Export complete")
				chunks_available = data["chunks_available"]
				total_chunks = chunks_available[-1]
				print(f"[+] Processing {total_chunks} chunks of data...")
				all_results = ""
				for chunk in chunks_available:
					print(f"    [-] Processing chunk {chunk}")
					url = f"https://cloud.tenable.com/assets/export/{export_uuid}/chunks/{chunk}"
					response = requests.get(url, headers=headers)
					all_results += response.text
					record_length = len(all_results)
				break
			else:
				print(f"Status is {status}. Dont know what to do, exiting..")
				sys.exit(1)
	print("    [-] Processing chunks complete")

	print(f"[+] Saving output to file {output_file}")
	with open(output_file, 'w') as file:
	    file.write(all_results)

	print("    [-] Export complete")

def main():
	export_uuid = exportAssets()
	exportStatus(export_uuid)

if __name__ == "__main__":
	main()
