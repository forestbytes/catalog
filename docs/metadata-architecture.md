```mermaid
flowchart LR
  subgraph MetadataArchitecture[Metadata Architecture]
    direction TB
    subgraph DataInputs[Data Inputs]
        direction LR
        NRM --> Review
        PosgreSQL --> Review
        Other --> Review
    end
    subgraph Review
        direction TB
        subgraph Step1
          direction LR
        end
        Step1 --> Step2
    end
  end
  A --> MetadataArchitecture --> B
  DataInputs --> Review

```
