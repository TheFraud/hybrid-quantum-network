#!/usr/bin/env python3
import yaml

def test_yaml_dump_and_load():
    data = {'hello': 'world', 'numbers': [1, 2, 3]}
    yaml_str = yaml.dump(data)
    loaded_data = yaml.safe_load(yaml_str)
    assert loaded_data == data, "Le dump et le load YAML ne conservent pas les données correctement"

if __name__ == "__main__":
    test_yaml_dump_and_load()
    print("Test YAML réussi.")

