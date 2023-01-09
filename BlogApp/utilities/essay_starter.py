from transformers import pipeline

def generate(text, length, gen, temp):
    if gen == 'gpt_125M':
        generator = pipeline('text-generation', model='EleutherAI/gpt-neo-125M')
    elif gen == 'gpt_13B':
        generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')
    elif gen == 'gpt_27B':
        generator = pipeline('text-generation', model='EleutherAI/gpt-neo-2.7B')
    else:
        print(gen)
        return 'error'
    
    prompt = str(text)
    length = int(length)
    res = generator(prompt, max_length=(int(len(text))+int(length)), do_sample=True, temperature=float(temp))
    return (res[0]['generated_text'])
        

#main('Everybody is equally culpable in causing climate change', 50)