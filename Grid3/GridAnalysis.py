import zipfile
import xml.etree.ElementTree as ET
import os
import argparse
import math
from collections import Counter
from collections import deque
from collections import defaultdict
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

def build_navigation_map_and_find_relevant_files(start_file):
	navigation_map = {}
	relevant_files = set()

	queue = deque([start_file])
	while queue:
		current_file = queue.popleft()
		if os.path.exists(current_file):
			tree = ET.parse(current_file)
			root = tree.getroot()
			grid_name = get_grid_name_from_path(current_file)
			relevant_files.add(current_file)

			for cell in root.findall('.//Cell'):
				jump_to_command = cell.find(".//Commands/Command[@ID='Jump.To']/Parameter[@Key='grid']")
				if jump_to_command is not None and jump_to_command.text:
					target_grid = jump_to_command.text
					if grid_name not in navigation_map:
						navigation_map[grid_name] = []
					navigation_map[grid_name].append(target_grid)

					target_file = os.path.join(os.path.dirname(os.path.dirname(current_file)), target_grid, "grid.xml")
					if target_file not in relevant_files and os.path.exists(target_file):
						relevant_files.add(target_file)
						queue.append(target_file)  # Continue the recursion by adding the new grid file to the queue

	return navigation_map, relevant_files


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
		#print(f"Target grid '{target_grid}' is the same as home grid.")
		return [home_grid]

	# Initialize BFS
	visited = set()	 # Set to keep track of visited grids
	queue = deque([(home_grid, [])])  # Queue for BFS, storing tuples of (current grid, path to current grid)

	while queue:
		current_grid, path = queue.popleft()
		path.append(current_grid)  # Add the current grid to the path

		#print(f"Visiting: {current_grid}, Path so far: {path}")

		if current_grid not in visited:
			visited.add(current_grid)

			# Check if we have reached the target grid
			if current_grid == target_grid:
				#print(f"Found path to {target_grid}: {path}")
				return path

			# Enqueue all adjacent (navigable) grids
			for next_grid in navigation_map.get(current_grid, []):
				if next_grid not in visited:  # Avoid re-visiting grids
					#print(f"Enqueuing next grid: {next_grid}")
					queue.append((next_grid, path.copy()))

	# print(f"No path found from {home_grid} to {target_grid}.")
	return []  # Return an empty list if no path is found

def extract_gridset_contents(file_path, extract_to):
	with zipfile.ZipFile(file_path, 'r') as zip_ref:
		zip_ref.extractall(extract_to)

def analyze_texts(text_list):
	# NB: Not really using any more but maybe useful in the future. 
	word_count = Counter()
	phrase_count = 0
	for text in text_list:
		words = text.split()
		if len(words) > 1:
			phrase_count += 1
		word_count.update(words)
	return word_count, phrase_count
	

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

	return round(x,2), round(y,2)

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
	NAVIGATION_STEP_WEIGHT = 1.0 

	button_size = BUTTON_SIZE_WEIGHT * grid_rows * grid_cols
	field_size = FIELD_SIZE_WEIGHT * total_visible_buttons
	# Calculate the linear scan position (assuming left-to-right, top-to-bottom scanning)
	linear_position = (button_position[0] - 1) * grid_cols + button_position[1]
	prior_scan = PRIOR_SCAN_WEIGHT * linear_position

	button_coordinates = calculate_button_coordinates(button_position, grid_rows, grid_cols, screen_dimensions)
	screen_width, screen_height = screen_dimensions
	end_x, end_y = button_coordinates
	start_x, start_y = screen_width, screen_height	# Default starting position
	distance = math.sqrt(((start_x - end_x) / screen_width) ** 2 + ((start_y - end_y) / screen_height) ** 2) / math.sqrt(2)

	# Calculate the number of steps to the button's grid and the associated effort
	path_to_button = find_path(home_grid, button_grid, navigation_map)
	navigation_steps = len(path_to_button) - 1 if path_to_button else 0
	navigation_effort = NAVIGATION_STEP_WEIGHT * navigation_steps

	prior_effort = len(path_to_button) - 1 if path_to_button else 0
	hits = len(path_to_button) if path_to_button else 1	 # Number of hits
	
	#print(f"Path from {home_grid} to {button_grid}: {path_to_button}, Hits: {hits}")
	total_effort = button_size + field_size + prior_scan + distance + prior_effort
	return round(total_effort,2), hits

