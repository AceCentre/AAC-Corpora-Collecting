## Grid 3

- Grid-OBF-WIP.py - a very rough Grid3 to OBF conversion tool
- Grid3-XML-Format.md - documentation on the grid3 format
- GridAnalysis.py. Diff two different gridsets or Analyse a single Gridset. Use it like: NB: Calculations on effort are WIP. It will find the home grid - but you can override it like:

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
Total Pages in Gridset 1: 529
Total Pages in Gridset 2: 456
Total Buttons in Gridset 1: 8234
Total Buttons in Gridset 2: 10088
Average Hits in Gridset 1: 4.723463687150838
Average Hits in Gridset 2: 4.585943695479778
Top 20 Easiest Words/Phrases in Gridset 1: ['it', 'you', 'not', 'more', 'I', 'in', 'good', 'see', 'now', 'want', 'help', 'be', 'er', 'est', 's', 'y', 'ly', "'s", 'happy', 'cold']
Top 20 Easiest Words/Phrases in Gridset 2: ['not', 'now', 'this', 'in', 'on', 'I', 'my', 'it', 'more', 'good', 'and', 'with', 'help', 'put', 'then', 'a', 'the', 'you', 'come', 'see']

```


Note it also spits out a range of csv files for the Gridsets of words and effort


- Grid-FindPathForSentence.py. Give it csv from our analysis - then a sentence to test. See what the effort scores for scanning or direct selection and alternatives. 
	
```python
	
	python Grid-FindPathForSentence.py gridset_data.csv "How are you ?" --input_technique scanning
Sentence Analysis:

Word: 'how'
  - Main Path: 01 CORE pg1 TEEN -> 03 QUESTIONS
  - Effort: 2.5
  - Alternative Paths:
    - 01 CORE pg1 TEEN -> 04a ACTIONS main -> 04d ACTIONS doing to things verbs pg1
    - 01 CORE pg1 TEEN -> 19 MAGIC WAND TEEN -> 23 APPS menu TEEN -> 23 APPS Alexa Home -> 23 APPS Alexa Music home -> 23 APPS Alexa Music Album
    - 01 CORE pg1 TEEN -> 19 MAGIC WAND TEEN -> 19 MAGIC WAND access settings -> 00 Choose Version -> 00 Child vocabulary -> 01 CORE pg1 -> 15aa TOPICS index pg1 -> 15c TOPICS Jokes
    ... and 26 more alternatives.

Word: 'are'
  - Main Path: 01 CORE pg1 TEEN -> 03 QUESTIONS
  - Effort: 5.5
  - Alternative Paths:
    - 01 CORE pg1 TEEN -> 15aa TOPICS index pg1 TEEN -> 15aa TOPICS index pg2 TEEN -> 15 TOPICS social care TEEN
    - 01 CORE pg1 TEEN -> 15aa TOPICS index pg1 TEEN -> 15aa TOPICS index pg2 TEEN -> 15 TOPICS social care TEEN
    - 01 CORE pg1 TEEN -> 15aa TOPICS index pg1 TEEN -> 15aa TOPICS index pg2 TEEN -> 15 TOPICS social care TEEN
    ... and 27 more alternatives.

Word: 'you'
  - Main Path: 01 CORE pg1 TEEN -> 19 MAGIC WAND TEEN -> 19 MAGIC WAND access settings -> 00 Choose Version -> 00 Child vocabulary -> 01 CORE pg1 -> 01 CORE pg2 -> 10 NEWS core
  - Effort: 2.5
  - Alternative Paths:
    - 01 CORE pg1 TEEN -> 19 MAGIC WAND TEEN -> 19 MAGIC WAND access settings -> 00 Choose Version -> 00 Child vocabulary -> 01 CORE pg1 -> 01 CORE pg2 -> 10 NEWS core
    - 01 CORE pg1 TEEN -> 19 MAGIC WAND TEEN -> 19 MAGIC WAND access settings -> 00 Choose Version -> 00 Child vocabulary -> 01 CORE pg1 -> 01 CORE pg2 -> 09 CHAT core
    - 01 CORE pg1 TEEN -> 19 MAGIC WAND TEEN -> 19 MAGIC WAND access settings -> 00 Choose Version -> 00 Child vocabulary -> 01 CORE pg1 -> 08a PLAY activity index -> 08i PLAY cars core -> 08i PLAY cars expanded
    ... and 84 more alternatives.

Word not found: ?
Word: '?'
  - Main Path: Spelling Path (if applicable)
  - Effort: 0
  - Alternative Paths:
    - 01 CORE pg1 TEEN -> 07a DAILY LIFE activity index TEEN -> 07x DAILY LIFE eating out core TEEN -> 07x DAILY LIFE eating out expanded TEEN
    - 01 CORE pg1 TEEN -> 19 MAGIC WAND TEEN -> 19 MAGIC WAND access settings -> 00 Choose Version -> 00 Child vocabulary -> 01 CORE pg1 -> 08a PLAY activity index -> 08i PLAY cars core -> 08i PLAY cars expanded
    - 01 CORE pg1 TEEN -> 19 MAGIC WAND TEEN -> 19 MAGIC WAND access settings -> 00 Choose Version -> 00 Child vocabulary -> 01 CORE pg1 -> 08a PLAY activity index -> 08i PLAY cars core -> 08i PLAY cars expanded
    ... and 118 more alternatives.

Total Effort for 'scanning' selection: 10.5

Total Effort for 'scanning' selection: 10.5
Paths: ['01 CORE pg1 TEEN -> 03 QUESTIONS', '01 CORE pg1 TEEN -> 03 QUESTIONS', '01 CORE pg1 TEEN -> 19 MAGIC WAND TEEN -> 19 MAGIC WAND access settings -> 00 Choose Version -> 00 Child vocabulary -> 01 CORE pg1 -> 01 CORE pg2 -> 10 NEWS core', 'Spelling Path (if applicable)']
	
```

- addFrequencyData.py SomeFile.csv

	parses a csv file where the first column is a word/phrase. It then finds the frequency count for that word in a corpus. Adds a new column for frquency data. Note this currently set for a news 2013 corpus. Your mileage may vary