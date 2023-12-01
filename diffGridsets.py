import zipfile
import xml.etree.ElementTree as ET
import os
import argparse
from collections import Counter

def extract_gridset_contents(file_path, extract_to):
	with zipfile.ZipFile(file_path, 'r') as zip_ref:
		zip_ref.extractall(extract_to)

def parse_xml(file_path):
	tree = ET.parse(file_path)
	root = tree.getroot()
	return root

def extract_wordlist_items(xml_root):
	wordlist_items = []
	for wordlist in xml_root.findall(".//WordList/Items/WordListItem/Text"):
		# Extracting text content from WordList items
		if wordlist.text:
			wordlist_items.append(wordlist.text)
	return wordlist_items

def extract_cell_contents(xml_root):
	texts = []
	# Existing code to extract CaptionAndImage/Caption
	for cell in xml_root.findall(".//Cell/Content/CaptionAndImage/Caption"):
		if cell.text:
			texts.append(cell.text)

	# Add WordList items to texts
	texts.extend(extract_wordlist_items(xml_root))
	return texts

def analyze_texts(text_list):
	word_count = Counter()
	phrase_count = 0
	for text in text_list:
		words = text.split()
		if len(words) > 1:
			phrase_count += 1
		word_count.update(words)
	return word_count, phrase_count

def compare_gridsets(gridset1, gridset2):
	# Extract cell contents
	cells1 = extract_cell_contents(parse_xml(gridset1))
	cells2 = extract_cell_contents(parse_xml(gridset2))

	# Analyze texts
	word_count1, phrase_count1 = analyze_texts(cells1)
	word_count2, phrase_count2 = analyze_texts(cells2)

	# Comparison logic here
	# e.g., unique words, shared words, etc.
	
	unique_words1 = set(word_count1.keys())
	unique_words2 = set(word_count2.keys())
	shared_words = unique_words1.intersection(unique_words2)
	exclusive_words1 = unique_words1 - shared_words
	exclusive_words2 = unique_words2 - shared_words

	comparison_results = {
		"Total Words in Gridset 1": sum(word_count1.values()),
		"Total Words in Gridset 2": sum(word_count2.values()),
		"Unique Words in Gridset 1": len(unique_words1),
		"Unique Words in Gridset 2": len(unique_words2),
		"Shared Words": len(shared_words),
		"Exclusive Words in Gridset 1": len(exclusive_words1),
		"Exclusive Words in Gridset 2": len(exclusive_words2),
		"Phrases in Gridset 1": phrase_count1,
		"Phrases in Gridset 2": phrase_count2
	}

	return comparison_results

def main():
	parser = argparse.ArgumentParser(description='Compare the language content of two .gridset files.')
	parser.add_argument('gridset1', type=str, help='Path to the first .gridset file')
	parser.add_argument('gridset2', type=str, help='Path to the second .gridset file')

	args = parser.parse_args()

	# Extract gridsets
	extract_gridset_contents(args.gridset1, "extracted1")
	extract_gridset_contents(args.gridset2, "extracted2")

	# Perform comparison
	results = compare_gridsets("extracted1/grid.xml", "extracted2/grid.xml")

	# Display results
	for key, value in results.items():
		print(f"{key}: {value}")

if __name__ == "__main__":
	main()
