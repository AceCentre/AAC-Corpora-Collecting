import csv
import argparse

def read_csv(file_path):
    # Read the CSV file and return a dictionary mapping words/phrases to their metrics
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return {row['Word/Phrase'].lower(): row for row in reader}

def find_alternative_paths(word, word_data):
    alternatives = []
    for key, value in word_data.items():
        if word in key:
            alternatives.append(value['Path'])
    return alternatives



def find_path_and_effort(word, word_data, input_technique):
    try:
        word_key = word.lower()  # assuming words in the CSV are in lower case
        if word_key in word_data:
            data = word_data[word_key]
            path = data['Path']
            effort_score = data['Effort Score'] if input_technique == 'direct' else data['Scanning Effort Score']
            return path, float(effort_score)
        else:
            print(f"Word not found: {word}")
            # Handle spelling or return default values
            return "Spelling Path (if applicable)", 0
    except KeyError:
        print(f"KeyError: The word '{word}' was not found in the data.")
        return "Error Path", 0
    except ValueError:
        print(f"ValueError: Invalid effort score format for the word '{word}'.")
        return "Error Path", 0
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "Error Path", 0


def calculate_total_effort(sentence, word_data, input_technique):
    # Check if the entire sentence is a phrase in the CSV
    if sentence.lower() in word_data:
        path, effort = find_path_and_effort(sentence, word_data, input_technique)
        print(f"Phrase: '{sentence}'\n- Path: {path}\n- Effort: {effort}\n")
        return effort, [path]

    words = sentence.lower().split()
    total_effort = 0
    paths = []
    print("Sentence Analysis:\n")
    for word in words:
        path, effort = find_path_and_effort(word, word_data, input_technique)
        alternatives = find_alternative_paths(word, word_data)
        
        # Limiting the number of alternatives displayed
        max_alternatives = 3
        alternatives_display = alternatives[:max_alternatives]
        more_alternatives = len(alternatives) - max_alternatives

        print(f"Word: '{word}'")
        print(f"  - Main Path: {path}")
        print(f"  - Effort: {effort}")
        if alternatives_display:
            print("  - Alternative Paths:")
            for alt_path in alternatives_display:
                print(f"    - {alt_path}")
            if more_alternatives > 0:
                print(f"    ... and {more_alternatives} more alternatives.")
        print()

        total_effort += effort
        paths.append(path)
    print(f"Total Effort for '{input_technique}' selection: {total_effort}\n")
    return total_effort, paths


def spell_word(word, word_data, input_technique):
    # Define logic to spell the word and calculate effort
    # Return the concatenated paths and total effort for spelling the word
    pass

def main(csv_file, sentence, input_technique):
    word_data = read_csv(csv_file)
    total_effort, paths = calculate_total_effort(sentence, word_data, input_technique)
    print(f"Total Effort for '{input_technique}' selection: {total_effort}")
    print("Paths:", paths)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze the effort to construct a sentence in an AAC device.')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file')
    parser.add_argument('sentence', type=str, help='Phrase, sentence, or word to analyze')
    parser.add_argument('--input_technique', type=str, default='direct', choices=['direct', 'scanning'], help='Input technique: direct or scanning (default: direct)')
    
    args = parser.parse_args()
    main(args.csv_file, args.sentence, args.input_technique)
