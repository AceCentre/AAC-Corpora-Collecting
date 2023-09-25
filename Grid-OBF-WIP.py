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
