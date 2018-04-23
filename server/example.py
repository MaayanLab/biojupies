# Import
import json
import requests

# Read JSON
with open('example.json') as openfile:
    notebook_configuration = json.dumps(json.loads(openfile.read()))

# Post Request
response =  requests.post('http://localhost:5000/notebook-generator-server-dev/api/generate', json=notebook_configuration)
# response =  requests.post('http://amp.pharm.mssm.edu/notebook-generator-server/api/generate', json=notebook_configuration)
results = response.text

# Print Results
print(results)
