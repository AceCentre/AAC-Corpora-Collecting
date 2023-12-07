## Grid 3

- Grid-OBF-WIP.py - a very rough Grid3 to OBF conversion tool
- Grid3-XML-Format.md - documentation on the grid3 format

# Gridset Analysis Tool

## Overview
The Gridset Analysis Tool is designed to analyze and compare the language content of `.gridset` files, commonly used in augmentative and alternative communication (AAC) systems. It provides detailed insights into the distribution and accessibility of words and phrases within these gridsets.

## Features
- **Effort Scoring**: Calculates effort scores for direct selection and scanning, helping to understand the ease of access for each word or phrase.
- **Word Type Classification**: Utilizes NLTK (Natural Language Toolkit) to categorize words into parts of speech such as nouns, verbs, adjectives, etc.
- **Comparative Analysis**: Compares two gridsets to provide insights into unique and shared vocabulary, word type distributions, and effort scores.
- **CSV Export**: Outputs detailed analysis results into CSV files for further examination and reporting.
- **Caching & Asynchronous API Calls**: Implements caching and asynchronous calls for efficient word frequency lookups.

## Installation

1. Clone the repository:

``git clone https://github.com/AceCentre/AAC-Corpora-Collecting/``

2. Navigate to the project directory:

``cd AAC-Corpora-Collecting/Grid3/``

## Usage

Run the tool from the command line, specifying the path to the gridset files and other optional arguments:

``python gridset_analysis.py --gridset1 path/to/gridset1.gridset --gridset2 path/to/gridset2.gridset --output path/to/output``

e.g.

```python

	python GridAnalysis.py "SuperCore30 switch scanning.gridset"  "Super Core 50.gridset" --gridset1home '01 CORE pg1 TEEN' --gridset2home '01 CORE - Home - TEEN ADULT'
	
	or
	
	
	python GridAnalysis.py "SuperCore30 switch scanning.gridset"  
```

example output

```

Total Words in Gridset 1: 9629
Total Words in Gridset 2: 11701
Unique Words in Gridset 1: 2979
Unique Words in Gridset 2: 2977
Shared Words: 2882
Exclusive Words in Gridset 1: 97
Exclusive Words in Gridset 2: 95
Phrases in Gridset 1: 487
Phrases in Gridset 2: 550
Word Type Counts 1:: Counter({'NOUN': 4688, 'PHRASE': 1672, 'ADV': 522, 'VERB': 506, 'ADJ': 486, 'PRON': 358, 'ADP': 282, 'NUM': 148, 'DET': 22, 'CONJ': 6, 'PRT': 4, 'X': 1})
Word Type Counts 2:: Counter({'NOUN': 5062, 'PHRASE': 1643, 'VERB': 1188, 'ADV': 696, 'ADP': 687, 'PRON': 571, 'ADJ': 483, 'DET': 412, 'CONJ': 131, 'PRT': 127, 'NUM': 104, 'X': 1})
Total Pages in Gridset 1: 529
Total Pages in Gridset 2: 456
Total Buttons in Gridset 1: 8234
Total Buttons in Gridset 2: 10088
Average Hits in Gridset 1: 4.723463687150838
Average Hits in Gridset 2: 4.585943695479778
Top 20 Easiest Words/Phrases in Gridset 1: ['it', 'you', 'not', 'more', 'I', 'in', 'good', 'see', 'now', 'want', 'help', 'be', 'er', 'est', 's', 'y', 'ly', "'s", 'happy', 'cold']
Top 20 Easiest Words/Phrases in Gridset 2: ['not', 'now', 'this', 'in', 'on', 'I', 'my', 'it', 'more', 'good', 'and', 'with', 'help', 'put', 'then', 'a', 'the', 'you', 'come', 'see']

```


Note it also spits out a range of csv files for the Gridsets of words and effort. use --output to change the directory



### Arguments
- `gridset1`: Path to the first `.gridset` file.
- `gridset2` (optional): Path to the second `.gridset` file for comparative analysis.
- `gridset1home` (optional): Override the home grid name for the first gridset.
- `gridset2home` (optional): Override the home grid name for the second gridset.
- `output`: Directory to save the output CSV files.

## Output
The program generates several CSV files with comprehensive data including word/phrase, effort scores, scanning effort scores, grid names, positions, and word types. These CSV files are stored in the specified output directory.

### Word Types

This is done using the brown corpus and NLTK. A quick reminder of what the types mean:

- NOUN: This tag is used for words that are nouns, which are typically people, places, things, or ideas. Examples include "dog", "city", "happiness".
- PHRASE: Represents multi-word expressions or phrases.
- ADV (Adverb): Adverbs modify verbs, adjectives, or other adverbs. They often express manner, place, time, frequency, degree, level of certainty, etc. Examples include "quickly", "here", "very".
- VERB: Verbs are action words or state of being words. Examples include "run", "is", "think".
- ADJ (Adjective): Adjectives describe or modify nouns. They can indicate size, quantity, color, etc. Examples include "big", "blue", "happy".
- PRON (Pronoun): Pronouns stand in for nouns or noun phrases. Examples include "he", "they", "it".
- ADP (Adposition): This can refer to prepositions and postpositions used to express spatial or temporal relations or mark various semantic roles. Examples include "in", "at", "by".
- NUM (Numeral): Numerals are words that denote numbers. Examples include "one", "first", "2019".
- DET (Determiner): Determiners are words placed in front of nouns to clarify what the noun refers to. Examples include "the", "a", "these".
- CONJ (Conjunction): Conjunctions connect clauses, sentences, words, or other parts of speech. Examples include "and", "but", "or".
- PRT (Particle): Particles are function words that must be associated with another word or phrase to impart meaning and do not fit well into other categories. This can include infinitive markers like "to" in "to run".
- X: This tag is often used for words that do not belong to any of the above categories or cannot be easily classified. It can also represent words or fragments that are not understood.

