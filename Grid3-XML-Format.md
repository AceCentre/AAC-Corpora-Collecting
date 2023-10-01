# Grid 3 File Docs

## Introduction

This document provides a detailed technical guide to the structure and functionalities of Grid 3 files, focusing on the .gridset format used in Augmentative and Alternative Communication (AAC) boards. This guide is targeted at developers, researchers, and advanced users.

## Terminology

- Gridset: A zipped archive containing grid files and settings.
- AAC: Augmentative and Alternative Communication.
- Cell: A button on an AAC board that can have various functionalities.
- ScanBlock: A group of cells that are scanned together.

## Gridset Archive Structure

The grid files are part of a `.gridset` zipped archive. Renaming the file to `.zip` allows you to unzip and explore its contents.

### Directory Structure

- **Grids/**: Directory where each XML grid file resides. E.g., `Grids/About me/grid.xml`
- **Settings0/**: Directory containing settings and styles for the grid.
- **FileMap.xml** An XML file that maps grid XML files and their associated dynamic files.

```xml
<FileMap xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!-- Entry for each grid XML file and its dynamic files -->
  <Entries>
    <Entry StaticFile="Grids\Treats\grid.xml">
      <DynamicFiles>
        <File>Grids\Treats\wordlist-0-0.gridbmp</File>
      </DynamicFiles>
    </Entry>
    <!-- ... -->
  </Entries>
</FileMap>
```

- **Settings0/ettings.xml** Contains settings related to the gridset.

```xml
<GridSetSettings xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!-- Various settings like Appearance, StartGrid, Description, etc. -->
</GridSetSettings>
```

- **Settings/Styles/style.xml** Defines various styles that can be applied to cells.

```xml
<StyleData xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!-- Definition of different styles -->
</StyleData>
```

Each style is documented here for then referencing ib each pages grid.xml e.g

```xml
 <Styles>	
    <Style Key="Workspace">
          <BackColour>#B8312FFF</BackColour>
          <TileColour>#FAC51CFF</TileColour>
          <BorderColour>#FEEFE7FF</BorderColour>
          <FontColour>#FDE8A4FF</FontColour>
          <FontName>Dosis</FontName>
          <FontSize>40</FontSize>
    </Style>
    <!-- ,, -->
```


## Grid XML File Format Documentation

### Overview

Grid XML files are used to describe the layout and content of AAC (Augmentative and Alternative Communication) boards used in the Grid software. They contain information about the grid layout (rows and columns), buttons (also called cells), and their properties.


#### Full Example 

```xml
<Grid xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!--Background colour - hex code -->
  <BackgroundColour>#E2EDF8FF</BackgroundColour>
  <!-- Unique ID -->
  <GridGuid>e631d2c5-cc2c-49b3-b6bb-eb1c81af84af</GridGuid>
  <!-- This defines the  column size -->
  <ColumnDefinitions>
    <ColumnDefinition />
    <ColumnDefinition />
    <ColumnDefinition />
    <ColumnDefinition />
    <ColumnDefinition />
    <ColumnDefinition />
    <ColumnDefinition />
    <ColumnDefinition />
    <ColumnDefinition />
  </ColumnDefinitions>
  <!-- This defines the row or column size -->
  <RowDefinitions>
    <RowDefinition />
    <RowDefinition />
    <RowDefinition />
    <RowDefinition />
    <RowDefinition />
    <RowDefinition />
    <RowDefinition />
  </RowDefinitions>
  <!-- AutoContentCommands - Need some more testing to detail this  -->
  <AutoContentCommands>
    <AutoContentCommandCollection AutoContentType="Prediction">
      <Commands>
        <Command ID="AutoContent.Activate">
          <Parameter Key="autocontenttype">Prediction</Parameter>
        </Command>
      </Commands>
    </AutoContentCommandCollection>
  </AutoContentCommands>
  <Cells>
    <Cell>
      <Content>
        <Commands>
          <Command ID="Jump.To">
            <Parameter Key="grid">Special</Parameter>
          </Command>
        </Commands>
        <CaptionAndImage>
          <Caption>Special</Caption>
          <Image>[grid3x]star.wmf</Image>
        </CaptionAndImage>
        <Style>
          <BasedOnStyle>Navigation category style</BasedOnStyle>
        </Style>
      </Content>
    </Cell>
    <!--etc-->
  </Cells>
  <!-- this gives highlight description text for each Block in the block scan. NB: max of 8 -->
  <ScanBlockAudioDescriptions>
    <ScanBlockAudioDescription>
      <ScanBlock>1</ScanBlock>
    </ScanBlockAudioDescription>
    <ScanBlockAudioDescription>
      <ScanBlock>2</ScanBlock>
    </ScanBlockAudioDescription>
    <ScanBlockAudioDescription>
      <ScanBlock>3</ScanBlock>
    </ScanBlockAudioDescription>
    <ScanBlockAudioDescription>
      <ScanBlock>4</ScanBlock>
    </ScanBlockAudioDescription>
    <ScanBlockAudioDescription>
      <ScanBlock>5</ScanBlock>
    </ScanBlockAudioDescription>
    <ScanBlockAudioDescription>
      <ScanBlock>6</ScanBlock>
    </ScanBlockAudioDescription>
    <ScanBlockAudioDescription>
      <ScanBlock>7</ScanBlock>
    </ScanBlockAudioDescription>
    <ScanBlockAudioDescription>
      <ScanBlock>8</ScanBlock>
    </ScanBlockAudioDescription>
  </ScanBlockAudioDescriptions>
  <!-- Wordlists - this is an AutoContent Type cell. More info to come here>
  <WordList>
    <Items />
  </WordList>
</Grid>
```

### Structure

- **Root Element**: The root element usually encapsulates the entire XML document and contains all other elements.
  
  ```xml
  <Root>
    <!-- Child elements go here -->
  </Root>
  ```
  
#### Elements and Attributes

- **Grid Element**
- **BackgroundColour**: Specifies the background color of the grid using a hex code. E.g., `<BackgroundColour>#E2EDF8FF</BackgroundColour>`
- **GridGuid**: A unique identifier for the grid. E.g., `<GridGuid>e631d2c5-cc2c-49b3-b6bb-eb1c81af84af</GridGuid>`

#### Layout Information

- **ColumnDefinitions**: Defines the number of columns in the grid.

  ```xml
  <ColumnDefinitions>
    <ColumnDefinition />
    <!-- Repeat for each column -->
  </ColumnDefinitions>
  ```

- **RowDefinitions**: Defines the number of rows in the grid.

  ```xml
  <RowDefinitions>
    <RowDefinition />
    <!-- Repeat for each row -->
  </RowDefinitions>
  ```

- **AutoContentCommands**:  A section for commands related to auto content like predictions.

```xml
<AutoContentCommands>
  <AutoContentCommandCollection AutoContentType="Prediction">
    <Commands>
      <Command ID="AutoContent.Activate">
        <Parameter Key="autocontenttype">Prediction</Parameter>
      </Command>
    </Commands>
  </AutoContentCommandCollection>
</AutoContentCommands>
```

- **ScanBlockAudioDescriptions**: Provides audio descriptions for each scan block. The maximum number of scan blocks is 8.
```xml
<ScanBlockAudioDescriptions>
  <ScanBlockAudioDescription>
    <ScanBlock>1</ScanBlock>
  </ScanBlockAudioDescription>
  <!-- ... -->
</ScanBlockAudioDescriptions>
```

- **WordList:** Defines an AutoContent Type cell, which may contain word lists or other dynamic content. 

```xml
<WordList>
    <Items>
      <WordListItem>
        <Text>
          <s Image="[widgit]widgit rebus\h\hello.emf">
            <r>Hello</r>
          </s>
        </Text>
        <Image>[widgit]widgit rebus\h\hello.emf</Image>
        <PartOfSpeech>Unknown</PartOfSpeech>
      </WordListItem>
	  <!--  etc  -->
    </Items>
  </WordList>
```

### Buttons (Cells)

#### Overview

- **Cells**: Contains the definitions for each button or cell.

  ```xml
  <Cells>
    <Cell>
      <!-- Cell properties go here -->
    </Cell>
    <!-- Repeat for each cell -->
  </Cells>
  ```
#### Attributes of Cell

Cells are the primary elements that make up a grid. They are defined using the <Cell> tag and can have various attributes.

- X and Y: These define the cell's position in the grid, corresponding to its column (X) and row (Y).
- ScanBlock:Optional attribute to define which scan block the cell belongs to.
   - There is a maximum of 8 scan blocks per page.
  - Values range from 1 to 8.
  - A cell can be in any of these blocks.
  - If not specified, the attribute is not needed for that particular cell.
  
```xml
<Cell X="7" Y="1" ScanBlock="2">
```

##### Properties of Cell

- **Caption**: The text displayed on the button.

```xml
<Caption>Hello</Caption>
```

- **CaptionAndImage**: It has a image and caption. Image relates to a ``[symbol-library]filename.extension`` (NB: The Grid licences Widgit)

```
 <CaptionAndImage>
	  <Caption>Keyboard</Caption>
	  <Image>[grid3x]keyboard.wmf</Image>
	</CaptionAndImage>
```

- **Style**: Styles are referenced within cells to determine their appearance.


```xml
<Cell X="7" Y="1">
  <Content>
    <!-- ... -->
    <Style>
      <BasedOnStyle>Actions category style</BasedOnStyle>
    </Style>
  </Content>
</Cell>
```

- **BasedOnStyle**: Refers to a predefined style from style.xml.

You can extend the style of a cell like this

```xml
	<Style>
	  <BasedOnStyle>Verbs</BasedOnStyle>
	  <BackColour>#B8312FFF</BackColour>
	  <TileColour>#FAC51CFF</TileColour>
	  <BorderColour>#FEEFE7FF</BorderColour>
	  <FontColour>#FDE8A4FF</FontColour>
	  <FontName>Dosis</FontName>
	  <FontSize>40</FontSize>
	</Style>
```

Note on WordList cells. These should have a ContentType = AutoContent ContentSubType = WodList

```xml
<Cell X="3" Y="2" ScanBlock="2">
      <Content>
        <ContentType>AutoContent</ContentType>
        <ContentSubType>WordList</ContentSubType>
        <CaptionAndImage xsi:nil="true" />
        <Style>
          <BasedOnStyle>Auto content</BasedOnStyle>
          <BorderColour>#2C82C9FF</BorderColour>
        </Style>
      </Content>
    </Cell>
```

## Commands

Commands are actions that a cell can execute when activated. They are defined under the `<Commands>` tag within a `<Content>` tag in a cell.

### Simple Command

A command without parameters looks like the following:

```xml
<Command ID="Jump.Back" />
```

### Command with Parameters

A command with additional settings can have parameters:

```xml
<Command ID="Action.Speak">
  <Parameter Key="unit">All</Parameter>
  <Parameter Key="movecaret">0</Parameter>
</Command>
```

### Common Commands and Parameters

#### `AutoContent.Activate`
- Parameters: Unknown

#### `Jump.To`
- Parameters: key 
- Value "Grid file name" e.g. "Places" found within the .gridset bundle

```xml
<Parameter Key="grid">Quantity</Parameter>`` is a Jump to the Grid "Quantity" page
```

#### `Jump.Back`
- Parameters: None

#### `Action.Speak`
- Parameters:
  - `unit`: Specifies what to speak (e.g., "All")
  - `movecaret`: Moves the caret position (e.g., "0")

#### `Settings.RestAll`
- Parameters:
  - `indicatorenabled`: Enables or disables an indicator (e.g., "1" for enabled)
  - `action`: Specifies the action to perform (e.g., "Toggle")

#### `Action.InsertText`
- Parameters:
  - `text`: Text to insert into the message window

#### `Action.DeleteWord`
- Parameters: None

#### `Action.Clear`
- Parameters: None

#### `Action.Letter`
- Parameters:
  - `letter`: Letter to insert into the message window
  


---

This is a basic outline and may not cover all the intricacies of the Grid XML format. Additional elements and attributes could be present based on the specific features used in the Grid software.