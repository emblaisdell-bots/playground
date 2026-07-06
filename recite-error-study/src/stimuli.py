"""
Stimuli for the copy-with-errors study.

Each stimulus is a famous/plentiful string (or a control with little/no training
presence). A corruption is one small edit: corrupted = canonical.replace(find,
replace, 1). We inject a single, recognizable deviation from the canonical form.

`prior` is a rough a-priori guess at how common the string is in web-scale
training data; the experiment MEASURES memorization directly, so `prior` is only
for labelling/sanity.
"""

STIMULI = [
    # ---------- very common: constants ----------
    dict(id="pi",        cat="digits", prior="very_high",
         canonical="Pi to twenty digits is 3.14159265358979323846.",
         find="8979", replace="8929",
         note="one digit 7->2 mid-pi"),
    dict(id="e",         cat="digits", prior="high",
         canonical="Euler's number e is 2.718281828459045.",
         find="281828", replace="281928",
         note="one digit in e"),
    dict(id="fib",       cat="sequence", prior="high",
         canonical="The Fibonacci sequence: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55.",
         find="13, 21", replace="13, 22",
         note="21->22"),

    # ---------- very common: canon text ----------
    dict(id="sonnet18",  cat="poetry", prior="very_high",
         canonical="Shall I compare thee to a summer's day? Thou art more lovely and more temperate.",
         find="summer's", replace="winter's",
         note="summer's->winter's"),
    dict(id="sonnet18b", cat="poetry", prior="very_high",
         canonical="Shall I compare thee to a summer's day? Thou art more lovely and more temperate.",
         find="temperate", replace="delicate",
         note="temperate->delicate (later in line)"),
    dict(id="hamlet",    cat="drama", prior="very_high",
         canonical="To be, or not to be, that is the question.",
         find="the question", replace="the answer",
         note="question->answer"),
    dict(id="genesis",   cat="scripture", prior="very_high",
         canonical="In the beginning God created the heaven and the earth.",
         find="the heaven", replace="the heavens",
         note="heaven->heavens"),
    dict(id="twinkle",   cat="rhyme", prior="very_high",
         canonical="Twinkle, twinkle, little star, how I wonder what you are.",
         find="little star", replace="little moon",
         note="star->moon"),
    dict(id="lords",     cat="prayer", prior="high",
         canonical="Our Father which art in heaven, hallowed be thy name.",
         find="thy name", replace="thy fame",
         note="name->fame"),
    dict(id="alphabet",  cat="sequence", prior="very_high",
         canonical="The alphabet: a b c d e f g h i j k l m n o p q r s t.",
         find=" g h", replace=" z h",
         note="g->z"),
    dict(id="gettysburg",cat="speech", prior="high",
         canonical="Four score and seven years ago our fathers brought forth on this continent a new nation.",
         find="seven years", replace="eight years",
         note="seven->eight"),
    dict(id="firstlines",cat="prose", prior="medium",
         canonical="It was the best of times, it was the worst of times.",
         find="the worst", replace="the strangest",
         note="worst->strangest"),

    # ---------- controls: low / zero memorization ----------
    dict(id="rand_digits", cat="control_digits", prior="none",
         canonical="My reference code is 4820573916402 for the order.",
         find="573", replace="593",
         note="random digits, no memorized prior (pure-copy baseline)"),
    dict(id="nonsense",    cat="control_prose", prior="none",
         canonical="The quiet auburn ferret balanced the brass teaspoon.",
         find="brass", replace="glass",
         note="novel sentence, no memorized prior"),
    dict(id="nonsense2",   cat="control_prose", prior="none",
         canonical="A violet abacus hummed beside the tin marigold.",
         find="tin", replace="oak",
         note="novel sentence 2"),
]


def corrupted_of(stim):
    c = stim["canonical"]
    assert stim["find"] in c, f"{stim['id']}: find not present"
    return c.replace(stim["find"], stim["replace"], 1)
