import requests

try:
    response = requests.get('http://localhost:51678/v1/metadata')
    response.raise_for_status()
    metadata = response.json()
    print(metadata)
except requests.exceptions.RequestException as e:
    print(f'Failed to retrieve ECS container metadata: {e}')
