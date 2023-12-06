import csv
import argparse
from difflib import get_close_matches

def read_csv(file_path):
	# Read the CSV file and return a dictionary mapping words/phrases to their metrics
	with open(file_path, mode='r', newline='', encoding='utf-8') as file:
		reader = csv.DictReader(file)
		return {row['Word/Phrase'].strip().lower(): row for row in reader}

def find_alternative_paths(word, word_data):
	alternatives = []
	for key, value in word_data.items():
		if word in key:
			alternatives.append(value['Path'])
	return alternatives



def find_path_and_effort(word, word_data, input_technique, spelling_page=None):
	try:
		word_key = word.lower()	 # assuming words in the CSV are in lower case
		if word_key in word_data:
			data = word_data[word_key]
			path = data['Path']
			effort_score = data['Effort Score'] if input_technique == 'direct' else data['Scanning Effort Score']
			return path, float(effort_score), False	 # Third value is False indicating no spelling was done
		elif spelling_page:
			# If the word is not found, spell it out using the spelling page
			spelling_effort, spelling_paths = spell_word_effort(word, word_data, input_technique, spelling_page)
			return spelling_paths, spelling_effort, True  # Spelling required, return the list of spelling paths
		else:
			# Handle cases where the word is not found and there is no spelling page
			print(f"Word not found and no spelling page provided: {word}")
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
	
	# Check for an exact match of the entire sentence
	if normalized_sentence in word_data:
		path, effort, _	 = find_path_and_effort(normalized_sentence, word_data, input_technique)
		print(f"Exact phrase match: '{sentence}'\n- Path: {path}\n- Effort: {effort}\n")
		return effort, [path]

	# Attempt fuzzy matching for the entire sentence
	close_matches = get_close_matches(normalized_sentence, word_data.keys(), n=1, cutoff=0.8)
	if close_matches:
		matched_phrase = close_matches[0]
		path, effort, _ = find_path_and_effort(matched_phrase, word_data, input_technique)
		print(f"Fuzzy match for phrase: '{sentence}' matched with '{matched_phrase}'\n- Path: {path}\n- Effort: {effort}\n")
		return effort, [path]

	# Process each word individually if no phrase match is found
	words = normalized_sentence.split()
	total_effort = 0
	paths = []
	print("Sentence Analysis:\n")
	for word in words:
		# Find path and effort, and check if spelling is needed
		path, effort, _ = find_path_and_effort(word, word_data, input_technique, spelling_page)
		print(f"Direct Lookup for '{word}':\n  - Path: {path}\n	 - Effort: {effort}\n")
		paths.append((word, path, effort))
		# Spelling
		if spelling_page:
			spelling_effort, spelling_paths = spell_word_effort(word, word_data, input_technique, spelling_page)
			print(f"Spelling '{word}':")
			for letter, letter_path, letter_effort in spelling_paths:
				print(f"  Letter '{letter}': Path - {letter_path}, Effort - {letter_effort}")
			print(f"  Total spelling effort for '{word}': {spelling_effort}\n")
			paths.extend(spelling_paths)  # Include spelling paths
			total_effort += spelling_effort
		else:
			alternatives = find_alternative_paths(word, word_data)
			# Limiting the number of alternatives displayed
			max_alternatives = 3
			alternatives_display = alternatives[:max_alternatives]
			more_alternatives = len(alternatives) - max_alternatives

			print(f"Word: '{word}'")
			print(f"  - Main Path: {path}")
			print(f"  - Effort: {effort}")
			if alternatives_display:
				print("	 - Alternative Paths:")
				for alt_path in alternatives_display:
					print(f"	- {alt_path}")
				if more_alternatives > 0:
					print(f"	... and {more_alternatives} more alternatives.")
			paths.append(path)
		print()

		total_effort += effort

	print(f"Total Effort for '{input_technique}' selection: {total_effort}\n")
	return total_effort, paths


def spell_word_effort(word, word_data, input_technique, spelling_page):
    total_spelling_effort = 0
    spelling_paths = []
    # Normalize spelling page name
    normalized_spelling_page = spelling_page.lower().strip()

    # If the spelling page exists in word_data
    if normalized_spelling_page in word_data:
        page_path = word_data[normalized_spelling_page]['Path']
        page_effort = float(word_data[normalized_spelling_page]['Effort Score'])
        
        for letter in word.lower():
            # Assuming each letter's effort score is under the spelling page
            letter_key = f"{normalized_spelling_page}_{letter}"
            if letter_key in word_data:
                letter_effort = float(word_data[letter_key]['Effort Score'])
            else:
                letter_effort = page_effort  # If the letter is not found, use the page's base effort

            # Add the page path only for the first letter
            if not spelling_paths:
                spelling_paths.append((letter, page_path, letter_effort))
            else:
                spelling_paths.append((letter, "Same as previous", letter_effort))
            
            total_spelling_effort += letter_effort

    else:
        print(f"Spelling page '{spelling_page}' not found in word data.")
        # Handle case where spelling page is not found
        # ...

    return total_spelling_effort, spelling_paths




def main(csv_file, sentence, input_technique,spelling_page):
	word_data = read_csv(csv_file)
	total_effort, paths = calculate_total_effort(sentence, word_data, input_technique,spelling_page)
	print(f"Total Effort for '{input_technique}' selection: {total_effort}")
	print("Paths:", paths)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Analyze the effort to construct a sentence in an AAC device.')
	parser.add_argument('csv_file', type=str, help='Path to the CSV file')
	parser.add_argument('sentence', type=str, help='Phrase, sentence, or word to analyze')
	parser.add_argument('--input_technique', type=str, default='direct', choices=['direct', 'scanning'], help='Input technique: direct or scanning (default: direct)')
	parser.add_argument('--spelling-page', type=str, help='Name of the spelling page for lookup')

	args = parser.parse_args()
	main(args.csv_file, args.sentence, args.input_technique, args.spelling_page)
