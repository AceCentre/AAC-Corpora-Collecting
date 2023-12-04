import zipfile
import xml.etree.ElementTree as ET
import os
import argparse
import math
from collections import Counter
from collections import deque
import csv


def parse_xml(file_path):
	tree = ET.parse(file_path)
	root = tree.getroot()
	return root

def get_grid_name_from_path(file_path):
	# Example file_path: "extracted1/Grids/00 child vocabulary/grid.xml"
	# Extract the grid name part of the path
	parts = file_path.split(os.sep)
	if len(parts) > 2 and parts[-2] != "Grids":
		return parts[-2]  # Returns "00 child vocabulary"
	return "Unknown"


def extract_gridset_contents(file_path, extract_to):
	with zipfile.ZipFile(file_path, 'r') as zip_ref:
		zip_ref.extractall(extract_to)

def extract_cell_contents(xml_root):
	texts = []
	for cell in xml_root.findall(".//Cell"):
		text_element = cell.find(".//Content/Commands/Command[@ID='Action.InsertText']/Parameter[@Key='text']/p/s/r")
		if text_element is not None and text_element.text:
			text = text_element.text.strip()
			if text:  # Ensure the text is not empty
				texts.append(text)
	return texts

def extract_wordlist_items(xml_root):
	wordlist_items = []
	for wordlist in xml_root.findall(".//WordList/Items/WordListItem/Text/r"):
		if wordlist.text:
			wordlist_items.append(wordlist.text)
	return wordlist_items

def analyze_texts(text_list):
	word_count = Counter()
	phrase_count = 0
	for text in text_list:
		words = text.split()
		if len(words) > 1:
			phrase_count += 1
		word_count.update(words)
	return word_count, phrase_count
	
def find_xml_files(directory):
	xml_files = []
	for root, dirs, files in os.walk(directory):
		for file in files:
			if file.endswith(".xml"):
				xml_files.append(os.path.join(root, file))
	return xml_files

def find_main_grid_xml(directory, start_grid_name):
	"""
	Construct the path to the main grid XML file based on the start grid name.

	:param directory: The directory containing the extracted gridset files.
	:param start_grid_name: The name of the start grid (from settings.xml).
	:return: The path to the main grid XML file, or None if not found.
	"""
	expected_file_path = os.path.join(directory, "Grids", start_grid_name, "grid.xml")

	if os.path.exists(expected_file_path):
		return expected_file_path
	else:
		return None


def parse_gridset_for_navigation(gridset_file):
	"""
	Parse a gridset file to extract navigation data.

	:param gridset_file: Path to the gridset file (XML format).
	:return: A dictionary where keys are grid names and values are lists of navigable target grids.
	"""
	navigation_data = {}
	try:
		tree = ET.parse(gridset_file)
		root = tree.getroot()

		# Iterate through all cells in the gridset
		for cell in root.findall('.//Cell'):
			# Find 'Jump.To' commands within each cell
			jump_to_command = cell.find(".//Commands/Command[@ID='Jump.To']/Parameter[@Key='grid']")
			if jump_to_command is not None:
				target_grid = jump_to_command.text
				grid_element = cell.find('..')	# Find the parent Grid element of the Cell				
				grid_name = get_grid_name_from_path(gridset_file)
				
				#print(f"Adding navigation: {grid_name} -> {target_grid}")	# Debugging
				if grid_name not in navigation_data:
					navigation_data[grid_name] = []
				navigation_data[grid_name].append(target_grid)

	except ET.ParseError as e:
		print(f"Error parsing the gridset file: {e}")
	#print(navigation_data)
	return navigation_data

