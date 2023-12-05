import requests

try:
    response = requests.get('http://169.254.170.2/v3/metadata')
    response.raise_for_status()
    metadata = response.json()
    print('METADATA:    ', metadata)
except requests.exceptions.RequestException as e:
    print(f'Failed to retrieve ECS container metadata: {e}')
