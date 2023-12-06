## Grid 3

- Grid-OBF-WIP.py - a very rough Grid3 to OBF conversion tool
- Grid3-XML-Format.md - documentation on the grid3 format
- GridAnalysis.py. Diff two different gridsets or Analyse a single Gridset. Use it like: NB: Calculations on effort are WIP. It will find the home grid - but you can override it like:

``python
	python GridAnalysis.py "SuperCore30 switch scanning.gridset"  "Super Core 50.gridset" --gridset1home '01 CORE pg1 TEEN' --gridset2home '01 CORE - Home - TEEN ADULT'
	
	or
	
	
	python GridAnalysis.py "SuperCore30 switch scanning.gridset"  
``

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

- addFrequencyData.py SomeFile.csv

	parses a csv file where the first column is a word/phrase. It then finds the frequency count for that word in a corpus. Adds a new column for frquency data. Note this currently set for a news 2013 corpus. Your mileage may vary