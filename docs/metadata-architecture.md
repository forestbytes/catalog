```mermaid

flowchart TB
  subgraph DataInputs
      direction LR
      NRM --> MetadataSpreadsheetEntry
      PostgreSQL --> MetadataSpreadsheetEntry
      Other --> MetadataSpreadsheetEntry
      MetadataSpreadsheetEntry
  end
```
