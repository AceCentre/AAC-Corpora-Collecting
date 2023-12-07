import csv
import argparse
from difflib import get_close_matches
from difflib import SequenceMatcher

def read_csv(file_path):
	with open(file_path, mode='r', newline='', encoding='utf-8') as file:
		reader = csv.DictReader(file)
		data_list = []
		for row in reader:
			data_list.append(row)  # Add each row as a dictionary to the list
		return data_list


def find_alternative_paths(word, word_data):
	alternatives = []
	word = word.lower().strip()
	for row in word_data:
		if row['Word/Phrase'].lower().strip() == word and row['Path'] not in alternatives:
			alternatives.append(row['Path'])
	return path, float(effort_score), int(data['Hits']), False	# Add Hits to the returned values

def find_alternative_paths(word, word_data, input_technique):
	alternatives = []
	for row in word_data:
		if word in row['Word/Phrase'].lower():
			effort_score = row['Effort Score'] if input_technique == 'direct' else row['Scanning Effort Score']
			alternatives.append((row['Path'], float(effort_score), int(row['Hits'])))
	return alternatives

def find_path_and_effort(word, word_data, input_technique, spelling_page=None):
	try:
		word_key = word.lower()	 # assuming words in the CSV are in lower case
		for data in word_data:
			if data['Word/Phrase'].lower() == word_key:
				path = data['Path']
				effort_score = data['Effort Score'] if input_technique == 'direct' else data['Scanning Effort Score']
				#print(f"Match found for '{word}': {path}, Effort: {effort_score}") # Debugging statement
				return path, float(effort_score), False	 # Found the word, no spelling done
		# If the word is not found in the word_data list, use spelling
		if spelling_page:
			#print(f"Word '{word}' not found, using spelling page: {spelling_page}")	 # Debugging statement
			spelling_effort, spelling_paths = spell_word_effort(word, word_data, input_technique, spelling_page)
			return spelling_paths, spelling_effort, True  # Spelling required
		else:
			#print(f"Word '{word}' not found and no spelling page provided")	 # Debugging statement
			return "Default Path", 0, False
	except KeyError as e:
		print(f"KeyError: The word '{word}' was not found in the data.")
		return "Error Path", 0, False
	except ValueError as e:
		print(f"ValueError: Invalid effort score format for the word '{word}'.")
		return "Error Path", 0, False
	except Exception as e:
		print(f"An unexpected error occurred: {e}")
		return "Error Path", 0, False



def calculate_total_effort(sentence, word_data, input_technique, spelling_page=None):
	normalized_sentence = sentence.lower().strip()

	# Attempt to find a close match for the entire sentence in word_data
	best_match = None
	highest_ratio = 0.8	 # Set a threshold for the match quality

	for row in word_data:
		word_or_phrase = row['Word/Phrase'].lower().strip()
		match_ratio = SequenceMatcher(None, normalized_sentence, word_or_phrase).ratio()
		if match_ratio > highest_ratio:
			highest_ratio = match_ratio
			best_match = row

	if best_match:
		path, effort = best_match['Path'], float(best_match['Effort Score'] if input_technique == 'direct' else best_match['Scanning Effort Score'])
		print(f"Fuzzy match for phrase: '{sentence}' matched with '{best_match['Word/Phrase']}'\n- Path: {path}\n- Effort: {effort}\n")
		return effort, [path]
		
	words = normalized_sentence.split()
	total_effort = 0
	paths = []
	print("Sentence Analysis:\n")
	for word in words:
		path, effort, spelled = find_path_and_effort(word, word_data, input_technique, spelling_page)
		
		if spelled and spelling_page:
			# Handle spelling
			spelling_effort, spelling_paths = spell_word_effort(word, word_data, input_technique, spelling_page)
			print(f"Spelling '{word}':")
			for letter, letter_path, letter_effort in spelling_paths:
				print(f"  Letter '{letter}': Path - {letter_path}, Effort - {letter_effort}")
			print(f"  Total spelling effort for '{word}': {spelling_effort}\n")
			total_effort += spelling_effort
			paths.extend(spelling_paths)
		else:
			alternatives = find_alternative_paths(word, word_data, input_technique)
			min_hits = float('inf')
			max_hits = 0

			# Summarize alternative paths
			for alt_path, alt_effort, alt_hits in alternatives:
				min_hits = min(min_hits, alt_hits)
				max_hits = max(max_hits, alt_hits)
				if alt_effort < effort:
					path, effort = alt_path, alt_effort

			print(f"Direct Lookup for '{word}':")
			print(f"  - Path: {path}")
			print(f"  - Effort: {effort}")
			print(f"  - Number of Alternative Paths: {len(alternatives)}")
			if alternatives:
				print(f"  - Hits Range for Alternative Paths: min {min_hits} - max {max_hits}")
			else:
				print("	 - No Alternative Paths Found")
			
			total_effort += effort
			paths.append((word, path, effort))
			print()


	return total_effort, paths