def find_path(home_grid, target_grid, navigation_map):
	"""
	Find the shortest path from the home grid to the target grid.

	:param home_grid: The starting grid (usually the home grid).
	:param target_grid: The grid where the target button is located.
	:param navigation_map: A dictionary representing the navigation paths between grids.
	:return: A list of grid names representing the path from home to target.
	"""
	# Edge case: If the target grid is the same as the home grid
	if home_grid == target_grid:
		return [home_grid]
	
	# Initialize BFS
	visited = set()	 # Set to keep track of visited grids
	queue = deque([(home_grid, [])])  # Queue for BFS, storing tuples of (current grid, path to current grid)

	while queue:
		current_grid, path = queue.popleft()
		#print(f"Current Grid: {current_grid}, Path: {path}")  # Debugging


		if current_grid not in visited:
			visited.add(current_grid)
			path.append(current_grid)

			# Check if we have reached the target grid
			if current_grid == target_grid:
				return path

			# Enqueue all adjacent (navigable) grids
			for next_grid in navigation_map.get(current_grid, []):
				#print(f"Next Grid: {next_grid}")  # Debugging
				queue.append((next_grid, path.copy()))

	return []  # Return an empty list if no path is found

def calculate_button_coordinates(button_position, grid_rows, grid_cols, screen_dimensions):
	"""
	Calculate the approximate center coordinates of a button on the screen.

	:param button_position: Tuple (row, col) of the button's position in the grid.
	:param grid_rows: Total number of rows in the grid.
	:param grid_cols: Total number of columns in the grid.
	:param screen_dimensions: Tuple (width, height) of the screen.
	:return: Tuple (x, y) representing the button's center coordinates.
	"""
	screen_width, screen_height = screen_dimensions
	row, col = button_position

	# Calculate the size of each grid cell
	cell_width = screen_width / grid_cols
	cell_height = screen_height / grid_rows

	# Calculate center coordinates of the button
	x = (col - 0.5) * cell_width
	y = (row - 0.5) * cell_height

	return x, y

def calculate_grid_effort(grid_rows, grid_cols, total_visible_buttons, button_position, screen_dimensions, home_grid, button_grid, navigation_map):
	"""
	Calculate the effort score for a button in a gridset using direct selection technique.
	
	:param grid_rows: Number of rows in the grid.
	:param grid_cols: Number of columns in the grid.
	:param total_visible_buttons: Total number of visible buttons on the grid.
	:param button_position: Tuple (row, col) of the button's position in the grid.
	:param screen_dimensions: Tuple (width, height) of the screen.
	:param home_grid: Name of the home grid.
	:param button_grid: Name of the grid where the button is located.
	:param navigation_map: A dictionary representing the navigation paths between grids.
	:return: Total effort score for the button.
	"""
	BUTTON_SIZE_WEIGHT = 0.003
	FIELD_SIZE_WEIGHT = 0.007
	PRIOR_SCAN_WEIGHT = 0.001

	button_size = BUTTON_SIZE_WEIGHT * grid_rows * grid_cols
	field_size = FIELD_SIZE_WEIGHT * total_visible_buttons
	prior_scan = PRIOR_SCAN_WEIGHT * ((button_position[0] - 1) * grid_cols + button_position[1])

	button_coordinates = calculate_button_coordinates(button_position, grid_rows, grid_cols, screen_dimensions)
	screen_width, screen_height = screen_dimensions
	end_x, end_y = button_coordinates
	start_x, start_y = screen_width, screen_height	# Default starting position
	distance = math.sqrt(((start_x - end_x) / screen_width) ** 2 + ((start_y - end_y) / screen_height) ** 2) / math.sqrt(2)

	# Calculate the number of steps to the button's grid
	path_to_button = find_path(home_grid, button_grid, navigation_map)
	prior_effort = len(path_to_button) - 1 if path_to_button else 0
	hits = len(path_to_button) - 1 if path_to_button else 0	 # Number of hits
	
	
	#print(f"Path from {home_grid} to {button_grid}: {path_to_button}, Hits: {hits}")

	total_effort = button_size + field_size + prior_scan + distance + prior_effort
	return total_effort, hits


