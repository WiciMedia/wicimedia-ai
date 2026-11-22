"""Builds the Arabic page from the English one.

Amiri (headlines) places stacked harakat too high, so Amiri strings avoid
damma/fatha and stacked marks; body text in Cairo keeps full diacritics.

The engine supports both directions: with CFG.mirror the whole world is drawn
mirrored (scenes, camera, pans and wipe run right to left) while every string
is counter-flipped so it reads correctly, and Arabic text is never
letter-spaced. This script swaps the config, fonts, strings and the narration
timeline (scene starts, pans, time warps, ducking intervals, subtitles).

Usage: python3 -I make-arabic.py how-glass-is-made.html how-glass-is-made-ar.html
"""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:100])
    s = s.replace(a, b)


def lit(en, ar):
    """Replace a quoted JS string literal everywhere it occurs."""
    global s
    q = "'" + en + "'"
    assert q in s, en
    s = s.replace(q, "'" + ar + "'")


# ---------------- config, fonts ----------------
rep("const CFG={lang:'en',mirror:false}; /*CFG*/", "const CFG={lang:'ar',mirror:true}; /*CFG*/")
rep("const FONT_SAMPLE='Glass 1500 °C SiO₂ ~73%';", "const FONT_SAMPLE='كيف يُصنع الزجاج؟ «الخلطة» Glass 1500 °م SiO₂ ~73%';")
s = re.sub(r"const FONT=\{ serif:.*?\};\n",
           "const FONT={ serif:(w,s)=>`${w>=600?700:400} ${s}px Amiri, Fraunces, Georgia, serif`, sans:(w,s)=>`${w} ${s}px Cairo, Archivo, Arial, sans-serif` };\n",
           s, count=1)
rep("family=Archivo:wght@400;500;600;700;800&family=Fraunces",
    "family=Amiri:wght@400;700&family=Cairo:wght@400;500;600;700;800&family=Archivo:wght@400;500;600;700;800&family=Fraunces")
rep('--f-display:"Fraunces", Georgia,', '--f-display:"Amiri", "Fraunces", Georgia,')
rep('--f-body:"Archivo", "Helvetica Neue",', '--f-body:"Cairo", "Archivo", "Helvetica Neue",')
rep("const faces=['600 90px Fraunces','700 54px Fraunces','500 30px Fraunces','500 36px Fraunces','700 150px Fraunces','400 22px Archivo','500 22px Archivo','600 22px Archivo','600 34px Archivo','700 18px Archivo','800 18px Archivo'];",
    "const faces=['700 90px Amiri','400 30px Amiri','700 54px Amiri','400 36px Amiri','700 150px Amiri','400 22px Cairo','500 22px Cairo','600 22px Cairo','600 34px Cairo','700 18px Cairo','800 18px Cairo','800 14px Cairo'];")

# ---------------- page chrome (HTML) ----------------
rep("<title>How Glass Is Made</title>", "<title>كيف يُصنع الزجاج</title>")
rep('<div class="wrap">', '<div class="wrap" dir="rtl" lang="ar">')
rep('<p class="eyebrow">Paper cut-out explainer · 61 seconds · narrated</p><h1>How Glass Is Made</h1>',
    '<p class="eyebrow">شرح بالورق المقصوص · 62 ثانية · بتعليق عربي</p><h1>كيف يُصنع الزجاج</h1>')
rep('<p class="meta">1920 × 1080 · 30 fps export · voiceover, subtitles and sound effects</p>',
    '<p class="meta">1920 × 1080 · تصدير بـ 30 إطارًا في الثانية · تعليق صوتي وترجمة ومؤثرات</p>')
