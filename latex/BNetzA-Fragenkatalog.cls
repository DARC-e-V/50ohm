\ProvidesClass{BNetzA-Fragenkatalog}

\ExplSyntaxOn
\keys_define:nn {ptxcd/Fragenkatalog} {
	tagging .bool_gset:N = \g_ptxcd_tagging_bool,
	tagging .initial:n = false,
}
\ExplSyntaxOff

\ProcessKeyOptions[ptxcd/Fragenkatalog]

\disable@package@load{physics}{}

\LoadClass[ngerman, 10pt,twocolumn=true,fontsize=9pt,parskip=half-,listof=leveldown,bibliography=leveldown]{scrreprt}
\deftocheading{toc}{\section*{\contentsname}}

\input{settings-pre.tex}

\RequirePackage{DARC-ausbildungsmaterialien}

\input{settings.tex}
\makeatletter% to ensure right setup -> todo cleanup settings

\usepackage{geometry}
\geometry{
	a4paper,
	left=25mm,
	right=25mm,
	top=25mm,
	bottom=20mm,
	columnsep=1cm,
}
\usepackage{anyfontsize}

%\usepackage[no-math]{fontspec}
\defaultfontfeatures[BundesSans]
{
    UprightFont = BundesSans-Office-Regular.ttf,
    ItalicFont = BundesSans-Office-Italic.ttf,
    BoldFont = BundesSans-Office-Bold.ttf,
    BoldItalicFont = BundesSans-Office-BoldItalic.ttf
}
\defaultfontfeatures[BundesSerif]
{
    UprightFont = BundesSerif-Office-Regular.ttf,
    ItalicFont = BundesSerif-Office-Italic.ttf,
    BoldFont = BundesSerif-Office-Bold.ttf,
    BoldItalicFont = BundesSerif-Office-BoldItalic.ttf
}
\setsansfont{BundesSans}
\setmainfont{BundesSerif}


\AfterTOCHead[toc]{\sffamily}

\definecolor{BNetzAblue}{RGB}{28,71,113}
\definecolor{BNetzAgray}{RGB}{127,127,127}

\addtokomafont{section}{\color{BNetzAblue}\fontsize{22pt}{25pt}\selectfont}
\setkomafont{chapter}{\usekomafont{section}}
\addtokomafont{subsection}{\color{BNetzAblue}\fontsize{15pt}{18pt}\selectfont}
\addtokomafont{subsubsection}{\color{BNetzAblue}\fontsize{11pt}{15pt}\selectfont}

\setcounter{secnumdepth}{4}
\setcounter{tocdepth}{4}

\RedeclareSectionCommand[style=chapter,afterindent=false,beforeskip=0pt,afterskip=20pt,tocindent=0pt,tocentryformat=\bfseries\fontsize{11pt}{14pt}\selectfont,
	tocpagenumberformat=\sffamily\bfseries,
	tocnumwidth=2em,
	tocentrybeforeskip=\baselineskip]{section}
\RedeclareSectionCommand[
	beforeskip=6pt,runin=false,
	afterskip=12pt,
	tocentrybeforeskip=1em plus 1pt,
	tocentrynumwidth=2.5em,
	tocentryentryformat=\bfseries,
	tocindent=0pt
	]{subsection}
\RedeclareSectionCommand[
	beforeskip=\baselineskip,
	runin=false,
	afterskip=1ex plus .2ex,
	tocindent=2.5em]{subsubsection}
\RedeclareSectionCommand[beforeskip=0pt,runin=false,afterskip=15pt]{paragraph}
\RedeclareSectionCommand[beforeskip=\baselineskip,runin=false,afterskip=15pt]{subparagraph}

\renewcommand*{\thesection}{\arabic{section}}
\renewcommand*{\chapterpagestyle}{scrheadings}

\renewcommand\addsectiontocentry[2]{%
    \addtocentrydefault{section}{#1}{\TOCUppercase{#2}}%
}

\ExplSyntaxOn
\DeclareRobustCommand{\TOCUppercase}[1]{\texorpdfstring{\text_uppercase:n {#1}}{#1}}
\ExplSyntaxOff

\KOMAoptions{parskip=full-}

\usepackage[footsepline=false] {scrlayer-scrpage}

\setkomafont{pageheadfoot}{\sffamily\footnotesize}
\setkomafont{pagenumber}{\sffamily\bfseries\textcolor{white}}

\DeclareNewLayer[
  background,
  topmargin,
  mode=picture,
  oddpage,
  outermargin,
  addhoffset=-10mm,
  width=10mm,
  height=15mm,
  contents={
    \putLL{%
        \textcolor{BNetzAgray}{\rule{10mm}{\layerheight}}%
    }
    \putC{\makebox(0,0){\pagemark}}
}
]{swatch.odd}
\DeclareNewLayer[
  clone=swatch.odd,
  evenpage,
  addhoffset=38mm
]{swatch.even}
% add the layers to pagestyle scrheadings:
\AddLayersAtBeginOfPageStyle{scrheadings}{swatch.odd,swatch.even}

\raggedbottom
\raggedright% flush left alignment

\ExplSyntaxOn
\bool_if:NT \g_ptxcd_tagging_bool {\file_input:n {tagging-setup}}
\ExplSyntaxOff


\setcounter{page}{5}%Manual page offset, handle with care!

\endinput