def extract_cell_data(cell_element, grid_element, grid_name):
	cell_data = {}

	# Extract grid rows and columns
	grid_rows = len(grid_element.findall(".//RowDefinitions/RowDefinition"))
	grid_cols = len(grid_element.findall(".//ColumnDefinitions/ColumnDefinition"))
	cell_data['grid_rows'] = grid_rows
	cell_data['grid_cols'] = grid_cols
	cell_data['grid_name'] = grid_name

	# Initialize text as empty
	cell_data['text'] = ''

	# Count total visible cells in the grid
	total_visible_cells = len(grid_element.findall(".//Cell"))
	cell_data['total_visible_buttons'] = total_visible_cells

	# Check if the cell has a Jump.To command only (exclude such cells)
	jump_command = cell_element.find(".//Command[@ID='Jump.To']")
	insert_text_command = cell_element.find(".//Command[@ID='Action.InsertText']")


	if insert_text_command is not None:
		# Extract text from the InsertText command
		text_element = insert_text_command.find(".//Parameter[@Key='text']/p/s/r")
		if text_element is not None and text_element.text:
			cell_data['text'] = text_element.text.strip()

	# If the cell has only a Jump.To command and no InsertText, exclude it
	if jump_command is not None and insert_text_command is None:
		return None

	# Extract other cell properties
	cell_x = int(cell_element.get('X', '1'))  # Default to 1 if not specified
	cell_y = int(cell_element.get('Y', '1'))  # Default to 1 if not specified
	cell_data['button_position'] = (cell_x, cell_y)

	return cell_data



def get_home_grid_from_settings(settings_file):
	"""
	Extract the home grid (StartGrid) from the settings XML file.

	:param settings_file: Path to the settings XML file.
	:return: The name of the home grid.
	"""
	try:
		tree = ET.parse(settings_file)
		root = tree.getroot()

		start_grid = root.find(".//StartGrid")
		if start_grid is not None and start_grid.text:
			return start_grid.text
		else:
			return None	 # or a default value if necessary

	except ET.ParseError as e:
		print(f"Error parsing the settings file: {e}")
		return None


def extract_combined_cell_and_wordlist_contents(xml_root, grid_name):
	"""
	Extracts a combined list of cell contents and wordlist items, along with additional details.

	:param xml_root: The root of the XML tree.
	:param grid_name: The name of the grid.
	:return: A list of dictionaries, each containing details about a cell or wordlist item.
	"""
	combined_contents = []
	wordlist_positions = []

	# Extract text and positions from cells
	for cell in xml_root.findall(".//Cell"):
		cell_data = {}
		cell_x = cell.get('X', '1')	 # Default to 1 if not specified
		cell_y = cell.get('Y', '1')	 # Default to 1 if not specified
		cell_position = f"({cell_x}, {cell_y})"
		
		# Check for wordlist cells
		if cell.find(".//ContentSubType") is not None and cell.find(".//ContentSubType").text == "WordList":
			wordlist_positions.append(cell_position)
			continue  # Skip adding to combined_contents for now

		text_element = cell.find(".//Content/Commands/Command[@ID='Action.InsertText']/Parameter[@Key='text']/p/s/r")
		if text_element is not None and text_element.text:
			cell_data['Text'] = text_element.text.strip()
			cell_data['Position'] = cell_position
			cell_data['PageName'] = grid_name
			cell_data['CellType'] = 'Regular'
			combined_contents.append(cell_data)

	# Extract items from wordlists
	for wordlist in xml_root.findall(".//WordList/Items/WordListItem/Text/r"):
		if wordlist.text:
			position = wordlist_positions.pop(0) if wordlist_positions else 'N/A'
			wordlist_data = {
				'Text': wordlist.text.strip(),
				'Position': position,
				'PageName': grid_name,
				'CellType': 'WordList'
			}
			combined_contents.append(wordlist_data)

	return combined_contents

