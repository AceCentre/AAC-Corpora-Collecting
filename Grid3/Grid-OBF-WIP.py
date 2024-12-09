import xml.etree.ElementTree as ET
import json
import argparse
import zipfile
import os
import tempfile
import shutil

def parse_styles(styles_xml_path):
    """
    Parse the styles XML file and create a mapping for button styles.
    """
    style_mapping = {}
    if styles_xml_path and os.path.exists(styles_xml_path):
        style_tree = ET.parse(styles_xml_path)
        style_root = style_tree.getroot()
        for style in style_root.findall(".//Style"):
            key = style.attrib.get("Key")
            back_colour = style.find("BackColour").text if style.find("BackColour") is not None else "#FFFFFFFF"
            font_colour = style.find("FontColour").text if style.find("FontColour") is not None else "#000000FF"
            style_mapping[key] = {
                "backgroundColor": back_colour[:7],
                "textColor": font_colour[:7]
            }
    return style_mapping

def parse_buttons(grid_root, style_mapping):
    """
    Extract buttons and their metadata from the Grid XML file.
    """
    buttons = []
    images = []
    button_counter = 1

    for cell in grid_root.findall(".//Cell"):
        style_key = cell.find("StyleKey")
        style = style_mapping.get(style_key.text, {}) if style_key is not None else {}

        label = ""
        caption = cell.find("Caption")
        if caption is not None:
            label = caption.text

        # Extract images
        image_tag = cell.find(".//Image")
        if image_tag is not None:
            image_path = image_tag.text.strip()
            image_id = f"image-{button_counter}"
            images.append({"id": image_id, "path": image_path})

        # Extract navigation
        navigation = None
        navigation_command = cell.find(".//Command[@ID='Jump.To']")
        if navigation_command is not None:
            target_grid = navigation_command.find(".//Parameter[@Key='grid']")
            if target_grid is not None:
                navigation = {"jump_to": target_grid.text}

        buttons.append({
            "id": f"button-{button_counter}",
            "label": label,
            "row": int(cell.attrib.get("GridRow", 0)),
            "col": int(cell.attrib.get("GridColumn", 0)),
            "width": int(cell.attrib.get("GridWidth", 1)),
            "height": int(cell.attrib.get("GridHeight", 1)),
            "style": style,
            "navigation": navigation
        })
        button_counter += 1

    return buttons, images

def grid_to_openboard(grid_xml_path, styles_xml_path=None, output_json_path="output.obf", locale="en"):
    """
    Convert a Grid 3 board to OpenBoard format.
    """
    # Parse grid and styles
    grid_tree = ET.parse(grid_xml_path)
    grid_root = grid_tree.getroot()
    style_mapping = parse_styles(styles_xml_path)
    
    # Extract grid dimensions
    rows = len(grid_root.find(".//RowDefinitions").findall("RowDefinition"))
    columns = len(grid_root.find(".//ColumnDefinitions").findall("ColumnDefinition"))
    
    # Extract buttons and images
    buttons, images = parse_buttons(grid_root, style_mapping)
    
    # Initialize OBF structure
    obf_data = {
        "format": "open-board-0.1",
        "id": "board",
        "locale": locale,
        "name": "Converted Grid",
        "description_html": "Converted from Grid XML format.",
        "buttons": buttons,
        "grid": {
            "rows": rows,
            "columns": columns,
            "order": []
        },
        "images": images,
    }
    
    # Populate grid order with button IDs
    button_positions = {f"{b['row']}-{b['col']}": b["id"] for b in buttons}
    for row in range(rows):
        row_order = []
        for col in range(columns):
            button_id = button_positions.get(f"{row}-{col}", None)
            row_order.append(button_id)
        obf_data["grid"]["order"].append(row_order)
    
    # Save OBF JSON file
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(obf_data, f, indent=4)
    return output_json_path

def extract_gridset(gridset_path, extract_to):
    """
    Extract a Gridset ZIP file to a temporary directory.
    """
    with zipfile.ZipFile(gridset_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    return extract_to

def main():
    parser = argparse.ArgumentParser(description="Convert Grid 3 files to Open Board Format (OBF).")
    parser.add_argument("gridset_path", help="Path to the Gridset (ZIP) file.")
    parser.add_argument("--styles", help="Path to the styles XML file.", default=None)
    parser.add_argument("--output", help="Path to save the converted OpenBoard JSON file.", default="output.obf")
    parser.add_argument("--locale", help="Language locale for the OpenBoard file.", default="en")
    args = parser.parse_args()

    # Create a temporary directory to extract the Gridset
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_gridset(args.gridset_path, temp_dir)
        
        # Find the main grid XML file
        grid_xml_path = os.path.join(temp_dir, "Grids", "grid.xml")  # Adjust as needed
        if not os.path.exists(grid_xml_path):
            print("Error: Could not find grid.xml in the Gridset.")
            return
        
        # Convert to OpenBoard format
        output_path = grid_to_openboard(
            grid_xml_path=grid_xml_path,
            styles_xml_path=args.styles,
            output_json_path=args.output,
            locale=args.locale
        )
        print(f"OpenBoard file saved to {output_path}")

if __name__ == "__main__":
    main()