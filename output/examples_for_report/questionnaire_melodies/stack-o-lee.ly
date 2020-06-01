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
f'16 g'8 a'16 
a'2 
d'16 e'8 g'16 
c''2 
a'8 g'16 a'16 
g'8 c''16 bes'16 
ees'2 
c''2 
f'8 g'16 a'16 
a'4. b'16 
f'4 
d'16 
g'16 c''16 bes'8 
ees'2 
d'4 
f'16 g'16 a'8 
d'8. a'16 
g'2}
\addlyrics {
I 
re -- mem -- ber 
one 
sep -- tem -- ber 
on 
a 
frid -- ay 
night 
Stack 
o' 
lee 
and 
Bil -- ly 
ly -- ons 
had 
a 
great 
fight 
Crying 
when 
you 
lose 
your 
mon -- ey 
learn 
to 
lose 
}
}
\new Staff {
\absolute
\clef bass
\time 3/4
\key g \minor

\set Staff.midiMaximumVolume = #0.7
< g bes d' >2.
< a, c e >2.
< c ees g >2.
< g bes d' >2.
< c ees g >2.
< d fis a >2.
< g bes d' >2.
< g bes d' >2.
< g bes d' >2.
\bar "|."}>>

  \layout {}

  \midi {}

}

