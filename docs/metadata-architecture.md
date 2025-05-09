```mermaid

flowchart TB
  subgraph DataInputs[Data Inputs]
      direction LR
      NRM
      PostgreSQL
      Other
      subgraph MetadataSpreadsheetEntry[Metadatda Spreadsheet Entry]
      end
  end

  NRM --> MetadataSpreadsheetEntry
  PostgreSQL --> MetadataSpreadsheetEntry
  Other --> MetadataSpreadsheetEntry

  subgraph Review
    direction TB
    A@{ shape: diamond, label: "Approval?" }      
  end

  subgraph EDW[Enterprise Data Wharehouse Ingest]
  end

  MetadataSpreadsheetEntry --> Review
  A --> |Yes| EDW
  A --> |No| DataInputs
  
```
