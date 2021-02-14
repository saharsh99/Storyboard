import requests

url = "https://quillbot.com/"
# word_url = "https://rest.quillbot.com/api/paraphraser/segment3?text={}&inputLang=en"
para_url = "https://rest.quillbot.com/api/paraphraser/single-paraphrase/2?text={}&strength=2&autoflip=false&wikify=false&fthresh=-1&inputLang=en"
sum_url = "https://www.tools4noobs.com/"

cookie = {
    "__cfduid": "d8a822c1a06dc88967bf974823e37c2b51612365505",
    "_gi": "dGA1.2.622949459.1612365507",
    "_gcl_au": "1.1.1031468685.1612365507",
    "user_status": "not registered",
    "_uetsid": "1242fff0663311eb86c3bf2b9b5bdcac",
    "_uetvid": "12432c00663311eb878353db6553cd82",
    "_scid": "ae0cc207-0583-43c3-8757-0fdd2c700802",
    "_fbp": "fb.1.1612365510933.1595070444",
    "__insp_wid": "379258038",
    "__insp_slim": "1612365513263",
    "__insp_nv": "true",
    "__insp_targlpu": "aHR0cHM6Ly9xdWlsbGJvdC5jb20v",
    "__insp_targlpt": "UGFyYXBocmFzaW5nIFRvb2wgfCBRdWlsbEJvdCBBSQ%3D%3D",
    "__insp_norec_sess": "true",
    "connect.sid": "s%3AYCThLINLVIRMuu8rYQwfl25hu1I7gH1i.Ug3U8HgvV6rqqlyUQ3C6jasYVi%2BwCD9HLo4zLwncOtE"
}


# def word(msg):
#     _ = requests.get(url)
#     res = requests.get(word_url.format(msg), cookies=cookie)
#     data = res.json()
#     main_data = data['data'][0]
#     fillers = main_data["fillers"]
#     suggestions = main_data['alts']
#     # print("*" * 50)
#     # print(fillers)
#     # print(suggestions)
#     # print("*" * 50)
#     return {
#         "fillers": fillers,
#         "suggestions": suggestions
#     }


def paraphrase(message):
    _ = requests.get(url)
    res = requests.get(para_url.format(message), cookies=cookie)
    data = res.json()
    main_data = data['data'][0]['paras_3']
    suggestions = []
    for i in main_data:
        suggestions.append(i['alt'])
    return {
        "suggestions": suggestions
    }


def summarize(text):
    _ = requests.get(sum_url)
    data = {
        "action": "ajax_summarize",
        "url": "",
        "text": text,
        "threshold": "70",
        "treshold_lines": "",
        "min_sentence_length": "50",
        "min_word_length": "4",
        "first_best": "10"
    }
    res = requests.post(sum_url, data=data)
    summary = res.text.split("<ol><li>")[1].split("</li></ol>")[0]
    return summary


# msg = "hello"
# message = "hello this a bad text no work"
# text = '''An essay is, generally, a piece of writing that gives the author's own argument, but the definition is vague, overlapping with those of a letter, a paper, an article, a pamphlet, and a short story. Essays have traditionally been sub-classified as formal and informal. Formal essays are characterized by "serious purpose, dignity, logical organization, length," whereas the informal essay is characterized by "the personal element (self-revelation, individual tastes and experiences, confidential manner), humor, graceful style, rambling structure, unconventionality or novelty of theme," etc.[1]
# Essays are commonly used as literary criticism, political manifestos, learned arguments, observations of daily life, recollections, and reflections of the author. Almost all modern essays are written in prose, but works in verse have been dubbed essays (e.g., Alexander Pope's An Essay on Criticism and An Essay on Man). While brevity usually defines an essay, voluminous works like John Locke's An Essay Concerning Human Understanding and Thomas Malthus's An Essay on the Principle of Population are counterexamples.
# In some countries (e.g., the United States and Canada), essays have become a major part of formal education. Secondary students are taught structured essay formats to improve their writing skills; admission essays are often used by universities in selecting applicants, and in the humanities and social sciences essays are often used as a way of assessing the performance of students during final exams.
# The concept of an "essay" has been extended to other media beyond writing. A film essay is a movie that often incorporates documentary filmmaking styles and focuses more on the evolution of a theme or idea. A photographic essay covers a topic with a linked series of photographs that may have accompanying text or captions.
# '''

# newText = '''Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.'''

# # # # print(word(msg))

# nstr = paraphrase(newText)

# print(nstr['suggestions'][0])

# #min length of text should be of 50 character
# print(summarize(text))


# USAGE
# from back import word, paraphrase, summarize
# call function
