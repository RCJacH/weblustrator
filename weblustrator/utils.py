import yaml

def load_meta(meta_file_folder, default=None):
    meta_file = meta_file_folder / 'config.yml'
    try:
        yaml_content = meta_file.read_text(encoding='utf-8')
    except FileNotFoundError:
        return default
    else:
        return yaml.safe_load(yaml_content)

