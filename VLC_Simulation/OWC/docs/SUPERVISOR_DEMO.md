# Five-minute supervisor demonstration

Start `python run.py --gui` from the project root. Use the URL printed by the NEW server; append `/demo`. An already running server must be restarted to recognize this new route. The previous port is not guaranteed to remain the same.

1. Minute 1: Explain the 2024 baseline and the added six-mirror optical RIS. The diagram is conceptual, not a scaled ray trace. The original paper curves are not numerically reproduced.
2. Minute 2: Press RIS off, then Aim Alice → Bob. Keep all other settings fixed. Show the reflected gain becoming nonzero and the total gain equaling direct plus reflected. Explain that manual metrics are not DRL evaluation.
3. Minute 3: Show the saved 10-seed frozen evaluation table. Explain the 2,000-slot training/1,000-slot evaluation split and static single-action operating points. Fixed RIS has positive paired improvement; joint superiority is not established.
4. Minute 4: Open `/ris` for the full controls. If needed run only a 24-slot smoke demonstration, explicitly saying this is not scientific evidence. Do not launch lengthy training during the presentation.
5. Minute 5: Explain near-Bob failure, oracle position knowledge and omitted switching energy. Ask which specific contribution and additional validation the supervisor recommends. Show `manuscript/draft.md` and `antigravity_report/AUTHORITATIVE_TABLES.md` if asked.

Bangla script: “আমরা ২০২৪ সালের system model-এর সঙ্গে optical RIS যোগ করেছি। এখানে একই jammer weights রেখে reflection-এর actual contribution দেখাচ্ছি। এরপর matched trained-policy comparison দেখাচ্ছি। Fixed RIS-এর লাভের evidence আছে; joint DRL সবচেয়ে ভালো—এমন দাবি করছি না।”

Use Print / save PDF on `/demo` for a handout after loading the live channel and saved study results. This is a simulation demonstration, not hardware proof. Saved numbers come from `supervisor_results.json`, derived from the existing complete study export; they are not a new experiment.
