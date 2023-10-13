from flask import Flask, render_template, redirect, url_for, request
import requests, json, time, os, random

app = Flask(__name__)

LCPP_ENDPOINT="http://144.76.91.241:13888/completion"
RESPONSES='responses/'

examples=[
  'Why did the vampire need mouthwash?',
  'My girlfriend changed after she became a vegetarian.',
  'My personal trainer told me I should do lunges to stay in shape.',
  'My wife bought me camouflage underwear',
  'When I was getting my prostate exam.',
  'What did the sick chickpea say to another chickpea?',
  'The professional bowlers tried to start a labor union, but they were terrible negotiators.'
]

# less numbers please
number_penalty=-4.0
biases=[
  [28774,number_penalty],
  [28783,number_penalty],
  [28787,number_penalty],
  [28784,number_penalty],
  [28782,number_penalty], 
  [28781,number_penalty], 
  [28770,number_penalty], 
  [28750,number_penalty], 
  [28740,number_penalty]
]

pinned=[
  {'base': 'Venture capitalist walks into a bar and says.', 'punchline': 'I’ll have what he’s having'},
  {'base': 'What manager says when enters a meeting naked and half an hour late?', 'punchline': 'My apologies, I had to see the CEO'},
  {'base': 'It''s a little known fact that Elton John doesn''t like iceberg lettuce.', 'punchline': 'He thinks it''s a little chilly'},
  {'base': 'A monad walks into a bar and asks.', 'punchline': 'Hi I''m _ , what is your name'},
  {'base': 'My son was chewing on electrical cords.', 'punchline': 'I knew he needed a power nap'},
  {'base': 'Why do they lock gas station bathrooms?', 'punchline': 'Because they contain too many combustible materials'},
  {'base': 'Why airplane food is so bad?', 'punchline': 'Because it''s made by people who are at high altitude'},
  {'base': 'What venture capitalist says to Pikachu?', 'punchline': 'I would like to Ash-ure you that this electric Pokémon is a good investment'},
  {'base': 'My wife bought me camouflage underwear', 'punchline': 'ive been wearing them for weeks now and she still can''t find them'},
  {'base': 'If I was to have sex with one animal it would be a horse.', 'punchline': 'Because they don''t fart when you ride em'},
]

@app.route("/")
def index():
  files=sorted(os.listdir(RESPONSES), reverse=True)[:20]
  jokes=[]
  for file in files:
    f = open(RESPONSES+file, 'r')
    response=json.loads(f.read())
    timings=response['timings']
    joke={
      'base': response['prompt'].replace('[INST]','').replace('[/INST]', ''), 
      'punchline': response['content'], 
      'prompt_ms': timings['prompt_ms'],
      'predicted_ms': timings['predicted_ms'],
      'prompt_n': timings['prompt_n'],
      'predicted_n': timings['predicted_n'],
      'predicted_per_token_ms': timings['predicted_per_token_ms']
    }
    f.close()
    jokes.append(joke)

  return render_template('index.html', prompt=random.choice(examples), latest=jokes, best=pinned)

@app.route("/generate", methods=['GET','POST'])
def generate():
  if request.method == 'POST':
    prompt=request.form['prompt']
    if len(prompt) < 10:
      return redirect('/')
    else:
      query={'prompt': '[INST] '+prompt+' [/INST] ', 'logit_bias': biases, 'mirostat': 2}
      http_response=requests.post(LCPP_ENDPOINT, json=query).content
      now = time.time()
      f = open(RESPONSES+str(time.time())+'.json','w')
      f.write(http_response.decode(encoding='utf-8', errors='strict'))
      f.close()
      print(http_response)
      json_response=json.loads(http_response)
      timings=json_response['timings']
      joke={
        'base': prompt, 
        'punchline': json_response['content'], 
        'prompt_ms': timings['prompt_ms'],
        'predicted_ms': timings['predicted_ms'],
        'prompt_n': timings['prompt_n'],
        'predicted_n': timings['predicted_n'],
        'predicted_per_token_ms': timings['predicted_per_token_ms']
      }
      return render_template('generate.html', joke=joke, prompt=prompt);
  else:
    return redirect('/')