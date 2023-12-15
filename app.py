from flask import Flask, request, render_template, jsonify, redirect
import json
import time
import random
import glob
import os
import ai
from werkzeug.utils import secure_filename
import os


app = Flask(__name__, static_url_path='/static/')
images = ["dropbox.png", "google.png", "gmail.png"]
DEFAULT_QUESTION = '''Begin by briefly describing what you are and what you are tasked to do. After this, print out the string "<NEXTPART>", 
and then provide a quick summarization about the contents of this file starting with "is a file..." without indicating that you're doing going to provide a summarization. Follow this by printing the string "<AFTERSUM>" and then directly print a 2-5 word description of the file without any context or punctuation (strip all punctuation).'''


data_folder = 'data'
os.makedirs(data_folder, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file', 400

    if file:
        filename = secure_filename(file.filename)
        if os.path.exists(os.path.join(data_folder, filename)) == False:
            file.save(os.path.join(data_folder, filename))
        return 'File uploaded successfully', 200

def generate_google_search_result_from_term(term):
    url = f"https://www.google.com/search?q={term.replace(' ', '+')}"
    return {"image": "/static/google_search.png", "content": term, "link": url}

def generate_google_scholar_result_from_term(term):
    url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C31&q={term.replace(' ', '+')}"
    return {"image": "/static/google_scholar.png", "content": term, "link": url}


def generate_wikipedia_result_from_term(term):
    url = f"https://en.wikipedia.org/wiki/Special:Search?go=Go&search={term.replace(' ', '+')}&ns0=1"
    return {"image": "/static/wikipedia.png", "content": term, "link": url}

# This is just mocked out
def find_files_from_term(term):
    values = [x for x in list(glob.glob("data/*")) if x != None and x.endswith(".png") == False and x.endswith(".jpeg") == False and x.endswith(".jpg") == False]
    # This looks better I think when we shuffle them
    random.shuffle(values)
    return values

def generate_file_explores_from_term(term, count=1):
    # url = f"/{term.replace(' ', '+')}"
    results = []
    files = find_files_from_term(term)
    for i in range(min(count, len(files))):
        filename = files[i]
        link = "/explore/" + filename.split("/")[-1]
        results.append({"image": get_icon_for_filename(filename), "content": filename, "link": link})
    return results

def generate_response(term):
    return {"image": "/static/" + random.choice(images), "content": f"Fake response generated at {str(time.time())}"}


@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    data = request.get_json()
    search_term = data.get('term', '')
    print(search_term)
    
    results = []
    results.append(generate_wikipedia_result_from_term(search_term))
    results.append(generate_google_scholar_result_from_term(search_term))
    results.append(generate_google_search_result_from_term(search_term))
    results += generate_file_explores_from_term(search_term, 5)

    #for val in [generate_response(search_term) for i in range(10)]:
    #    results.append(val)
    
    return jsonify({"results": results})

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")
import random
file_cache = {}
def get_icon_for_filename(filename):
    typez = filename.split(".")[-1]
    if typez not in file_cache:
        if os.path.exists(f"static/32/{typez}.png"):
            vv = f"/static/32/{typez}.png"
        else:
            vv = "/" + random.choice(list(glob.glob("static/32/*.png")))
        file_cache[typez] = vv
    return file_cache[typez]

def get_random_file_list(filenamez=None, count=10):
    values = ['/static/excel.png', '/static/gmail.png', '/static/dropbox.png', '/static/file_icon.jpeg']
    xx = []
    files = [x for x in list(glob.glob("data/*")) if x != None and x.endswith(".png") == False and x.endswith(".jpeg") == False and x.endswith(".jpg") == False]
    r = None
    for z in files:
        if z.endswith(filenamez):
            r = z
            break
    xxr = [x for x in files[:count] if x.endswith(filenamez) == False] + [r]
    
    for filename in xxr:
        # input(filename)
        if filename.endswith(filenamez):
            xx.append({'icon': get_icon_for_filename(filename), 'filename': filename, 'primary': True})
        else:
            xx.append({'icon': get_icon_for_filename(filename), 'filename': filename, 'primary': False})
    return xx



@app.route('/graph', methods=['GET'])
def graph():
    return render_template("graph2.html", dataValues=[{'label': 'data.csv', 'icon': 'excel.png'}, {'label': 'image.png', 'icon': 'excel.png'}])
import random
@app.route('/randomExplore')
def random_explore():
    ll = [x['link'] for x in generate_file_explores_from_term("", count=50)]
    print(ll)
    return redirect(random.choice(ll), code=302)
    return ""

@app.route('/explore/<filename>', methods=['GET'])
def explore(filename):
    if os.path.exists(f"data/{filename}") == False:
        return "File doesn't exist", 500
    
    file_contents = open(f"data/{filename}").read()
    start_val = random.randint(1,len(file_contents)-500)
    file_contents = file_contents[start_val:start_val+500]


    question = request.args.get('prompt', DEFAULT_QUESTION)
    file_description = request.args.get('file_description', '')
    short_description =  request.args.get('short_description', '')
    
    for i in range(3):

        # This does the chat gpt integration
        ai_response = ai.get_response_from_question(file_contents, question=question)
        if len(file_description) == 0 and '<NEXTPART>' in ai_response and "<AFTERSUM>" in ai_response:
            ai_response, file_description = ai_response.split("<NEXTPART>")
            file_description, short_description = file_description.split("<AFTERSUM>")
            short_description = short_description.strip().replace(".", "")
            ai_response = ai_response.strip()
            file_description = file_description.strip()
            break
        if len(file_description) > 0:
            break

        print("Looping again to try to get both prompts in 1 query")
            
    if len(file_description) == 0:
        file_description = "File description failed to load"

        
    return render_template("explore.html", mappings=json.dumps(get_random_file_list(filename)), filename=filename, file_contents=file_contents, ai_response=ai_response, file_description=file_description, short_description=short_description)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)