# kici

The repository contains the source code of the docker image. Designed to automate the development of electronic devices in kicad.

I do not guarantee the functionality and backward compatibility of the pipeline. I support it for my processes.

Examples of usage can be found in repository [kici-example](https://github.com/MuratovAS/kici-example).

A detailed description of my interaction processes can be found [here](https://github.com/Artel-Inc/faq)

I work with two platforms `github`, `gitea`

## Features

- `kicad-command` - Project editing tool via commands via `Issues`
  
  - `/CHG WORD1 WORD2` # Search and replace
  
  - `/PROPHIDE PROP,PROP` # Hides the parameter of parts in the diagram
  
  - `/PROPEDIT search_name search_value change_name change_value` # Allows you not only to replace but also to add parameters

- `kicad-order` - System for generating order documents via `Issues`
  
  - Temporary parts replacement document
  
  - List of parts requiring additional purchase

- `kicad-release` - System for generating production documentation
  
  - gerber + drill
  
  - bom + interactive bom
  
  - assembly drawing + board legend
  
  - schematic diagram
  
  - placement file with jlc corrections

- `kicad-rules-check` - Project consistency check
  
  - ERC
  
  - DRC

- `kicad-stock` - Parts Availability Check System
  
  - lcsc
  
  - promelec
  
  - elitan
  
  - Automatic `mpn` detection function by `sku` lcsc

- ISSUE_TEMPLATE

## Usage

### Repository settings

1. Settings -> Actions  -> General
   
   1. Actions permissions = Allow all actions and reusable workflows
   
   2. Approval for running fork pull request workflows from contributors = Require approval for all external contributors
   
   3. Workflow permissions =  Read and write permissions
   
   4. Allow GitHub Actions to create and approve pull requests = true

2. Issues -> Labels -> New lable
   
   1. [command] (Run a command on a repository) {#C1C3E5}
   
   2. [order] (Order details) {#A86D25}

3. Edit repository details -> Topics
   
   1. kicad? - Indicates the version of kicad (ex. `kicad9`)
   
   2. ki?ci? - pipeline version (ex. `ki9ci3`)

### Requirements:

- There should be no spaces in directory and file names. [See](https://github.com/Artel-Inc/faq/blob/main/general_naming_guid.md)

- The `kicad` project must be named `main` (Can be changed via env pipeline). [See](https://github.com/Artel-Inc/faq/blob/main/hardware_repository_structure.md)

- One repository can store several PCBs. The directory should be called hardware, hardware-test....

- The board version should be `vV.V.V-VVV`. [See](https://github.com/Artel-Inc/faq/blob/main/general_version_guid.md)

### Description of versioning

Notation: vA.B.C

Where:

- A - MAJOR version `kicad`

- B - MINOR version `kicad`

- C - Edition number `kici`

I recommend specifying the exact version of the docker image in the pipeline.

## Changelog:

### v9.0.2

- Fix asm pdf

### v9.0.1

- Add PROPHIDE, PROPEDIT in kicad-command
- Add PROPEDIT in kicad-stock

### v9.0.0

- Init
