correct_xml and generate_xml are two scripts that allow to generate a MIS Report Templates for the Balance Sheet and the Profit & Loss

First, use the generate_xml script to generate the template of the model that you need.
Then, use the correct_xml script which will make some modification to the template previously generated.

**MODELS**

- Micro model company with capital [m07-f]
- Abridged model company with capital [m01-f]
- Full model company with capital [m02-f]
- Micro model company without capital [m87-f]
- Abridged model company without capital [m81-f]
- Full model company without capital [m82-f]
- Micro model association [m08-f]
- Abridged model association [m04-f]
- Full model association [m05-f]

**GENERATE_XML**

This script generates the XML MIS Builder template for a specified model (see above)

It uses two JSON files. The first one is located in the 'data' folder and contains all the data of an annual account. The second file is located in the 'calc' folder and contains the rubrics' calculations.

There are also three mandatories options : --filename, --author and --year (see --help for more information)

*USAGE*

python generate_xml.py --filename=FILENAME --author=AUTHOR --year=YEAR data/mXX-f.json calc/22_19_mXX-f.json

Where XX correspond to the model that you want


**CORRECT_XML**

This script corrects some calculations and styles of the XML MIS Builder template for a specified model.

*USAGE*

1) Balance Sheet
python correct_xml.py ../data/mis_report_bs_mXX.xml

2) Profit & Loss
python correct_xml.py ../data/mis_report_pl_mXX.xml

Where XX correspond to the model that you want
