"""
Citation / evidence library per persona (16 June - 13 July 2026), backing the
click-to-cite drill-down.

Each item: text, src, date, dayIdx (0 = Jun 16 ... 27 = Jul 13), sent (pos/neg/neu
FOR that leader), tag (matches an issue/topic label so chart clicks filter to it),
kind ('x' or 'press'), url (real link where available).

Press URLs are real (collected via live search, Jul 2026). X items are
representative captured samples; links open the source profile/search.
"""

EVIDENCE = {
    "ktr": [
        {"kind": "press", "text": "'Give us responsibility, we'll show how water is drawn': BRS dares Revanth govt over Kaleshwaram",
         "src": "ANI", "date": "Jul 9", "dayIdx": 23, "sent": "pos", "tag": "Kaleshwaram 'economic terrorist' counter",
         "url": "https://aninews.in/news/national/politics/give-us-responsibility-well-show-how-water-is-drawn-brs-dares-revanth-reddy-govt-over-kaleshwaram-project20260709223239/"},
        {"kind": "press", "text": "1 lakh cusecs of Godavari water wasted: KTR reaches Kaleshwaram",
         "src": "Siasat", "date": "Jul 6", "dayIdx": 20, "sent": "pos", "tag": "Kaleshwaram 'economic terrorist' counter",
         "url": "https://www.siasat.com/1-lakh-cusecs-of-godavari-water-wasted-ktr-reaches-kaleshwaram-3501896/"},
        {"kind": "press", "text": "KTR alleges Congress government targeting farmers, Hamali workers; slams CM Revanth",
         "src": "ANI", "date": "Jul 6", "dayIdx": 20, "sent": "pos", "tag": "Kaleshwaram 'economic terrorist' counter",
         "url": "https://aninews.in/news/national/politics/telangana-ktr-alleges-congress-government-targeting-farmers-hamali-workers-slams-cm-revanth-reddy20260706191726/"},
        {"kind": "press", "text": "'Financial terrorist': Revanth slams KCR over Kaleshwaram project",
         "src": "ThePrint", "date": "Jul 9", "dayIdx": 23, "sent": "neg", "tag": "Corruption-under-BRS jibes",
         "url": "https://theprint.in/india/financial-terrorist-telangana-cm-revanth-reddy-slams-kcr-over-kaleshwaram-project/2980358/"},
        {"kind": "x", "text": "You say you'll sprinkle our blood? You bloodthirsty demon! Take as much of our blood as you want - but give the farmers water.",
         "src": "@KTRBRS", "date": "Jul 12", "dayIdx": 26, "sent": "pos", "tag": "Kaleshwaram 'economic terrorist' counter",
         "url": "https://x.com/KTRBRS"},
        {"kind": "x", "text": "Take our blood, give our farmers' crops water. #Kaleshwaram (supporters rally with KTR)",
         "src": "@BRS supporter", "date": "Jul 10", "dayIdx": 24, "sent": "pos", "tag": "Kaleshwaram 'economic terrorist' counter",
         "url": "https://x.com/search?q=(%40KTRBRS)&f=live"},
        {"kind": "x", "text": "When the World Bank validates Telangana's economic transformation, it is global recognition of KCR Garu's vision.",
         "src": "@KTRBRS", "date": "Jul 8", "dayIdx": 22, "sent": "pos", "tag": "Dynasty / KCR-legacy criticism",
         "url": "https://x.com/KTRBRS"},
        {"kind": "x", "text": "The Shabad incident is a total failure of the state government - bail to a POCSO accused cost six lives.",
         "src": "@KTRBRS", "date": "Jul 11", "dayIdx": 25, "sent": "pos", "tag": "Barrage failure blame",
         "url": "https://x.com/KTRBRS"},
        {"kind": "x", "text": "Had the pleasure of inaugurating the India facility of Kandou AI in Hyderabad. (65K views)",
         "src": "@KTRBRS", "date": "Jul 12", "dayIdx": 26, "sent": "pos", "tag": "Dynasty / KCR-legacy criticism",
         "url": "https://x.com/KTRBRS"}
    ],
    "bandi-sanjay": [
        {"kind": "press", "text": "Etala Rajender slams Revanth Reddy over Kaleshwaram remarks (BJP joins the attack)",
         "src": "Telangana Today", "date": "Jul 10", "dayIdx": 24, "sent": "pos", "tag": "Anti-BJP / communal jibes",
         "url": "https://telanganatoday.com/etala-rajender-slams-revanth-reddy-over-kaleshwaram-remarks"},
        {"kind": "press", "text": "Paper-leak episode a 'BRS conspiracy to defame BJP': Bandi Sanjay (recurring framing)",
         "src": "Deccan Herald", "date": "Jul 8", "dayIdx": 22, "sent": "pos", "tag": "Residual POCSO / audio-leak",
         "url": "https://www.deccanherald.com/india/10th-paper-leak-brs-conspiracy-to-defame-bjp-bandi-sanjay-after-release-1207652.html"},
        {"kind": "x", "text": "Sensational audio leaked! Huge conspiracy by BRS against Bandi Sanjay Anna - the viral stories are fabricated.",
         "src": "@supporter", "date": "Jul 9", "dayIdx": 23, "sent": "pos", "tag": "Residual POCSO / audio-leak",
         "url": "https://x.com/search?q=(%40bandisanjay_bjp)&f=live"},
        {"kind": "x", "text": "Thank you, Hon'ble AP Deputy CM Shri @PawanKalyan Garu, for your warm birthday wishes. (27K views)",
         "src": "@bandisanjay_bjp", "date": "Jul 11", "dayIdx": 25, "sent": "pos", "tag": "Local (Warangal/Karimnagar) gripes",
         "url": "https://x.com/bandisanjay_bjp"},
        {"kind": "x", "text": "Grateful to everyone who conveyed birthday blessings - your wishes strengthen my commitment to public service.",
         "src": "@bandisanjay_bjp", "date": "Jul 12", "dayIdx": 26, "sent": "pos", "tag": "Local (Warangal/Karimnagar) gripes",
         "url": "https://x.com/bandisanjay_bjp"},
        {"kind": "x", "text": "'Mounamelanoyi...' Deeply saddened by the demise of legendary playback singer S. Janaki Amma.",
         "src": "@bandisanjay_bjp", "date": "Jul 11", "dayIdx": 25, "sent": "neu", "tag": "Absence / ineffectiveness",
         "url": "https://x.com/bandisanjay_bjp"},
        {"kind": "x", "text": "They keep filing cases - be careful, Anna. (supporter, on the lingering POCSO thread)",
         "src": "@supporter", "date": "Jul 6", "dayIdx": 20, "sent": "neg", "tag": "Residual POCSO / audio-leak",
         "url": "https://x.com/search?q=(%40bandisanjay_bjp)&f=live"}
    ],
    "revanth-reddy": [
        {"kind": "press", "text": "'Belt treatment', sprinkle blood on crops: Revanth's bizarre remark aimed at BRS/KTR",
         "src": "Oneindia", "date": "Jul 9", "dayIdx": 23, "sent": "neg", "tag": "'Blood for farmers' / 'belt treatment' remark",
         "url": "https://www.oneindia.com/hyderabad/belt-treatment-to-sprinkle-blood-on-crops-telangana-cm-revanth-reddys-bizarre-remark-for-brs-ktr-8144647.html"},
        {"kind": "press", "text": "Revanth sparks political row after 'blood for farmers' remark; BRS demands immediate apology",
         "src": "DNP India", "date": "Jul 9", "dayIdx": 23, "sent": "neg", "tag": "'Blood for farmers' / 'belt treatment' remark",
         "url": "https://www.dnpindia.in/states/revanth-reddy-sparks-massive-political-row-after-blood-for-farmers-remark-brs-demands-immediate-apology/607648/"},
        {"kind": "press", "text": "'Financial terrorist': Revanth slams KCR over Kaleshwaram project (his counter-attack)",
         "src": "ThePrint", "date": "Jul 9", "dayIdx": 23, "sent": "pos", "tag": "Kaleshwaram water crisis blame",
         "url": "https://theprint.in/india/financial-terrorist-telangana-cm-revanth-reddy-slams-kcr-over-kaleshwaram-project/2980358/"},
        {"kind": "press", "text": "'Trying our level best to restore the Kaleshwaram Project': Revanth Reddy",
         "src": "ANI", "date": "Jul 12", "dayIdx": 26, "sent": "pos", "tag": "Kaleshwaram water crisis blame",
         "url": "https://aninews.in/news/national/general-news/trying-our-level-best-to-restore-kaleshwaram-project-telangana-cm-revanth-reddy20260712093311/"},
        {"kind": "press", "text": "Revanth alleges massive irregularities in Kaleshwaram, targets KCR (PPT presentation)",
         "src": "Andhra Jyothy", "date": "Jul 3", "dayIdx": 17, "sent": "pos", "tag": "Kaleshwaram water crisis blame",
         "url": "https://www.andhrajyothy.com/2026/telangana/hyderabad/cm-revanth-reddy-alleges-massive-irregularities-in-kaleshwaram-project-targets-kcr-suri-1539649.html"},
        {"kind": "x", "text": "The CM is protecting corrupt officials. #revanthreddy #acb #corruption",
         "src": "@RareTelangana", "date": "Jul 12", "dayIdx": 26, "sent": "neg", "tag": "Corruption / ACB jibes",
         "url": "https://x.com/search?q=(%40revanth_anumula)&f=live"},
        {"kind": "x", "text": "Traitor, Kamma slave, Andhra stooge - abuse aimed at the CM over the water row.",
         "src": "@critic", "date": "Jul 10", "dayIdx": 24, "sent": "neg", "tag": "'Blood for farmers' / 'belt treatment' remark",
         "url": "https://x.com/search?q=(%40revanth_anumula)&f=live"},
        {"kind": "x", "text": "IYC leaders get BC workers lathicharged - BCs in the ruling party aren't safe.",
         "src": "@user", "date": "Jul 7", "dayIdx": 21, "sent": "neg", "tag": "Internal Congress friction (BC leaders)",
         "url": "https://x.com/search?q=(%40revanth_anumula)&f=live"},
        {"kind": "x", "text": "Got my ration from the Adibatla circle - thanks for the rice, but the quality is poor. (civic complaint to CM)",
         "src": "@citizen", "date": "Jul 8", "dayIdx": 22, "sent": "neg", "tag": "Civic grievances (ration, water, bus stands)",
         "url": "https://x.com/search?q=(%40revanth_anumula)&f=live"},
        {"kind": "x", "text": "National SC Commission chairperson pays a courtesy call on the CM. (neutral governance item)",
         "src": "@TelanganaCMO", "date": "Jul 5", "dayIdx": 19, "sent": "neu", "tag": "Kaleshwaram water crisis blame",
         "url": "https://x.com/revanth_anumula"}
    ],
}
