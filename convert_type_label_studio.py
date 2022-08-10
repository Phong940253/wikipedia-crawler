import os
import re
import json
res = [f for f in os.listdir() if re.search(
    r'^((?!session).).*crawl\.txt', f)]
# res = [f for f in os.listdir() if re.search(r'^information\-crawl\.txt', f)]
array = []
for f in res:
    label = f.split('-crawl')[0]
    print("processing", label)
    with open(f, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        lines = set(lines)
        lines = [l.strip() for l in lines]

    for line in lines:
        object = {
            "data": {
                "my_text": line
            },
            "predictions": [
                {
                    "result": [
                        {
                            "value": {
                                "choices": [
                                    label
                                ]
                            },
                            "from_name": "sentiment",
                            "to_name": "text",
                            "type": "choices",
                            "origin": "manual"
                        }

                    ]
                }
            ]
        }
        array.append(object)
# Serializing json
json_object = json.dumps(array, ensure_ascii=False, indent=4)

# Writing to sample.json
with open("upload_label_studio.json", "w+", encoding="utf-8") as outfile:
    outfile.write(json_object)