def calculate_scanning_effort(button_position, scan_time_per_unit, selection_time):
	row_effort = (button_position[0] - 1) * scan_time_per_unit
	col_effort = (button_position[1] - 1) * scan_time_per_unit
	total_effort = row_effort + col_effort + selection_time

	# Debugging print statements
	#print(f"Button position: {button_position}, Row effort: {row_effort}, Col effort: {col_effort}, Total effort: {total_effort}")

	return total_effort


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


def extract_combined_cell_and_wordlist_contents(xml_root, grid_name, screen_dimensions):
	"""
	Extracts a combined list of cell contents and wordlist items, along with additional details.

	:param xml_root: The root of the XML tree.
	:param grid_name: The name of the grid.
	:param screen_dimensions: Tuple (width, height) of the screen.
	:return: A list of dictionaries, each containing details about a cell or wordlist item.
	"""
	combined_contents = []
	wordlist_positions = []
	wordlist_grid_positions = []

	# Extract grid rows and columns
	grid_rows = len(xml_root.findall(".//RowDefinitions/RowDefinition"))
	grid_cols = len(xml_root.findall(".//ColumnDefinitions/ColumnDefinition"))

	# Extract text and positions from cells
	for cell in xml_root.findall(".//Cell"):
		cell_data = {}
		cell_x = int(cell.get('X', '1'))  # Default to 1 if not specified
		cell_y = int(cell.get('Y', '1'))  # Default to 1 if not specified
		cell_position = calculate_button_coordinates((cell_x, cell_y), grid_rows, grid_cols, screen_dimensions)
		
		# Check for wordlist cells
		if cell.find(".//ContentSubType") is not None and cell.find(".//ContentSubType").text == "WordList":
			wordlist_positions.append(cell_position)
			wordlist_grid_positions.append((cell_x, cell_y))
			continue

		# Handle regular cells
		text_elements = cell.findall(".//Content/Commands/Command[@ID='Action.InsertText']/Parameter[@Key='text']//r")
		full_text = ' '.join([elem.text.strip() for elem in text_elements if elem.text and elem.text.strip()])
		if full_text:
			cell_data['Text'] = full_text
			cell_data['Position'] = cell_position
			cell_data['XY'] = (cell_x, cell_y)
			cell_data['PageName'] = grid_name
			cell_data['CellType'] = 'Regular'
			combined_contents.append(cell_data)

	# Skip wordlist processing if no WordList ContentSubType cells are found
	if not wordlist_positions:
		return combined_contents

	# Extract items from wordlists
	for wordlist_item in xml_root.findall(".//WordList/Items/WordListItem"):
		word_texts = wordlist_item.findall(".//Text//r")
		full_text = ' '.join([word_text.text.strip() for word_text in word_texts if word_text.text and word_text.text.strip()])

		if full_text:
			position = wordlist_positions.pop(0) if wordlist_positions else 'N/A'
			grid_position = wordlist_grid_positions.pop(0) if wordlist_grid_positions else 'N/A'
			wordlist_data = {
				'Text': full_text,
				'Position': position,
				'XY': grid_position,
				'PageName': grid_name,
				'CellType': 'WordList'
			}
			combined_contents.append(wordlist_data)
	return combined_contents


def process_single_grid_file(file, navigation_map, screen_dimensions, home_grid, scan_time_per_unit, selection_time):
	root = parse_xml(file)
	grid_name = get_grid_name_from_path(file)

	combined_contents = extract_combined_cell_and_wordlist_contents(root, grid_name, screen_dimensions)

	word_count = Counter()
	phrase_count = 0
	cell_data_list = []
	total_hits = 0
	num_cells = 0

	for data in combined_contents:
		word_count.update(data['Text'].split())
		phrase_count += 1 if len(data['Text'].split()) > 1 else 0
		grid_position = data.get('XY', (1, 1))  # Default to (1, 1) if not specified
		path_to_button = find_path(home_grid, grid_name, navigation_map)
		path_str = ' -> '.join(path_to_button)
		rows = len(root.findall(".//RowDefinitions/RowDefinition"))
		cols = len(root.findall(".//ColumnDefinitions/ColumnDefinition"))
		cells = len(root.findall(".//Cell"))
		
		if data['XY'] != 'N/A':
			grid_position = data['XY']		
			effort_score, hits = calculate_grid_effort(
				rows,
				cols,
				cells,
				grid_position,
				screen_dimensions,
				home_grid,
				grid_name,
				navigation_map
			)
			total_hits += hits

			scanning_effort_score = calculate_scanning_effort(
				grid_position,
				scan_time_per_unit,
				selection_time
			)
		else:
			# Handle the 'N/A' case - either skip or set a default effort score
			scanning_effort_score = 0  # Example default value, adjust as needed
			effort_score = 0
		num_cells += 1
		
		cell_data_list.append({
			'text': data['Text'],
			'effort_score': effort_score,
			'Scanning Effort Score': scanning_effort_score,
			'hits': hits,
			'grid_name': grid_name,
			'position_x': data['Position'][0],
			'position_y': data['Position'][1],
			'xy': data['XY'],
			'position': data['Position'],
			'path': path_str,
			'cell_type': data['CellType']
		})

	return word_count, phrase_count, cell_data_list, total_hits, num_cells

