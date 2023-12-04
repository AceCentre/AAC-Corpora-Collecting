# Parse the new uploaded XML file to understand its structure and content
parsed_xml = ET.parse(file_path)

# Create a dictionary to store parsed data
parsed_data = {
    "grid": {},
    "buttons": []
}

# Extract the number of columns
columns = parsed_xml.find("ColumnDefinitions")
parsed_data["grid"]["columns"] = len(columns.findall("ColumnDefinition")) if columns is not None else 0

# Extract the number of rows
rows = parsed_xml.find("RowDefinitions")
parsed_data["grid"]["rows"] = len(rows.findall("RowDefinition")) if rows is not None else 0

# Extract cell/button information
cells = parsed_xml.find("Cells")
if cells is not None:
    for cell in cells.findall("Cell"):
        cell_data = {}
        caption = cell.find(".//Caption")
        if caption is not None:
            cell_data["label"] = caption.text if caption.text else ""
        parsed_data["buttons"].append(cell_data)

# Display the parsed data for review (limited to first 10 buttons for brevity)
parsed_data["buttons"][:10], parsed_data["grid"]["rows"], parsed_data["grid"]["columns"]


# Initialize the OBF structure based on the parsed data
obf_data = {
    "format": "open-board-0.1",
    "id": "1",  # Example ID, can be changed
    "locale": "en",  # Example locale, can be changed
    "name": "Converted Grid",  # Example name, can be changed
    "description_html": "Converted from Grid XML format.",  # Example description, can be changed
    "buttons": [],
    "grid": {
        "rows": parsed_data["grid"]["rows"],
        "columns": parsed_data["grid"]["columns"],
        "order": []
    },
    "images": []  # No images for now, can be added later
}

# Populate the buttons and the grid order based on the parsed data
button_counter = 1  # Counter to generate button IDs
for i, row in enumerate(range(parsed_data["grid"]["rows"])):
    row_order = []
    for j, col in enumerate(range(parsed_data["grid"]["columns"])):
        button_index = i * parsed_data["grid"]["columns"] + j
        if button_index < len(parsed_data["buttons"]):
            label = parsed_data["buttons"][button_index].get("label", "")
            button_id = str(button_counter)
            obf_data["buttons"].append({
                "id": button_id,
                "label": label,
            })
            row_order.append(button_id)
            button_counter += 1
        else:
            row_order.append(None)
    obf_data["grid"]["order"].append(row_order)

# Generate the OBF JSON file
obf_json = json.dumps(obf_data, indent=4)

# Save the JSON to a file
obf_file_path = '/mnt/data/converted_grid_complex.obf'
with open(obf_file_path, 'w', encoding='utf-8') as f:
    f.write(obf_json)

obf_file_path


// What follows is a second type for more complex 

# Importing necessary libraries
import xml.etree.ElementTree as ET
import json

def grid_to_openboard(grid_xml_path, styles_xml_path, output_json_path):
    """
    Convert a Grid 3 board to OpenBoard format.

    Parameters:
    - grid_xml_path: str, path to Grid 3 board XML file
    - styles_xml_path: str, path to Grid 3 styles XML file
    - output_json_path: str, path to output OpenBoard JSON file
    """
    
    # Parse Grid XML file
    tree = ET.parse(grid_xml_path)
    root = tree.getroot()
    
    # Parse styles XML file
    style_tree = ET.parse(styles_xml_path)
    style_root = style_tree.getroot()
    
    # Extract Grid 3 styles and map them to OpenBoard button styles
    style_mapping = {}
    for style in style_root.findall(".//Style"):
        key = style.attrib.get('Key')
        back_colour = style.find('BackColour').text if style.find('BackColour') is not None else '#FFFFFFFF'
        font_colour = style.find('FontColour').text if style.find('FontColour') is not None else '#000000FF'
        style_mapping[key] = {
            'backgroundColor': back_colour[:7],  # Remove alpha channel
            'textColor': font_colour[:7]  # Remove alpha channel
        }
    
    # Create OpenBoard JSON structure
    openboard_json = {
        'id': 'board',
        'name': 'Board',
        'width': len(root.find('.//ColumnDefinitions').findall('ColumnDefinition')),
        'height': len(root.find('.//RowDefinitions').findall('RowDefinition')),
        'buttons': []
    }
    
    # Convert Grid 3 buttons to OpenBoard buttons
    for button in root.findall(".//Button"):
        style_key = button.find('StyleKey').text if button.find('StyleKey') is not None else 'Default'
        style = style_mapping.get(style_key, {})
        
        # Extract label from Caption or WordList
        label = ''
        caption = button.find('Caption')
        if caption is not None:
            label = caption.text
        else:
            wordlist = button.find('WordList')
            if wordlist is not None:
                label = wordlist.find('.//Item').find('Name').text  # Use the first word list item as label

        openboard_button = {
            'id': button.attrib.get('Id'),
            'label': label,
            'row': int(button.find('GridRow').text),
            'col': int(button.find('GridColumn').text),
            'width': int(button.find('GridWidth').text),
            'height': int(button.find('GridHeight').text),
            'style': style
        }
        openboard_json['buttons'].append(openboard_button)
    
    # Save OpenBoard JSON file
    with open(output_json_path, 'w') as f:
        json.dump(openboard_json, f, indent=4)

# Example usage
grid_to_openboard('/path/to/grid.xml', '/path/to/styles.xml', '/path/to/output.json')


