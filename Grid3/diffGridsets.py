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
	for wordlist in xml_root.findall(".//WordList/Items/WordListItem/Text/r"):
		if wordlist.text:
			wordlist_items.append(wordlist.text)
	return wordlist_items

def extract_cell_contents(xml_root):
	texts = []
	for cell in xml_root.findall(".//Cell/Content/CaptionAndImage/Caption"):
		if cell.text:
			texts.append(cell.text)
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

def compare_texts(texts1, texts2):
	word_count1, phrase_count1 = analyze_texts(texts1)
	word_count2, phrase_count2 = analyze_texts(texts2)

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

def find_xml_files(directory):
	xml_files = []
	for root, dirs, files in os.walk(directory):
		for file in files:
			if file.endswith(".xml"):
				xml_files.append(os.path.join(root, file))
	return xml_files

def main():
	parser = argparse.ArgumentParser(description='Compare the language content of two .gridset files.')
	parser.add_argument('gridset1', type=str, help='Path to the first .gridset file')
	parser.add_argument('gridset2', type=str, help='Path to the second .gridset file')

	args = parser.parse_args()

	extract_gridset_contents(args.gridset1, "extracted1")
	extract_gridset_contents(args.gridset2, "extracted2")

	grid_xml_files_1 = find_xml_files("extracted1")
	grid_xml_files_2 = find_xml_files("extracted2")

	all_texts_1 = []
	all_texts_2 = []

	for file in grid_xml_files_1:
		all_texts_1.extend(extract_cell_contents(parse_xml(file)))

	for file in grid_xml_files_2:
		all_texts_2.extend(extract_cell_contents(parse_xml(file)))

	results = compare_texts(all_texts_1, all_texts_2)

	for key, value in results.items():
		print(f"{key}: {value}")

if __name__ == "__main__":
	main()