def compare_gridsets(grid_xml_files_1, grid_xml_files_2, navigation_map1, navigation_map2, screen_dimensions, home_grid1, home_grid2, scan_time_per_unit, selection_time):
	# Initialize variables
	word_counts_1, phrase_counts_1, effort_scores_1, cell_data_1, total_hits_1, num_cells_1 = Counter(), 0, [], [], 0, 0
	word_counts_2, phrase_counts_2, effort_scores_2, cell_data_2, total_hits_2, num_cells_2 = Counter(), 0, [], [], 0, 0

	# Process each file in gridset 1
	for file in grid_xml_files_1:
		word_count, phrase_count, cell_data, hits, num_cells = process_single_grid_file(
			file, navigation_map1, screen_dimensions, home_grid1, scan_time_per_unit, selection_time
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
			file, navigation_map2, screen_dimensions, home_grid2, scan_time_per_unit, selection_time
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
		"Average Hits in Gridset 1": round((total_hits_1 / num_cells_1 if num_cells_1 > 0 else 0),2),
		"Average Hits in Gridset 2": round((total_hits_2 / num_cells_2 if num_cells_2 > 0 else 0),2),
		"Top 20 Easiest Words/Phrases in Gridset 1": [x['text'] for x in top_20_easiest_1],
		"Top 20 Easiest Words/Phrases in Gridset 2": [x['text'] for x in top_20_easiest_2],
	}

	return comparison_results

def analyze_single_gridset(grid_xml_files, navigation_map, screen_dimensions, home_grid):
	word_counts, phrase_counts, cell_data, total_hits, num_cells = Counter(), 0, [], 0, 0

	# Process each file in the gridset
	for file in grid_xml_files:
		word_count, phrase_count, cells, hits, cells_count = process_single_grid_file(file, navigation_map, screen_dimensions, home_grid)
		word_counts.update(word_count)
		phrase_counts += phrase_count
		cell_data.extend(cells)
		total_hits += hits
		num_cells += cells_count

	unique_words = set(word_counts)
	total_pages = len(set(file for file in grid_xml_files))
	total_buttons = len(cell_data)
	top_20_easiest = sorted(cell_data, key=lambda x: x['effort_score'])[:20]

	return {
		"Total Words": sum(word_counts.values()),
		"Unique Words": len(unique_words),
		"Phrases": phrase_counts,
		"Total Pages": total_pages,
		"Total Buttons": total_buttons,
		"Average Hits": round((total_hits / num_cells if num_cells > 0 else 0),2),
		"Top 20 Easiest Words/Phrases": [x['text'] for x in top_20_easiest]
	}


