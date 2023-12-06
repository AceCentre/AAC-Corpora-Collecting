import aiohttp
import asyncio
import csv
import argparse

async def get_word_frequency(word, session, semaphore):
	"""Asynchronously fetches word frequency from the Wortschatz Leipzig API."""
	async with semaphore:
		url = f"https://api.wortschatz-leipzig.de/ws/words/eng_news_2013_3M/word/{word}"
		headers = {'accept': 'application/json'}
		try:
			async with session.get(url, headers=headers) as response:
				if response.status == 200:
					data = await response.json()
					return data.get('freq', 0)
				else:
					print(f"Error: Received status code {response.status} for word '{word}'")
					return 0  # or some default value
		except Exception as e:
			print(f"An error occurred while fetching frequency for word '{word}': {e}")
			return 0  # or some default value

async def process_words(words, max_concurrent_requests=5):
	async with aiohttp.ClientSession() as session:
		semaphore = asyncio.Semaphore(max_concurrent_requests)
		tasks = [get_word_frequency(word, session, semaphore) for word in words]
		return await asyncio.gather(*tasks)
		
def read_in_csv(csv_file):
	with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
		reader = csv.DictReader(file)
		data = [row for row in reader]
	return data

def is_single_word(phrase):
	return len(phrase.split()) == 1

def parse_csv(data):
	unique_words = set()
	for row in data:
		word = row['Word/Phrase']
		if is_single_word(word):
			unique_words.add(word)
	return unique_words

def update_csv(data, frequency_dict, csv_file):
	for row in data:
		word = row['Word/Phrase']
		if is_single_word(word):
			row['Frequency'] = frequency_dict.get(word, 0)
		else:
			row['Frequency'] = 'N/A'  # or some other placeholder for phrases

	with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
		fieldnames = list(data[0].keys())
		writer = csv.DictWriter(file, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(data)

def main(csv_file):
	data = read_in_csv(csv_file)
	unique_words = parse_csv(data)

	# Run asynchronous processing
	word_frequencies = asyncio.run(process_words(unique_words))

	# Now `word_frequencies` is a list of frequencies corresponding to `unique_words`
	frequency_dict = dict(zip(unique_words, word_frequencies))
	
	# Now add a column to our csv
	update_csv(data, frequency_dict, csv_file)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Add word frequency data to a CSV file.')
	parser.add_argument('csv_file', type=str, help='Path to the CSV file')
	args = parser.parse_args()
	main(args.csv_file)
