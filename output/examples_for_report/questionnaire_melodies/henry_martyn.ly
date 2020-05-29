\version "2.18.2"



\score {

<<\new Staff {
\absolute
\clef treble
\time 4/4
\key e \minor

{
\autoBeamOff
a4. 
e'8 d'8. 
e'4 g'16 
a4 
c'8. b8. 
a4 
b8 
e'4 
a'4 
d'8 a'16 a'16 
d'16 a8([ b16 ]) 
fis'4 
b8. c'8. 
b4 
a8 
e'4 
a'8 e'16 a16 
c'4. 
e'8 
a'4 
a'8 e'16 a16 
a4 
d'16 a8([ b16 ]) 
e'4 
f'16 e'8 a16 
c'4. 
e'8 
\bar "|."}
\addlyrics {
There 
were 
three 
brot -- hers 
in 
mer -- ry 
scot -- land 
In 
mer -- ry 
scot -- land 
there 
were 
three 
And 
they 
did 
cast 
lots 
which 
of 
them 
should 
go 
Should 
go 
should 
go 
And 
turn 
robb -- er 
all 
on 
the 
salt 
sea 
}
}
\new Staff {
\absolute
\clef bass
\time 4/4
\key e \minor

\set Staff.midiMaximumVolume = #0.7
< e g b >1
< a c' e' >1
< a c' e' >1
< b, dis fis >1
< e g b >1
< a c' e' >1
< e g b >1
\bar "|."}>>

  \layout {}

  \midi {}

}

