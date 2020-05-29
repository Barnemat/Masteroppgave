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
fis'2. 
c'4 
d'8 g'2 
e'4 
g'16 e'16 
g'4. 
c''16 b'16 g'8 
a'4 
e'8 
b'2. 
c''8 b'16 g'16 
d'8 g'2 
e'4 
b'16 e'16 
a'2 b'8 
a'4 
e'8 
g'16 e'4 d'16 
e'4 
a'4 
g'8 
\bar "|."}
\addlyrics {
There's 
an 
old 
mill 
by 
the 
stream 
Nel -- lie 
Dean 
Where 
we 
used 
to 
sit 
and 
dream 
Nel -- lie 
Dean 
And 
the 
wat -- ers 
as 
they 
flow 
Seem 
to 
mur -- mur 
sweet 
and 
low 
You're 
my 
heart's 
de -- si -- re 
i 
love 
you 
Nel -- lie 
Dean 
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
< d fis a >1
< b, d fis >1
< g b d' >1
< g b d' >1
< b, d fis >1
< g b d' >1
< d fis a >1
< g b d' >1
\bar "|."}>>

  \layout {}

  \midi {}

}