rep('<div class="veil" id="veil">Cutting paper…</div>', '<div class="veil" id="veil">نقصّ الورق…</div>')
rep('<span id="playLabel">Play</span>', '<span id="playLabel">تشغيل</span>')
rep('</svg>Restart</button>', '</svg>إعادة</button>')
rep('<span class="time" id="time">0:00.0 / 1:01.0</span>', '<span class="time" id="time" dir="ltr">0:00.0 / 1:01.7</span>')
rep('max="61000"', 'max="61700"')
rep('aria-pressed="true">Voiceover: on</button>', 'aria-pressed="true">التعليق الصوتي: مُفعّل</button>')
rep('aria-pressed="true">Sound effects: on</button>', 'aria-pressed="true">المؤثرات: مُفعّلة</button>')
rep('aria-pressed="true">Subtitles: on</button>', 'aria-pressed="true">الترجمة: مُفعّلة</button>')
rep('id="srt" type="button">Download SRT</button>', 'id="srt" type="button">تحميل ملف الترجمة</button>')
rep('id="export" type="button">Export Video</button>', 'id="export" type="button">تصدير الفيديو</button>')
rep('id="cancel" type="button">Cancel</button>', 'id="cancel" type="button">إلغاء</button>')
rep('id="download" type="button">Download Video</button>', 'id="download" type="button">تحميل الفيديو</button>')
rep('for="voFile">Load narration MP3</label>', 'for="voFile">اختيار ملف التعليق MP3</label>')
rep('The narration file could not be loaded here. Pick how-glass-is-made-narration.mp3 to hear it.',
    'تعذّر تحميل ملف التعليق هنا. اختر الملف how-glass-is-made-ar-narration.mp3 لسماعه.')
s = re.sub(r'<p class="note" id="expNote">.*?</p>',
           '<p class="note" id="expNote">يرسم التصدير كل الإطارات بدقة 1920 × 1080 و30 إطارًا في الثانية، ويرمّزها H.264 داخل ملف MP4 في هذا المتصفح، ويمزج التعليق والمؤثرات في مسار صوت واحد. تُطبع الترجمة على الفيديو إن كانت مُفعّلة. يستغرق نحو دقيقتين.</p>',
           s, count=1)

# ---------------- player strings (JS) ----------------
rep("$('playLabel').textContent=P.playing?'Pause':'Play';", "$('playLabel').textContent=P.playing?'إيقاف':'تشغيل';")
rep("$(id).textContent=label+': '+(on?'on':'off');", "$(id).textContent=label+': '+(on?'مُفعّل':'مُطفأ');")
rep("toggle('sfx','Sound effects',SFX_ON)", "toggle('sfx','المؤثرات',SFX_ON)")
rep("toggle('vo','Voiceover',VO_ON)", "toggle('vo','التعليق الصوتي',VO_ON)")
rep("toggle('subs','Subtitles',SUBS_ON)", "toggle('subs','الترجمة',SUBS_ON)")
rep("['Intro','Batch','Melt','Form','Anneal','Recycle']", "['المقدمة','الخلطة','الصهر','التشكيل','التلدين','التدوير']")
rep("b.style.left=(SCN[i].start/DUR*100)+'%';", "b.style.right=(SCN[i].start/DUR*100)+'%';")
for en, ar in [("Loading the MP4 encoder…", "جارٍ تحميل مُرمِّز MP4…"), ("Mixing narration and sound effects…", "جارٍ مزج التعليق والمؤثرات…"),
               ("Rendering frames…", "جارٍ رسم الإطارات…"), ("Finalizing MP4…", "جارٍ إنهاء ملف MP4…"), ("MP4 ready.", "ملف MP4 جاهز."),
               ("Export cancelled.", "أُلغي التصدير."), ("Cancelling…", "جارٍ الإلغاء…"), ("Download declined.", "رُفض التحميل.")]:
    lit(en, ar)
rep("say(`Rendering frame ${i+1} of ${N}…`);", "say(`رسم الإطار ${i+1} من ${N}…`);")
rep("$('download').textContent=`Download Video (${res.label} · ${mb} MB)`;", "$('download').textContent=`تحميل الفيديو (${res.label} · ${mb} MB)`;")
rep("'how-glass-is-made.'+r.ext", "'how-glass-is-made-ar.'+r.ext")
rep("saveFile('how-glass-is-made.srt',SRT,DL?'how-glass-is-made-subtitles.srt.txt':null)",
    "saveFile('how-glass-is-made-ar.srt',SRT,DL?'how-glass-is-made-ar-subtitles.srt.txt':null)")

# ---------------- canvas strings ----------------
rep("const STEPS=['BATCH','MELT','FORM','ANNEAL','RECYCLE'];", "const STEPS=['الخلطة','الصهر','التشكيل','التلدين','التدوير'];")
rep("[['MIX',C.mustard,C.char],['MELT',C.terra,C.card],['SHAPE',C.blue,C.card],['COOL',C.sage,C.card]]",
    "[['خلط',C.mustard,C.char],['صهر',C.terra,C.card],['تشكيل',C.blue,C.card],['تبريد',C.sage,C.card]]")
