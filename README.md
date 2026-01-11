# Tex to Dtx Converter

[<img alt="Linting status of master" src="https://img.shields.io/github/actions/workflow/status/rwarnking/tex-to-dtx-converter/linter.yml?label=Linter&style=for-the-badge" height="23">](https://github.com/marketplace/actions/super-linter)
[<img alt="Version" src="https://img.shields.io/github/v/release/rwarnking/tex-to-dtx-converter?style=for-the-badge" height="23">](https://github.com/rwarnking/tex-to-dtx-converter/releases/latest)
[<img alt="Licence" src="https://img.shields.io/github/license/rwarnking/tex-to-dtx-converter?style=for-the-badge" height="23">](https://github.com/rwarnking/tex-to-dtx-converter/blob/main/LICENSE)

## Description
This is a small python application to convert .tex files to one .dtx file.
All functionalities are accesseable via a simple GUI or console.

## Table of Contents
- [Tex to Dtx Converter](#tex-to-dtx-converter)
  - [Description](#description)
  - [Table of Contents](#table-of-contents)
  - [List of Features](#list-of-features)
  - [Installation](#installation)
    - [Dependencies](#dependencies)
  - [Usage](#usage)
    - [GUI](#gui)
  - [Contributing](#contributing)
  - [Credits](#credits)
  - [License](#license)

## List of Features

- execution via GUI or console
- combine multiple .tex files into one .dtx file
  - [explanation on how a dtx file can look like](https://tex.stackexchange.com/questions/228133/how-to-modify-latex-package-documentation)
- specify meta information like name, author, date and others

## Installation

Download this repository or install directly from GitHub
```bash
pip install git+https://github.com/rwarnking/tex-to-dtx-converter.git
```

### Dependencies

This project uses python. One of the tested versions is python 3.13.

The main dependency is tkinter which can be found here:
* [tkinter](https://docs.python.org/3/library/tkinter.html) for the interface/GUI

Further dependencies that should be present anyway are:
* [os](https://docs.python.org/3/library/os.html)
* [re (regex)](https://docs.python.org/3/library/re.html) for parsing file names
* [sys](https://docs.python.org/3/library/re.html) for parsing file names
* [datetime](https://docs.python.org/3/library/datetime.html) for all time data objects
* [argparse](https://docs.python.org/3/library/argparse.html) for argument loading
* [pathlib](https://docs.python.org/3/library/pathlib.html) for path creation
* [threading](https://docs.python.org/3/library/threading.html) used such that the gui is not freezed while processing,
  [Details](https://realpython.com/intro-to-python-threading/)

## Usage

Run the program using your usual Python IDE (like Visual Code) or via the console `python src\main.py`

### GUI

The GUI lets you select the input and output directory.
Progress-bars are given for continuous observation of the progress.

## Contributing

I encourage you to contribute to this project, in form of bug reports, feature requests
or code additions. Although it is likely that your contribution will not be implemented.

Please check out the [contribution](docs/CONTRIBUTING.md) guide for guidelines about how to proceed
as well as a styleguide.

## Credits
Up until now there are no further contributors other than the repository creator.

## License
This project is licensed under the [MIT License](LICENSE).