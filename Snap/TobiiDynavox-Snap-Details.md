# Tobii Dynavox Snap Database Structure

Exports are .sps files which are SQLite databases without encryption.

## Key Tables for Translation

The translatable text content is found in:
- `Button.Label` - The visible text on buttons
- `Button.Message` - The text spoken when button is pressed
- `Page.Title` - The name of each page

## Core Structure

### Pages and Layout
- Pages are defined in the `Page` table
- Each page has a unique identifier (`UniqueId`) and a grid layout (`GridDimension` stored as "rows,cols")
- The layout hierarchy is:
  ```
  Page -> PageLayout -> ElementPlacement -> ElementReference -> Button
  ```

### Button Placement
Buttons are positioned through:
1. `ElementReference` - Links buttons to the layout system
2. `ElementPlacement` - Contains grid position info
   - `GridPosition` - Stored as "row,col" string
   - `GridSpan` - For buttons spanning multiple cells

### Navigation
Navigation between pages is handled by:
- `ButtonPageLink` table which connects:
  - `ButtonId` -> The source button
  - `PageUniqueId` -> The target page's unique identifier

### Database Schema

Key tables and their relationships:

```dbml
Table Page {
  Id int [pk]
  UniqueId varchar(36)
  Title varchar
  GridDimension varchar  // Format: "rows,cols"
  Language varchar
}

Table ElementReference {
  Id int [pk]
  ElementType int
  PageId int [ref: > Page.Id]
}

Table ElementPlacement {
  Id int [pk]
  GridPosition varchar  // Format: "row,col"
  GridSpan varchar
  ElementReferenceId int [ref: > ElementReference.Id]
  PageLayoutId int
}

Table Button {
  Id int [pk]
  UniqueId varchar(36)
  Label varchar
  Message varchar
  ElementReferenceId int [ref: > ElementReference.Id]
}

Table ButtonPageLink {
  Id int [pk]
  ButtonId int [ref: > Button.Id]
  PageUniqueId varchar(36)  // References Page.UniqueId
}
```

## Important Notes

1. Button positions are determined through the ElementReference/ElementPlacement system, not stored directly on buttons
2. Navigation uses UniqueIds rather than numeric IDs for page references
3. Grid dimensions and positions are stored as comma-separated strings
4. The ElementReference table acts as a bridge between Buttons and their placement in the grid

## Translation Workflow

When translating:
1. Extract text from:
   - `Button.Label`
   - `Button.Message`
   - `Page.Title`
2. Update these fields with translations
3. Optionally update `Button.Language` and `Page.Language` with target language code
