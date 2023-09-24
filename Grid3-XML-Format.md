# Grid 3 File Docs

## Gridset Archive Structure

The grid files are part of a `.gridset` zipped archive. Renaming the file to `.zip` allows you to unzip and explore its contents.

### Directory Structure

- **Grids/**: Directory where each XML grid file resides. E.g., `Grids/About me/grid.xml`
- **Settings0/**: Directory containing settings and styles for the grid.

#### FileMap.xml

An XML file that maps grid XML files and their associated dynamic files.

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

settings.xml

Contains settings related to the gridset.

```xml
<GridSetSettings xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!-- Various settings like Appearance, StartGrid, Description, etc. -->
</GridSetSettings>
```

style.xml

Defines various styles that can be applied to cells.

```xml
<StyleData xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!-- Definition of different styles -->
</StyleData>
```

### Style in Cell
Styles are referenced within cells to determine their appearance.


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

BasedOnStyle: Refers to a predefined style from style.xml.

## Grid XML File Format Documentation

### Overview

Grid XML files are used to describe the layout and content of AAC (Augmentative and Alternative Communication) boards used in the Grid software. They contain information about the grid layout (rows and columns), buttons (also called cells), and their properties.

### Structure

- **Root Element**: The root element usually encapsulates the entire XML document and contains all other elements.
  
  ```xml
  <Root>
    <!-- Child elements go here -->
  </Root>
  ```

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

##### Properties of Cell

- Caption: The text displayed on the button.

```xml
<Caption>Hello</Caption>
```

Other properties like Image, Sound, Action, etc., can also be defined within each <Cell> element.

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
- e.g. ``<Parameter Key="grid">Quantity</Parameter>`` is a Jump to the Grid "Quantity" page


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