def find_all_letters(data_list, spelling_page):
	normalized_spelling_page = spelling_page.lower().strip()
	letters = []

	for row in data_list:
		if row['Grid Name'].lower().strip() == normalized_spelling_page:
			letters.append(row)

	return letters


def spell_word_effort(word, word_data, input_technique, spelling_page):
	total_spelling_effort = 0
	spelling_paths = []
	normalized_spelling_page = spelling_page.lower().strip()

	letters = find_all_letters(word_data, spelling_page)

	if not letters:
		print(f"No letters found for spelling page '{spelling_page}'.")
		return 0, []

	# Find the path for the spelling page
	page_path = "Default Spelling Path"
	page_effort = 0
	for row in letters:
		if row['Word/Phrase'] == spelling_page:
			page_path = row['Path']
			page_effort = float(row['Scanning Effort Score']) if input_technique == 'scanning' else float(row['Effort Score'])
			break
	
	for letter in word.lower():
		letter_found = False
		for row in letters:
			if row['Word/Phrase'].lower() == letter:
				letter_effort = float(row['Scanning Effort Score']) if input_technique == 'scanning' else float(row['Effort Score'])
				letter_found = True
				break

		if not letter_found:
			#print(f"Debug: Effort score for letter '{letter}' not found in spelling page '{spelling_page}'.")
			letter_effort = page_effort

		if not spelling_paths:
			spelling_paths.append((letter, page_path, letter_effort))
		else:
			spelling_paths.append((letter, "Same as previous", letter_effort))

		total_spelling_effort += letter_effort

	return total_spelling_effort, spelling_paths

	# Find the path for the spelling page
	page_path = "Default Spelling Path"
	for key, value in word_data.items():
		if value['Grid Name'].lower().strip() == normalized_spelling_page:
			if page_path == "Default Spelling Path":
				page_path = value['Word/Phrase']
				print(f"Debug: Found spelling page path: {page_path}")
			print(f"Debug: Letter/Phrase in spelling page: {value['Word/Phrase']}")

	for letter in word.lower():
		letter_found = False
		for key, value in word_data.items():
			if value['Grid Name'].lower().strip() == normalized_spelling_page and value['Word/Phrase'].lower() == letter:
				letter_effort = float(value['Scanning Effort Score']) if input_technique == 'scanning' else float(value['Effort Score'])
				print(f"Debug: Found effort score for letter '{letter}': {letter_effort}")
				letter_found = True
				break

		if not letter_found:
			print(f"Debug: Effort score for letter '{letter}' not found in spelling page '{spelling_page}'.")
			letter_effort = 0

		if not spelling_paths:
			spelling_paths.append((letter, page_path, letter_effort))
		else:
			spelling_paths.append((letter, "Same as previous", letter_effort))

		total_spelling_effort += letter_effort

	return total_spelling_effort, spelling_paths


def main(csv_file, sentence, input_technique,spelling_page):
	word_data = read_csv(csv_file)
	total_effort, paths = calculate_total_effort(sentence, word_data, input_technique,spelling_page)
	print(f"Total Effort for '{input_technique}' selection: {total_effort}")
   # Spelling the entire sentence if a spelling page is provided
	if spelling_page:
		print("\nDemonstrating spelling of the entire sentence:\n")
		spelling_effort, spelling_paths = spell_word_effort(sentence, word_data, input_technique, spelling_page)
		print(f"Spelling Entire Sentence: '{sentence}'")
		for letter, letter_path, letter_effort in spelling_paths:
			print(f"  Letter '{letter}': Path - {letter_path}, Effort - {letter_effort}")
		print(f"  Total Effort for Spelling Entire Sentence: {spelling_effort}\n")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Analyze the effort to construct a sentence in an AAC device.')
	parser.add_argument('csv_file', type=str, help='Path to the CSV file')
	parser.add_argument('sentence', type=str, help='Phrase, sentence, or word to analyze')
	parser.add_argument('--input_technique', type=str, default='direct', choices=['direct', 'scanning'], help='Input technique: direct or scanning (default: direct)')
	parser.add_argument('--spelling-page', type=str, help='Name of the spelling page for lookup')

	args = parser.parse_args()
	main(args.csv_file, args.sentence, args.input_technique, args.spelling_page)
	