## Warnings

- Effort scores are based on this: https://docs.google.com/document/d/1ZJAt1JkpXcHgazEkWMFxxD_l117eD21p1uEFLMqjrjA/edit#heading=h.h0hbg6a3svdx - we havent checked this much yet
- Note top scores etc in output shouldnt be relied on 
- Note too summary data is largely on total - not de-deuplicated words. Use the CSVs to do your own Analysis

## License
MIT


## Contributing
Contributions to the Gridset Analysis Tool are welcome. Please read `CONTRIBUTING.md` for details on our code of conduct, and the process for submitting pull requests to us.

## Authors
- Will Wade
- Simon Judge
- ChatGPT 4 with Advanced Code Analysis



# Grid-FindPathForSentence.py.

## Overview 
Give it csv from our analysis - then a sentence to test. See what the effort scores for scanning or direct selection and alternatives. 
	
```python
	
	 python Grid-FindPathForSentence.py gridset_data.csv "What colour eyes do you have ?" --spelling-page "18e SPELLING qwerty phonics keyboard" --input_technique direct
Sentence Analysis:

Direct Lookup for 'what':
  - Path: 01 CORE pg1 TEEN -> 17a MESSAGES index
  - Effort: 1.94
  - Number of Alternative Paths: 63
  - Hits Range for Alternative Paths: min 2 - max 9

Direct Lookup for 'colour':
  - Path: 01 CORE pg1 TEEN -> 04a ACTIONS main -> 04f ACTIONS A to Z list
  - Effort: 0.0
  - Number of Alternative Paths: 15
  - Hits Range for Alternative Paths: min 3 - max 9

Direct Lookup for 'eyes':
  - Path: 01 CORE pg1 TEEN -> 15aa TOPICS index pg1 TEEN -> 15aa TOPICS index pg2 TEEN -> 15 TOPICS race TEEN
  - Effort: 4.08
  - Number of Alternative Paths: 4
  - Hits Range for Alternative Paths: min 4 - max 9

Direct Lookup for 'do':
  - Path: 01 CORE pg1 TEEN -> 04a ACTIONS main -> 04f ACTIONS A to Z list
  - Effort: 0.0
  - Number of Alternative Paths: 290
  - Hits Range for Alternative Paths: min 2 - max 9

Direct Lookup for 'you':
  - Path: 01 CORE pg1 TEEN -> 05a DESCRIBE main -> 05g DESCRIBE A to Z list
  - Effort: 0.0
  - Number of Alternative Paths: 288
  - Hits Range for Alternative Paths: min 1 - max 9

Direct Lookup for 'have':
  - Path: 01 CORE pg1 TEEN -> 04a ACTIONS main -> 04f ACTIONS A to Z list
  - Effort: 0.0
  - Number of Alternative Paths: 22
  - Hits Range for Alternative Paths: min 2 - max 9

18e spelling qwerty phonics keyboard
18e spelling qwerty phonics keyboard
Spelling '?':
  Letter '?': Path - Default Spelling Path, Effort - 0
  Total spelling effort for '?': 0

Total Effort for 'direct' selection: 6.02

Demonstrating spelling of the entire sentence:

18e spelling qwerty phonics keyboard
Spelling Entire Sentence: 'What colour eyes do you have ?'
  Letter 'w': Path - Default Spelling Path, Effort - 4.34
  Letter 'h': Path - Same as previous, Effort - 4.04
  Letter 'a': Path - Same as previous, Effort - 4.3
  Letter 't': Path - Same as previous, Effort - 4.13
  Letter ' ': Path - Same as previous, Effort - 0
  Letter 'c': Path - Same as previous, Effort - 4.15
  Letter 'o': Path - Same as previous, Effort - 4.23
  Letter 'l': Path - Same as previous, Effort - 4.18
  Letter 'o': Path - Same as previous, Effort - 4.23
  Letter 'u': Path - Same as previous, Effort - 4.12
  Letter 'r': Path - Same as previous, Effort - 4.18
  Letter ' ': Path - Same as previous, Effort - 0
  Letter 'e': Path - Same as previous, Effort - 4.26
  Letter 'y': Path - Same as previous, Effort - 4.11
  Letter 'e': Path - Same as previous, Effort - 4.26
  Letter 's': Path - Same as previous, Effort - 4.3
  Letter ' ': Path - Same as previous, Effort - 0
  Letter 'd': Path - Same as previous, Effort - 4.2
  Letter 'o': Path - Same as previous, Effort - 4.23
  Letter ' ': Path - Same as previous, Effort - 0
  Letter 'y': Path - Same as previous, Effort - 4.11
  Letter 'o': Path - Same as previous, Effort - 4.23
  Letter 'u': Path - Same as previous, Effort - 4.12
  Letter ' ': Path - Same as previous, Effort - 0
  Letter 'h': Path - Same as previous, Effort - 4.04
  Letter 'a': Path - Same as previous, Effort - 4.3
  Letter 'v': Path - Same as previous, Effort - 3.97
  Letter 'e': Path - Same as previous, Effort - 4.26
  Letter ' ': Path - Same as previous, Effort - 0
  Letter '?': Path - Same as previous, Effort - 0
  Total Effort for Spelling Entire Sentence: 96.29	
```

- addFrequencyData.py SomeFile.csv

	parses a csv file where the first column is a word/phrase. It then finds the frequency count for that word in a corpus. Adds a new column for frquency data. Note this currently set for a news 2013 corpus. Your mileage may vary