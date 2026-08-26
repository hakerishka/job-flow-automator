// ==========================================
// KANONISCHER ATS-LEBENSLAUF (main_de.template.typ)
// ==========================================
// Kopieren Sie diese Datei nach `main_de.typ` und tragen Sie Ihre Kontaktdaten ein.
// Variablen aus tailored.typ werden automatisch importiert.

#import "tailored.typ": target-role, summary, skills, experience

#set page(
  paper: "a4",
  margin: (x: 1.2cm, top: 0.85cm, bottom: 0.85cm),
)

#set text(
  font: "Liberation Sans",
  size: 9.1pt,
  fill: rgb("#111111"),
  lang: "de",
)

#set par(justify: false, leading: 0.50em)

// Strikte Standard-Überschriften
#show heading.where(level: 1): it => {
  v(0.35em)
  text(weight: "bold", size: 9.8pt)[#upper(it.body)]
  v(-0.38em)
  line(length: 100%, stroke: 0.5pt + rgb("#666666"))
  v(0.12em)
}

// --- KOPFZEILE (Passen Sie Ihre persönlichen Kontaktdaten an) ---
#align(center)[
  #text(weight: "bold", size: 14pt)[VOLLSTÄNDIGER NAME]\
  #v(-0.25em)
  #text(weight: "bold", size: 9.5pt, fill: rgb("#333333"))[#target-role]\
  #v(0.1em)
  #text(size: 8.5pt)[
    Stadt, Land · #link("mailto:ihre.email@example.com")[ihre.email\@example.com] · +49 123 4567890 · #link("https://linkedin.com/in/ihrprofil")[linkedin.com/in/ihrprofil] · #link("https://github.com/ihrbenutzername")[github.com/ihrbenutzername]
  ]\
  #text(size: 8pt, fill: rgb("#444444"))[
    Volle Arbeitserlaubnis für Deutschland · Sprachen: Deutsch (Verhandlungssicher), Englisch (Fließend)
  ]
]

// --- DYNAMISCHE ABSCHNITTE (Generiert vom ATS Tailor Engine) ---
= Profil
#summary

= Kenntnisse & Fähigkeiten
#skills

= Berufserfahrung
#experience

// --- STATISCHE ABSCHNITTE (Passen Sie Ihre statischen Einträge an) ---
= Projekte & Initiativen
- *Ausgewählter Projektname* #h(1fr) 2022 – Heute\
  Beschreibung der Projektergebnisse, Kernarchitektur und messbaren Erfolge.

= Ausbildung & Zertifikate
- *Abschlussbezeichnung im Fachbereich* — Universität / Kolleg Name #h(1fr) 2018 – 2022
- *Zertifikatsbezeichnung* — Ausstellende Organisation #h(1fr) 2023
