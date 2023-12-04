## Grid 3

- Grid-OBF-WIP.py - a very rough Grid3 to OBF conversion tool
- Grid3-XML-Format.md - documentation on the grid3 format
- DiffGrid2.py. Diff two different gridsets. Use it like: NB: Calculations on effort are WIP. It will find the home grid - but you can override it like:

``python
	python diffGrid2.py "SuperCore30 switch scanning.gridset"  "Super Core 50.gridset" --gridset1home '01 CORE pg1 TEEN' --gridset2home '01 CORE - Home - TEEN ADULT'
``

