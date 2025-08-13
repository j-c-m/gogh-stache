#!/usr/bin/env python3
import json
import yaml
import pystache
import os
import re
from pathlib import Path
import glob
from unidecode import unidecode

def load_config(config_path):
    """Load the config.json file."""
    with open(config_path, 'r') as f:
        return json.load(f)

def load_yaml(yaml_path):
    """Load a YAML color scheme file."""
    try:
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading YAML file {yaml_path}: {e}")
        return None

def slugify(name):
    """Convert theme name to a slug (lowercase, replace spaces with hyphens)."""
    name = unidecode(name);
    name = name.lower()
    name = name.replace(' ', '-').replace('_', '-')
    name = re.sub(r'[^0-9a-z-]', '', name)
    return name

def map_theme_data(theme_data, source, theme_path):
    """Map theme data from different sources to the standard context for Mustache templates."""
    context = {
        'theme-source': source,
        'theme-source-slug': slugify(source)
    }

    if source == 'gogh':
        # Required fields for Gogh schema
        required_fields = [
            'name', 'author', 'variant',
            'color_01', 'color_02', 'color_03', 'color_04',
            'color_05', 'color_06', 'color_07', 'color_08',
            'color_09', 'color_10', 'color_11', 'color_12',
            'color_13', 'color_14', 'color_15', 'color_16',
            'foreground', 'background', 'cursor'
        ]
        missing_fields = [field for field in required_fields if theme_data.get(field) is None]
        if missing_fields:
            raise ValueError(f"Missing required fields in {theme_path}: {', '.join(missing_fields)}")

        context.update({
            'theme-slug': slugify(theme_data['name']),
            'theme-name': theme_data['name'],
            'theme-variant': theme_data['variant'],
            'theme-author': theme_data['author'],
            'ansi-0-hex': theme_data['color_01'],
            'ansi-1-hex': theme_data['color_02'],
            'ansi-2-hex': theme_data['color_03'],
            'ansi-3-hex': theme_data['color_04'],
            'ansi-4-hex': theme_data['color_05'],
            'ansi-5-hex': theme_data['color_06'],
            'ansi-6-hex': theme_data['color_07'],
            'ansi-7-hex': theme_data['color_08'],
            'ansi-8-hex': theme_data['color_09'],
            'ansi-9-hex': theme_data['color_10'],
            'ansi-10-hex': theme_data['color_11'],
            'ansi-11-hex': theme_data['color_12'],
            'ansi-12-hex': theme_data['color_13'],
            'ansi-13-hex': theme_data['color_14'],
            'ansi-14-hex': theme_data['color_15'],
            'ansi-15-hex': theme_data['color_16'],
            'foreground-hex': theme_data['foreground'],
            'background-hex': theme_data['background'],
            'cursor-hex': theme_data['cursor'],
            'selection-hex': theme_data['color_08']
        })
    elif source == 'base16':
        # Required fields for Base16 schema
        required_fields = ['name', 'author', 'variant', 'palette']
        missing_fields = [field for field in required_fields if theme_data.get(field) is None]
        if missing_fields:
            raise ValueError(f"Missing required fields in {theme_path}: {', '.join(missing_fields)}")

        palette = theme_data['palette']
        required_palette_fields = [
            'base00', 'base01', 'base02', 'base03', 'base04',
            'base05', 'base06', 'base07', 'base08', 'base09',
            'base0A', 'base0B', 'base0C', 'base0D', 'base0E', 'base0F'
        ]
        missing_palette_fields = [field for field in required_palette_fields if palette.get(field) is None]
        if missing_palette_fields:
            raise ValueError(f"Missing required palette fields in {theme_path}: {', '.join(missing_palette_fields)}")

        context.update({
            'theme-slug': slugify(theme_data['name']),
            'theme-name': theme_data['name'],
            'theme-variant': theme_data['variant'],
            'theme-author': theme_data['author'],
            'ansi-0-hex': palette['base00'],  # Black
            'ansi-1-hex': palette['base08'],  # Red
            'ansi-2-hex': palette['base0B'],  # Green
            'ansi-3-hex': palette['base0A'],  # Yellow
            'ansi-4-hex': palette['base0D'],  # Blue
            'ansi-5-hex': palette['base0E'],  # Magenta
            'ansi-6-hex': palette['base0C'],  # Cyan
            'ansi-7-hex': palette['base05'],  # White
            'ansi-8-hex': palette['base03'],  # Bright Black
            'ansi-9-hex': palette['base08'],  # Bright Red
            'ansi-10-hex': palette['base0B'],  # Bright Green
            'ansi-11-hex': palette['base0A'],  # Bright Yellow
            'ansi-12-hex': palette['base0D'],  # Bright Blue
            'ansi-13-hex': palette['base0E'],  # Bright Magenta
            'ansi-14-hex': palette['base0C'],  # Bright Cyan
            'ansi-15-hex': palette['base07'],  # Bright White
            'foreground-hex': palette['base05'],  # Foreground
            'background-hex': palette['base00'],  # Background
            'cursor-hex': palette['base05'],  # Cursor
            'selection-hex': palette['base02'] # Selection Background
        })
    else:
        # Placeholder for other theme sources (no strict validation)
        context.update({
            'theme-slug': slugify(theme_data.get('theme_name', 'unknown')),
            'theme-name': theme_data.get('theme_name', 'Unknown Theme'),
            'theme-variant': theme_data.get('type', ''),
            'theme-author': theme_data.get('creator', ''),
            'ansi-0-hex': theme_data.get('colors', {}).get('black', '#000000'),
            'ansi-1-hex': theme_data.get('colors', {}).get('red', '#000000'),
            'ansi-2-hex': theme_data.get('colors', {}).get('green', '#000000'),
            'ansi-3-hex': theme_data.get('colors', {}).get('yellow', '#000000'),
            'ansi-4-hex': theme_data.get('colors', {}).get('blue', '#000000'),
            'ansi-5-hex': theme_data.get('colors', {}).get('magenta', '#000000'),
            'ansi-6-hex': theme_data.get('colors', {}).get('cyan', '#000000'),
            'ansi-7-hex': theme_data.get('colors', {}).get('white', '#000000'),
            'ansi-8-hex': theme_data.get('colors', {}).get('bright_black', '#000000'),
            'ansi-9-hex': theme_data.get('colors', {}).get('bright_red', '#000000'),
            'ansi-10-hex': theme_data.get('colors', {}).get('bright_green', '#000000'),
            'ansi-11-hex': theme_data.get('colors', {}).get('bright_yellow', '#000000'),
            'ansi-12-hex': theme_data.get('colors', {}).get('bright_blue', '#000000'),
            'ansi-13-hex': theme_data.get('colors', {}).get('bright_magenta', '#000000'),
            'ansi-14-hex': theme_data.get('colors', {}).get('bright_cyan', '#000000'),
            'ansi-15-hex': theme_data.get('colors', {}).get('bright_white', '#000000'),
            'foreground-hex': theme_data.get('foreground', '#FFFFFF'),
            'background-hex': theme_data.get('background', '#000000'),
            'cursor-hex': theme_data.get('cursor', '#FFFFFF'),
            'selection-hex': theme_data.get('selection', '#CCCCCC')
        })

    return context

