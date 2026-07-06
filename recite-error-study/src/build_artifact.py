import base64, os
HERE = os.path.dirname(__file__)
FIG = os.path.join(HERE, "..", "figures")
OUT = os.path.join(HERE, "..", "report.html")

def datauri(name):
    with open(os.path.join(FIG, name), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

F = {k: datauri(v) for k, v in {
    "size": "fig1_size_effect.png",
    "common": "fig2_commonness.png",
    "framing": "fig3_framing.png",
    "distance": "fig4_distance.png",
}.items()}

def meter(fid, label):
    pct = int(round(fid * 100))
    return f'''<div class="meter"><div class="meter-label"><span>{label}</span><span class="mono">{fid:.2f}</span></div>
    <div class="meter-track"><div class="meter-fill" style="width:{pct}%"></div></div></div>'''

HTML = f'''<title>Do models copy your errors, or silently correct them?</title>
<style>
:root{{
  --paper:#eef0f0; --card:#f7f8f8; --ink:#15191c; --ink-soft:#4c565b; --line:#d6dbda;
  --copy:#12808f; --copy-soft:#12808f22; --memory:#cc3b2e; --memory-soft:#cc3b2e1a;
  --accent:var(--copy);
}}
@media (prefers-color-scheme:dark){{
  :root{{--paper:#0f1417; --card:#161d21; --ink:#e7ecec; --ink-soft:#93a0a3; --line:#25302f;
    --copy:#3fb6c4; --copy-soft:#3fb6c422; --memory:#f0715f; --memory-soft:#f0715f22;}}
}}
:root[data-theme="light"]{{--paper:#eef0f0; --card:#f7f8f8; --ink:#15191c; --ink-soft:#4c565b; --line:#d6dbda;
  --copy:#12808f; --copy-soft:#12808f22; --memory:#cc3b2e; --memory-soft:#cc3b2e1a;}}
:root[data-theme="dark"]{{--paper:#0f1417; --card:#161d21; --ink:#e7ecec; --ink-soft:#93a0a3; --line:#25302f;
  --copy:#3fb6c4; --copy-soft:#3fb6c422; --memory:#f0715f; --memory-soft:#f0715f22;}}

*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  font-size:17px;line-height:1.65;-webkit-font-smoothing:antialiased;}}
.mono{{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-variant-numeric:tabular-nums;}}
.serif{{font-family:Charter,"Iowan Old Style",Georgia,"Times New Roman",serif;}}
.wrap{{max-width:720px;margin:0 auto;padding:0 24px;}}
h1,h2,h3{{font-family:Charter,"Iowan Old Style",Georgia,serif;line-height:1.15;text-wrap:balance;font-weight:650;}}
h1{{font-size:2.5rem;margin:0 0 .3em;letter-spacing:-.01em;}}
h2{{font-size:1.55rem;margin:0 0 .4em;}}
h3{{font-size:1.12rem;margin:1.6em 0 .3em;}}
p{{margin:0 0 1em;}}
a{{color:var(--copy);}}
.eyebrow{{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-soft);
  font-weight:700;margin-bottom:1.1em;font-family:system-ui,sans-serif;}}

/* hero */
header{{border-bottom:1px solid var(--line);padding:72px 0 44px;
  background:linear-gradient(180deg,var(--copy-soft),transparent);}}
.lede{{font-size:1.28rem;line-height:1.5;color:var(--ink);max-width:40ch;}}
.answer{{margin-top:26px;padding:20px 22px;background:var(--card);border:1px solid var(--line);
  border-left:4px solid var(--memory);border-radius:4px;}}
.answer strong{{color:var(--memory);}}

section{{padding:40px 0;border-bottom:1px solid var(--line);}}
.k{{color:var(--copy);font-weight:650;}} .m{{color:var(--memory);font-weight:650;}}

/* forces table */
.forces{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:22px 0;}}
.force{{border:1px solid var(--line);border-radius:6px;padding:16px 18px;background:var(--card);}}
.force.copy{{border-top:3px solid var(--copy);}} .force.mem{{border-top:3px solid var(--memory);}}
.force h4{{margin:.1em 0 .3em;font-size:1rem;font-family:system-ui,sans-serif;}}
.force.copy h4{{color:var(--copy);}} .force.mem h4{{color:var(--memory);}}
.force p{{margin:0;font-size:.9rem;color:var(--ink-soft);}}

figure{{margin:22px 0 8px;}}
figure img{{width:100%;height:auto;border:1px solid var(--line);border-radius:6px;background:#fff;}}
figcaption{{font-size:.82rem;color:var(--ink-soft);margin-top:8px;font-family:system-ui,sans-serif;}}

table{{width:100%;border-collapse:collapse;font-size:.9rem;margin:16px 0;
  font-variant-numeric:tabular-nums;}}
th,td{{text-align:right;padding:8px 10px;border-bottom:1px solid var(--line);}}
th:first-child,td:first-child{{text-align:left;}}
thead th{{font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-soft);
  font-family:system-ui,sans-serif;font-weight:700;}}
tbody tr:last-child td{{border-bottom:none;}}
td.mono,th.mono{{font-family:ui-monospace,Menlo,monospace;}}
.tablewrap{{overflow-x:auto;}}

/* fidelity meters */
.meters{{display:flex;flex-direction:column;gap:12px;margin:20px 0;}}
.meter-label{{display:flex;justify-content:space-between;font-size:.85rem;margin-bottom:4px;
  font-family:system-ui,sans-serif;}}
.meter-track{{height:9px;border-radius:5px;background:linear-gradient(90deg,var(--memory),var(--copy));
  position:relative;opacity:.28;}}
.meter{{position:relative;}}
.meter-fill{{position:absolute;left:0;top:22px;height:9px;border-radius:5px;
  background:linear-gradient(90deg,var(--memory),var(--copy));}}
.meter .meter-track{{opacity:1;background:var(--line);}}
.meter .meter-fill{{top:0;}}

.swap{{display:inline-block;background:var(--memory-soft);border:1px solid var(--memory);
  border-radius:4px;padding:0 6px;font-family:ui-monospace,monospace;font-size:.85em;}}
.keep{{display:inline-block;background:var(--copy-soft);border:1px solid var(--copy);
  border-radius:4px;padding:0 6px;font-family:ui-monospace,monospace;font-size:.85em;}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:18px;}}
@media (max-width:620px){{.forces,.grid2{{grid-template-columns:1fr;}}}}
footer{{padding:40px 0 80px;color:var(--ink-soft);font-size:.85rem;}}
.tag{{display:inline-block;font-size:.7rem;letter-spacing:.05em;text-transform:uppercase;
  padding:2px 8px;border-radius:20px;border:1px solid var(--line);color:var(--ink-soft);
  font-family:system-ui,sans-serif;font-weight:700;margin-right:6px;}}
</style>

<header><div class="wrap">
  <div class="eyebrow">Empirical note · GPT&#8209;2 family, 82M&#8211;774M · open weights, run locally</div>
  <h1>Will a model copy your&nbsp;<span class="m">deliberate&nbsp;error</span>, or silently&nbsp;<span class="k">correct</span>&nbsp;it?</h1>
  <p class="lede">You hand a model a famous string it has memorized &mdash; digits of &pi;, a
  Shakespeare sonnet, a nursery rhyme &mdash; but you&rsquo;ve quietly changed one token.
  You ask it to copy the text back. Does the error come out?</p>
  <div class="answer"><strong>Yes, models can silently &ldquo;fix&rdquo; your error &mdash; but it isn&rsquo;t a
  fixed trait.</strong> It&rsquo;s a token&#8209;by&#8209;token tug&#8209;of&#8209;war between copying the prompt and
  recalling training data. Correction only wins when the model is <span class="m">big enough</span>
  and that <span class="m">exact token</span> is <span class="m">deeply memorized</span>. On anything the model
  hasn&rsquo;t memorized, the error survives every time.</div>
</div></header>

<section><div class="wrap">
  <h2>The two forces being measured</h2>
  <p>Copying a string that is <em>also</em> memorized pits two transformer mechanisms
  against each other. We read the contest directly off the logits at the error position and
  define <strong>copy fidelity</strong> = P(error) / (P(error)&nbsp;+&nbsp;P(canonical)).</p>
  <div class="forces">
    <div class="force copy"><h4>In&#8209;context copying</h4>
      <p>Induction / copy heads emit the token literally in the prompt &mdash; <strong>your error</strong>.
      Fidelity&nbsp;&rarr;&nbsp;<span class="k">1.0</span>.</p></div>
    <div class="force mem"><h4>Memorized prior</h4>
      <p>Parametric recall emits the token seen in training &mdash; <strong>the canonical version</strong>.
      Fidelity&nbsp;&rarr;&nbsp;<span class="m">0.0</span>.</p></div>
  </div>
  <div class="meters">
    {meter(1.00, "Random ID code (no memorized prior) — copied faithfully")}
    {meter(0.98, "π error at the 40th digit (nobody memorizes it) — copied")}
    {meter(0.62, "sonnet: “compare thee to a <span class=swap>winter&#39;s</span> day” — pulled toward summer")}
    {meter(0.39, "π error at the 6th digit (everyone knows 3.14159…) — corrected")}
    {meter(0.01, "prayer: “hallowed be thy <span class=swap>fame</span>” — snapped back to “name”")}
  </div>
  <p style="font-size:.85rem;color:var(--ink-soft)">All five are gpt2&#8209;large. Same model, same
  &ldquo;copy this&rdquo; request &mdash; the outcome is set by how memorized that one token is.</p>
</div></section>

<section><div class="wrap">
  <h2><span class="tag">Factor 1</span>Model size is the biggest lever</h2>
  <p>Mean fidelity on memorized strings falls monotonically as the model grows, while
  zero&#8209;memorization <span class="k">controls stay pinned near 1.0</span> at every size. Small models
  simply copy your error; correction <em>emerges with scale</em>.</p>
  <div class="tablewrap"><table>
    <thead><tr><th>model</th><th>params</th><th>fidelity · memorized</th><th>fidelity · controls</th><th>corr(mem, correction)</th></tr></thead>
    <tbody>
      <tr><td>distilgpt2</td><td class="mono">82M</td><td class="mono">0.980</td><td class="mono">0.999</td><td class="mono">&minus;0.18</td></tr>
      <tr><td>gpt2</td><td class="mono">124M</td><td class="mono">0.970</td><td class="mono">0.999</td><td class="mono">&minus;0.19</td></tr>
      <tr><td>gpt2&#8209;medium</td><td class="mono">355M</td><td class="mono">0.870</td><td class="mono">0.998</td><td class="mono">+0.35</td></tr>
      <tr><td>gpt2&#8209;large</td><td class="mono">774M</td><td class="mono">0.793</td><td class="mono">0.998</td><td class="mono">+0.45</td></tr>
    </tbody>
  </table></div>
  <p>The coupling between memorization and correction literally <strong>flips sign</strong>:
  absent in small models, strong and positive once the model is large. Modern 7B&ndash;70B
  open&#8209;weight models memorize far more &mdash; expect them to correct <em>more</em> aggressively.</p>
  <figure><img alt="Fidelity vs model size: memorized strings drop with scale, controls stay flat near 1.0" src="{F['size']}">
    <figcaption>Each line is one stimulus across the four sizes. Grey dashed = controls
    (random digits, novel sentences) &mdash; flat at the top regardless of size.</figcaption></figure>
</div></section>

<section><div class="wrap">
  <h2><span class="tag">Factor 2</span>Commonness of the data &mdash; measured, not assumed</h2>
  <p>We didn&rsquo;t guess how common each string is; we <strong>measured</strong> it as the model&rsquo;s
  ability to continue it unaided. Correction rises with memorization &mdash; but only once the
  model is large enough to <em>have</em> a prior. Both conditions are required.</p>
  <figure><img alt="Correction rate vs measured memorization, colored by model" src="{F['common']}">
    <figcaption>The high&#8209;correction corner (top&#8209;right) is entirely <span class="m">orange/red</span>
    &mdash; big models on well&#8209;memorized strings. No memorized prior (left) &rarr; no correction, any size.</figcaption></figure>
</div></section>

<section><div class="wrap">
  <h2><span class="tag">Factor 3</span>Commonness is <em>local</em> &mdash; the key nuance</h2>
  <p>Memorization lives in the <strong>specific token in its context</strong>, not in the
  &ldquo;string.&rdquo; Two demonstrations from the same famous sources:</p>
  <div class="grid2">
    <div class="force copy"><h4>Same sonnet line, two errors</h4>
      <p>Corrupt <span class="swap">winter&#39;s</span> in <span class="serif">&ldquo;compare thee to a ___ day&rdquo;</span>
      (a slot that screams &ldquo;summer&rdquo;) &rarr; pulled toward correction, fidelity <span class="mono">0.62</span>.
      Corrupt <span class="swap">delicate</span> in <span class="serif">&ldquo;more lovely and more ___&rdquo;</span>
      (weakly constrained) &rarr; copied faithfully, fidelity <span class="mono">1.00</span> at every size.</p></div>
    <div class="force mem"><h4>Depth into &pi;</h4>
      <p>Corrupt one digit of &pi; at increasing depth. gpt2&#8209;large <em>corrects</em> the
      <span class="mono">6th</span> digit (everyone&rsquo;s data knows 3.14159&hellip;) but faithfully copies
      errors at depth <span class="mono">&ge;30</span>. The famous <em>prefix</em> is dangerous; the rare
      <em>tail</em> is safe.</p></div>
  </div>
  <figure><img alt="Fidelity vs error depth into pi; early digits corrected, deep digits copied" src="{F['distance']}">
    <figcaption>Deeper into a long recitation, both the copy signal strengthens <em>and</em> the
    tokens are less memorized &mdash; both push the error toward surviving. This also answers the
    <strong>prompt&#8209;size / distance</strong> factor: errors late in a long copy survive.</figcaption></figure>
</div></section>

<section><div class="wrap">
  <h2><span class="tag">Factor 4</span>Insistence on exactness &mdash; a weak lever <em>for base models</em></h2>
  <p>&ldquo;Copy EXACTLY, preserve mistakes&rdquo; vs &ldquo;correct any errors&rdquo; moved fidelity only
  <span class="mono">~0.06</span> on these base LMs, in the right direction. The reason is simple:
  <strong>GPT&#8209;2 isn&rsquo;t instruction&#8209;tuned</strong>, so it barely obeys. This is the factor most likely
  to differ on chat models, where &ldquo;character&#8209;for&#8209;character&rdquo; is followed far more literally &mdash;
  so treat these numbers as a <em>lower bound</em> on the exactness lever.</p>
  <figure><img alt="Prompt framing has only a modest effect on base GPT-2" src="{F['framing']}">
    <figcaption>Clutter (an unrelated distractor paragraph) also barely mattered &mdash; even nudging
    fidelity slightly <em>up</em> by pushing the model into &ldquo;just continue the text&rdquo; copy mode.</figcaption></figure>
</div></section>

<section><div class="wrap">
  <h2>When does <em>your</em> error survive?</h2>
  <div class="grid2">
    <div class="force copy"><h4>Survives (error preserved)</h4>
      <p>&bull; small model<br>&bull; data not really memorized (random IDs, novel text, the rare
      tail of a constant)<br>&bull; explicit &ldquo;copy exactly, keep mistakes&rdquo; (esp. chat models)<br>
      &bull; error deep inside a long verbatim copy</p></div>
    <div class="force mem"><h4>Gets corrected (error vanishes)</h4>
      <p>&bull; large / modern model<br>&bull; the token sits in a high&#8209;frequency, highly&#8209;predictable
      slot of a very famous string<br>&bull; the prompt doesn&rsquo;t insist on verbatim copying<br>
      &bull; e.g. the opening of &pi;, first words of a canonical quote or prayer</p></div>
  </div>
  <p style="margin-top:20px"><strong>The clean invariant:</strong> on strings with no memorized
  prior, fidelity is <span class="k">&asymp;1.0 regardless of size, framing, or clutter</span>. Silent
  correction is a <em>memorization</em> phenomenon &mdash; it can only overwrite what the model already knows.</p>
</div></section>

<footer><div class="wrap">
  <p><strong>Method.</strong> Four real open&#8209;weight models (full&#8209;precision GPT&#8209;2 family) run locally
  on CPU with <span class="mono">transformers</span>. Each stimulus is put in an explicit copy regime
  (<span class="mono">Original: X / Copy: X&hellip;</span>); at the first corrupted token we read
  P(error) vs P(canonical). &ldquo;Commonness&rdquo; is measured as greedy continuation accuracy from a bare
  prefix. 15 stimuli (incl. 3 zero&#8209;memorization controls), 5 prompt framings, a &pi;&#8209;depth sweep,
  and greedy&#8209;generation examples.</p>
  <p><strong>Caveats.</strong> Base LMs, not chat models &mdash; so the exactness&#8209;instruction lever is a
  lower bound and the free&#8209;generation probe is noisy (base GPT&#8209;2 riffs instead of copying), which is
  why the primary result is the logit&#8209;level metric. Single&#8209;token errors, measured at one position.
  Code, CSV results, and figures are in the repository; the harness is model&#8209;agnostic and ready to
  point at Llama&nbsp;/&nbsp;Qwen&nbsp;/&nbsp;Mistral.</p>
</div></footer>
'''

with open(OUT, "w") as f:
    f.write(HTML)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
