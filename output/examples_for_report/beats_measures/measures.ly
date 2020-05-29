\version "2.18.2"



\score {

<<\new Staff {
\absolute
\clef treble
\time 4/4
\key g \major

{
\autoBeamOff
d'2 
a'2 
a'2 g'8 
a'4 
e'8 
g'4. 
a'4 
e'4 
g'8 
d'2 g'8 
a'4 
e'8 
}
}
\new Staff {
\absolute
\clef bass
\time 4/4
\key g \major

\set Staff.midiMaximumVolume = #0.7
< g b d' >1
< d fis a >1
< g b d' >1
< d fis a >1}>>

  \layout {}

}

