import sqlite3
import argparse

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


def connect_to_database(file_path):
	""" Connect to the SQLite database and return a connection object. """
	return sqlite3.connect(file_path)

def extract_data_from_snap_db(connection):
	""" Extract relevant data from the database for analysis. """
	cursor = connection.cursor()
	
	# Extracting button labels and corresponding page titles
	query = """
	SELECT b.Label, p.Title 
	FROM Button AS b
	JOIN ButtonPageLink AS bpl ON b.Id = bpl.ButtonId
	JOIN Page AS p ON bpl.PageUniqueId = p.UniqueId
	"""
	cursor.execute(query)
	button_page_data = cursor.fetchall()

	# Example of additional data extraction and processing
	# ...

	return button_page_data

def extract_cell_data_from_snap_db(connection):
	""" Extract cell data from the database for analysis. """
	cursor = connection.cursor()
	
	# SQL query to extract data related to cells (buttons) and their placement
	query = """
	SELECT 
		b.Label AS text, 
		bp.GridPosition AS position,
		p.Title AS grid_name
	FROM Button AS b
	JOIN ButtonPlacement AS bp ON b.Id = bp.ButtonId
	JOIN Page AS p ON bp.PageLayoutId = p.Id
	"""
	cursor.execute(query)
	cell_data = cursor.fetchall()

	# Convert data into a list of dictionaries
	cell_data_list = []
	for text, position, grid_name in cell_data:
		cell_data_dict = {
			'text': text,
			'grid_name': grid_name,
			'position': position,
			# Additional fields like 'effort_score', 'hits', etc. can be calculated or added here
			# 'effort_score': calculate_effort_score(...),
			# 'hits': ...,
			# ...
		}
		cell_data_list.append(cell_data_dict)

	return cell_data_list
	
def analyze_snap_data(button_page_data):
	""" Analyze the extracted data and return statistics or insights. """
	# Example analysis: Count of buttons per page
	page_button_count = {}
	for label, page_title in button_page_data:
		if page_title in page_button_count:
			page_button_count[page_title] += 1
		else:
			page_button_count[page_title] = 1

	# More complex analysis can be added here
	# ...

	return page_button_count


def process_snap_gridset(file_path):
	""" Process a Snap gridset file and return statistics. """
	with connect_to_database(file_path) as connection:
		button_page_data = extract_data_from_snap_db(connection)
		statistics = analyze_snap_data(button_page_data)
	
	return statistics

def main():
	parser = argparse.ArgumentParser(description='Analyse the language content of Snap SPS files.')
	parser.add_argument('snap', type=str, help='Path to the first .sps file')
	args = parser.parse_args()

	# Main logic for processing a Snap gridset
	snap_stats = process_snap_gridset(args.snap)

if __name__ == "__main__":
	main()
