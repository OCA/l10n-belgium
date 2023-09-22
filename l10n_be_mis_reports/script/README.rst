generate_xml.sh is a script that use two python scripts (correct_xml and generate_xml) and
allow to generate a MIS Report Templates for the Balance Sheet and the Profit & Loss

**USAGE**

./generate_xml.sh -a AUTHOR_NAME -f XX -y YEAR

*Options*

-a : The author name for the copyright

-f : The file model (see bellow). You only need to specify the two digits of the model (mXX-f)

-y : The date of the copyright

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


**GENERATE_XML.py**

This python script generates the XML MIS Builder template for a specified model (see above)

It uses two JSON files. The first one is located in the 'data' folder and contains all the data of an annual account. The second file is located in the 'calc' folder and contains the rubrics' calculations.

There are also three mandatories options : --filename, --author and --year (see --help for more information)

*USAGE*

python generate_xml.py --filename=FILENAME --author=AUTHOR --year=YEAR data/mXX-f.json calc/22_19_mXX-f.json

Where XX correspond to the model that you want


**CORRECT_XML.py**

This python script corrects some calculations and styles of the XML MIS Builder template for a specified model.

*USAGE*

1) Balance Sheet
python correct_xml.py ../data/mis_report_bs_mXX.xml

2) Profit & Loss
python correct_xml.py ../data/mis_report_pl_mXX.xml

Where XX correspond to the model that you want
