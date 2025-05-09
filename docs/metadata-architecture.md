```mermaid

flowchart TB
  subgraph DataInputs
      direction LR
      NRM
      PostgreSQL
      Other
      MetadataSpreadsheetEntry
  end

  NRM --> MetadataSpreadsheetEntry
  PostgreSQL --> MetadataSpreadsheetEntry
  Other --> MetadataSpreadsheetEntry  
```
