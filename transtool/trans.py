import os
import time
from dotenv import load_dotenv # pip3 install python-dotenv
load_dotenv()

import openai # pip3 install openai

OPENAI_MODEL = 'gpt-3.5-turbo'
DOC_PATH_SOURCE = '../'
DOC_PATH_TARGET = '../zh/'

def init_chatgpt():
    openai.organization = os.getenv("OPENAI_ORG")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print('init_chatgpt: ChatGPT inited.')

'''
Translate a paragraph by OpenAI
'''
def chatgpt_translate(content):
    if content == '':
        return ''
    
    time.sleep(1)

    messages = [
        {"role": "system", "content": "Translate the following content to Chinese. Keep the markdown format. Just return the translated content."},
        {"role": "user", "content": content}
        ]
    
    #print('chatgpt_translate: content submitted. ')

    response = openai.ChatCompletion.create(model=OPENAI_MODEL, messages=messages)

    translated = response.choices[0].message.content
    usage = response.usage

    print('chatgpt_translate: Content processed. usage: prompt_tokens={0}, completion_tokens={1}, total_tokens={2}'
          .format(usage.prompt_tokens, usage.completion_tokens, usage.total_tokens))

    return translated.strip()

'''
Append content to target file.
'''
def save_content_append(target, content=''):
    if content == '':
        return
    
    f = open(target, 'a')
    f.write(content)
    f.close()

'''
Let's do it!
'''
def main():
    doc_names = ['404.md', 'about.md', 'create-slide-decks.md', 'deliver-a-talk.md', 'final-words.md',
                'get-speaking-opportunities.md', 'index.md', 'prepare-for-outreach.md', 'prepare-slide-decks.md',
                'record.md', 'recording-talks.md', 'slide-checklist.md', 'talk-delivery-tips.md',
                'things-not-to-say-on-stage.md', 'toc.md', 'travel-and-conference-participation.md',
                'use-the-web.md', 'videos.md', 'what-is-developer-advocacy.md', 'working-from-your-own-computer.md',
                'working-with-your-company.md', 'working-with-your-competition.md', 'write-excellent-code-examples.md',
                'write-great-posts-and-articles.md']

    doc_index = 0 # 0 ~ 23
    skip_para_index = 0 # start with 0 or else when error occured

    print('main: Processing document - {}'.format(doc_names[doc_index]))

    doc_target = os.path.join(DOC_PATH_TARGET, doc_names[doc_index])

    paragraphs, frontmatters = load_paragraphs(doc_names[doc_index])

    if skip_para_index == 0:
        # create target file first because of frontmatter
        # or faild in invoking the OpenAI API
        # then you'd remove the exist content in your target file first. err....
        save_content_append(doc_target, '\n'.join(frontmatters))

    # translate and append to target file
    para_count = len(paragraphs)
    current_para = 0
    for para in paragraphs:
        current_para += 1

        # skip the translated paragraphs
        if current_para <= skip_para_index:
            print('main: Skip paragraph - {}/{}'.format(current_para, para_count))
            continue

        print('main: Translating paragraph - {}/{}'.format(current_para, para_count))
        tran = chatgpt_translate(para)

        # append to target file
        save_content_append(doc_target, '\n\n{}'.format(tran))

    

'''
Load paramgraphs and frontmatters from a markdown document.
'''
def load_paragraphs(doc_name):
    doc = os.path.join(DOC_PATH_SOURCE, doc_name)
    print('load_paragraphs: Loading {}'.format(doc))

    file = open(doc, 'r')
    content = file.read()
    file.close()

    lines = content.split('\n')

    paragraphs = []
    para_lines = []
    frontmatters = []
    in_frontmatter = False

    for idx, l in enumerate(lines):
        #print('load_paragraphs: Line {0}/{1}: {2}'.format(idx + 1, len(lines), l))
        # ignore frontmatter
        if l.startswith('---'):
            in_frontmatter = not in_frontmatter # will occour 2 times
            frontmatters.append(l)
            #print('load_paragraphs: ignore frontmatter {0}/{1}: in_frontmatter: {2}'.format(idx + 1, len(lines), in_frontmatter))
            continue

        if not in_frontmatter:
            # prepare paragraph in multiple lines
            if not l == '':
                # in a paragraph
                para_lines.append(l.strip())
                #print('load_paragraphs: in_paragraph {0}/{1} -- {2}'.format(idx + 1, len(lines), l))
            else:
                # paragraph break, the last line doesn't contain break
                if len(para_lines) > 0:
                    paragraphs.append(' '.join(para_lines))
                    para_lines = []
                #print('load_paragraphs: paragraph_br {0}/{1} <> {2}'.format(idx + 1, len(lines), l))
        else:
            frontmatters.append(l)

    paragraphs.append(' '.join(para_lines))

    return paragraphs, frontmatters


if __name__ == "__main__":
    init_chatgpt()
    main()