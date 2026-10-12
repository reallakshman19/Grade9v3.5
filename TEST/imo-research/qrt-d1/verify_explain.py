"""Original EXPLAIN-D1 mechanism oracle, no official exam material."""
def leftover(n):
    assert isinstance(n,int) and n>=0
    return n//2,n%2

def explain_odd_plus_odd(a,b):
    assert a>0 and b>0 and a%2==1 and b%2==1
    full_a,lone_a=leftover(a)
    full_b,lone_b=leftover(b)
    assert lone_a==lone_b==1
    new_pairs=(lone_a+lone_b)//2
    combined_pairs=full_a+full_b+new_pairs
    assert combined_pairs*2==a+b
    assert (lone_a+lone_b)%2==0
    return combined_pairs

def verify():
    assert explain_odd_plus_odd(3,5)==4
    assert explain_odd_plus_odd(7,9)==8
    assert explain_odd_plus_odd(5,7)==6
    assert explain_odd_plus_odd(11,13)==12
    assert leftover(9+4)==(6,1)
    total=18
    known=7
    remaining=total-known
    assert remaining==11
    assert leftover(total)[1]==0
    assert leftover(known)[1]==1 and leftover(remaining)[1]==1
    count=0
    for a in range(1,30,2):
        for b in range(1,30,2):
            explain_odd_plus_odd(a,b)
            count+=1
    print(f"EXPLAIN-D1 {count} odd-pair causal mechanism cases + 6 authored boundary facts PASS")

if __name__=="__main__":
    verify()
