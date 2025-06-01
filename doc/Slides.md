# Erstellen von Folien

Das Erstellen von Folien ist direkt im Directus möglich. Wir verwenden reveal.js als Framework, um die Inhalte darzustellen.

## Directus

Im Directus gibt es zu jeder Sektion ein Feld _Slide_ in dem vereinfacht die Inhalte von Folien eingegeben werden können.

## Unterstützte Formate

### Folientrennung

Jede Folie (außer die erste) beginnt mit `---`. Dadurch wird eine neue Folie erzeugt.

#### Spezielle Folien

Reveal.js erlaubt es, Folien bestimmte Attribute, wie beispielsweise die Hintergrundfarbe zu übermitteln. Das kann direkt beim Erstellen einer Folie angegeben werden.

``` MarkDown
--- data-background="#FF0000"
```

Dadurch wird die Folie in knallrot gefärbt. Das sollte nur in Ausnahmen verwendet werden.

Alternativ werden drei Begriffe ausgewertet, die bereits auf der Webseitenansicht zum Einsatz kommen.

``` MarkDown
--- unit
```

Wird verwendet, um eine neue Einheit einzuführen.
Färbt die Folie hellgrün ein.

``` MarkDown
--- attention
```

Wird verwendet, um die Aufmerksamkeit zu erregen. Beispielsweise bei Hinweisen auf die Gültigkeit bei Inkrafttreten der AfuV.
Färbt die Folie hellblau ein.

``` attention
--- danger
```

Wird verwendet, um auf Gefahren hinzuweisen. Beispielsweise beim Umgang mit elektrischem Strom.
Färbt die Folie hellrot ein.

### Überschriften

Überschriften werden mit dem `#`-Zeichen eingeleitet. Dabei gibt die Häufigkeit des Zeichens die Ebene der Überschrift an.

``` MarkDown
# Überschrift 1
## Überschrift 2
### Überschrift 3
```

Die maximale Ebene ist 6.

### Listen

Häufig sind auf Folien Listen zu sehen. Diese lassen sich mit `*` einleiten.

``` MarkDown
* Listenpunkt
* Noch ein Listenpunkt
```

TODO: Verschachtelte Listen sind noch nicht möglich

### Tabellen

Tabellen werden mit Zeichen `|` zur Unterteilung der Spalten gesetzt. Die erste Spalte ist eine Kopfspalte. In ihr kann angegeben werden, ob der Inhalt der Spalte linksbündig (`l`), rechtsbündig (`r`) oder mittig (`c`) ausgerichtet sein soll.

``` Markdown
| l: Wert | l: Bereich | l: Bedeutung | l: Englisch |
| R | 1 - 5 | Lesbarkeit | Readability |
| S | 1 - 9 | Signalstärke | Signal Strength |
| T | 1 - 9 | Tonqualität | Tone |
[table:n_rst:Die Bestandteile des RST-Rapports]
```

Die Tabelle muss mit `[table:referenz:Beschreibung]` abgeschlossen werden. Dadurch wird intern eine Referenz gesetzt, auf die verwiesen werden kann.

### Textauszeichnung

Es kann einfache Textauszeichnung, wie _hervorgehoben_ oder <u>unterstrichen</u> verwendet werden.

``` MarkDown
Es kann einfache Textauszeichnung, wie *hervorgehoben* oder <u>unterstrichen</u> verwendet werden.
```

### Bilder

Bilder werden mit einer Referenz auf das Bild in der Datenbank eingefügt.

``` MarkDown
[photo:123:n_rst_s-meter:Display eines IC9700-Transceivers, hervorgehoben ist das S-Meter, das den aktuellen Empfangspegel anzeigt]
```

Es kann `photo` oder `picture` verwendet werden, je nach Datenbanktabelle in der das Bild abgelegt ist. Als nächstes wird die Nummer des Bildes angegeben. Darauf folgt eine Referenz für Verweise. Und abschließend die Beschreibung, die unter dem Bild angezeigt wird. Die Bilder werden pro Dokument durchnummeriert.

### Fragen aus dem Prüfungskatalog

Fragen aus dem Fragenkatalog können durch eine Referenz auf die Fragennummer eingefügt werden.

``` Markdown
[question:2482]
```

Fragen sollten auf einer eigenen Folie angezeigt werden, da sie in der Regel sehr groß sind.

``` Markdown
---
[question:2482]
---
```

