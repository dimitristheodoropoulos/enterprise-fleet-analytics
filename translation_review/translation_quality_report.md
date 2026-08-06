# Machine Translation Quality Review (EN → EL)

**Total samples reviewed:** 20 / 20

## 📊 Overall Verdict Breakdown
- **Pass:** 12 (60%)
- **Pass with note:** 8 (40%)

## ✅ Meaning Correctness Breakdown
- **Correct:** 20 (100%)

## ✅ No critical errors (0 flagged sentences).

## 📝 Detailed Insights from 'Pass with note'

*The 8 cases below are fully accurate in meaning, but contain subtle nuances in formality, tense, or capitalization that are worth documenting for evaluation purposes.*

**ID #5:** `I do not understand.`
- **Human Ref:** `Δεν καταλαβαίνω.`
- **MT:** `δεν καταλαβαίνω.`
- **Tone/Formality Note:** Informal
- **Grammar/Pronoun Note:** Minor capitalization error
- **Your Comment:** MT missing capital "Δ" in "Δεν". Minor mechanical issue

**ID #7:** `I'm back! Oh? Have we got a guest?`
- **Human Ref:** `Ήρθα! Ο; Έχουμε καλεσμένο;`
- **MT:** `γύρισα! Ω; Έχουμε καλεσμένο;`
- **Tone/Formality Note:** Informal
- **Grammar/Pronoun Note:** Minor issues (typo & capitalization)
- **Your Comment:** Reference has a typo "Ο;" (should be "Ω;" or "Α;"). MT corrects the tone but starts with lowercase "γύρισα". Content is fine.

**ID #8:** `I'll show you around the city.`
- **Human Ref:** `Θα σου δείξω την πόλη.`
- **MT:** `Θα σας ξεναγήσω στην πόλη.`
- **Tone/Formality Note:** Formality mismatch (Formal vs Informal)
- **Grammar/Pronoun Note:** Correct
- **Your Comment:** Key find! Reference uses informal "σου" + simple verb. MT uses formal "σας" + more elaborate verb "ξεναγήσω". Formality mismatch without context.

**ID #9:** `I will show you around the city.`
- **Human Ref:** `Θα σου δείξω την πόλη.`
- **MT:** `Θα σας ξεναγήσω στην πόλη.`
- **Tone/Formality Note:** Formality mismatch (Formal vs Informal)
- **Grammar/Pronoun Note:** Correct
- **Your Comment:** Same as #8. MT defaults to formal tone.

**ID #11:** `Excuse me, I'm lost.`
- **Human Ref:** `Συγνώμη, έχω χαθεί.`
- **MT:** `Με συγχωρείτε, χάθηκα.`
- **Tone/Formality Note:** Formality mismatch (Formal vs Informal)
- **Grammar/Pronoun Note:** Correct
- **Your Comment:** Reference uses informal/colloquial "Συγνώμη". MT uses formal polite "Με συγχωρείτε". Good catch on formality layers.

**ID #12:** `You have been missing all these years.`
- **Human Ref:** `Έχεις λείψει τόσα χρόνια.`
- **MT:** `Έλειπες όλα αυτά τα χρόνια.`
- **Tone/Formality Note:** Tense mismatch (Present Perfect vs Simple Past)
- **Grammar/Pronoun Note:** Correct
- **Your Comment:** Reference uses Present Perfect ("Έχεις λείψει") implying ongoing effect. MT uses Simple Past ("Έλειπες") implying completed action. Subtle but real aspect difference.

**ID #18:** `One person more or less doesn't make much difference.`
- **Human Ref:** `Ένα άτομο περισσότερο ή λιγότερο δεν κάνει και μεγάλη διαφορά.`
- **MT:** `Ένα άτομο λίγο πολύ δεν κάνει μεγάλη διαφορά.`
- **Tone/Formality Note:** Idiomatic vs Literal
- **Grammar/Pronoun Note:** Correct
- **Your Comment:** Reference is literal ("περισσότερο ή λιγότερο"). MT uses a more natural/idiomatic Greek phrase "λίγο πολύ". However

**ID #19:** `Let's try something.`
- **Human Ref:** `Ας δοκιμάσουμε κάτι!`
- **MT:** `Ας δοκιμάσουμε κάτι.`
- **Tone/Formality Note:** Tone mismatch (Exclamation vs Period)
- **Grammar/Pronoun Note:** Correct
- **Your Comment:** MT correctly translates the phrase but drops the exclamation mark present in the reference. Minor punctuation mismatch.

## 📌 Methodology
- Sample taken from the Tatoeba parallel corpus (EN-EL).
- Machine translation generated via a local LibreTranslate endpoint.
- Evaluation criteria: Meaning, Tone/Formality, Grammar/Pronouns.
- Final verdict based on combined human judgment.