def process_single_grid_file(file, navigation_map, screen_dimensions, home_grid):
	"""
	Process a single grid XML file and return cell data along with text analysis.
	"""
	root = parse_xml(file)
	grid_name = get_grid_name_from_path(file)
	texts = extract_cell_contents(root)
	word_count, phrase_count = analyze_texts(texts)

	cell_data_list = []
	total_hits = 0
	num_cells = 0

	for cell in root.findall(".//Cell"):
		cell_data = extract_cell_data(cell, root, grid_name)
		if cell_data is None or cell_data['text'] == '':
			continue

		effort_score, hits = calculate_grid_effort(
			cell_data['grid_rows'],
			cell_data['grid_cols'],
			cell_data['total_visible_buttons'],
			cell_data['button_position'],
			screen_dimensions,
			home_grid,
			cell_data['grid_name'],
			navigation_map
		)
		total_hits += hits
		num_cells += 1
		
		path_to_button = find_path(home_grid, cell_data['grid_name'], navigation_map)
		path_str = ' -> '.join(path_to_button)
		position_str = f"({cell_data['button_position'][0]}, {cell_data['button_position'][1]})"
		
		cell_type = "Wordlist Item" if "WordList" in cell.tag else "Regular Cell"

		cell_data_list.append({
			'text': cell_data['text'],
			'effort_score': effort_score,
			'hits': hits,
			'grid_name': cell_data['grid_name'],
			'position': position_str,
			'path': path_str,
			'cell_type': cell_type
		})

	return word_count, phrase_count, cell_data_list, total_hits, num_cells


def compare_gridsets(grid_xml_files_1, grid_xml_files_2, navigation_map1, navigation_map2, screen_dimensions, home_grid1, home_grid2):
	# Initialize variables
	word_counts_1, phrase_counts_1, effort_scores_1, cell_data_1, total_hits_1, num_cells_1 = Counter(), 0, [], [], 0, 0
	word_counts_2, phrase_counts_2, effort_scores_2, cell_data_2, total_hits_2, num_cells_2 = Counter(), 0, [], [], 0, 0

	# Process each file in gridset 1
	for file in grid_xml_files_1:
		word_count, phrase_count, cell_data, hits, num_cells = process_single_grid_file(
			file, navigation_map1, screen_dimensions, home_grid1
		)
		word_counts_1.update(word_count)
		phrase_counts_1 += phrase_count
		effort_scores_1.extend([data['effort_score'] for data in cell_data])
		cell_data_1.extend(cell_data)
		total_hits_1 += hits
		num_cells_1 += num_cells

	# Process each file in gridset 2
	for file in grid_xml_files_2:
		word_count, phrase_count, cell_data, hits, num_cells = process_single_grid_file(
			file, navigation_map2, screen_dimensions, home_grid2
		)
		word_counts_2.update(word_count)
		phrase_counts_2 += phrase_count
		effort_scores_2.extend([data['effort_score'] for data in cell_data])
		cell_data_2.extend(cell_data)
		total_hits_2 += hits
		num_cells_2 += num_cells

	# Calculate the total, unique, and shared words
	unique_words_1 = set(word_counts_1)
	unique_words_2 = set(word_counts_2)
	shared_words = unique_words_1.intersection(unique_words_2)
	exclusive_words_1 = unique_words_1 - shared_words
	exclusive_words_2 = unique_words_2 - shared_words

	# Additional metrics
	total_pages_1 = len(set(file for file in grid_xml_files_1))
	total_pages_2 = len(set(file for file in grid_xml_files_2))
	total_buttons_1 = len(cell_data_1)
	total_buttons_2 = len(cell_data_2)
	top_20_easiest_1 = sorted(cell_data_1, key=lambda x: x['effort_score'])[:20]
	top_20_easiest_2 = sorted(cell_data_2, key=lambda x: x['effort_score'])[:20]

	comparison_results = {
		"Total Words in Gridset 1": sum(word_counts_1.values()),
		"Total Words in Gridset 2": sum(word_counts_2.values()),
		"Unique Words in Gridset 1": len(unique_words_1),
		"Unique Words in Gridset 2": len(unique_words_2),
		"Shared Words": len(shared_words),
		"Exclusive Words in Gridset 1": len(exclusive_words_1),
		"Exclusive Words in Gridset 2": len(exclusive_words_2),
		"Phrases in Gridset 1": phrase_counts_1,
		"Phrases in Gridset 2": phrase_counts_2,
		"Total Pages in Gridset 1": total_pages_1,
		"Total Pages in Gridset 2": total_pages_2,
		"Total Buttons in Gridset 1": total_buttons_1,
		"Total Buttons in Gridset 2": total_buttons_2,
		"Average Hits in Gridset 1": total_hits_1 / num_cells_1 if num_cells_1 > 0 else 0,
		"Average Hits in Gridset 2": total_hits_2 / num_cells_2 if num_cells_2 > 0 else 0,
		"Top 20 Easiest Words/Phrases in Gridset 1": [x['text'] for x in top_20_easiest_1],
		"Top 20 Easiest Words/Phrases in Gridset 2": [x['text'] for x in top_20_easiest_2],
	}

	return comparison_results


