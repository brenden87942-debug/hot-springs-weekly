#!/usr/bin/env python3
"""Post-process for HSW standalone page: swap beehiiv poll/guess for on-page Google Form widgets.
Run after any rebuild: python3 /workspace/hsw-site/tools/add_forms.py [path/to/index.html]
Idempotent."""
import re, sys
p = sys.argv[1] if len(sys.argv) > 1 else "/workspace/hsw-site/issue-1/index.html"
h = open(p).read()
if 'id="hsw-poll"' in h:
    print("already applied"); sys.exit()
FORM = "https://docs.google.com/forms/d/e/1FAIpQLSeyAcVwimqJYlOQdtGwAXoif7ejURrci2Myn9V6CK9otAqmEg"
opts = ["A place to eat or hang out late at night",
        "More shopping, like clothes, hardware or electronics",
        "Things for kids and teens to do", "Something else"]
inp = 'width:100%;box-sizing:border-box;padding:12px;font-size:16px;border:2px solid #F2C48D;border-radius:10px;background:#fff;margin:0 0 10px;font-family:inherit'
btn = 'display:block;width:100%;background:#C8572B;color:#fff;border:0;font-weight:bold;font-size:17px;padding:14px;border-radius:24px;cursor:pointer;font-family:inherit'
ob = ''.join(f'<button type="button" class="hsw-opt" data-v="{o}" style="display:block;width:100%;text-align:left;background:#fff;color:#5A2E1A;border:2px solid #2E8B8B;border-radius:12px;padding:14px 16px;margin:0 0 10px;font-size:16px;cursor:pointer;font-family:inherit"><strong>{"ABCD"[i]}.</strong> {o}</button>' for i,o in enumerate(opts))
poll = f'''<div id="hsw-poll" style="margin:0 0 18px">{ob}
<input id="hsw-other" type="text" placeholder="What would you like to see?" style="{inp};display:none">
<input id="hsw-pname" type="text" placeholder="Your first name (optional)" style="{inp}">
<button type="button" id="hsw-vote" style="{btn}">Submit vote</button>
<p id="hsw-pmsg" style="margin:10px 0 0;color:#C8572B;font-weight:bold;text-align:center"></p></div>
<noscript><p style="margin:0 0 18px;text-align:center"><a style="color:#2E8B8B" href="{FORM}/viewform">Vote here</a></p></noscript>
<p style="margin:0 0 18px">Tap your answer above, then hit Submit vote. No sign-up needed. We'll share the results next week. If you add your name, you agree we can print it with the results.</p>
'''
h, n = re.subn(r'<ul style="padding-left:20px;margin:0 0 18px">\s*<li[^\n]*<strong>A\.</strong> A place to eat.*?</ul>\s*<p style="margin:0 0 18px;text-align:center"><a href="https://hotspringsweekly\.beehiiv\.com/p/[^"]*"[^>]*>Tap here to vote</a></p><p[^>]*>.*?</p>\n?', poll, h, flags=re.S)
assert n == 1, "poll block not found"
guess = f'''<div id="hsw-guess" style="margin:0 0 18px">
<input id="hsw-gtext" type="text" placeholder="Your guess" style="{inp}">
<input id="hsw-gname" type="text" placeholder="Your first name (optional)" style="{inp}">
<button type="button" id="hsw-gsend" style="{btn}">Send my guess</button>
<p id="hsw-gmsg" style="margin:10px 0 0;color:#C8572B;font-weight:bold;text-align:center"></p></div>
<noscript><p style="margin:0 0 18px;text-align:center"><a style="color:#2E8B8B" href="{FORM}/viewform">Send your guess here</a></p></noscript>
<p style="margin:0 0 18px">Type your guess above and send it, no sign-up needed. We'll reveal the answer next week and print the names of everyone who got it right.'''
h, n = re.subn(r'<p style="margin:0 0 18px">Subscribe free, then reply to any issue with your guess\. We\'ll reveal the answer next week and print the names of everyone who got it right\.', guess, h)
assert n == 1, "guess text not found"
js = f'''<script>(function(){{var E="{FORM}/formResponse",sel="";
function send(d,m,t){{fetch(E,{{method:"POST",mode:"no-cors",body:new URLSearchParams(d)}}).then(function(){{m.textContent=t}}).catch(function(){{m.textContent="Hmm, that didn't go through. Try again in a minute."}})}}
var ob=document.querySelectorAll(".hsw-opt"),oth=document.getElementById("hsw-other");
ob.forEach(function(b){{b.addEventListener("click",function(){{sel=b.getAttribute("data-v");ob.forEach(function(x){{x.style.background="#fff";x.style.color="#5A2E1A"}});b.style.background="#2E8B8B";b.style.color="#fff";oth.style.display=sel=="Something else"?"block":"none"}})}});
document.getElementById("hsw-vote").addEventListener("click",function(){{var m=document.getElementById("hsw-pmsg");if(!sel){{m.textContent="Tap an answer first.";return}}
var d={{"entry.1305367044":sel}};if(sel=="Something else"&&oth.value.trim())d["entry.515436282"]=oth.value.trim();var n=document.getElementById("hsw-pname").value.trim();if(n)d["entry.1740411383"]=n;
this.disabled=true;send(d,m,"Thanks, your vote is in. Results in next week's issue.")}});
document.getElementById("hsw-gsend").addEventListener("click",function(){{var m=document.getElementById("hsw-gmsg"),g=document.getElementById("hsw-gtext").value.trim();if(!g){{m.textContent="Type a guess first.";return}}
var d={{"entry.1616857246":g}};var n=document.getElementById("hsw-gname").value.trim();if(n)d["entry.1740411383"]=n;this.disabled=true;send(d,m,"Got it. The answer is in next week's issue.")}});
}})();</script>
'''
h = h.replace("</body>", js + "</body>", 1) if "</body>" in h else h + js
open(p, "w").write(h); print("applied")