def main():
    config_path = Path('templates/config.json')

    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        return

    themes_base_dir = Path('themes')
    theme_sources = [d for d in themes_base_dir.iterdir() if d.is_dir()]

    if not theme_sources:
        print("No theme source directories found in themes/ directory.")
        return

    for source_dir in theme_sources:
        source_name = source_dir.name  # e.g., 'gogh', 'base16'
        theme_files = sorted(glob.glob(str(source_dir / '*.yaml')) + glob.glob(str(source_dir / '*.yml')))

        if not theme_files:
            print(f"No theme files found in {source_dir} directory.")
            continue

        for theme_file in theme_files:
            theme_path = Path(theme_file)
            theme_data = load_yaml(theme_path)
            if theme_data is None:
                continue

            # Map theme data to standard context based on source
            try:
                context = map_theme_data(theme_data, source_name, theme_path)
            except ValueError as e:
                print(f"Validation error for {theme_path}: {e}")
                continue

            for template_key, template_config in config.items():
                template_path = Path('templates') / template_key
                if not template_path.exists():
                    print(f"Template file {template_path} not found, skipping for theme {context['theme-name']}...")
                    continue

                try:
                    with open(template_path, 'r') as f:
                        template = f.read()
                except Exception as e:
                    print(f"Error reading template file {template_path}: {e}")
                    continue

                rendered = pystache.render(template, context)

                output_dir = Path(template_config['directory'])
                output_filename = pystache.render(template_config['filename'], context)
                output_path = 'build' / output_dir / output_filename

                try:
                    os.makedirs('build' / output_dir, exist_ok=True)
                except Exception as e:
                    print(f"Error creating output directory {output_dir}: {e}")
                    continue

                try:
                    with open(output_path, 'w') as f:
                        f.write(rendered)
                    print(f"Generated theme file for [{template_key}] [{context['theme-source']}] {context['theme-name']} at: {output_path}")
                except Exception as e:
                    print(f"Error writing output file {output_path}: {e}")

if __name__ == "__main__":
    main()
