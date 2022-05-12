import csv
import sys
import xml.etree.ElementTree as ET
from io import StringIO
from pathlib import Path
import html


# Function which takes the tsv and xml files and 
# Uses tsv data to add ttu_ids to the standoff markup 
def ttu_updates(tsv, xml, namespaces):
    proj_ids = {} 
    tsv_data = [] 
    with open(tsv) as file:
        # read the tsv file
        t = csv.reader(file, delimiter="\t")
        for line in t:
            tsv_data.append(line)
        try:
            # get each ttu_id from the tsv and map it to the 
            # ttu interview instance 
            # ie. ttu_001_person_01 : ttu_902
            ttu_header = tsv_data[0].index('ttu_id')
            tsv_type = tsv_data[1][0].split('_')
            data_type = tsv_type[2]
            data_type = data_type.capitalize()
            for i in range(1, len(tsv_data)):
                if tsv_data[i][ttu_header] != '':
                    proj_ids[tsv_data[i][0]] = tsv_data[i][ttu_header]
        except:
            print("Error: No ttu_id header found")

    standoff_list = 'list' + data_type

    for s in xml.findall('ns0:standOff', namespaces):
        sub = s

    for s in sub.findall('ns0:'+standoff_list, namespaces):
        l = s

    for person in l.findall('ns0:'+tsv_type[2], namespaces):
        # Gets the ttu interview id of the entities
        ttuId = person.attrib.values()
        ttuId = list(ttuId)
        ttuId = ttuId[0]
        # Checks if the interview id maps to a project id from the tsv 
        if ttuId in proj_ids:
            id = ET.SubElement(person,'ns0:idno')
            id.text = proj_ids[ttuId]
            id.set('type', 'project')
            ET.indent(id)
           
# Takes an xml document formatted as a string and returns it's namespaces
def get_namespaces(xml_string):
    namespaces = dict([node for _, node in ET.iterparse(StringIO(xml_string), events=['start-ns'])])
    namespaces["ns0"] = namespaces[""]
    return namespaces

# updates standoff with ttu_ids
# to run: python3 ttu_updates.py <tsv file path> <narrator_updates.xml file path>
if __name__ == "__main__":
    output = 'updated.xml'

    tsv_name = sys.argv[1]
    if tsv_name == '-h':
        print('This is a tool to add ttu_ids from a tsv into an existing standOff markup of an xml file.')
        print('To run the tool:\n \tpython3 ttu_updates.py <tsv file path> <narrator_updates.xml file path>')
    else: 
        xml_name = sys.argv[2]
        
        # reads xml into a string so that StringIO can find namespaces
        xml_string = ""
        with open(xml_name) as file:
            t = file.readlines()
            for line in t:
                xml_string += line
        
        namespaces = get_namespaces(xml_string)

        # Using ElementTree python library to manipulate xml file
        tree = ET.parse(xml_name)
        root = tree.getroot()
        ttu_updates(tsv_name, root, namespaces)

        # Setting the updated xml file name
        narrator = xml_name.split('.')
        output = narrator[0]
        tree.write(output)
        
        # Removing the default namespace string from the xml output 
        # then creating the final output file
        xml_string = ""
        with open(output) as file:
            t = file.readlines()
            for line in t:
                xml_string += line

        txt = xml_string.replace("ns0:", "")
        text_file = open(output, "w")
        text_file.write(html.unescape(txt))
        text_file.close()

        p = Path(output)
        p.rename(p.with_suffix('.xml'))
        

