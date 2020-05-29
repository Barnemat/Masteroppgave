\version "2.18.2"



\score {

<<\new Staff {
\absolute
\clef treble
\time 3/4
\key g \minor

{
\autoBeamOff
g'2 
c''8 g'16 c'16 
c'4 
d'8. g'16 
a'4 
g'16 c''4. 
c''8 g'16 f'16 
g'16 
bes'2 
c''8 g'16 a'16 
ees'2 
g'8 a'8 
c'4 
d'8 g'8 
a'4 
g'2 
c''8 g'16 c'16 
c'4 
d'16 g'8. 
bes'4 
a'8 g'16 a'4 
a'8. c''8 
g'16 c''4. 
g'4 
c''16 
\bar "|."}
\addlyrics {
Earl -- y 
one 
mor -- ning 
just 
as 
the 
sun 
was 
ri -- sing 
I 
heard 
a 
maid 
sing 
in 
the 
val -- ley 
be -- low 
Oh 
don't 
de -- ceive 
me 
oh 
nev -- er 
leave 
me 
How 
could 
you 
use 
a 
poor 
mai -- den 
so 
}
}
\new Staff {
\absolute
\clef bass
\time 3/4
\key g \minor

\set Staff.midiMaximumVolume = #0.7
< g bes d' >2.
< c ees g >2.
< g bes d' >2.
< ees g bes >2.
< ees g bes >2.
< c ees g >2.
< g bes d' >2.
< c ees g >2.
< d fis a >2.
< g bes d' >2.
\bar "|."}>>

  \layout {}

  \midi {}

}

