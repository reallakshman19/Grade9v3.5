"""Original TEST QRT-RETRIEVE-D1: independent divisor-count oracle."""
def divisors(n):
    assert isinstance(n,int) and n>0
    return [d for d in range(1,n+1) if n % d == 0]

def classify(n):
    c=len(divisors(n))
    return "PRIME" if c == 2 else "COMPOSITE" if c > 2 else "NEITHER"

def verify():
    expected={1:([1],"NEITHER"),2:([1,2],"PRIME"),9:([1,3,9],"COMPOSITE"),13:([1,13],"PRIME"),22:([1,2,11,22],"COMPOSITE"),23:([1,23],"PRIME"),25:([1,5,25],"COMPOSITE")}
    for n,(ds,category) in expected.items():
        assert divisors(n)==ds, (n,divisors(n),ds)
        assert classify(n)==category,(n,category)
    for n in range(1,101):
        ds=divisors(n)
        assert ds[0]==1 and ds[-1]==n
        assert len(ds)==len(set(ds))
        assert all(n%d==0 for d in ds)
        assert classify(n)==("PRIME" if len(ds)==2 else "COMPOSITE" if len(ds)>2 else "NEITHER")
    print("RETRIEVE-D1: 100 complete divisor-card classifications + 7 boundary fixtures PASS")

if __name__ == "__main__":
    verify()