def process_gridset_for_csv(grid_xml_files, navigation_map, screen_dimensions, home_grid):
	# Initialize list for CSV data
	csv_data = []

	# Process grid files
	for file in grid_xml_files:
		_, _, cell_data, _, _ = process_single_grid_file(
			file, navigation_map, screen_dimensions, home_grid
		)
		for data in cell_data:
			csv_data.append({
				'Word/Phrase': data['text'],
				'Effort Score': data['effort_score'],
				'Hits': data['hits'],
				'Grid Name': data['grid_name'],
				'Position': data['position'],
				'Path': data['path'],
				'Cell Type': data['cell_type']
			})

	return csv_data


def save_to_csv(data, filename):
	"""
	Save data to a CSV file.

	:param data: List of dictionaries with cell data.
	:param filename: Name of the CSV file to save.
	"""
	with open(filename, mode='w', newline='', encoding='utf-8') as file:
		writer = csv.DictWriter(file, fieldnames=data[0].keys())
		writer.writeheader()
		for row in data:
			writer.writerow(row)


def main():
	parser = argparse.ArgumentParser(description='Compare the language content of two .gridset files.')
	parser.add_argument('gridset1', type=str, help='Path to the first .gridset file')
	parser.add_argument('gridset2', type=str, help='Path to the second .gridset file')
	parser.add_argument('--gridset1home', type=str, help='Override home grid name for the first gridset', default=None)
	parser.add_argument('--gridset2home', type=str, help='Override home grid name for the second gridset', default=None)

	args = parser.parse_args()

	extract_gridset_contents(args.gridset1, "extracted1")
	extract_gridset_contents(args.gridset2, "extracted2")

	# Extract home grid names from settings files of each gridset
		# Use specified home grid names if provided, otherwise extract from settings
	home_grid1 = args.gridset1home or get_home_grid_from_settings("extracted1/Settings0/settings.xml")
	home_grid2 = args.gridset2home or get_home_grid_from_settings("extracted2/Settings0/settings.xml")
	
	screen_dimensions = (1920, 1080)  # Define screen dimensions
	
	# Find the main XML file in the extracted directories
	main_xml_file_1 = find_main_grid_xml("extracted1", home_grid1)
	main_xml_file_2 = find_main_grid_xml("extracted2", home_grid2)
		
	# Build navigation maps for each gridset
	navigation_map1 = parse_gridset_for_navigation(main_xml_file_1)
	navigation_map2 = parse_gridset_for_navigation(main_xml_file_2)
	
	# Extract and process grid XML files
	grid_xml_files_1 = find_xml_files("extracted1")
	grid_xml_files_2 = find_xml_files("extracted2")

	gridset1_data = process_gridset_for_csv(grid_xml_files_1, navigation_map1, screen_dimensions, home_grid1)
	save_to_csv(gridset1_data, 'gridset1_data.csv')

	gridset2_data = process_gridset_for_csv(grid_xml_files_2, navigation_map2, screen_dimensions, home_grid2)
	save_to_csv(gridset2_data, 'gridset2_data.csv')

	# Compare gridsets
	results = compare_gridsets(grid_xml_files_1, grid_xml_files_2, navigation_map1, navigation_map2, screen_dimensions, home_grid1, home_grid2)

	# Print results
	for key, value in results.items():
		print(f"{key}: {value}")


if __name__ == "__main__":
	main()