def process_gridset_for_csv(grid_xml_files, navigation_map, screen_dimensions, home_grid, scan_time_per_unit, selection_time):
	# Initialize list for CSV data
	csv_data = []

	# Process grid files
	for file in grid_xml_files:
		_, _, cell_data, _, _ = process_single_grid_file(
			file, navigation_map, screen_dimensions, home_grid, scan_time_per_unit, selection_time
		)
		for data in cell_data:
			csv_data.append({
				'Word/Phrase': data['text'],
				'Effort Score': data['effort_score'],
				'Scanning Effort Score': data['Scanning Effort Score'],
				'Hits': data['hits'],
				'Grid Name': data['grid_name'],
				'Actual Position X': data['position_x'],
				'Actual Position Y': data['position_y'],
				'XY': data['xy'],
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

def deduplicate_dicts(grid_data):
	deduplicated_dict = {}
	count_dict = defaultdict(int)

	for item in grid_data:
		word_phrase = item.get('Word/Phrase')
		if word_phrase not in deduplicated_dict:
			deduplicated_dict[word_phrase ] = item
		count_dict[word_phrase] += 1

	deduplicated_list = list(deduplicated_dict.values())

	# Add count as another key in each dictionary
	for item in deduplicated_list:
		word_phrase	 = item.get('Word/Phrase')
		item['count'] = count_dict[word_phrase]

	return deduplicated_list


def find_unique_words(grid_data1, grid_data2):
	wordlist2 = set(item['Word/Phrase'] for item in grid_data2)
	unique_dicts_in_list1 = [item for item in grid_data1 if item['Word/Phrase'] not in wordlist2]

	return unique_dicts_in_list1

def main():
	parser = argparse.ArgumentParser(description='Compare the language content of two .gridset files.')
	parser.add_argument('gridset1', type=str, help='Path to the first .gridset file')
	parser.add_argument('gridset2', nargs='?', type=str, help='Path to the second .gridset file')
	parser.add_argument('--gridset1home', type=str, help='Override home grid name for the first gridset', default=None)
	parser.add_argument('--gridset2home', type=str, help='Override home grid name for the second gridset', default=None)
	parser.add_argument('--output', type=str, help='output directory for csv files', default=None)

	args = parser.parse_args()
	screen_dimensions = (1920, 1080)  # Define screen dimensions

	scan_time_per_unit = 1	# Example value, adjust as needed
	selection_time = 0.5  # Example value, adjust as needed
	
	extract_gridset_contents(args.gridset1, "extracted1")

	home_grid1 = args.gridset1home or get_home_grid_from_settings("extracted1/Settings0/settings.xml")
	navigation_map1, relevant_xml_files_1 = build_navigation_map_and_find_relevant_files(os.path.join("extracted1", "Grids", home_grid1, "grid.xml"))

	
	if args.gridset2:	
		extract_gridset_contents(args.gridset2, "extracted2")

		# Extract home grid names from settings files of each gridset
	
		home_grid2 = args.gridset2home or get_home_grid_from_settings("extracted2/Settings0/settings.xml")
		
		# Build navigation maps and find relevant XML files for each gridset
		navigation_map2, relevant_xml_files_2 = build_navigation_map_and_find_relevant_files(os.path.join("extracted2",	 "Grids", home_grid2, "grid.xml"))
	
		# Process and save CSV data for each gridset
		gridset1_data = process_gridset_for_csv(relevant_xml_files_1, navigation_map1, screen_dimensions, home_grid1,scan_time_per_unit, selection_time)
		save_to_csv(gridset1_data, os.path.join(args.output, "gridset1_data.csv"))

		gridset2_data = process_gridset_for_csv(relevant_xml_files_2, navigation_map2, screen_dimensions, home_grid2,scan_time_per_unit, selection_time)
		save_to_csv(gridset2_data, os.path.join(args.output,'gridset2_data.csv'))

		deduplicated_words1 = deduplicate_dicts(gridset1_data)
		save_to_csv(deduplicated_words1, os.path.join(args.output,'gridset1_dedup_data.csv'))

		deduplicated_words2 = deduplicate_dicts(gridset2_data)
		save_to_csv(deduplicated_words2, os.path.join(args.output,'gridset2_dedup_data.csv'))

		gridset1_unique = find_unique_words(deduplicated_words1, deduplicated_words2)
		save_to_csv(gridset1_unique, os.path.join(args.output,'gridset1unique_data.csv'))

		gridset2_unique = find_unique_words(deduplicated_words2, deduplicated_words1)
		save_to_csv(gridset2_unique, os.path.join(args.output,'gridset2unique_data.csv'))

		# Compare gridsets
		results = compare_gridsets(relevant_xml_files_1, relevant_xml_files_2, navigation_map1, navigation_map2, screen_dimensions, home_grid1, home_grid2, scan_time_per_unit, selection_time)


	else:
		# Compare gridsets
		gridset_data = process_gridset_for_csv(relevant_xml_files_1, navigation_map1, screen_dimensions, home_grid1,scan_time_per_unit, selection_time)
		save_to_csv(gridset_data, 'gridset_data.csv')

		# Analyze single gridset
		results = analyze_single_gridset(relevant_xml_files_1, navigation_map1, screen_dimensions, home_grid1)
		
	# Print results
	for key, value in results.items():
		print(f"{key}: {value}")

if __name__ == "__main__":
	main()
