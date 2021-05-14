# AAC-Corpora-Collecting
Research figuring out how we collect corpora/message histories from AAC system

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Windows OS Based AAC Software](#windows-os-based-aac-software)
  - [Grid 3](#grid-3)
  - [TobiiDynavox - Communicator](#tobiidynavox---communicator)
  - [TobiiDynavox - Snap+Core](#tobiidynavox---snapcore)
  - [PRC NuVoice](#prc-nuvoice)
- [iOS only](#ios-only)
  - [Proloquo4Text](#proloquo4text)
- [MultiPlatform](#multiplatform)
  - [CoughDrop](#coughdrop)
  - [AAC Speech Assistant](#aac-speech-assistant)
    - [iOS](#ios)
    - [Android](#android)
  - [Predictable](#predictable)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Windows OS Based AAC Software

## Grid 3

* Download a demo: https://thinksmartbox.com/product/grid-3/
* Prediction engine is SwiftKey (you can see the .net sdk files of learned.json)
* Stores all preferences in C:\Users\Public\Documents\Smartbox\Grid 3\Users\UserName\langCode\Phrases\history.sqlite 
      
   UserName - is whatever users have been set by the Grid. Usually there will only be one. LanCode = e.g en-gb

NB: This ``C:\Users\Public\Documents\`` directory is in the Registry - HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders\Common Document

``FOR /F "tokens=3*" %%A IN ('REG.EXE QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /V "Common Documents" 2^>NUL ^| FIND "REG_SZ"') DO SET CommonDocs=%%B``


* Data is in Table *PhraseHistory* - Phraseid is matched on Table Phrases -id. Each item has a timestamp. So you can do counts on when and how many phrases are in each History. See this [SQLlite database](https://acecentreuk.sharepoint.com/:u:/s/AnonymousShares/ET2O79W1QQlIjVbRNQ2tgMwBCf5c3oncVo5QDOgSr5Tq9w?e=Q0T1co) for what the History data looks like



## TobiiDynavox - Communicator 

* https://uk.tobiidynavox.com/pages/communicator-5-ap
* Download at https://uk.tobiidynavox.com/pages/communicator-5-product-support?tab=1 - eg  https://download.mytobiidynavox.com/Communicator/software/5.5.7/TobiiDynavox_CommunicatorSuite_Installer_5.5.7.12303_en-GB.exe 
* Settings at C:\Users\userName\AppData\Roaming\Tobii Dynavox\Communicator\5\Users\User 1\Settings\VocabularyUsage
* Cant figure this out. Seems to only update on exiting Communicator. 
* Prediction engine is SwiftKey (you can see the .net sdk files of learned.json)

* Looks like its not possible to "read" a swiftkey learned.lm file which is a bummer: https://support.swiftkey.com/hc/en-us/community/posts/115002963989-How-do-I-see-a-library-of-what-SwiftKey-has-learned-

* So we do have some .phr files in "C:\Users\wwade\AppData\Roaming\Tobii Dynavox\Communicator\5\Users\User 1\Phrases"

For example we have one called "Speech history.phr"

It has a file like this:

     ÿþÿ+H e l l o   h o w   a r e   y o u   I   t h i n k   i t ' s   o v e r   c o o k e d . @B ÿþÿH e l l o   h o w   a r e   y o u @B ÿþÿH e l l o @B ÿþÿ H e l l o ,   m y   n a m e   i s   t h i s   l o w   c a r b ? @B ÿþÿH i ,   t h i s   i s   d e l i c i o u s ! @B 
     
See file in the repo with this name. There are other files. Note - these are phrases a user/Tobii predefine. They might not actually use them

## TobiiDynavox - Snap+Core

* https://uk.tobiidynavox.com/products/snap-core-first 
* A UWP App - So sandboxed - Data can be found at `%LOCALAPPDATA%\Packages\`
* uses swiftkey at leaat on windows

## PRC NuVoice

* Uses LAM - Language Activity Monitoring. 
* PRC defined this format many years ago. More on its structure here: https://aacinstitute.org/language-sample-collection-in-aac/ - https://eric.ed.gov/?id=ED441300 
* Its really not designed for this kind of collection. More like every hit. Its going to take quite a lot of parsing for it to be useful. For example this is hello world - and being corrected then spoken. You would have to look for SPE commands - and what preceded it until you hit a DEL or CLEAR command. 
* See LAM-example.txt in this repo for a full example. 

```
        ### CAUTION ###
The following data represents personal communication.
Please respect privacy accordingly.

Automatic Data Logging NuVoice PASS
Version 2.17 2020-09-12
Prentke Romich Company

*[YY-MM-DD=21-05-10]*
11:43:25.017 RECORD ON
11:43:30.697 LOC =I5
11:43:32.217 LOC =G4 [ ]
11:43:32.218 SPE "h"
11:43:32.937 LOC =C3 [ ]
11:43:32.938 SPE "e"
11:43:32.952 LOC =C3 [ ]
11:43:32.953 SPE "e"
11:43:35.657 LOC =J5 [ ]
11:43:36.903 LOC =J4 [ ]
11:43:36.905 SPE "l"
11:43:37.097 LOC =J4 [ ]
11:43:37.098 SPE "l"
11:43:37.577 LOC =I3 [ ]
11:43:37.577 SPE "o"
11:43:38.297 LOC =E6 [ ]
11:43:38.306 SPE " "
11:43:41.737 LOC =B3 [ ]
11:43:41.738 SPE "w"
11:43:41.769 LOC =B3 [ ]
11:43:41.770 SPE "w"
11:43:42.537 LOC =I3 [ ]
11:43:42.538 SPE "o"
11:43:43.177 LOC =D3 [ ]
11:43:43.178 SPE "r"
11:43:44.137 LOC =J4 [ ]
11:43:44.138 SPE "l"
11:43:44.777 LOC =D4 [ ]
11:43:44.778 SPE "d"
11:43:49.097 LOC =J5 [ ]
11:43:49.257 LOC =J5 [ ]
11:43:49.417 LOC =J5 [ ]
11:43:49.657 LOC =J5 [ ]
11:43:50.057 LOC =J5 [ ]
11:43:50.937 LOC =I3 [ ]
11:43:50.938 SPE "o"
11:43:51.648 LOC =D3 [ ]
11:43:51.650 SPE "r"
11:43:52.457 LOC =J4 [ ]
11:43:52.458 SPE "l"
11:43:53.257 LOC =D4 [ ]
11:43:53.258 SPE "d"
11:43:53.897 LOC =E6 [ ]
11:43:53.906 SPE " "

```
# iOS only

## Proloquo4Text

* Something may be in this backup https://www.assistiveware.com/support/proloquo4text/protect-customizations/export-to-dropbox
* 

# MultiPlatform 

## CoughDrop

* https://www.coughdrop.com
* Uses OBL https://www.openboardformat.org/logs

From Brian:

"Extracting just strings from an obl file should be pretty easy. it's just JSON and you'd do the following pseudo-code:

```obj['sessions'].each |session|
  session['events'].each |event|
    if event['label']
      // only button events have labels
    end
  end
end
```

obla files would have gibberish in the label field for any words that weren't considered "core" for that user"

## AAC Speech Assistant
### iOS
Message History can be exported as a plain text file
### Android
You cant export message history


## Predictable

??

