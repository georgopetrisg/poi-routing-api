import json

input_file = 'data/pois.json'
output_file = 'data/pois_updated.json'

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Η enumerate μας δίνει το index και το αντικείμενο feature
for index, feature in enumerate(data['features']):
    # poi_0, poi_1...
    new_id = f"poi_{index}"
    
    # Ενημέρωση του εξωτερικού 'id'
    if 'id' in feature:
        feature['id'] = new_id
    
    # Ενημέρωση του '@id' μέσα στα properties
    if 'properties' in feature and '@id' in feature['properties']:
        feature['properties']['@id'] = new_id

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Η διαδικασία ολοκληρώθηκε! Δημιουργήθηκε το αρχείο {output_file}")