import json 
test = {
    'a' : 0.2651,
    'b' : 0.3216,
}
json_f = json.dumps(test)
out_file = open('test.json', 'w')
out_file.write(json_f)
out_file.close()
