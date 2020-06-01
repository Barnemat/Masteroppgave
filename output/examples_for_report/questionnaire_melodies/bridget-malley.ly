\version "2.18.2"



\score {

<<\new Staff {
\absolute
\clef treble
\time 3/4
\key e \major

{
\autoBeamOff
b4 
dis'4 e'16 
e'8 dis'16 
fis'4 
gis'2 
a'4 
dis'16 e'4 
e'8 dis'16 
a'4 
dis'4 e'16 
e'16 a'8 
a'4 
dis'4 e'16 
e'8 a'16 
a'4 
dis'4 e'16 
e'8 dis'16 
a'4 
b'16 a'4 
e'8 e'16 
fis'4 
gis'2 
e'4 
dis'4 e'16 
e'16 a'8 
fis'4 
g'16 e'16 b16 e'16 
f'8. e'16 
e'4 
c'8 e'4 
e'16 b'16 
e'4}
\addlyrics {
Oh 
brid -- get 
'Mal -- ley 
you -- 've 
left 
my 
heart 
sha -- ken 
With 
a 
ho -- pe -- less 
de -- so -- la -- tion 
i'd 
have 
you 
to 
know 
It's 
the 
won -- ders 
of 
admi -- ra -- tion 
your 
quiet 
face 
has 
ta -- ken 
And 
your 
beau -- ty 
will 
haunt 
me 
whe -- rev -- er 
i 
go 
}
}
\new Staff {
\absolute
\clef bass
\time 3/4
\key e \major

\set Staff.midiMaximumVolume = #0.7
< e gis b >2.
< a, cis e b >2.
< a, cis e b >2.
< e gis b >2.
< e gis b >2.
< a, cis e b >2.
< e gis b >2.
< b, dis fis >2.
< e gis b >2.
< b, dis fis >2.
< e gis b >2.
< e gis b >2.
\bar "|."}>>

  \layout {}

  \midi {}

}