rep("txt(g,'?',2,48,", "txt(g,'؟',2,48,")
rep("Math.round(Tc).toLocaleString('en-US')+' °C'", "Math.round(Tc)+' °م'")
rep("Math.round(T/10)*10+' °C'", "Math.round(T/10)*10+' °م'")
rep("'~'+Math.round(tT/5)*5+' °C'", "'نحو '+Math.round(tT/5)*5+' °م'")
rep("key:'trk',minW:72", "key:'trk',minW:110")
rep("['Skin cools first,','trapped stress','can crack it later']", "['يبرد السطح أولًا،','فيُحبس إجهاد','قد يشقّه لاحقًا']")
rep("['Stress relaxes while','still hot: strong,','stable glass']", "['يزول الإجهاد وهو','ما زال ساخنًا:','زجاج متين ومستقر']")
for en, ar in [
    ("HOW GLASS IS MADE", "كيف يُصنع الزجاج"), ("INTRO", "المقدمة"),
    ("THE QUESTION", "السؤال"), ("How does sand become glass?", "كيف يصبح الرمل زجاجًا؟"), ("ORDINARY SAND", "رمل عادي"),
    ("tiny grains of quartz:", "حبيبات دقيقة من الكوارتز:"), ("silicon dioxide, SiO_2", "ثاني أكسيد السيليكون SiO₂"),
    ("CRYSTAL-CLEAR GLASS", "زجاج صافٍ كالبلّور"), ("also mostly silica (SiO_2)", "وهو أيضًا من السيليكا في معظمه"), ("HEAT", "حرارة"),
    ("01 · THE BATCH", "01 · الخلطة"), ("Three key ingredients.", "ثلاثة مكوّنات أساسية."),
    ("Limestone", "الحجر الجيري"), ("STABILIZER", "المُثبِّت"), ("keeps glass from dissolving", "يمنع ذوبان الزجاج في الماء"),
    ("Soda ash", "رماد الصودا"), ("FLUX", "مساعد الصهر"), ("lowers the melting point", "يخفض درجة الانصهار"),
    ("Silica sand", "رمل السيليكا"), ("FORMER", "مكوّن الزجاج"), ("builds the glass network", "يبني شبكة الزجاج"),
    ("SAND", "رمل"), ("SODA", "صودا"), ("LIME", "جير"),
    ("INSIDE A TYPICAL BOTTLE", "داخل قارورة عادية"), ("soda-lime glass, share by weight", "زجاج الصودا والجير، النِّسب بالوزن"),
    ("Silica · SiO_2", "سيليكا · SiO₂"), ("Sodium oxide · Na_2O", "أكسيد الصوديوم · Na₂O"), ("Calcium oxide · CaO", "أكسيد الكالسيوم · CaO"),
    ("Other · MgO, Al_2O_3", "أخرى · MgO، Al₂O₃"), ("Stirred together, the mix is called the batch.", "وبعد خلطها معًا يسمّى المزيج «الخلطة»."),
    ("02 · THE MELT", "02 · الصهر"), ("Melted at ~1,500 °C", "ينصهر عند نحو 1500 °م"),
    ("Batch slides in", "تدخل الخلطة"), ("with recycled glass (cullet)", "مع زجاج مُعاد تدويره (الكِسَر)"),
    ("Flames melt it", "يصهرها اللهب"), ("into a thick, glowing liquid", "إلى سائل كثيف متوهّج"),
    ("Bubbles rise out", "تصعد الفقاعات"), ('this cleaning step is "fining"', "تُسمّى هذه المرحلة «التنقية»"),
    ("Cullet melts more easily:", "الكِسَر تنصهر بسهولة أكبر:"), ("every 10% used saves", "كل 10% منها توفّر"), ("about 2–3% of the energy", "نحو 2–3% من الطاقة"),
    ("THE FLUX EFFECT", "أثر مساعد الصهر"), ("soda ash lets the furnace run cooler", "رماد الصودا يُخفّض حرارة الفرن اللازمة"),
    ("1,000 °C", "1000 °م"), ("1,800", "1800"), ("furnace ~1,500 °C", "الفرن نحو 1500 °م"), ("pure silica needs ~1,700 °C", "السيليكا النقية تحتاج نحو 1700 °م"),
    ("WHY IT’S GLASS, NOT CRYSTAL", "لماذا هو زجاج لا بلّورة؟"), ("CRYSTAL · ORDERED", "بلّورة · ذرّات منتظمة"), ("GLASS · FROZEN JUMBLE", "زجاج · فوضى متجمّدة"),
    ("melt +", "صهر +"), ("cool", "تبريد"),
    ("03 · FORMING", "03 · التشكيل"), ("Floated flat, or blown hollow.", "مسطّح بالتعويم، أو مجوّف بالنفخ."),
    ("A · FLOAT GLASS", "أ · الزجاج المُعوَّم"), ("→ flat sheets", "← ألواح مسطّحة"), ("B · CONTAINER GLASS", "ب · زجاج العبوات"), ("→ bottles & jars", "← قوارير وبرطمانات"),
    ("MOLTEN TIN", "قصدير منصهر"), ("~1,100 °C", "نحو 1100 °م"), ("~600 °C", "نحو 600 °م"), ("cools as it flows", "يبرد وهو يتدفّق"),
    ("Glass floats on molten tin, so it spreads perfectly flat.", "يطفو الزجاج على القصدير المنصهر، فينبسط مستويًا تمامًا."),
    ("WINDOWS · MIRRORS · SCREENS", "نوافذ · مرايا · شاشات"), ("AIR", "هواء"), ("Compressed air", "هواء مضغوط"),
    ("inflates it to the", "ينفخه ليأخذ"), ("mold’s shape", "شكل القالب"),
    ("1 · CUT A GOB", "1 · قطع كتلة"), ("2 · PARISON", "2 · الشكل الأوّلي"), ("3 · BLOW", "3 · النفخ"), ("BOTTLES · JARS", "قوارير · برطمانات"),
    ("04 · ANNEALING", "04 · التلدين"), ("Cooled slowly, so it won’t crack.", "تبريد بطيء كي لا يتشقّق."),
    ("TEMPERATURE THROUGH THE LEHR", "الحرارة داخل فرن التلدين"), ("ENTRY → EXIT", "الدخول ← الخروج"),
    ("TOO FAST", "سريع جدًا"), ("HOLD ~550 °C · STRESS RELAXES", "تثبيت عند 550 °م · يزول الإجهاد"), ("SLOW COOL", "تبريد بطيء"), ("THEN FASTER", "ثم أسرع"),
    ("WHY COOL SLOWLY?", "لماذا التبريد البطيء؟"), ("COOLED TOO FAST", "بُرِّد بسرعة"), ("ANNEALED", "مُلدَّن"),
    ("05 · RECYCLING", "05 · إعادة التدوير"), ("Old glass, new life.", "زجاج قديم، حياة جديدة."),
    ("USE", "الاستخدام"), ("windows, bottles, jars", "نوافذ وقوارير وبرطمانات"), ("COLLECT & SORT", "الجمع والفرز"), ("sorted by color", "حسب اللون"),
    ("CRUSH", "التكسير"), ("into cullet", "إلى كِسَر"), ("REMELT", "إعادة الصهر"), ("less energy, less sand", "طاقة أقل، ورمل أقل"),
    ("Recyclable", "قابل للتدوير"), ("again and again", "مرّة بعد مرّة"), ("with no loss in quality", "دون أن تقلّ جودته"),
    ("FROM SAND TO BOTTLE", "من الرمل إلى القارورة"), ("Mix sand, soda ash & limestone", "خلط الرمل ورماد الصودا والجير"),
    ("Melt at ~1,500 °C", "الصهر عند نحو 1500 °م"), ("Float flat or blow into shape", "التعويم أو النفخ في قالب"),
    ("Anneal: cool it slowly", "التلدين: تبريد بطيء"), ("Recycle, and repeat", "إعادة التدوير، والتكرار"),
]:
    lit(en, ar)

