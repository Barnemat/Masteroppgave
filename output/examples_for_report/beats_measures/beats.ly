\version "2.18.2"



\score {

<<\new Staff {
\absolute
\clef treble
\time 3/4
\key d \major
\autoBeamOff

{
cis'4 
a8 
a16([ d'16 ]) 
a''8 
d'4 
e'8 
cis'4 
a8 
d'8([ e'8 ]) 
cis'1 
a8 
a8 
d'8([ e'8 ]) 
b'1
}
}
\new Staff {
\absolute
\clef bass
\time 3/4
\key d \major
< g, b, d >2.
< d fis a b >2.
< a, cis e b >2.
< a, cis e b >2.
< a, cis e b >2.
}>>

  \layout {}

  \midi {}

}

