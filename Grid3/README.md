## Grid 3

- Grid-OBF-WIP.py - a very rough Grid3 to OBF conversion tool
- Grid3-XML-Format.md - documentation on the grid3 format
- GridAnalysis.py. Diff two different gridsets or Analyse a single Gridset. Use it like: NB: Calculations on effort are WIP. It will find the home grid - but you can override it like:

``python
	python GridAnalysis.py "SuperCore30 switch scanning.gridset"  "Super Core 50.gridset" --gridset1home '01 CORE pg1 TEEN' --gridset2home '01 CORE - Home - TEEN ADULT'
	python GridAnalysis.py "SuperCore30 switch scanning.gridset"  
``

