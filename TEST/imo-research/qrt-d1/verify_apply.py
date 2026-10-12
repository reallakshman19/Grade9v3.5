"""QRT APPLY-D1 original rectangle-area mathematical checks."""
def area(length:int,width:int)->int:
    assert isinstance(length,int) and isinstance(width,int) and length>0 and width>0
    return length*width

def recover_length(given_area:int,width:int)->int:
    assert given_area>0 and width>0 and given_area%width==0
    return given_area//width

def verify():
    assert area(3,5)==15
    assert area(7,4)==28
    assert area(5,3)==15
    assert area(4,4)==16
    assert area(8,2)==16
    assert recover_length(24,4)==6
    tested=0
    for length in range(1,26):
        for width in range(1,26):
            a=area(length,width)
            assert recover_length(a,width)==length
            tested+=1
    print(f"APPLY-D1: {tested} rectangle area/inverse checks + 6 authored boundaries PASS")

if __name__=="__main__":
    verify()
