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

#### Buttons (Cells)

- **Cells**: Contains the definitions for each button or cell.

  ```xml
  <Cells>
    <Cell>
      <!-- Cell properties go here -->
    </Cell>
    <!-- Repeat for each cell -->
  </Cells>
  ```

##### Cell Properties

- **Caption**: The text displayed on the button.

  ```xml
  <Caption>Hello</Caption>
  ```

- Other properties like `Image`, `Sound`, `Action`, etc., can also be defined within each `<Cell>` element.

## Commands

Commands are actions that a cell can execute when activated. They are defined under the `<Commands>` tag within a `<Content>` tag in a cell.

### Simple Command

A command without parameters looks like the following:

```xml
<Command ID="Jump.Back" />
```

#### Command with Parameters

A command with additional settings can have parameters:

```xml
<Command ID="Action.Speak">
  <Parameter Key="unit">All</Parameter>
  <Parameter Key="movecaret">0</Parameter>
</Command>
```

#### Common Commands

- AutoContent.Activate: Unknown purpose
- Jump.To: Navigates to a different board
- Jump.Back: Returns to the previous board
- Action.Speak: Activates the speech output
- Settings.RestAll: Resets all settings
- Action.InsertText: Inserts text into the message window
- Action.DeleteWord: Deletes the last word in the message window
- Action.Clear: Clears the message window
- Action.Letter: Inserts a single letter into the message window

---

This is a basic outline and may not cover all the intricacies of the Grid XML format. Additional elements and attributes could be present based on the specific features used in the Grid software.
