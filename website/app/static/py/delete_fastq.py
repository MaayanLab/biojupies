import urllib.request, urllib.parse, json

# Get samples
req =  urllib.request.Request('https://amp.pharm.mssm.edu/charon/files?username=biojupies&password=sequencing')
uploaded_files = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))['filenames']
samples = [x for x in uploaded_files if not x.startswith('RTXbwXZ0Ssv')]

# Delete
for sample in samples:
    print(sample)
    url = urllib.parse.quote('https://amp.pharm.mssm.edu/charon/delete?username=biojupies&password=sequencing&file='+sample, safe=':/-?=&')
    print(url)
    req =  urllib.request.Request(url)
    resp = urllib.request.urlopen(req).read()
    print(resp)