```mermaid

flowchart TB
  subgraph Inputs[Data Inputs]
      direction TB
      NRM
      PostgreSQL
      Other[Other<br>WebApp, Healthy Forest Restoration]     
  end

  subgraph Review
    direction TB
    Spreadsheet --> Application --> PowerPoint
  end

  NRM --> Spreadsheet
  PostgreSQL --> Spreadsheet
  Other --> Spreadsheet

  subgraph EDW
    direction TB
    Approve{Approve?}
    EDWIngest
  end

  PowerPoint --> Approve
  Approve --> |Yes| EDWIngest
  Approve --> |No| Inputs
```