Die Antworten werden beim Erstellen der Folien in eine zufällige Reihenfolge gebracht, sodass nicht wie im Prüfungskatalog die erste Antwort die richtige ist.

### QSO

Ein beispielhaftes QSO kann folgendermaßen hinzugefügt werden:

``` Markdown
<qso>
Ist diese Frequenz frei? DL1PZ
> *(keine Antwort)*
Ist diese Frequenz frei? DL1PZ
> *(keine Antwort)*
CQ CQ hier ist DL1PZ mit einem allgemeinen Anruf, hier ist DL1PZ und hört.
> DL1PZ hier ist DL9MJ bitte kommen
</qso>
```

Jede Zeile ist eine Sprechblase. Die einzelnen Sprechblasen werden nacheinander aufgedeckt. Zeilen, die mit `>` beginnen, werden als Teil der Gegenstelle angezeigt.

### Einblendeeffekt

Soll ein Teil der Folie erst später aufgedeckt werden, kann dieser in `<fragment>` eingebettet werden.

``` MarkDown
<fragment>
Dieser Text erscheint erst später.
</fragment>
```

Mehrere `<fragment>`-Abschnitte nacheinander sorgen dafür, dass die Inhalte Schritt für Schritt aufgedeckt werden.

### Notizen

Es ist möglich, Notizen für den oder die Vortragende hinzuzufügen. Die sind nur in der "Speaker-Ansicht" (Taste 's' drücken) sichtbar.

Sinnvoll sind kurze Hinweise auf die Erklärungen, die in der Webseitenversion gegeben werden oder Hintergrundinformationen. Die brauchen nicht auf die Folien. Und kurze Hinweise sollten für Funkamateure ausreichend sein, um die Notiz zu verstehen und den Inhalt zu vermitteln.

``` MarkDown
<note>
Die Notiz wird nur in der Speaker-Ansicht angezeigt
* Listen sind auch möglich
* Am besten kurz halten
* Der Platz ist begrenzt
</note>
```

### Formeln

Es können Formeln im LaTeX-Stil angegeben werden. Diese werden in `$` gesetzt.

``` MarkDown
$\lambda[[\text{m}]] = \dfrac{300}{f[[\text{MHz}]]} = \dfrac{300}{145,3 \ \text{MHz}} \approx 2,06 \ \text{m}$
```

Abweichend von LaTeX müssen die rechteckigen Klammern gedoppelt werden.

### Links

Es können Links eingefügt werden.

``` MarkDown
[Link zum DARC](https://darc.de/)
```

### Zwei Spalten

Manchmal ist es sinnvoll, zwei Spalten zu verwenden. Beispielsweise bei einem Bild mit Beschreibung. Dazu gibt es die beiden Tags `<left>` und `<right>`.

``` MarkDown
<left>
[photo:167:rufzeichen_flugzeug:Flugzeug mit dem Rufzeichen DEBPF]
</left>
<right>
* Funkstationen verwenden Rufzeichen, um sich zu identifizieren
* Folge von Buchstaben und Ziffern
* Jedes mit Funk ausgerüstete Flugzeug und Schiff hat ein Rufzeichen
</right>
```

### Webseite interaktiv einbetten

Es kann eine ganze Webseite interaktiv eingebettet werden, sodass darin agiert werden kann. Zusätzlich sind die Navigationspfeile und der Speaker-View erhalten.

``` MarkDown
--- data-background-iframe="https://f5len.org/tools/locator/" data-background-interactive

<note>
* Es wird eine interaktive Karte mit Maidenhead-Locator gezeigt.
</note>
```

Zusätzlich eine Speaker-Note einzufügen ist sinnvoll, um keine leere Slide zu erzeugen und den Speaker darauf hinzuweisen, dass die Webseite nur vom Hauptbildschirm bedient werden kann.

### Kleinere Schrift

In ganz seltenen Ausnahmen kann eine kleinere Schrift verwendet werden. Das kann dann angewandt werden, wenn ein oder zwei Zeilen einer Tabelle nicht mehr auf die Folie passen.

``` MarkDown
--- style="font-size: smaller;"

* Längere
* Liste
```

### Direkter Übergang

Ohne verschieben der Folie zur nächsten Schalten. Das kann als Effekt genutzt werden, damit auf der Folie ein Austauscheffekt stattfindet.

```MarkDown
---
## Folie
Mit Text
--- data-transition="none"
## Folie
Mit anderem Text
```
