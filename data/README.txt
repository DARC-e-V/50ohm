Prüfungsfragen zum Erwerb von Amateurfunkprüfungsbescheinigungen
3. Auflage, März 2024

Hinweis:
========

Die Prüfungsfragen werden in maschinenlesbarer Form von der 
Bundesnetzagentur für Elektrizität, Gas, Telekommunikation, Post und Eisenbahnen, 
Tulpenfeld 4, 53113 Bonn
unter der Datenlizenz DL-DE->BY-2.0 bereitgestellt.

Die bereitgestellten Daten und Metadaten dürfen für die kommerzielle und nicht kommerzielle Nutzung insbesondere 
vervielfältigt, ausgedruckt, präsentiert, verändert, bearbeitet sowie an Dritte übermittelt werden;
mit eigenen Daten und Daten Anderer zusammengeführt und zu selbständigen neuen Datensätzen verbunden werden;
in interne und externe Geschäftsprozesse, Produkte und Anwendungen in öffentlichen und nicht öffentlichen 
elektronischen Netzwerken eingebunden werden.

Bei der Nutzung ist sicherzustellen, dass folgende Angaben als Quellenvermerk enthalten sind:

"Prüfungsfragen zum Erwerb von Amateurfunkprüfungsbescheinigungen, Bundesnetzagentur, 3. Auflage, März 2024, 
(www.bundesnetzagentur.de/amateurfunk), Datenlizenz Deutschland – Namensnennung – Version 2.0 
(www.govdata.de/dl-de/by-2-0)"

Veränderungen, Bearbeitungen, neue Gestaltungen oder sonstige Abwandlungen sind im Quellenvermerk mit dem Hinweis 
zu versehen, dass die Daten geändert wurden.


Anleitung:
==========

Die maschinenlesbare Version der Prüfungsfragen teilt sich in zwei Teile auf:

    1. Die Struktur des Katalogs und die Prüfungsfragen als JSON-Datei
    2. Alle Bilder zu den Prüfungsfragen als SVG-Dateien

Das JSON-Schema besteht aus Kapiteln "sections", die jeweils einen Titel
"title" beinhalten. Eine Section kann entweder weitere Unterkapitel "sections"
beinhalten, oder eine Liste von Prüfungsfragen "questions". Eine Prüfungsfrage
beinhaltet folgende Attribute:

    - "number"           : Die Prüfungsnummer im Fragenkatalog
    - "class"            : Die Klasse (1:N, 2:E, 3:A)
    - "question"         : Der Fragenkopf
    - "answer_a"         : Die richtige Antwort A
    - "answer_b"         : Ein Distraktor B (falsche Antwort)
    - "answer_c"         : Ein Distraktor C (falsche Antwort)
    - "answer_d"         : Ein Distraktor D (falsche Antwort)
    - "picture_question" : Das Fragenbild [Optional]
    - "picture_a"        : Das Antwortbild A [Optional]
    - "picture_b"        : Das Antwortbild B [Optional]
    - "picture_c"        : Das Antwortbild C [Optional]
    - "picture_d"        : Das Antwortbild D [Optional]

Die Prüfungsfragen enthalten LaTeX-Code für die Darstellung der Formeln. Diese
können durch verschiedene Bibliotheken z. B. durch KaTeX (https://katex.org)
angezeigt werden.

