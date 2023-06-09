import re

"""SET OF FUNCTIONS THAT HELPS ON READING AND STRUCTURING DATA FROM SEC FILES INTO PYTHON STANDARDS"""

def find_bracket_contents(file_path):
    with open(file_path, 'r', encoding = 'latin-1') as file:
        lines = file.readlines()

    pattern = r'\[([^\]]+)\]'  # Matches contents inside brackets [ ]
    contents = []
    next_lines = []
    current_cluster = []

    bracket_found = False
    for line in lines:
        if not bracket_found:
            match = re.search(pattern, line)
            if match:
                contents.append(match.group(1))
                current_cluster = []
                bracket_found = True
            else:
                current_cluster.append(line)
        else:
            match = re.search(pattern, line)
            if match:
                next_lines.append(tuple(current_cluster))
                contents.append(match.group(1))
                current_cluster = []
            current_cluster.append(line)

    next_lines.append(tuple(current_cluster))  # Append the last cluster of lines

    result_dict = {}
    for content, lines in zip(contents, next_lines):
        result_dict[content] = lines

    return result_dict

def shape_result(result_dict):
    desired_output = {}
    for key,values in result_dict.items():
        std_dict={}
        for item in values:
            if "=" in item:
                KV = item.split("=")
                std_dict.setdefault(KV[0],KV[1].replace('\n',''))
        desired_output[key]=std_dict
    return desired_output

#connect the data from the .SEC file into the Analyst output
#.BIN files can be read with the Reticulate