# ---------------- Arabic narration timeline ----------------
def line(prefix, new):
    global s
    m = re.search(r"^" + re.escape(prefix) + r".*$", s, flags=re.M)
    assert m, prefix
    s = s[:m.start()] + new + s[m.end():]

line("const DUR=", "const DUR=61.7, FPS=30;")
line("const SCN=[", "const SCN=[{start:0,dur:11.5,draw:sceneH,wx:-1920,wy:0},{start:11.05,dur:13.45,draw:scene1,wx:0,wy:0},{start:24.05,dur:11.45,draw:scene2,wx:1920,wy:0},{start:35.05,dur:7.45,draw:scene3,wx:3840,wy:240},{start:42.05,dur:7.65,draw:scene4,wx:5760,wy:309},{start:49.2,dur:12.5,draw:scene5}];")
line("const PANS=[", "const PANS=[[10.4,11.5,0,1],[23.4,24.5,1,2],[34.4,35.5,2,3],[41.4,42.5,3,4]];")
line("const WIPE=[", "const WIPE=[48.75,49.7];")
line("const WARPS=", "const WARPS=[[[0,0],[1.85,2.19],[3.39,3.27],[6.31,5.69],[7.99,7.75],[10.4,11.45]],"
     "[[0,0],[1.36,1.4],[3.7,3.28],[5.0,4.7],[6.32,6.02],[7.78,6.92],[8.94,8.54],[10.12,9.24],[11.34,10.46],[12.35,11.95]],"
     "[[0,0],[.55,.55],[.95,1.91],[3.09,3.29],[4.13,4.49],[6.03,6.07],[6.83,7.15],[8.97,9.03],[10.35,10.05]],"
     "[[0,0],[.5,.5],[3.06,2.96],[6.35,6.35]],"
     "[[0,0],[1.11,1.11],[2.95,2.79],[3.61,3.69],[4.97,4.75],[6.7,6.55]],"
     "[[0,0],[.55,.55],[2.25,2.13],[3.47,3.09],[4.11,4.01],[5.11,4.99],[6.45,6.13],[7.17,6.69],[7.79,7.29],[8.43,8.43],[9.57,9.13],[12.5,11.6]]];")
