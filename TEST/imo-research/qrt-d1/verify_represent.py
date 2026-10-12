"""Original D1 independent signed-direction mathematical oracle (no official sources)."""
from __future__ import annotations

def encode(horizontal_amount:int, horizontal_direction:str, vertical_amount:int, vertical_direction:str):
    assert horizontal_amount >= 0 and vertical_amount >= 0
    assert horizontal_direction in {"E","W"} and vertical_direction in {"N","S"}
    return (horizontal_amount*(1 if horizontal_direction=="E" else -1),
            vertical_amount*(1 if vertical_direction=="N" else -1))

def decode(pair):
    x,y=pair
    return (abs(x),"E" if x>=0 else "W",abs(y),"N" if y>=0 else "S")

def verify() -> None:
    assert encode(4,"E",2,"S")==(4,-2)
    assert encode(1,"W",4,"S")==(-1,-4)
    assert decode((-3,5))==(3,"W",5,"N")
    for x in range(-8,9):
        for y in range(-8,9):
            a,e,b,n=decode((x,y))
            assert encode(a,e,b,n)==(x,y)
    print("REPRESENT-D1 289 signed-pair roundtrips plus 3 authored boundaries PASS")

if __name__=="__main__": verify()
