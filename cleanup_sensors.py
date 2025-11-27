import json

with open('/var/lib/docker/volumes/hass_config/_data/.storage/core.entity_registry', 'r') as f:
    data = json.load(f)

to_remove = []
for i, entity in enumerate(data['data']['entities']):
    eid = entity['entity_id']
    if eid.startswith('sensor.maanstraat_17_') and ('vandaag' in eid or 'morgen' in eid or 'electricity_price_to' in eid):
        to_remove.append(i)

for i in reversed(to_remove):
    print(f"Removing: {data['data']['entities'][i]['entity_id']}")
    del data['data']['entities'][i]

with open('/var/lib/docker/volumes/hass_config/_data/.storage/core.entity_registry', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Removed {len(to_remove)} duplicate sensors")