line("const VO_PLACE=", "const VO_PLACE=[[1,0,8.83,.45],[2,0,12.04,11.55],[3,0,9.64,24.6],[4,0,4.0,35.55],[4,4.0,9.87,42.0],[5,0,11.08,49.75]];")
line("const SPEECH=", "const SPEECH=[[.45,9.25],[11.55,23.15],[24.6,34.0],[35.55,38.85],[42.9,47.85],[49.75,60.25]];")
caps_start = s.index("const CAPS=[")
caps_end = s.index("]];", caps_start) + 3
s = s[:caps_start] + """const CAPS=[[.45,2.7,'كيف تتحوّل حبّات الرمل العاديّة'],[2.73,5.75,'إلى قارورة زجاجٍ صافيةٍ كالبلّور؟'],[6.31,9.3,'الجواب يكمن في تحوّلٍ مذهل.'],
 [11.55,14.7,'تبدأ الحكاية بثلاثة مكوّناتٍ أساسيّة:'],[14.75,18.75,'رمل السيليكا، ورماد الصودا، والحجر الجيريّ.'],[18.83,20.8,'ولكلٍّ منها دورٌ جوهريّ'],[20.85,23.3,'في صنع زجاجٍ متينٍ وشفّاف.'],
 [24.6,25.98,'داخل فرنٍ هائل،'],[26.02,30.75,'تبلغ حرارة الخليط نحو 1500 درجة مئويّة،'],[30.88,34.1,'فينصهر ويصير سائلًا متوهّجًا.'],
 [35.55,38.95,'تُشكّل الآلات الزجاجَ المنصهر على هيئة قوارير،'],[42.91,44.55,'ثمّ تُبرَّد تدريجيًّا'],[44.6,47.95,'لمنع التشقّق، وتقوية المنتَج النهائيّ.'],
 [49.75,52.0,'والمدهش أنّ الزجاج القديم'],[52.03,55.6,'يمكن تدويره وتحويله إلى منتجاتٍ جديدة.'],[55.65,57.58,'من الرمل إلى القارورة،'],[57.63,60.3,'يبدأ الزجاج حياةً جديدة.']];""" + s[caps_end:]

leftover = [m for m in re.findall(r"txt\((?:ctx|g),'([^']*[A-Za-z]{3,}[^']*)'", s) if not re.search(r"[؀-ۿ]", m)]
if leftover:
    print("note: Latin strings left as-is:", leftover)
open(dst, "w", encoding="utf-8").write(s)
print("wrote", dst, len(s))
