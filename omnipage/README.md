# omnipage

This is a sample C++ command-line tool build using the OmniPage Capture SDK for Linux by Nuance for parsing PDFs to XML.

## Build

Run `make` after `cd omnipage/`.  This should output an executable called `corvid`.

## Usage

The command-line argument looks like

```bash
corvid -i PAPER_ID.pdf -o PAPER_ID.xml 
```

## Miscellaneous

Unintended, but this also works for PNG inputs.